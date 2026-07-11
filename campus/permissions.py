"""RBAC matrix for the campus viewset.

Contract (static reference data, like transport/library/events): every
authenticated role reads; only admins write.
"""
from core.permissions import Role

ALL_ROLES = list(Role.ALL)
ADMINS = list(Role.ADMINS)

CAMPUS_MATRIX = {
    "list": ALL_ROLES,
    "retrieve": ALL_ROLES,
    "create": ADMINS,
    "update": ADMINS,
    "partial_update": ADMINS,
    "destroy": ADMINS,
}
