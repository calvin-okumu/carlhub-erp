# DjangoCRM Agent Playbook

## When to Use Each Agent

- Explorer: first pass to locate files, entry points, and data flow.
- Frontend Dev: UI features, pages, components, hooks, types.
- Backend Dev: API work, models, serializers, views, migrations.
- API Contract: ensure frontend calls match backend endpoints and serializers.
- Debugger: errors, failing tests, runtime exceptions.
- Performance: slow pages, heavy queries, large responses.
- Test Runner: validate changes quickly.
- Docs/Notes: summarize changes, release notes, PR text.

## Recommended Order by Task Type

### New Feature (full stack)

Explorer -> Frontend Dev + Backend Dev -> API Contract -> Test Runner -> Docs/Notes

### Bug Fix (frontend)

Explorer -> Debugger -> Frontend Dev -> Test Runner -> Docs/Notes

### Bug Fix (backend/API)

Explorer -> Debugger -> Backend Dev -> API Contract -> Test Runner -> Docs/Notes

### Refactor

Explorer -> (Frontend/Backend Dev) -> Performance (optional) -> Test Runner -> Docs/Notes

### Performance Issue

Explorer -> Performance -> (Frontend/Backend Dev) -> Test Runner -> Docs/Notes

## Sample Prompts

- Explorer
  "Find where <feature> lives; return entry points and key files."

- Frontend Dev
  "Implement <feature> in Next.js App Router. List files, approach, UI risks, and tests."

- Backend Dev
  "Add/modify <endpoint> in Django/DRF. Include models/serializers/views/migrations."

- API Contract
  "Verify frontend <feature> API calls match backend endpoints. List mismatches and fixes."

- Debugger
  "Analyze this error log; propose 1-3 fixes and how to verify."

- Performance
  "Scan for performance hotspots related to <feature> and propose improvements."

- Test Runner
  "Smallest test set to validate <change>; run via Makefile if possible."

- Docs/Notes
  "Summarize changes and write brief release notes."

## Default Command Behavior

- Prefer Makefile commands:
  - make dev-frontend, make dev-backend
  - make test-frontend, make test-backend
  - make lint-frontend
- Run tests after non-trivial changes.
- Avoid destructive commands unless explicitly requested.
