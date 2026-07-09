"""Notifications URLs. ``config/urls.py`` mounts this under ``/api/v1/``.

Two surfaces are exposed:

* **Mobile API contract (canonical)** — snake_case, ``{user_id}``-parameterised:
  - ``GET /api/v1/notifications/{user_id}``          — a user's notifications.
  - ``GET /api/v1/notifications/unread/{user_id}``   — ``{ unread_count }``.
  - ``PUT /api/v1/notifications/read/{notification_id}`` — mark one read.

  These are declared ahead of the router so they take precedence over the
  ViewSet's ``{pk}`` detail route.

* **Legacy console** (router) — ``/notifications`` (self-scoped list),
  ``/notifications/{id}/read`` (POST), ``/notifications/read-all``,
  ``/notifications/unread-count``, ``/notifications/broadcast``, admin CRUD.
"""
from django.urls import path
from rest_framework.routers import DefaultRouter

from notifications.views import (
    NotificationReadView,
    NotificationsByUserView,
    NotificationsUnreadByUserView,
    NotificationViewSet,
)

app_name = "notifications"

router = DefaultRouter(trailing_slash=False)
router.register("notifications", NotificationViewSet, basename="notification")

urlpatterns = [
    # Spec (canonical mobile) routes — declared before the router.
    path(
        "notifications/unread/<uuid:user_id>",
        NotificationsUnreadByUserView.as_view(),
        name="notifications-unread-by-user",
    ),
    path(
        "notifications/read/<uuid:notification_id>",
        NotificationReadView.as_view(),
        name="notifications-read-spec",
    ),
    path(
        "notifications/<uuid:user_id>",
        NotificationsByUserView.as_view(),
        name="notifications-by-user",
    ),
    *router.urls,
]
