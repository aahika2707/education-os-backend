from django.db import models
from django.urls import reverse


class Course(models.Model):
    """A single course offered on the platform."""

    LEVEL_CHOICES = [
        ("BEG", "Beginner"),
        ("INT", "Intermediate"),
        ("ADV", "Advanced"),
    ]

    code = models.CharField(max_length=20, unique=True, help_text="e.g. CS101")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    instructor = models.CharField(max_length=120, blank=True)
    level = models.CharField(max_length=3, choices=LEVEL_CHOICES, default="BEG")
    credits = models.PositiveIntegerField(default=3)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} — {self.title}"

    def get_absolute_url(self):
        return reverse("courses:detail", kwargs={"pk": self.pk})
