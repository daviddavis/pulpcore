import os
from gettext import gettext as _

from django.conf import settings
from django.db.models import FileField

from pulpcore.app.files import TemporaryDownloadedFile


class ArtifactFileField(FileField):
    """
    A custom FileField that always saves files to location specified by 'upload_to'.

    The field can be set as either a path to the file or File object. In both cases the file is
    moved or copied to the location specified by 'upload_to' field parameter.
    """

    def pre_save(self, model_instance, add):
        """
        Return FieldFile object which specifies path to the file to be stored in database.

        There are two ways to get artifact into Pulp: sync and upload.

        The upload case
         - file is not stored yet, aka file._committed = False
         - nothing to do here in addition to Django pre_save actions

        The sync case:
         - file is already stored in a temporary location, aka file._committed = True
         - it needs to be moved into Pulp artifact storage if it's not there
         - TemporaryDownloadedFile takes care of correctly set storage path
         - only then Django pre_save actions should be performed

        Args:
            model_instance (`class::pulpcore.plugin.Artifact`): The instance this field belongs to.
            add (bool): Whether the instance is being saved to the database for the first time.
                        Ignored by Django pre_save method.

        Returns:
            FieldFile object just before saving.

        """
        file = model_instance.file
        artifact_storage_path = self.upload_to(model_instance, "")

        if file.name != artifact_storage_path and file.name.startswith(
            os.path.join(settings.MEDIA_ROOT, "artifact")
        ):
            raise ValueError(
                _(
                    "The file referenced by the Artifact is already present in "
                    "Artifact storage. Files must be stored outside this location "
                    "prior to Artifact creation."
                )
            )

        move = file._committed and file.name != artifact_storage_path
        if move:
            file._file = TemporaryDownloadedFile(open(file.name, "rb"))
            file._committed = False

        return super().pre_save(model_instance, add)
