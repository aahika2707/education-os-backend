"""Smoke tests for core primitives (envelope, pagination meta, cache helpers)."""
from django.test import TestCase

from core.cache import cache_get_or_set, cache_key, invalidate
from core.renderers import EnvelopeJSONRenderer


class CacheHelperTests(TestCase):
    def test_cache_key_joins_parts(self):
        self.assertEqual(cache_key("dashboard", "student", "42"), "dashboard:student:42")

    def test_get_or_set_computes_once(self):
        calls = {"n": 0}

        def producer():
            calls["n"] += 1
            return "value"

        key = cache_key("test", "once")
        self.assertEqual(cache_get_or_set(key, 60, producer), "value")
        self.assertEqual(cache_get_or_set(key, 60, producer), "value")
        self.assertEqual(calls["n"], 1)
        invalidate(key)


class EnvelopeRendererTests(TestCase):
    def _render(self, data, status_code=200):
        renderer = EnvelopeJSONRenderer()
        return renderer._build_envelope(data, status_code)

    def test_wraps_success(self):
        env = self._render({"x": 1})
        self.assertEqual(env["status"], "success")
        self.assertEqual(env["data"], {"x": 1})
        self.assertNotIn("errors", env)
        self.assertNotIn("meta", env)

    def test_keeps_pagination_shape(self):
        env = self._render({"results": [1, 2], "pagination": {"count": 2}})
        self.assertEqual(env["status"], "success")
        self.assertEqual(env["data"], {"results": [1, 2], "pagination": {"count": 2}})

    def test_error_body_passes_through(self):
        body = {"status": "error", "message": "nope", "errors": []}
        self.assertEqual(self._render(body, status_code=400), body)
