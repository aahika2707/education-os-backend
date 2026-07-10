"""Students URLs. ``config/urls.py`` mounts this under ``/api/v1/`` so the router
paths resolve to ``/api/v1/students``, ``/api/v1/students/me``,
``/api/v1/students/{pk}``, ``/api/v1/student-addresses``, etc.

The router registers the ``me`` custom action ahead of the ``{pk}`` detail route,
so ``/students/me`` never collides with a UUID lookup.

The spec profile-by-user read lives at the distinct ``/students/by-user/{user_id}``
path. It previously sat at ``/students/{user_id}`` and, being declared before the
router, shadowed the ViewSet's ``{pk}`` detail route for every method — so
``PATCH``/``DELETE /students/{pk}`` (roster edit/remove) returned 405. Giving it
its own path frees ``/students/{pk}`` for full admin CRUD.
"""
from django.urls import path
from rest_framework.routers import DefaultRouter

from students.views import (
    GuardianViewSet,
    MedicalViewSet,
    StudentAddressViewSet,
    StudentDocumentViewSet,
    StudentProfileByUserView,
    StudentViewSet,
)

app_name = "students"

router = DefaultRouter(trailing_slash=False)
router.register("students", StudentViewSet, basename="student")
router.register("student-addresses", StudentAddressViewSet, basename="student-address")
router.register("student-guardians", GuardianViewSet, basename="student-guardian")
router.register("student-medical", MedicalViewSet, basename="student-medical")
router.register("student-documents", StudentDocumentViewSet, basename="student-document")

urlpatterns = [
    # Spec (canonical mobile) profile read — resolves by accounts user_id.
    # On its own path so it does NOT shadow the ViewSet's {pk} detail route.
    path(
        "students/by-user/<uuid:user_id>",
        StudentProfileByUserView.as_view(),
        name="student-profile-by-user",
    ),
    *router.urls,
]
