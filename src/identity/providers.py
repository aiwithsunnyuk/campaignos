from .models import Identity


class IdentityProviderError(ValueError):
    pass


def build_identity(
    *,
    identity_id: str,
    email: str,
    display_name: str,
    provider: str,
    provider_subject: str,
    verified: bool,
) -> Identity:
    allowed = {
        "work_email",
        "google",
        "apple",
        "github",
    }

    if provider not in allowed:
        raise IdentityProviderError(
            f"Unsupported identity provider: {provider}"
        )

    if not email.strip():
        raise IdentityProviderError("Email is required.")

    if not provider_subject.strip():
        raise IdentityProviderError(
            "Provider subject is required."
        )

    return Identity(
        identity_id=identity_id,
        email=email.strip().lower(),
        display_name=display_name.strip(),
        provider=provider,
        provider_subject=provider_subject,
        verified=verified,
    )
