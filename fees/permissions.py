"""RBAC for the fees viewset.

Matrix (mirrors the BUILD_CONTRACT fees row):
* student  — R self
* parent   — R + pay child
* admin    — full RW
* hod/principal — R (institution/department oversight)

The action matrix gates *which roles* may reach an action; object-level scoping
(:class:`CanAccessInvoice`) and queryset filtering (in the viewset) restrict a
student/parent to their *own* / *child's* invoices.
"""
from rest_framework.permissions import BasePermission

from core.permissions import Role

STAFF = list(Role.STAFF)          # super_admin, admin, principal, hod, faculty
ADMINS = list(Role.ADMINS)        # super_admin, admin
READERS = [
    Role.SUPER_ADMIN,
    Role.ADMIN,
    Role.PRINCIPAL,
    Role.HOD,
    Role.STUDENT,
    Role.PARENT,
]
# Who may hit POST /fees/{id}/pay: parents (for their child) and admins.
PAYERS = [Role.SUPER_ADMIN, Role.ADMIN, Role.PARENT]
# Who may hit the mobile-contract POST /fees/payment: the student pays their own
# fees from the app, parents pay for a child, admins record any payment.
SPEC_PAYERS = [Role.SUPER_ADMIN, Role.ADMIN, Role.PARENT, Role.STUDENT]

FEE_MATRIX = {
    "list": READERS,
    "retrieve": READERS,
    "create": ADMINS,
    "update": ADMINS,
    "partial_update": ADMINS,
    "destroy": ADMINS,
    "pay": PAYERS,
    # total-due: any reader gets a scoped total.
    "total_due": READERS,
    # Mobile API contract v1 actions ({user_id}-parameterized, snake_case).
    "by_user": READERS,          # GET /api/v1/fees/{user_id}
    "make_payment": SPEC_PAYERS,  # POST /api/v1/fees/payment
    "receipt": READERS,          # GET /api/v1/fees/receipt/{payment_id}
}

_STAFF_ROLES = set(Role.STAFF)


def student_ids_for(user):
    """Student ids this ``user`` is entitled to see (self for students, linked
    children for parents). Staff get ``None`` meaning "no restriction".
    """
    from students.models import Guardian, Student

    role = getattr(user, "role", None)
    if role in _STAFF_ROLES:
        return None
    if role == Role.STUDENT:
        return list(
            Student.objects.filter(user=user).values_list("id", flat=True)
        )
    if role == Role.PARENT:
        # No formal guardian↔user model yet: link a parent to a child by the
        # guardian contact email recorded on the student record.
        ids = set(
            Student.objects.filter(user=user).values_list("id", flat=True)
        )
        if user.email:
            ids.update(
                Guardian.objects.filter(email__iexact=user.email).values_list(
                    "student_id", flat=True
                )
            )
        return list(ids)
    return []


class CanAccessInvoice(BasePermission):
    """Object-level: staff any invoice; student/parent only their own/child's."""

    message = "You can only access your own fees."

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        if getattr(user, "role", None) in _STAFF_ROLES:
            return True
        allowed = student_ids_for(user)
        return obj.student_id in set(allowed or [])
