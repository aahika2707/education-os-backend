"""Assignments URLs. ``config/urls.py`` mounts this under ``/api/v1/`` so paths
resolve to:

- ``/api/v1/assignments/`` (list, ``?status=``) + ``POST`` create,
- ``/api/v1/assignments/{id}/`` (retrieve),
- ``/api/v1/assignments/{id}/submit/`` (student turn-in),
- ``/api/v1/faculty/assignments/`` (faculty-created list).

The faculty list is a ``detail=False`` action on the same viewset; it is routed
at the top-level ``faculty/assignments/`` path (rather than nested under the
``assignments/`` prefix) to match the mobile contract exactly.
"""
from django.urls import path
from rest_framework.routers import DefaultRouter

from assignments.views import AssignmentViewSet

app_name = "assignments"

router = DefaultRouter(trailing_slash=False)
router.register("assignments", AssignmentViewSet, basename="assignments")

urlpatterns = [
    path(
        "faculty/assignments",
        AssignmentViewSet.as_view(
            {"get": "faculty_assignments", "post": "faculty_create"}
        ),
        name="faculty-assignments",
    ),
    path(
        "faculty/assignments/<uuid:pk>",
        AssignmentViewSet.as_view({"get": "faculty_detail"}),
        name="faculty-assignment-detail",
    ),
    *router.urls,
]
