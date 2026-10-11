# M17 | Knowledge and RAG

## Goal
Provide tenant-aware, source-grounded retrieval for campaign, product, and operational knowledge.

## Pipeline
1. Ingest and validate source.
2. Extract text and metadata.
3. Chunk with stable source references.
4. Embed through a provider adapter.
5. Store vectors and metadata.
6. Retrieve with tenant/ACL filters.
7. Rerank where justified.
8. Return answer with source citations and confidence/abstention behavior.

## Controls
- Enforce tenant ACLs before retrieval, not only in the prompt.
- Track source version, ingestion time, and deletion status.
- Support re-indexing and removal.
- Defend against instructions embedded in retrieved documents.
- Keep authoritative transactional facts in domain services, not RAG.
- Evaluate retrieval quality, citation correctness, and cross-tenant leakage.

## Deliverables
- `docs/architecture/m17_rag_contract.md`
- Ingestion and retrieval interfaces.
- Small representative evaluation dataset.
- Tests for tenant isolation, stale sources, citation integrity, and empty retrieval.

## Acceptance criteria
Answers are attributable to accessible sources; unsupported answers can abstain; cross-tenant retrieval is blocked.
