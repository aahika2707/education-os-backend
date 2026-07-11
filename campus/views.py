"""HTTP layer for the campus app.

- ``GET /campus/locations`` — app-shaped list (camelCase), optional ``?category=``
  filter; backs the student campus map.
- Admin CRUD over locations flows through :class:`core.viewsets.BaseModelViewSet`.
"""
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from core.viewsets import BaseModelViewSet

from campus.models import CampusLocation
from campus.permissions import CAMPUS_MATRIX
from campus.serializers import (
    CampusLocationAppSerializer,
    CampusLocationSerializer,
)

VALID_CATEGORIES = {c[0] for c in CampusLocation.CATEGORY_CHOICES}


class CampusLocationViewSet(BaseModelViewSet):
    """Campus locations: ``GET /campus/locations`` (app-shaped) + admin CRUD."""

    queryset = CampusLocation.objects.all()
    serializer_class = CampusLocationSerializer
    permission_matrix = CAMPUS_MATRIX
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["category"]
    search_fields = ["name", "building"]
    ordering_fields = ["name", "eta_mins", "category"]

    @extend_schema(
        parameters=[OpenApiParameter("category", str, required=False)],
        responses={200: CampusLocationAppSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        """``GET /campus/locations?category=`` — app-shaped list."""
        qs = self.get_queryset()
        category = request.query_params.get("category")
        if category in VALID_CATEGORIES:
            qs = qs.filter(category=category)
        return Response(CampusLocationAppSerializer(qs, many=True).data)
