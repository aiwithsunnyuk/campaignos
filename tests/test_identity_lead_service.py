from dataclasses import dataclass

from src.identity.models import Identity, TenantMembership
from src.next_best_action.identity_lead_service import (
    IdentityLeadNextBestActionService,
)
from src.session.identity_session import IdentitySession


@dataclass
class FakeLead:
    tenant_id: str


class FakeLeadService:
    def __init__(self):
        self.calls = []

    def get_next_best_action(self, *, lead, tenant_id):
        self.calls.append((lead, tenant_id))
        return {"tenant_id": tenant_id}


def make_identity_session() -> IdentitySession:
    identity = Identity(
        identity_id="default:test-user",
        email="sunnyukdesign@gmail.com",
        display_name="Sunny",
        provider="default",
        provider_subject="test-user",
        verified=True,
    )
    membership = TenantMembership(
        identity_id=identity.identity_id,
        tenant_id="reetha",
        role="director",
        status="active",
    )
    return IdentitySession(identity=identity, membership=membership)


def test_identity_service_uses_session_tenant():
    fake = FakeLeadService()
    service = IdentityLeadNextBestActionService(fake)
    session = make_identity_session()
    lead = FakeLead(tenant_id="reetha")

    result = service.get_next_best_action(session, lead)

    assert result["tenant_id"] == "reetha"
    assert fake.calls == [(lead, "reetha")]


def test_identity_service_does_not_accept_tenant_from_caller():
    fake = FakeLeadService()
    service = IdentityLeadNextBestActionService(fake)
    session = make_identity_session()
    lead = FakeLead(tenant_id="reetha")

    service.get_next_best_action(session, lead)

    _, tenant_id = fake.calls[0]
    assert tenant_id == session.tenant_id
    assert tenant_id != "some-other-tenant"
