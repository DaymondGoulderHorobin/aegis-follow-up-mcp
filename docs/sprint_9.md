# Sprint 9

## Objective

Finalize marketplace-facing branding and submission polish for Aegis Follow-Up
without adding risky new clinical functionality.

Clinical decision support only. For clinician review. Not a diagnosis or treatment directive.

## Branch

```text
codex/sprint-9-aegis-marketplace-polish
```

## Scope

- Rebrand marketplace-facing docs to Aegis Follow-Up.
- Keep repository, package, Render service, and endpoint names stable.
- Add the Aegis Follow-Up logo asset.
- Add final marketplace listing, judge testing guide, and Render/Gemini checklist.
- Tighten the demo script to a 5-step flow.
- Explain the two-AI-layer architecture.
- Bump app/package version to `0.9.0`.

## Two-AI-Layer Architecture

- Prompt Opinion agent: interprets user intent and chooses MCP tools.
- Aegis Follow-Up MCP: performs deterministic clinical review, audit explanation,
  task queue generation, FHIR transparency, handoff payload creation, and optional
  Gemini narrative synthesis.
- Gemini: summarizes structured deterministic evidence only.
- Safety validator: blocks unsafe wording and uses deterministic fallback when needed.
- Source of truth: deterministic findings, priority tier, audit trail, and task context.

## Deferred

- Full repo/package rename.
- Render service/domain rename.
- Real EHR writes.
- Full A2A transport.
- Persistent workflow database.
- New clinical decision-making tools.
- Additional LLM tools beyond controlled narrative synthesis.

## Validation

```bash
python -m pip install -e ".[dev]"
python -m pytest
ruff check .
python scripts/smoke_mcp.py --url http://127.0.0.1:8000/mcp/ --attempts 2 --delay-seconds 1 --timeout 30
```

Post-merge Render validation:

```bash
python scripts/smoke_mcp.py --url https://follow-up-radar-mcp.onrender.com/mcp/ --attempts 3 --delay-seconds 2 --timeout 30
python scripts/smoke_mcp.py --url https://follow-up-radar-mcp.onrender.com/mcp/ --expect-real-llm
```
