from django.conf import settings
from django.test import TestCase


class CorsConfigurationTests(TestCase):
    def test_origins_are_explicit_not_wildcard(self):
        self.assertIn("http://127.0.0.1:5173", settings.CORS_ALLOWED_ORIGINS)
        self.assertIn("http://localhost:5173", settings.CORS_ALLOWED_ORIGINS)
        self.assertNotIn("*", settings.CORS_ALLOWED_ORIGINS)

    def test_preflight_from_react_origin_is_allowed(self):
        response = self.client.options(
            "/api/exams/",
            HTTP_ORIGIN="http://127.0.0.1:5173",
            HTTP_ACCESS_CONTROL_REQUEST_METHOD="GET",
            HTTP_ACCESS_CONTROL_REQUEST_HEADERS="authorization,content-type",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers.get("Access-Control-Allow-Origin"),
            "http://127.0.0.1:5173",
        )

    def test_preflight_from_other_origin_is_not_allowed(self):
        response = self.client.options(
            "/api/exams/",
            HTTP_ORIGIN="http://evil.example",
            HTTP_ACCESS_CONTROL_REQUEST_METHOD="GET",
        )
        self.assertNotIn("Access-Control-Allow-Origin", response.headers)
