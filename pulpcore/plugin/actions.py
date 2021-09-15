from gettext import gettext as _
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework.serializers import ValidationError

from pulpcore.app import tasks
from pulpcore.app.models import Content, RepositoryVersion
from pulpcore.app.response import OperationPostponedResponse
from pulpcore.app.serializers import (
    AsyncOperationResponseSerializer,
    RepositoryAddRemoveContentSerializer,
)
from pulpcore.app.viewsets import NamedModelViewSet
from pulpcore.tasking.tasks import dispatch


__all__ = ["ModifyRepositoryActionMixin"]


class ModifyRepositoryActionMixin:
    @extend_schema(
        description="Trigger an asynchronous task to create a new repository version.",
        summary="Modify Repository Content",
        responses={202: AsyncOperationResponseSerializer},
    )
    @action(detail=True, methods=["post"], serializer_class=RepositoryAddRemoveContentSerializer)
    def modify(self, request, pk):
        """
        Queues a task that creates a new RepositoryVersion by adding and removing content units
        """
        add_content_units = []
        remove_content_units = []
        repository = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if "base_version" in request.data:
            base_version_pk = self.get_resource(request.data["base_version"], RepositoryVersion).pk
        else:
            base_version_pk = None

        if "add_content_units" in request.data:
            add_content_units = self._extract_content_units(request.data["add_content_units"])
            add_content_units.touch()

        if "remove_content_units" in request.data:
            if "*" in request.data["remove_content_units"]:
                remove_content_units = ["*"]
            else:
                remove_content_units = self._extract_content_units(request.data["remove_content_units"])

        task = dispatch(
            tasks.repository.add_and_remove,
            exclusive_resources=[repository],
            kwargs={
                "repository_pk": pk,
                "base_version_pk": base_version_pk,
                "add_content_units": add_content_units,
                "remove_content_units": remove_content_units,
            },
        )
        return OperationPostponedResponse(task, request)

    def _extract_content_units(self, content_units):
        """Extract and verify content units."""
        content_map = {NamedModelViewSet.extract_pk(url): url for url in content_units}
        existing_pks = Content.objects.filter(pk__in=content_map.keys())

        missing_pks = set(content_map.keys()) - set(existing_pks.values_list("pk", flat=True))
        if missing_pks:
            missing_hrefs = [content_map[pk] for pk in missing_pks]
            raise ValidationError(
                _("Could not find the following content units: {}").format(missing_hrefs)
            )
        return content_map.keys()
