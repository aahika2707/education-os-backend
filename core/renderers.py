"""Response envelope renderer.

Wraps every successful response body in the spec envelope
``{status:"success", message, data}``. Paginated payloads (from
:class:`core.pagination.StandardPagination`) keep their
``{results, pagination}`` shape as ``data``. Error bodies (shaped by
:func:`core.exceptions.envelope_exception_handler`) pass through untouched.
"""
from rest_framework.renderers import JSONRenderer

SUCCESS_ENVELOPE_KEYS = {"status", "message", "data"}
ERROR_ENVELOPE_KEYS = {"status", "message", "errors"}


class EnvelopeJSONRenderer(JSONRenderer):
    """DRF renderer that emits the standard success response envelope."""

    def render(self, data, accepted_media_type=None, renderer_context=None):
        renderer_context = renderer_context or {}
        response = renderer_context.get("response")
        status_code = getattr(response, "status_code", 200)

        payload = self._build_envelope(data, status_code)
        return super().render(payload, accepted_media_type, renderer_context)

    # ------------------------------------------------------------------
    def _build_envelope(self, data, status_code):
        # Error responses are shaped by the exception handler — pass through.
        if status_code >= 400:
            return data

        # Pass through if already a success envelope (e.g. a view built one).
        if isinstance(data, dict) and SUCCESS_ENVELOPE_KEYS.issubset(data.keys()):
            return data

        message = self._default_message(status_code)
        if isinstance(data, dict) and "detail" in data and len(data) == 1:
            message = str(data["detail"])
            data = None

        return {
            "status": "success",
            "message": message,
            "data": data,
        }

    @staticmethod
    def _default_message(status_code):
        if 200 <= status_code < 300:
            return "Success"
        if 400 <= status_code < 500:
            return "Request failed"
        return "Server error"
