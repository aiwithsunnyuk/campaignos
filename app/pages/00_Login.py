import streamlit as st

from src.session.streamlit_session import (
    get_session,
    sign_in,
    sign_out,
)
from src.workspace.service import TenantWorkspaceService
from src.identity.oidc import (
    identity_from_streamlit_user,
    is_authenticated as oidc_authenticated,
)
from src.identity.access import IdentityAccessService, IdentityAccessError
from src.session.identity_session import IdentitySession
from src.session.streamlit_session import sign_in_identity


st.set_page_config(
    page_title="CampaignOS | Sign in",
    page_icon="◈",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------
# Styling
# ---------------------------------------------------------

st.markdown(
    """
    <style>
        /* Page */
        .stApp {
            background:
                radial-gradient(
                    circle at 50% 0%,
                    rgba(79, 70, 229, 0.16),
                    transparent 38%
                ),
                linear-gradient(180deg, #070b14 0%, #0b1020 55%, #080c16 100%);
            color: #f8fafc;
        }

        [data-testid="stHeader"] {
            background: transparent;
        }

        [data-testid="stSidebar"] {
            display: none;
        }

        .block-container {
            max-width: 760px;
            padding-top: 5rem;
            padding-bottom: 3rem;
        }

        /* Brand */
        .brand {
            text-align: center;
            margin-bottom: 2.2rem;
        }

        .brand-mark {
            width: 58px;
            height: 58px;
            margin: 0 auto 1rem auto;
            border-radius: 16px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 28px;
            font-weight: 800;
            color: white;
            background: linear-gradient(135deg, #6366f1, #8b5cf6);
            box-shadow:
                0 12px 35px rgba(99, 102, 241, 0.35);
        }

        .brand-name {
            font-size: 30px;
            font-weight: 750;
            letter-spacing: -1px;
            color: #f8fafc;
        }

        .brand-subtitle {
            margin-top: 7px;
            font-size: 14px;
            color: #94a3b8;
        }

        /* Card */
        .login-card {
            background: rgba(15, 23, 42, 0.78);
            border: 1px solid rgba(148, 163, 184, 0.14);
            border-radius: 22px;
            padding: 2.2rem 2.3rem;
            box-shadow:
                0 30px 80px rgba(0, 0, 0, 0.35);
            backdrop-filter: blur(18px);
        }

        .login-title {
            text-align: center;
            font-size: 22px;
            font-weight: 700;
            color: #f8fafc;
            margin-bottom: 6px;
        }

        .login-description {
            text-align: center;
            font-size: 14px;
            color: #94a3b8;
            margin-bottom: 1.7rem;
        }

        /* Provider labels */
        .provider-label {
            font-size: 12px;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin: 1.1rem 0 0.65rem 0;
            text-align: center;
        }

        /* Buttons */
        .stButton > button {
            width: 100%;
            min-height: 46px;
            border-radius: 11px;
            border: 1px solid rgba(148, 163, 184, 0.20);
            background: rgba(30, 41, 59, 0.72);
            color: #f8fafc;
            font-weight: 600;
            transition: all 0.18s ease;
        }

        .stButton > button:hover {
            border-color: rgba(129, 140, 248, 0.75);
            background: rgba(49, 46, 129, 0.32);
            color: white;
            transform: translateY(-1px);
        }

        /* Primary */
        .primary-login button {
            background: linear-gradient(135deg, #6366f1, #7c3aed);
            border: none;
            box-shadow: 0 8px 24px rgba(99, 102, 241, 0.25);
        }

        .primary-login button:hover {
            background: linear-gradient(135deg, #4f46e5, #6d28d9);
        }

        /* Divider */
        .divider {
            display: flex;
            align-items: center;
            gap: 12px;
            margin: 1.5rem 0;
            color: #475569;
            font-size: 12px;
        }

        .divider::before,
        .divider::after {
            content: "";
            height: 1px;
            flex: 1;
            background: rgba(148, 163, 184, 0.14);
        }

        /* Demo box */
        .demo-box {
            margin-top: 1.4rem;
            padding: 13px 15px;
            border-radius: 12px;
            background: rgba(30, 41, 59, 0.42);
            border: 1px solid rgba(148, 163, 184, 0.10);
            color: #94a3b8;
            font-size: 12px;
            line-height: 1.55;
        }

        .demo-box strong {
            color: #cbd5e1;
        }

        /* Security */
        .security {
            text-align: center;
            margin-top: 1.4rem;
            color: #64748b;
            font-size: 11px;
            line-height: 1.6;
        }

        /* Workspace */
        .workspace-card {
            background: rgba(15, 23, 42, 0.80);
            border: 1px solid rgba(99, 102, 241, 0.25);
            border-radius: 20px;
            padding: 1.8rem;
            text-align: center;
        }

        .workspace-icon {
            font-size: 34px;
            margin-bottom: 8px;
        }

        .workspace-title {
            font-size: 21px;
            font-weight: 700;
            color: #f8fafc;
        }

        .workspace-meta {
            margin-top: 8px;
            color: #94a3b8;
            font-size: 13px;
        }

        .status-pill {
            display: inline-block;
            margin-top: 14px;
            padding: 5px 11px;
            border-radius: 999px;
            background: rgba(34, 197, 94, 0.10);
            border: 1px solid rgba(34, 197, 94, 0.20);
            color: #86efac;
            font-size: 11px;
        }

        /* Footer */
        .footer {
            text-align: center;
            margin-top: 2rem;
            color: #475569;
            font-size: 11px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# External identity → CampaignOS workspace bridge
# ---------------------------------------------------------

if oidc_authenticated(st.user) and get_session() is None:
    try:
        identity = identity_from_streamlit_user(st.user)

        access_service = IdentityAccessService()

        membership = access_service.resolve_membership(
            identity,
            tenant_id="reetha",
        )

        identity_session = IdentitySession(
            identity=identity,
            membership=membership,
        )

        sign_in_identity(identity_session)
        st.rerun()

    except IdentityAccessError as exc:
        st.error(
            "Your identity is authenticated, but your account is not "
            "authorized for this CampaignOS tenant."
        )
        st.caption(str(exc))

        st.info(
            "You are signed in with a Google account that does not have "
            "access to this CampaignOS workspace."
        )

        if st.button("Use another Google account", type="primary"):
            st.login()

        st.stop()

    except Exception as exc:
        st.error("CampaignOS could not establish your workspace session.")
        st.caption(str(exc))
        st.stop()


# ---------------------------------------------------------
# Existing authenticated session
# ---------------------------------------------------------

session = get_session()

if session is not None:

    workspace = TenantWorkspaceService().resolve(session)

    st.markdown(
        """
        <div class="brand">
            <div class="brand-mark">◈</div>
            <div class="brand-name">CampaignOS</div>
            <div class="brand-subtitle">
                GTM intelligence & orchestration platform
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="workspace-card">
            <div class="workspace-icon">✓</div>
            <div class="workspace-title">
                Welcome back, {workspace.display_name}
            </div>
            <div class="workspace-meta">
                {workspace.tenant_id} · {workspace.role}
            </div>
            <div class="status-pill">
                ● Authenticated workspace
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")

    if st.button("Open Command Center", type="primary"):
        st.switch_page("pages/0_Command_Center.py")

    if st.button("Sign out"):
        sign_out()
        st.logout()

    st.markdown(
        """
        <div class="footer">
            CampaignOS · Secure tenant-aware workspace
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.stop()


# ---------------------------------------------------------
# Login UI
# ---------------------------------------------------------

st.markdown(
    """
    <div class="brand">
        <div class="brand-mark">◈</div>
        <div class="brand-name">CampaignOS</div>
        <div class="brand-subtitle">
            GTM intelligence & orchestration platform
        </div>
    </div>

    <div class="login-card">
        <div class="login-title">Sign in to your workspace</div>
        <div class="login-description">
            Access campaigns, leads, intelligence and governed GTM actions.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# Company email
# ---------------------------------------------------------

st.markdown(
    '<div class="provider-label">Company account</div>',
    unsafe_allow_html=True,
)

email = st.text_input(
    "Work email",
    placeholder="name@company.com",
    label_visibility="collapsed",
)

if st.button("Continue with work email", type="primary"):
    if not email.strip():
        st.error("Enter your work email to continue.")
    else:
        st.info(
            "Email verification will be connected to the production identity "
            "provider in the next authentication milestone."
        )


# ---------------------------------------------------------
# Social / identity providers
# ---------------------------------------------------------

st.markdown(
    '<div class="divider">or continue with</div>',
    unsafe_allow_html=True,
)

col1, col2 = st.columns(2)

with col1:
    if st.button("G  Google"):
        st.login()

with col2:
    if st.button("  Apple"):
        st.info("Apple identity sign-in will be connected in production.")

if st.button("◆  GitHub"):
    st.info("GitHub identity sign-in will be connected in production.")


# ---------------------------------------------------------
# Demo workspace
# ---------------------------------------------------------

st.markdown(
    '<div class="divider">development workspace</div>',
    unsafe_allow_html=True,
)

st.caption("Select a demo identity")

demo_options = {
    "Reetha Marketing Manager": "reetha-marketing",
    "Reetha Director": "reetha-director",
    "Reetha Sales User": "reetha-sales",
}

selected_identity = st.selectbox(
    "Demo identity",
    list(demo_options.keys()),
    label_visibility="collapsed",
)

if st.button("Enter demo workspace"):
    sign_in(demo_options[selected_identity])
    st.rerun()

st.markdown(
    """
    <div class="demo-box">
        <strong>Development mode</strong><br>
        Demo identities are available while CampaignOS authentication is being
        connected to a production identity provider.
        Production users will authenticate through verified identity and
        tenant membership.
    </div>

    <div class="security">
        Identity provider → verified identity → tenant membership → role →
        CampaignOS workspace
        <br><br>
        No passwords are stored by CampaignOS.
    </div>

    <div class="footer">
        CampaignOS · GTM Engineering Platform
    </div>
    """,
    unsafe_allow_html=True,
)
