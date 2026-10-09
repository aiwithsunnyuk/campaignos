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
