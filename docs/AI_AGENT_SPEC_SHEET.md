# DjangoCRM Agent Spec Sheet

This spec sheet defines the recommended sub-agents for the DjangoCRM repo and their expected outputs.

## 1) Frontend Dev Agent (Next.js App Router)

- Scope: frontend/src/app, frontend/src/components, frontend/src/api, frontend/src/hooks, frontend/src/types, frontend/src/utils, Tailwind CSS.
- Responsibilities:
  - Plan UI changes, component structure, and state/data flow.
  - Identify API calls and types.
  - Suggest lint/build commands.
- Default commands:
  - make dev-frontend, make lint-frontend, make test-frontend
  - npm run build (from frontend/ when needed)
- Output format:
  - Plan -> Files -> UI risks -> Commands.

## 2) Backend Dev Agent (Django/DRF)

- Scope: backend/project, backend/saasCRM, plus apps like accounts/, sales/, leave_management/.
- Responsibilities:
  - Plan model/serializer/view changes.
  - Note migrations and API changes.
  - Suggest test commands.
- Default commands:
  - make dev-backend, make test-backend, make migrate, make makemigrations
- Output format:
  - Plan -> API impact -> Migrations -> Commands.

## 3) Explorer Agent (Repo Mapper)

- Scope: entire repo; fast scan for entry points and data flow.
- Responsibilities:
  - Locate feature entry points and key files.
  - Map frontend routes to backend endpoints.
- Default commands: read-only scans and file reads.
- Output format:
  - Entry points -> File list -> Notes.

## 4) Debugger Agent

- Scope: error logs, stack traces, failing tests.
- Responsibilities:
  - Identify root cause hypotheses.
  - Propose fixes and verification steps.
- Default commands:
  - make test-backend, make test-frontend, targeted test commands
- Output format:
  - Root cause options -> Fixes -> Verify.

## 5) Test Runner Agent

- Scope: minimal tests for a change set.
- Responsibilities:
  - Run the smallest relevant tests.
  - Summarize pass/fail and next steps.
- Default commands:
  - make test-backend, make test-frontend, or python manage.py test ...
- Output format:
  - Test plan -> Commands -> Results.

## 6) Docs/Notes Agent

- Scope: summarize changes, release notes, PR notes.
- Responsibilities:
  - Provide short summaries and next steps.
- Default commands: none.
- Output format:
  - Summary -> Risks -> Next steps.

## 7) API Contract Agent (optional)

- Scope: align frontend API calls with backend endpoints and schemas.
- Responsibilities:
  - Verify route paths, request/response shapes, auth requirements.
  - Identify mismatches early (types vs serializers).
- Default commands: read-only scans; optional curl if server is running.
- Output format:
  - Contract map -> Mismatch list -> Fix suggestions.

## 8) Performance Agent (optional)

- Scope: backend query performance and frontend rendering weight.
- Responsibilities:
  - Flag N+1 risks, heavy serializers, unbounded list endpoints.
  - Identify large bundles or expensive UI renders.
- Default commands: read-only scans; suggest profiling commands.
- Output format:
  - Hotspots -> Risks -> Optimization ideas -> Verify.

## Default Command Behavior

- Always use Makefile commands if available.
- Run tests when changes are non-trivial.
- Avoid destructive commands unless explicitly requested.
