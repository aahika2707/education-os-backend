"""Guardians URLs. ``config/urls.py`` mounts this under ``/api/v1/``.

**Mobile API contract (canonical)** — snake_case:
- ``GET /api/v1/parents/{user_id}`` → ``{ parent_name, mobile, email,
  children: [{ student_id, name, roll_no }] }``.

**Legacy** (router) — ``/guardians`` admin CRUD + ``/guardians/parent/children``.
"""
from django.urls import path
from rest_framework.routers import DefaultRouter

from guardians.views import ParentLinkViewSet, ParentProfileByUserView

app_name = "guardians"

router = DefaultRouter(trailing_slash=False)
router.register("guardians", ParentLinkViewSet, basename="guardians")

urlpatterns = [
    # Spec (canonical mobile) parent profile route — resolves by accounts user_id.
    path(
        "parents/<uuid:user_id>",
        ParentProfileByUserView.as_view(),
        name="parent-profile-by-user",
    ),
    *router.urls,
]
