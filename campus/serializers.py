"""I/O serializers for the campus app.

* ``CampusLocationSerializer`` — admin CRUD serializer (model fields).
* ``CampusLocationAppSerializer`` — emits the exact camelCase shape the mobile
  app expects (``types.ts`` ``CampusLocation``: ``{id, name, category, building,
  floor?, etaMins}``) for ``GET /campus/locations``.
"""
from rest_framework import serializers

from campus.models import CampusLocation


class CampusLocationSerializer(serializers.ModelSerializer):
    """Admin CRUD serializer for CampusLocation."""

    class Meta:
        model = CampusLocation
        fields = [
            "id",
            "name",
            "category",
            "building",
            "floor",
            "eta_mins",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class CampusLocationAppSerializer(serializers.ModelSerializer):
    """Matches ``types.ts`` ``CampusLocation`` (camelCase ``etaMins``)."""

    id = serializers.CharField(read_only=True)
    etaMins = serializers.IntegerField(source="eta_mins", read_only=True)

    class Meta:
        model = CampusLocation
        fields = ["id", "name", "category", "building", "floor", "etaMins"]
