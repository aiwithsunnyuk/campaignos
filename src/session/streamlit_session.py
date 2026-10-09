import streamlit as st

from .models import AuthenticatedSession
from .service import AuthenticationService


SESSION_KEY = "campaignos_session"


def get_session() -> AuthenticatedSession | None:
    return st.session_state.get(SESSION_KEY)


def sign_in(user_id: str) -> AuthenticatedSession:
    session = AuthenticationService().authenticate(user_id)
    st.session_state[SESSION_KEY] = session
    return session


def sign_out() -> None:
    st.session_state.pop(SESSION_KEY, None)
    st.session_state.pop("governed_action", None)
    st.session_state.pop("decision_events", None)
    st.session_state.pop("dry_run_result", None)


def is_authenticated() -> bool:
    return get_session() is not None


def sign_in_identity(identity_session):
    """Create a CampaignOS session from an authenticated external identity."""
    from .models import AuthenticatedSession

    session = AuthenticatedSession(
        user_id=identity_session.user_id,
        email=identity_session.email,
        display_name=identity_session.display_name,
        tenant_id=identity_session.tenant_id,
        role=identity_session.role,
        authenticated=True,
    )

    st.session_state[SESSION_KEY] = session
    return session
