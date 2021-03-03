import os

from gettext import gettext as _

from django.conf import settings
from django.core.management import BaseCommand, CommandError
from django.db.models import Q
from pulpcore import constants
from pulpcore.app import pulp_hashlib
from pulpcore.plugin.models import Artifact, ContentArtifact, RemoteArtifact, RepositoryVersion

import logging

log = logging.getLogger("")

CHUNK_SIZE = 1024 * 1024  # 1 Mb


def _show_on_demand_content(checksums):
    query = Q(pk__in=[])
    for checksum in checksums:
        query |= Q(**{f"{checksum}__isnull": False})
    remote_artifacts = RemoteArtifact.objects.filter(query)

    content = (
        ContentArtifact.objects.filter(remoteartifact__pk__in=remote_artifacts)
        .filter(artifact=None)
        .values_list("content", flat=True)
    )
    repo_versions = RepositoryVersion.has_content(content)

    print(_("Found {} on-demand content units with forbidden checksums.").format(content.count()))

    if repo_versions.exists():
        print(_("\nAffected repository versions:"))
        for repo_version in repo_versions:
            print(_("{} (version {})").format(repo_version.repository.name, repo_version.number))


class Command(BaseCommand):
    """
    Django management command for populating or removing checksums on artifacts.
    """

    help = _("Handle missing and forbidden checksums on the artifacts")

    def add_arguments(self, parser):
        parser.add_argument("--report", action="store_true")
        parser.add_argument("--checksums", help=_("Comma separated list of checksums to evaluate"))

    def _download_artifact(self, artifact, checksum, file_path):
        restored = False
        for ca in artifact.content_memberships.all():
            if not restored:
                for ra in ca.remoteartifact_set.all():
                    remote = ra.remote.cast()
                    if remote.policy == "immediate":
                        self.stdout.write(_("Restoring missing file {}").format(file_path))
                        downloader = remote.get_downloader(ra)
                        dl_result = downloader.fetch()
                        # FIXME in case url is not available anymore this will break
                        if dl_result.artifact_attributes["sha256"] == artifact.sha256:
                            with open(dl_result.path, "rb") as src:
                                filename = artifact.file.name
                                artifact.file.save(filename, src, save=False)
                            setattr(artifact, checksum, dl_result.artifact_attributes[checksum])
                            restored = True
                            break
            else:
                break
        return restored

    def _report(self, checksums):
        if checksums:
            checksums = checksums.split(",")
            if "sha256" not in checksums:
                raise CommandError(_("Checksums must contain sha256"))
        else:
            checksums = settings.ALLOWED_CONTENT_CHECKSUMS

        forbidden_checksums = set(constants.ALL_KNOWN_CONTENT_CHECKSUMS).difference(checksums)

        _show_on_demand_content(forbidden_checksums)

    def handle(self, *args, **options):

        if options["report"]:
            self._report(options["checksums"])
            return

        if options["checksums"] and not options["report"]:
            print(_("Checksums cannot be supplied with --report argument"))
            exit(1)

        log.setLevel(logging.ERROR)
        hrefs = set()
        for checksum in settings.ALLOWED_CONTENT_CHECKSUMS:
            params = {f"{checksum}__isnull": True}
            artifacts_qs = Artifact.objects.filter(**params)
            for a in artifacts_qs:
                hasher = pulp_hashlib.new(checksum)
                try:
                    for chunk in a.file.chunks(CHUNK_SIZE):
                        hasher.update(chunk)
                    a.file.close()
                    setattr(a, checksum, hasher.hexdigest())
                except FileNotFoundError:
                    file_path = os.path.join(settings.MEDIA_ROOT, a.file.name)
                    restored = self._download_artifact(a, checksum, file_path)
                    if not restored:
                        hrefs.add(file_path)

            if artifacts_qs:
                self.stdout.write(_("Updating artifacts with missing checksum {}").format(checksum))
                Artifact.objects.bulk_update(objs=artifacts_qs, fields=[checksum], batch_size=1000)
        if hrefs:
            raise CommandError(
                _("Some files that were missing could not be restored: {}").format(hrefs)
            )

        forbidden_checksums = set(constants.ALL_KNOWN_CONTENT_CHECKSUMS).difference(
            settings.ALLOWED_CONTENT_CHECKSUMS
        )
        for checksum in forbidden_checksums:
            search_params = {f"{checksum}__isnull": False}
            update_params = {f"{checksum}": None}
            artifacts_qs = Artifact.objects.filter(**search_params)
            if artifacts_qs:
                self.stdout.write(
                    _("Removing forbidden checksum {} from database").format(checksum)
                )
                artifacts_qs.update(**update_params)

        self.stdout.write(_("Finished aligning checksums with settings.ALLOWED_CONTENT_CHECKSUMS"))
