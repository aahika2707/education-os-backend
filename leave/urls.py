"""Leave URLs. ``config/urls.py`` mounts this under ``/api/v1/``.

**Mobile API contract (canonical)** — snake_case, declared ahead of the router
so they take precedence over the ViewSet's collection/detail routes:

- ``POST /api/v1/leaves``                    — apply ``{ type, from_date, to_date, reason }``.
- ``GET  /api/v1/leaves``                    — the caller's visible leaves.
- ``GET  /api/v1/leaves/{user_id}``          — that user's leaves.
- ``PUT  /api/v1/leaves/{leave_id}``         — approve/reject ``{ status }``.
- ``GET  /api/v1/leaves/parent/{user_id}``   — a parent's children's leaves.

**Legacy** (router) — ``/leaves/{id}/approve``, ``/leaves/{id}/reject`` remain.
"""
from django.urls import path
from rest_framework.routers import DefaultRouter

from leave.views import (
    LeaveDetailView,
    LeaveRequestViewSet,
    LeavesCollectionView,
    LeavesForParentView,
)

app_name = "leave"

router = DefaultRouter(trailing_slash=False)
router.register("leaves", LeaveRequestViewSet, basename="leaves")

urlpatterns = [
    # Spec (canonical mobile) routes — declared before the router.
    path("leaves", LeavesCollectionView.as_view(), name="leaves-collection"),
    path(
        "leaves/parent/<uuid:user_id>",
        LeavesForParentView.as_view(),
        name="leaves-parent",
    ),
    path("leaves/<uuid:pk>", LeaveDetailView.as_view(), name="leaves-detail-spec"),
    *router.urls,
]
