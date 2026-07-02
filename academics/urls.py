"""Academics URLs. ``config/urls.py`` mounts this under ``/api/v1/`` so the
router paths resolve to ``/api/v1/departments/``, ``/api/v1/subjects/{id}``,
``/api/v1/timetable/week/``, etc.
"""
from django.urls import path
from rest_framework.routers import DefaultRouter

from academics.views import (
    AcademicProgressView,
    AcademicRecordView,
    DepartmentViewSet,
    ProgramViewSet,
    SectionViewSet,
    SemesterViewSet,
    SubjectViewSet,
    TimetableViewSet,
)

app_name = "academics"

router = DefaultRouter(trailing_slash=False)
router.register("departments", DepartmentViewSet, basename="department")
router.register("programs", ProgramViewSet, basename="program")
router.register("semesters", SemesterViewSet, basename="semester")
router.register("sections", SectionViewSet, basename="section")
router.register("subjects", SubjectViewSet, basename="subject")
router.register("timetable", TimetableViewSet, basename="timetable")

# Mobile API contract v1 canonical, {user_id}-scoped endpoints.
urlpatterns = router.urls + [
    path(
        "academics/<uuid:user_id>",
        AcademicRecordView.as_view(),
        name="academic-record-by-user",
    ),
    path(
        "progress/<uuid:user_id>",
        AcademicProgressView.as_view(),
        name="academic-progress-by-user",
    ),
]
