"""Chat URLs. ``config/urls.py`` mounts this under ``/api/v1/``.

**Mobile API contract (canonical)** — snake_case:
- ``POST /api/v1/chat``            — create a conversation.
- ``POST /api/v1/chat/message``    — send ``{ conversation_id, text }``.
- ``GET  /api/v1/chat/{user_id}``  — a user's conversations + history.

**Legacy** (router) — ``/chat/threads`` list/retrieve + ``messages``/``read``
actions remain available.
"""
from django.urls import path
from rest_framework.routers import DefaultRouter

from chat.views import (
    ChatByUserView,
    ChatConversationView,
    ChatMessageView,
    ChatThreadViewSet,
)

app_name = "chat"

router = DefaultRouter(trailing_slash=False)
router.register("chat/threads", ChatThreadViewSet, basename="chat-threads")

urlpatterns = [
    # Spec (canonical mobile) routes — declared before the router.
    path("chat", ChatConversationView.as_view(), name="chat-create"),
    path("chat/message", ChatMessageView.as_view(), name="chat-message"),
    path("chat/<uuid:user_id>", ChatByUserView.as_view(), name="chat-by-user"),
    *router.urls,
]
