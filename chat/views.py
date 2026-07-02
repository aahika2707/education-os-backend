"""HTTP layer for the chat app.

A single :class:`ChatThreadViewSet` serves the mobile ``chatService`` contract:

- ``GET  /chat/threads``                    — the requesting user's threads
  (``ChatThread[]``, ``lastMessageAt`` desc), paginated/filterable.
- ``GET  /chat/threads/{id}``               — one thread (``ChatThread``).
- ``POST /chat/threads/{id}/messages``      — send a message (``{ text }`` →
  ``ChatThread``); increments the recipient's unread + broadcasts realtime.
- ``POST /chat/threads/{id}/read``          — mark the thread read for the
  requesting user (``void``).

Only the two thread participants (or an admin) may see or act on a thread —
enforced object-level by :class:`chat.permissions.IsThreadParticipant`. The
queryset is *also* scoped to the requesting user's threads so list never leaks
other conversations. Writes flow through :class:`chat.services.ChatService`
(audit + cache-invalidation).
"""
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.permissions import Role, RoleModelPermission

from chat.models import ChatThread
from chat.permissions import CHAT_MATRIX, CHAT_ROLES, IsThreadParticipant
from chat.repositories import ChatThreadRepository
from chat.serializers import (
    ChatCreateSerializer,
    ChatMessageInputSerializer,
    ChatThreadSerializer,
    ChatThreadSpecSerializer,
    SendMessageSerializer,
)
from chat.services import ChatService, ChatThreadService

User = get_user_model()
_STAFF_ROLES = set(Role.STAFF)
_CHAT_ROLES = set(CHAT_ROLES)


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


class ChatThreadViewSet(viewsets.ReadOnlyModelViewSet):
    """List/retrieve the requesting user's chat threads + message/read actions."""

    serializer_class = ChatThreadSerializer
    permission_classes = [IsAuthenticated, RoleModelPermission, IsThreadParticipant]
    permission_matrix = CHAT_MATRIX
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["teacher_name", "subject_label"]
    ordering_fields = ["last_message_at", "created_at"]
    ordering = ["-last_message_at"]

    def get_queryset(self):
        """Scope to threads the requesting user participates in.

        Admins see every thread (support/oversight); everyone else only their
        own conversations, so ``list`` cannot leak another user's threads.
        """
        repo = ChatThreadRepository()
        user = self.request.user
        if getattr(user, "role", None) in set(Role.ADMINS):
            return repo.get_queryset()
        return repo.for_participant(user)

    # -- service helpers --------------------------------------------------
    def _client_ip(self):
        xff = self.request.META.get("HTTP_X_FORWARDED_FOR")
        if xff:
            return xff.split(",")[0].strip()
        return self.request.META.get("REMOTE_ADDR")

    def _chat_service(self):
        return ChatService(actor=self.request.user, ip=self._client_ip())

    # -- POST /chat/threads/{id}/messages ---------------------------------
    @action(detail=True, methods=["post"])
    def messages(self, request, *args, **kwargs):
        """Send a message to the thread; returns the updated thread."""
        thread = self.get_object()  # runs object-level participant check
        serializer = SendMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self._chat_service().send_message(
            thread=thread, user=request.user, text=serializer.validated_data["text"]
        )
        thread = self.get_queryset().get(pk=thread.pk)  # refreshed with new message
        return Response(
            ChatThreadSerializer(thread, context=self.get_serializer_context()).data,
            status=status.HTTP_201_CREATED,
        )

    # -- POST /chat/threads/{id}/read -------------------------------------
    @action(detail=True, methods=["post"])
    def read(self, request, *args, **kwargs):
        """Mark the thread read for the requesting user (``void``)."""
        thread = self.get_object()  # runs object-level participant check
        self._chat_service().mark_read(thread=thread, user=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


# ---------------------------------------------------------------------------
# Mobile API contract (spec) endpoints — snake_case + {user_id} resolution.
# ---------------------------------------------------------------------------
class ChatConversationView(APIView):
    """``POST /api/v1/chat`` — create (or return an existing) conversation.

    The requesting participant is inferred from their role; a parent supplies
    ``teacher_id``, a teacher supplies ``parent_id``, and staff/admin supply
    both. Returns the conversation in the spec snake_case shape.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.role not in _CHAT_ROLES:
            raise PermissionDenied("Your role has no chat access.")
        serializer = ChatCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        role = request.user.role
        teacher_id = data.get("teacher_id")
        parent_id = data.get("parent_id")
        if role == Role.PARENT:
            parent_id = request.user.id
            if not teacher_id:
                raise ValidationError({"teacher_id": "This field is required."})
        elif role == Role.FACULTY:
            teacher_id = request.user.id
            if not parent_id:
                raise ValidationError({"parent_id": "This field is required."})
        else:  # admin / super_admin
            if not (teacher_id and parent_id):
                raise ValidationError(
                    "teacher_id and parent_id are required for staff."
                )

        teacher = User.objects.filter(pk=teacher_id).first()
        parent = User.objects.filter(pk=parent_id).first()
        if teacher is None or parent is None:
            raise NotFound("Participant not found.")

        # Idempotent: return the existing conversation if one already exists.
        existing = ChatThread.objects.filter(teacher=teacher, parent=parent).first()
        if existing is not None:
            return Response(
                ChatThreadSpecSerializer(
                    existing, context={"request": request}
                ).data,
                status=status.HTTP_200_OK,
            )

        thread = ChatThreadService(
            actor=request.user, ip=_client_ip(request)
        ).create(
            teacher=teacher,
            parent=parent,
            teacher_name=teacher.full_name,
            subject_label=data.get("subject", ""),
            avatar_color=getattr(teacher, "avatar_color", "") or "",
            unread_count={},
        )
        return Response(
            ChatThreadSpecSerializer(thread, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )


class ChatMessageView(APIView):
    """``POST /api/v1/chat/message`` — send ``{ conversation_id, text }``.

    Only a thread participant may post; returns the updated conversation.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.role not in _CHAT_ROLES:
            raise PermissionDenied("Your role has no chat access.")
        serializer = ChatMessageInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        repo = ChatThreadRepository()
        thread = repo.get_queryset().filter(pk=data["conversation_id"]).first()
        if thread is None:
            raise NotFound("Conversation not found.")
        if not thread.is_participant(request.user):
            raise PermissionDenied("You are not a participant in this conversation.")

        ChatService(actor=request.user, ip=_client_ip(request)).send_message(
            thread=thread, user=request.user, text=data["text"]
        )
        thread = repo.get_queryset().get(pk=thread.pk)  # refreshed with new message
        return Response(
            ChatThreadSpecSerializer(thread, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )


class ChatByUserView(APIView):
    """``GET /api/v1/chat/{user_id}`` — a user's conversations + history.

    ``{user_id}`` is the accounts user id (self or staff). ``unread`` on each
    conversation is that user's per-user counter.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        _assert_self_or_staff(request.user, user_id)
        target = User.objects.filter(pk=user_id).first()
        if target is None:
            raise NotFound("User not found.")
        qs = ChatThreadRepository().for_participant(target)
        return Response(
            ChatThreadSpecSerializer(
                qs,
                many=True,
                context={"request": request, "unread_user": target},
            ).data
        )
