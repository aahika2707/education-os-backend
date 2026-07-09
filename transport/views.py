"""HTTP layer for the transport app.

- ``GET /transport/routes/`` — list routes (app-shaped, nested stops), cached.
- ``GET /transport/routes/{id}/`` — a single route (app-shaped), cached.
- ``GET /transport/routes/{id}/live/`` — live status for a route, cached.
- Admin CRUD on routes (and stops / live-status management viewsets) flows
  through the service layer (audit + cache-invalidation) via
  :class:`core.viewsets.BaseModelViewSet`.

The realtime WebSocket consumer (live push) is added in a later step; this
module exposes the REST reads now.
"""
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from core.cache import TTL_LIBRARY, cache_get_or_set, cache_key
from core.permissions import Role
from core.viewsets import BaseModelViewSet

from students.models import Student

from transport.models import BusLiveStatus, BusRoute, BusStop
from transport.permissions import ADMIN_WRITE_MATRIX, TRANSPORT_MATRIX
from transport.serializers import (
    BusLiveStatusAppSerializer,
    BusLiveStatusSerializer,
    BusRouteAppSerializer,
    BusRouteSerializer,
    BusStopSerializer,
    TransportSpecSerializer,
    TransportStopSpecSerializer,
)

_STAFF_ROLES = set(Role.STAFF)
from transport.services import (
    BusLiveStatusService,
    BusRouteService,
    BusStopService,
)

# Transport reads are relatively static; reuse the library TTL (600s).
TTL_TRANSPORT = TTL_LIBRARY
TRANSPORT_PREFIX = "transport"


class BusRouteViewSet(BaseModelViewSet):
    """Bus routes: ``GET /transport/routes`` + admin CRUD + ``.../{id}/live``."""

    queryset = BusRoute.objects.prefetch_related("stops").all()
    serializer_class = BusRouteSerializer
    service_class = BusRouteService
    permission_matrix = TRANSPORT_MATRIX
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["number"]
    search_fields = ["name", "number", "driver"]
    ordering_fields = ["number", "name", "created_at"]

    def list(self, request, *args, **kwargs):
        """App-shaped list of routes (camelCase, nested stops), cached."""
        data = cache_get_or_set(
            cache_key(TRANSPORT_PREFIX, "routes", "all"),
            TTL_TRANSPORT,
            lambda: BusRouteAppSerializer(
                self.filter_queryset(self.get_queryset()), many=True
            ).data,
        )
        return Response(data)

    def retrieve(self, request, *args, **kwargs):
        """App-shaped single route (camelCase, nested stops), cached."""
        instance = self.get_object()
        data = cache_get_or_set(
            cache_key(TRANSPORT_PREFIX, "route", instance.pk),
            TTL_TRANSPORT,
            lambda: BusRouteAppSerializer(instance).data,
        )
        return Response(data)

    @extend_schema(responses={200: BusLiveStatusAppSerializer})
    @action(detail=True, methods=["get"])
    def live(self, request, pk=None):
        """``GET /transport/routes/{id}/live`` — live status for a route (cached)."""
        route = self.get_object()

        def build():
            status = (
                BusLiveStatus.objects.select_related("route")
                .filter(route_id=route.pk)
                .first()
            )
            if status is None:
                return None
            return BusLiveStatusAppSerializer(status).data

        data = cache_get_or_set(
            cache_key(TRANSPORT_PREFIX, "live", route.pk), TTL_TRANSPORT, build
        )
        if data is None:
            raise NotFound("No live status available for this route.")
        return Response(data)

    # -- GET /api/v1/transport/{user_id} (mobile API contract v1) ------------
    def _assert_user_access(self, request, user_id):
        """Non-staff may only use their own accounts user id; staff any."""
        if getattr(request.user, "role", None) in _STAFF_ROLES:
            return
        if str(request.user.id) != str(user_id):
            raise PermissionDenied("You can only access your own transport info.")

    @extend_schema(responses={200: TransportSpecSerializer})
    def by_user(self, request, pk=None):
        """Spec: ``{ route, driver, phone, live_location, eta, occupancy, stops }``.

        The ``<uuid:pk>`` is the accounts user id. Resolves the student (access
        checked) and returns their bus route with live status. No student↔route
        allocation model exists yet (avoid new fields this phase), so the
        college's primary route is returned; swap in the allocation lookup once
        it lands. Cached under ``transport:student:{user_id}``.
        """
        self._assert_user_access(request, pk)
        try:
            student = Student.objects.get(user_id=pk)
        except Student.DoesNotExist:
            raise NotFound("No student profile is linked to this user.")

        def build():
            route = (
                BusRoute.objects.prefetch_related("stops")
                .order_by("number")
                .first()
            )
            if route is None:
                return None
            live = BusLiveStatus.objects.filter(route_id=route.pk).first()
            stops = TransportStopSpecSerializer(
                route.stops.all(), many=True
            ).data
            return {
                "route": route.name,
                "driver": route.driver,
                "phone": route.driver_phone,
                "live_location": {
                    "lat": live.lat if live else None,
                    "lng": live.lng if live else None,
                },
                "eta": live.eta_mins if live else None,
                "occupancy": live.occupancy if live else None,
                "stops": stops,
            }

        data = cache_get_or_set(
            cache_key(TRANSPORT_PREFIX, "student", student.user_id),
            TTL_TRANSPORT,
            build,
        )
        if data is None:
            raise NotFound("No transport route is available.")
        return Response(data)


class BusStopViewSet(BaseModelViewSet):
    """Admin management of individual stops on a route."""

    queryset = BusStop.objects.select_related("route").all()
    serializer_class = BusStopSerializer
    service_class = BusStopService
    permission_matrix = ADMIN_WRITE_MATRIX
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["route"]
    search_fields = ["name"]
    ordering_fields = ["order", "name", "created_at"]


class BusLiveStatusViewSet(BaseModelViewSet):
    """Admin management of the per-route live status rows."""

    queryset = BusLiveStatus.objects.select_related("route").all()
    serializer_class = BusLiveStatusSerializer
    service_class = BusLiveStatusService
    permission_matrix = ADMIN_WRITE_MATRIX
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["route"]
    ordering_fields = ["eta_mins", "occupancy", "created_at"]
