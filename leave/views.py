"""HTTP layer for the leave app.

A single :class:`LeaveRequestViewSet` serves the whole workflow, mounted under
``/api/v1/`` by ``config/urls.py``:

- ``GET /leaves`` — the requester's own requests (approvers additionally see the
  requests they may act on: children / department students; admins see all).
- ``GET /leaves/{id}`` — one request (scoped the same way).
- ``POST /leaves`` — apply (``{ type, from, to, reason }``); filed for the
  current user with status ``pending``.
- ``POST /leaves/{id}/approve`` — approve (object-scoped: parent→child,
  faculty/hod→dept students, admin→all).
- ``POST /leaves/{id}/reject`` — reject (same scoping).

Writes flow through :class:`leave.services.LeaveRequestService` (audit + cache
invalidation); the service also owns the approval scoping rules.
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

from core.permissions import Role
from core.viewsets import BaseModelViewSet

from leave.models import LeaveRequest
from leave.permissions import APPLICANTS, LEAVE_MATRIX
from leave.repositories import LeaveRequestRepository
from leave.serializers import (
    LeaveInputSerializer,
    LeaveRequestSerializer,
    LeaveSpecInputSerializer,
    LeaveSpecSerializer,
    LeaveStatusSerializer,
)
from leave.services import LeaveRequestService

User = get_user_model()
_STAFF_ROLES = set(Role.STAFF)


def _client_ip(request):
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def _assert_self_or_staff(request_user, user_id) -> None:
    """Contract ``{user_id}`` rule: non-staff may only use their own id."""
    if getattr(request_user, "role", None) in _STAFF_ROLES:
        return
    if str(getattr(request_user, "id", "")) != str(user_id):
        raise PermissionDenied("You can only access your own resource.")


class LeaveRequestViewSet(BaseModelViewSet):
    """Leave requests: apply + own list + approve/reject workflow."""

    queryset = LeaveRequest.objects.select_related("user", "decided_by").all()
    serializer_class = LeaveRequestSerializer
    service_class = LeaveRequestService
    permission_matrix = LEAVE_MATRIX
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["status", "type"]
    search_fields = ["reason"]
    ordering_fields = ["applied_on", "start_date", "end_date"]

    # -- scoped queryset -------------------------------------------------
    def get_queryset(self):
        """Scope reads to what the requester may see (own + approvable).

        For detail/approve/reject the scoped set still contains the target (an
        approver's children / department students), and the service re-checks
        authority before mutating.
        """
        service = LeaveRequestService(actor=self.request.user)
        return service.visible_queryset(self.request.user)

    # -- apply -----------------------------------------------------------
    @extend_schema(
        request=LeaveInputSerializer,
        responses={201: LeaveRequestSerializer},
    )
    def create(self, request, *args, **kwargs):
        """``POST /leaves`` — file a leave request for the current user."""
        serializer = LeaveInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        service = LeaveRequestService(actor=request.user, ip=self._client_ip())
        leave = service.apply(
            request.user,
            type=data["type"],
            start_date=data["from_date"],
            end_date=data["to"],
            reason=data.get("reason", ""),
        )
        return Response(LeaveRequestSerializer(leave).data, status=201)

    # -- approve / reject ------------------------------------------------
    @extend_schema(request=None, responses={200: LeaveRequestSerializer})
    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        """``POST /leaves/{id}/approve`` — approve (object-scoped)."""
        leave = self.get_object()
        service = LeaveRequestService(actor=request.user, ip=self._client_ip())
        leave = service.approve(leave, request.user)
        return Response(LeaveRequestSerializer(leave).data)

    @extend_schema(request=None, responses={200: LeaveRequestSerializer})
    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        """``POST /leaves/{id}/reject`` — reject (object-scoped)."""
        leave = self.get_object()
        service = LeaveRequestService(actor=request.user, ip=self._client_ip())
        leave = service.reject(leave, request.user)
        return Response(LeaveRequestSerializer(leave).data)


# ---------------------------------------------------------------------------
# Mobile API contract (spec) endpoints — snake_case + {user_id} resolution.
# ---------------------------------------------------------------------------
class LeavesCollectionView(APIView):
    """``/api/v1/leaves`` — apply (POST) and the caller's visible leaves (GET).

    - ``POST`` (apply) accepts ``{ type, from_date, to_date, reason }`` and files
      a request for the current user (roles in ``APPLICANTS``).
    - ``GET`` returns the requester's visible leaves (own + those they may act
      on) in the spec snake_case shape.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: LeaveSpecSerializer(many=True)})
    def get(self, request):
        service = LeaveRequestService(actor=request.user)
        qs = service.visible_queryset(request.user)
        return Response(LeaveSpecSerializer(qs, many=True).data)

    @extend_schema(request=LeaveSpecInputSerializer, responses={201: LeaveSpecSerializer})
    def post(self, request):
        if request.user.role not in set(APPLICANTS):
            raise PermissionDenied("Your role may not file a leave request.")
        serializer = LeaveSpecInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        service = LeaveRequestService(actor=request.user, ip=_client_ip(request))
        leave = service.apply(
            request.user,
            type=data["type"],
            start_date=data["from_date"],
            end_date=data["to_date"],
            reason=data.get("reason", ""),
        )
        return Response(LeaveSpecSerializer(leave).data, status=201)


class LeaveDetailView(APIView):
    """``/api/v1/leaves/{id}`` — the same URL serves two spec verbs.

    - ``GET /api/v1/leaves/{user_id}`` → that user's leaves (student/self or
      staff), newest first.
    - ``PUT /api/v1/leaves/{leave_id}`` → approve/reject via ``{ status }``
      (object-level authority enforced by the service).
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: LeaveSpecSerializer(many=True)})
    def get(self, request, pk):
        # ``pk`` is a user_id here (the leaves of that user).
        _assert_self_or_staff(request.user, pk)
        qs = LeaveRequestRepository().for_user(pk)
        return Response(LeaveSpecSerializer(qs, many=True).data)

    @extend_schema(request=LeaveStatusSerializer, responses={200: LeaveSpecSerializer})
    def put(self, request, pk):
        # ``pk`` is a leave_id here (approve/reject).
        leave = LeaveRequestRepository().get_or_none(pk)
        if leave is None:
            raise NotFound("Leave request not found.")
        serializer = LeaveStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        status_value = serializer.validated_data["status"]
        service = LeaveRequestService(actor=request.user, ip=_client_ip(request))
        if status_value == LeaveRequest.STATUS_APPROVED:
            leave = service.approve(leave, request.user)
        else:
            leave = service.reject(leave, request.user)
        return Response(LeaveSpecSerializer(leave).data)


class LeavesForParentView(APIView):
    """``GET /api/v1/leaves/parent/{user_id}`` — a parent's children's leaves.

    ``{user_id}`` is the parent's accounts user id (self or staff). Returns the
    leave requests filed by the students linked to that parent.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: LeaveSpecSerializer(many=True)})
    def get(self, request, user_id):
        _assert_self_or_staff(request.user, user_id)
        from guardians.models import ParentLink

        child_user_ids = list(
            ParentLink.objects.filter(parent_id=user_id)
            .exclude(student__user__isnull=True)
            .values_list("student__user_id", flat=True)
        )
        qs = (
            LeaveRequestRepository()
            .get_queryset()
            .filter(user_id__in=child_user_ids)
            .order_by("-applied_on")
        )
        return Response(LeaveSpecSerializer(qs, many=True).data)
