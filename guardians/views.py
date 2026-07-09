"""HTTP layer for the guardians app.

A single :class:`ParentLinkViewSet` serves both surfaces:

- ``/guardians/`` — admin CRUD + list of parent↔student links.
- ``GET /guardians/parent/children`` — the children (students) of the
  requesting parent, in the app's ``Student`` shape (``types.ts``) with the
  guardian ``relation`` attached.

The self-scoped children read is cached under the ``guardians`` prefix (TTL
600s); writes flow through the service layer (audit + cache-invalidation) via
:class:`core.viewsets.BaseModelViewSet`.
"""
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.cache import TTL_LIBRARY, cache_get_or_set, cache_key
from core.permissions import Role
from core.viewsets import BaseModelViewSet

from guardians.models import ParentLink
from guardians.permissions import PARENT_LINK_MATRIX
from guardians.repositories import ParentLinkRepository
from guardians.serializers import (
    ParentChildSerializer,
    ParentLinkSerializer,
    ParentProfileSpecSerializer,
)
from guardians.services import ParentLinkService

User = get_user_model()
_STAFF_ROLES = set(Role.STAFF)

# The children read is small and reference-like; use the library TTL (600s).
TTL_GUARDIANS = TTL_LIBRARY


class ParentLinkViewSet(BaseModelViewSet):
    """Parent↔student links: admin CRUD + list, plus the parent children read."""

    queryset = (
        ParentLink.objects.select_related(
            "parent",
            "student",
            "student__program",
            "student__department",
            "student__semester",
            "student__section",
        ).all()
    )
    serializer_class = ParentLinkSerializer
    service_class = ParentLinkService
    permission_matrix = PARENT_LINK_MATRIX
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["parent", "student", "relation", "is_primary"]
    search_fields = [
        "parent__full_name",
        "parent__email",
        "student__full_name",
        "student__roll_no",
    ]
    ordering_fields = ["relation", "is_primary", "created_at"]

    @extend_schema(responses={200: ParentChildSerializer(many=True)})
    @action(detail=False, methods=["get"], url_path="parent/children")
    def children(self, request):
        """``GET /guardians/parent/children`` — the requesting parent's children.

        Admins see an empty list here (they manage links via the CRUD surface);
        a parent sees the students they are linked to, in the app's ``Student``
        shape with the guardian ``relation`` attached.
        """

        def build():
            links = (
                ParentLink.objects.select_related(
                    "student",
                    "student__program",
                    "student__department",
                    "student__semester",
                    "student__section",
                )
                .filter(parent=request.user)
                .order_by("-is_primary", "student__roll_no")
            )
            return [ParentChildSerializer(link).data for link in links]

        data = cache_get_or_set(
            cache_key("guardians", "children", request.user.id),
            TTL_GUARDIANS,
            build,
        )
        return Response(data)


# ---------------------------------------------------------------------------
# Mobile API contract (spec) endpoint — snake_case + {user_id} resolution.
# ---------------------------------------------------------------------------
class ParentProfileByUserView(APIView):
    """``GET /api/v1/parents/{user_id}`` — a parent's profile + children.

    ``{user_id}`` is the parent's accounts user id (self or staff). Returns
    ``{ parent_name, mobile, email, children: [{ student_id, name, roll_no }] }``.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: ParentProfileSpecSerializer})
    def get(self, request, user_id):
        if request.user.role not in _STAFF_ROLES and str(request.user.id) != str(
            user_id
        ):
            raise PermissionDenied("You can only access your own profile.")
        parent = User.objects.filter(pk=user_id).first()
        if parent is None:
            raise NotFound("Parent not found.")
        links = ParentLinkRepository().for_parent(parent)
        return Response(
            ParentProfileSpecSerializer(parent, context={"links": links}).data
        )
