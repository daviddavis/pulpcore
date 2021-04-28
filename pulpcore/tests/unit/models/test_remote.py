from uuid import uuid4

from django.db import connection
from django.test import TestCase, override_settings

from pulpcore.app.models import Remote
from pulpcore.app.models.fields import EncryptedTextField


class RepositoryTestCase(TestCase):
    def setUp(self):
        self.remote = None

    def tearDown(self):
        if self.remote:
            self.remote.delete()

    @override_settings(SECRET_KEY="test")
    def test_encrypted_proxy_password(self):
        self.remote = Remote(name=uuid4(), proxy_password="test")
        self.remote.save()
        self.assertEqual(Remote.objects.get(pk=self.remote.pk).proxy_password, "test")

        # check the database that proxy_password is encrypted
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT proxy_password FROM core_remote " f"WHERE pulp_id = '{self.remote.pulp_id}'"
            )
            db_proxy_password = cursor.fetchone()[0]
            proxy_password = EncryptedTextField().from_db_value(db_proxy_password, None, connection)
            self.assertEqual(proxy_password, "test")
