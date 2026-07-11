"""Faculty URLs. ``config/urls.py`` mounts this under ``/api/v1/`` so the router
paths resolve to ``/api/v1/faculty/``, ``/api/v1/faculty/me/``,
``/api/v1/faculty/classes/``, ``/api/v1/faculty/classes/{id}/``, and
``/api/v1/faculty/classes/{id}/roster/``.
"""
from django.urls import path
from rest_framework.routers import DefaultRouter

from faculty.views import AllocationViewSet, FacultyProfileViewSet

app_name = "faculty"

router = DefaultRouter(trailing_slash=False)
router.register("faculty", FacultyProfileViewSet, basename="faculty")

urlpatterns = [
    # Subject↔faculty allocations (HOD): list + reassign, backed by FacultyClass.
    path(
        "allocations",
        AllocationViewSet.as_view({"get": "list"}),
        name="allocations",
    ),
    path(
        "allocations/<uuid:pk>/reassign",
        AllocationViewSet.as_view({"post": "reassign"}),
        name="allocation-reassign",
    ),
    *router.urls,
]
