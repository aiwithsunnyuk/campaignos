from __future__ import annotations

from typing import Any

from .models import Identity


class OIDCIdentityError(ValueError):
    """Raised when an authenticated OIDC identity is invalid."""


def identity_from_streamlit_user(user: Any) -> Identity:
    if not user:
        raise OIDCIdentityError(
            "No authenticated identity was provided."
        )

    email = getattr(user, "email", None)
    name = getattr(user, "name", None)

    if not email:
        raise OIDCIdentityError(
            "Authenticated identity does not contain an email address."
        )

    subject = (
        getattr(user, "sub", None)
        or getattr(user, "id", None)
        or email
    )

    provider = getattr(user, "provider", None) or "oidc"

    return Identity(
        identity_id=f"{provider}:{subject}",
        email=email.strip().lower(),
        display_name=(name or email).strip(),
        provider=provider,
        provider_subject=str(subject),
        verified=True,
    )


def is_authenticated(user: Any) -> bool:
    if not user:
        return False

    authenticated = getattr(user, "is_logged_in", None)

    if authenticated is not None:
        return bool(authenticated)

    return bool(getattr(user, "email", None))
