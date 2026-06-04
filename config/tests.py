from django.apps import apps
from django.conf import settings
from django.test import SimpleTestCase
from django.urls import reverse

from config.settings import base


class ProjectBootTests(SimpleTestCase):
    def test_home_page_loads(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ClassPulse")

    def test_expected_apps_are_installed(self):
        for app_name in ("accounts", "courses", "attendance", "reports"):
            with self.subTest(app_name=app_name):
                self.assertTrue(apps.is_installed(app_name))

    def test_custom_user_model_is_configured(self):
        self.assertEqual(settings.AUTH_USER_MODEL, "accounts.User")

    def test_database_settings_use_postgresql_outside_tests(self):
        self.assertEqual(
            base.DATABASES["default"]["ENGINE"],
            "django.db.backends.postgresql",
        )

    def test_test_command_uses_isolated_sqlite_database(self):
        self.assertEqual(
            settings.DATABASES["default"]["ENGINE"],
            "django.db.backends.sqlite3",
        )
