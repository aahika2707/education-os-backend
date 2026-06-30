from django.contrib import admin

from .models import Course


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "title",
        "instructor",
        "level",
        "credits",
        "is_active",
        "updated_at",
    )
    list_filter = ("level", "is_active")
    search_fields = ("code", "title", "instructor")
    ordering = ("code",)
