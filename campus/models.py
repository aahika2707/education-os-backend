"""Campus domain models.

A :class:`CampusLocation` is a navigable place on campus (mirrors the mobile
``types.ts`` ``CampusLocation``): a name, a ``category`` (academic / food /
sports / admin / hostel / medical), its ``building``, an optional ``floor``, and
a walking ``eta_mins``. Powers ``GET /campus/locations`` (student campus map).

Extends :class:`core.models.BaseModel` (UUID PK, audit fields, soft-delete).
"""
from django.db import models

from core.models import BaseModel


class CampusLocation(BaseModel):
    """A navigable campus location shown on the student campus map."""

    CATEGORY_ACADEMIC = "academic"
    CATEGORY_FOOD = "food"
    CATEGORY_SPORTS = "sports"
    CATEGORY_ADMIN = "admin"
    CATEGORY_HOSTEL = "hostel"
    CATEGORY_MEDICAL = "medical"
    CATEGORY_CHOICES = [
        (CATEGORY_ACADEMIC, "Academic"),
        (CATEGORY_FOOD, "Food"),
        (CATEGORY_SPORTS, "Sports"),
        (CATEGORY_ADMIN, "Admin"),
        (CATEGORY_HOSTEL, "Hostel"),
        (CATEGORY_MEDICAL, "Medical"),
    ]

    name = models.CharField(max_length=255)
    category = models.CharField(
        max_length=16, choices=CATEGORY_CHOICES, db_index=True
    )
    building = models.CharField(max_length=255, blank=True, default="")
    # Free-form (e.g. "Ground", "1-3", "Ground-4"); optional in the app contract.
    floor = models.CharField(max_length=64, blank=True, default="")
    # Walking ETA from a central reference point, in minutes.
    eta_mins = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["name"]
        verbose_name = "Campus Location"
        verbose_name_plural = "Campus Locations"
        indexes = [models.Index(fields=["category"])]

    def __str__(self):
        return f"{self.name} ({self.category})"
