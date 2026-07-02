"""Fees URLs. ``config/urls.py`` mounts this under ``/api/v1/``.

Mobile API contract v1 (canonical) endpoints:
- ``GET  /api/v1/fees/{user_id}``            — fee summary + invoices for a user.
- ``POST /api/v1/fees/payment``              — record a payment ``{ fee_id }``.
- ``GET  /api/v1/fees/receipt/{payment_id}`` — the payment receipt.

Retained admin/management surface (via the router):
- ``POST /api/v1/fees``                      — create an invoice.
- ``PUT/PATCH/DELETE /api/v1/fees/{fee_id}`` — update / soft-delete an invoice.
- ``GET  /api/v1/fees``                      — list invoices (scoped/searchable).
- ``GET  /api/v1/fees/total-due`` · ``POST /api/v1/fees/{id}/pay``.

Because ``{user_id}`` and an invoice ``{fee_id}`` are both UUIDs on the same
``/fees/<uuid>`` path, the explicit route below maps by HTTP method: ``GET`` →
the spec ``by_user`` summary; ``PUT``/``PATCH``/``DELETE`` → the invoice CRUD
actions (which resolve the same UUID as an invoice pk). The literal
``fees/payment`` and ``fees/receipt/...`` paths are declared before the ``<uuid>``
route so they never bind as a detail lookup.
"""
from django.urls import path
from rest_framework.routers import DefaultRouter

from fees.views import FeeInvoiceViewSet

app_name = "fees"

router = DefaultRouter(trailing_slash=False)
router.register("fees", FeeInvoiceViewSet, basename="fee")

urlpatterns = [
    # POST /api/v1/fees/payment — record a payment ({ fee_id }).
    path(
        "fees/payment",
        FeeInvoiceViewSet.as_view({"post": "make_payment"}),
        name="fee-payment",
    ),
    # GET /api/v1/fees/receipt/{payment_id} — the payment receipt.
    path(
        "fees/receipt/<uuid:payment_id>",
        FeeInvoiceViewSet.as_view({"get": "receipt"}),
        name="fee-receipt",
    ),
    # GET /api/v1/fees/{user_id} — spec summary; PUT/PATCH/DELETE — invoice CRUD.
    path(
        "fees/<uuid:pk>",
        FeeInvoiceViewSet.as_view(
            {
                "get": "by_user",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
        name="fee-detail-spec",
    ),
] + router.urls
