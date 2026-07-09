"""User data-access layer."""
from __future__ import annotations

from typing import Optional

from django.contrib.auth import get_user_model

from core.repositories import BaseRepository

User = get_user_model()


class UserRepository(BaseRepository):
    model = User

    def __init__(self):
        super().__init__(User)

    def get_by_email(self, email: str) -> Optional["User"]:
        if not email:
            return None
        return self.get_queryset().filter(email__iexact=email.strip()).first()

    def get_by_phone(self, phone: str) -> Optional["User"]:
        if not phone:
            return None
        return self.get_queryset().filter(phone=phone.strip()).first()

    def get_by_login(self, credential: str) -> Optional["User"]:
        """Resolve a user by any accepted login identifier: email or phone.

        The mobile contract accepts ``username``/``email``/``phone`` in one
        credential field. This model has no separate username, so a credential
        containing ``@`` (or matching an email) resolves by email; otherwise we
        fall back to phone."""
        if not credential:
            return None
        return self.get_by_email(credential) or self.get_by_phone(credential)

    def email_exists(self, email: str) -> bool:
        return self.get_queryset().filter(email__iexact=email.strip()).exists()

    def by_role(self, role: str):
        return self.get_queryset().filter(role=role)

    def active(self):
        return self.get_queryset().filter(is_active=True)
