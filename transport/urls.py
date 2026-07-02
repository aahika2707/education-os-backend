"""Transport URLs. ``config/urls.py`` mounts this under ``/api/v1/`` so the
router paths resolve to ``/api/v1/transport/routes/``,
``/api/v1/transport/routes/{id}/live/``, etc.
"""
from django.urls import path
from rest_framework.routers import DefaultRouter

from transport.views import (
    BusLiveStatusViewSet,
    BusRouteViewSet,
    BusStopViewSet,
)

app_name = "transport"

router = DefaultRouter(trailing_slash=False)
router.register("transport/routes", BusRouteViewSet, basename="busroute")
router.register("transport/stops", BusStopViewSet, basename="busstop")
router.register("transport/live-status", BusLiveStatusViewSet, basename="buslivestatus")

urlpatterns = [
    # Mobile API contract v1: GET /api/v1/transport/{user_id}. The <uuid:pk> is
    # the accounts user id; declared before the router so the more specific
    # ``transport/routes`` etc. still resolve to their own viewsets.
    path(
        "transport/<uuid:pk>",
        BusRouteViewSet.as_view({"get": "by_user"}),
        name="transport-by-user",
    ),
] + router.urls
