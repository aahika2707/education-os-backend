"""Business-logic layer for the students app.

Services extend :class:`core.services.BaseService` so every write auto-stamps
``created_by``/``updated_by``, emits an :class:`~core.models.AuditLog` row and
invalidates the cached roster/profile views. The student roster and per-student
profile are cached under the ``students`` prefix.
"""
from __future__ import annotations

from core.cache import invalidate_prefix
from core.permissions import Role
from core.services import BaseService

from students.models import (
    Guardian,
    Medical,
    Student,
    StudentAddress,
    StudentDocument,
)
from students.repositories import (
    GuardianRepository,
    MedicalRepository,
    StudentAddressRepository,
    StudentDocumentRepository,
    StudentRepository,
)

# Cache key prefix owned by this app.
STUDENTS_PREFIX = "students"
# The admin dashboard caches student counts under this prefix (see
# administration.services); bust it too whenever a student changes so the
# headline "active students" count stays accurate.
DASHBOARD_PREFIX = "dashboard"


class StudentService(BaseService):
    model = Student
    repository_class = StudentRepository
    entity_name = "Student"

    def invalidate_cache(self, instance=None) -> None:
        invalidate_prefix(STUDENTS_PREFIX)
        invalidate_prefix(DASHBOARD_PREFIX)

    def delete(self, instance):
        """Soft-delete the profile, then deactivate its linked login.

        ``BaseService.delete`` soft-deletes the row (it leaves the default
        ``objects`` manager, so it drops out of the roster). We also deactivate
        the linked ``accounts.User`` so a removed student can no longer sign in
        and no working orphan account lingers — but only when that user has no
        other active student profile and is not a staff/admin account.
        """
        user = instance.user
        result = super().delete(instance)
        if user is not None and user.role not in set(Role.STAFF):
            has_other_profile = (
                Student.objects.filter(user=user).exclude(pk=instance.pk).exists()
            )
            if not has_other_profile and user.is_active:
                user.is_active = False
                user.save(update_fields=["is_active"])
        return result


class StudentAddressService(BaseService):
    model = StudentAddress
    repository_class = StudentAddressRepository
    entity_name = "StudentAddress"

    def invalidate_cache(self, instance=None) -> None:
        invalidate_prefix(STUDENTS_PREFIX)


class GuardianService(BaseService):
    model = Guardian
    repository_class = GuardianRepository
    entity_name = "Guardian"

    def invalidate_cache(self, instance=None) -> None:
        invalidate_prefix(STUDENTS_PREFIX)


class MedicalService(BaseService):
    model = Medical
    repository_class = MedicalRepository
    entity_name = "Medical"

    def invalidate_cache(self, instance=None) -> None:
        invalidate_prefix(STUDENTS_PREFIX)


class StudentDocumentService(BaseService):
    model = StudentDocument
    repository_class = StudentDocumentRepository
    entity_name = "StudentDocument"

    def invalidate_cache(self, instance=None) -> None:
        invalidate_prefix(STUDENTS_PREFIX)
