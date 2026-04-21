from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from api.models import GenerationRequest, Song

User = get_user_model()


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin configuration for the custom User model."""

    list_display = (
        "id",
        "username",
        "email",
        "google_id",
        "is_staff",
        "is_active",
        "date_joined",
    )
    search_fields = ("username", "email", "google_id")
    list_filter = ("is_staff", "is_superuser", "is_active")

    fieldsets = BaseUserAdmin.fieldsets + (
        ("OAuth", {"fields": ("google_id",)}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("OAuth", {"fields": ("google_id",)}),
    )


@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    """Admin configuration for generated songs."""

    list_display = (
        "id",
        "title",
        "user",
        "genre",
        "tone",
        "occasion",
        "privacy_level",
        "created_at",
    )
    search_fields = ("title", "description", "user__username", "user__email")
    list_filter = ("genre", "tone", "occasion", "privacy_level", "created_at")
    readonly_fields = ("created_at", "updated_at")


@admin.register(GenerationRequest)
class GenerationRequestAdmin(admin.ModelAdmin):
    """Admin configuration for generation requests."""

    list_display = (
        "id",
        "title",
        "user",
        "generator_strategy",
        "status",
        "external_task_id",
        "song",
        "created_at",
    )
    search_fields = (
        "title",
        "description",
        "error_message",
        "generator_strategy",
        "external_task_id",
        "user__username",
        "user__email",
    )
    list_filter = (
        "generator_strategy",
        "status",
        "genre",
        "tone",
        "occasion",
        "created_at",
    )
    readonly_fields = ("created_at", "updated_at")
