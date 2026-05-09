# Sprint 2

## Goals

- Harden FastMCP HTTP transport for Prompt Opinion and MCP Inspector testing.
- Connect Prompt Opinion-style FHIR headers to tool execution where FastMCP exposes request headers.
- Keep synthetic fixture mode as the default safe demo path.
- Improve deterministic patient lookup, observation parsing, and follow-up matching.
- Add deployment and Prompt Opinion runbooks.

## What Was Built

- Explicit `streamable-http` FastMCP transport configuration.
- Runtime FHIR context resolution from active HTTP headers.
- Multiple synthetic patients with patient-specific lookup and observation filtering.
- Safer observation normalization that skips malformed or non-numeric values.
- Recursive deterministic follow-up reference matching across supported FHIR resources.
- MCP Inspector documentation, Prompt Opinion setup notes, deployment guidance, and smoke script.
- CI Docker build step.

## Known Limitations

- Sprint 2 still uses synthetic fixtures by default and does not call external FHIR servers from the tool path.
- Header propagation depends on the MCP client forwarding custom HTTP headers.
- AI summarisation remains intentionally deferred to Sprint 3.
