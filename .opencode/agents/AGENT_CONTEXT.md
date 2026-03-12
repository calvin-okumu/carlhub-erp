# DjangoCRM Agent Context
# Use this file as shared guidance for all agents.

## Repo overview
- Backend: Django + DRF in `backend/`.
- Frontend: Next.js App Router + TypeScript in `frontend/`.
- Makefile provides canonical commands for setup, dev, lint, tests, build.

## Key locations
- Backend project: `backend/project/`, `backend/saasCRM/`.
- Django apps: `backend/accounts/`, `backend/sales/`, `backend/leave_management/`.
- Frontend app: `frontend/src/app/`.
- Frontend components: `frontend/src/components/`.
- Frontend API/hooks/types/utils: `frontend/src/api/`, `frontend/src/hooks/`, `frontend/src/types/`, `frontend/src/utils/`.
- Docs: `docs/` (API and features references).

## Cursor/Copilot rules
- No Cursor rules found in `.cursor/rules/` or `.cursorrules`.
- No Copilot instructions found in `.github/copilot-instructions.md`.

## Default commands (prefer Makefile)
### Setup
- `./setup.sh` or `make setup`
- `make setup-backend`
- `make setup-frontend`
- `make setup-docker`

### Development
- `make dev`
- `make dev-backend`
- `make dev-frontend`
- `make check-servers`
- `make stop`

### Lint
- `make lint-frontend` (calls `npm run lint`)
- `make lint` (frontend only; backend linter not configured)

### Test
- `make test`
- `make test-backend`
- `make test-frontend` (fallback if no test script is configured)

### Build
- `make build`
- `make build-backend` (collectstatic)
- `make build-frontend` (Next build)

### Docker
- `make docker-up`
- `make docker-down`
- `make docker-up-staging`
- `make docker-down-staging`

### CI
- `make ci-setup`
- `make ci-test`
- `make ci-build`

## Running a single test
### Backend (Django)
- Module: `cd backend && . venv/bin/activate && python manage.py test app.tests.test_module`
- Test case: `cd backend && . venv/bin/activate && python manage.py test app.tests.test_module.TestCase`
- Test method: `cd backend && . venv/bin/activate && python manage.py test app.tests.test_module.TestCase.test_method`

### Frontend
- No dedicated test runner in `frontend/package.json`.
- If you add Jest/Vitest later, document single-test commands here.

### Standalone scripts
- Some scripts live at repo root (for example `test_currency.py`).
- Run as needed: `python test_currency.py` (verify env first).

## Code style and conventions
### General
- Prefer Makefile commands for common workflows.
- Follow patterns in nearby files; stay consistent within each app/module.
- Keep changes scoped; avoid unrelated refactors.
- Do not commit secrets; use `.env` and `env.example`.

### Python / Django / DRF
- Formatting: PEP 8, 4-space indent, readable line lengths.
- Imports: stdlib, third-party, local; deterministic ordering.
- Naming:
  - Modules/functions/vars: `snake_case`.
  - Classes: `PascalCase`.
  - Constants: `UPPER_SNAKE_CASE`.
- Types: add hints for public APIs or complex returns.
- Models/serializers/views:
  - Keep model fields explicit and consistent with migrations.
  - Use DRF serializers for validation.
  - Prefer class-based views/viewsets consistent with existing code.
- Error handling:
  - Use DRF `ValidationError` and standard exceptions where appropriate.
  - Avoid broad `except Exception` unless re-raising with context.
  - Return JSON error shapes consistent with `docs/api/*`.

### Frontend / Next.js / React / TypeScript
- TypeScript is strict (`frontend/tsconfig.json`); avoid `any` when possible.
- Use path aliases like `@/components/...` and `@/types/...`.
- Naming:
  - Components: `PascalCase`.
  - Hooks: `useX`.
  - Utilities: `camelCase`.
- Client/server:
  - Use `"use client"` in client components that rely on hooks or browser APIs.
  - Keep server components pure and data-fetching-focused.
- Imports:
  - React/Next first, then third-party, then local.
  - Prefer absolute alias imports for shared modules.
- Styling:
  - Follow existing Tailwind/utility usage where present.
  - Keep class ordering consistent within a file.

### API contract expectations
- Keep request/response schemas aligned with DRF serializers.
- Match pagination, filtering, and error handling in `docs/api/*`.
- Update frontend types and API calls alongside backend schema changes.

## Recommended agent order (by task)
- New feature (full stack): Explorer -> Frontend Dev + Backend Dev -> API Contract -> Test Runner -> Docs/Notes.
- Bug fix (frontend): Explorer -> Debugger -> Frontend Dev -> Test Runner -> Docs/Notes.
- Bug fix (backend/API): Explorer -> Debugger -> Backend Dev -> API Contract -> Test Runner -> Docs/Notes.
- Refactor: Explorer -> (Frontend/Backend Dev) -> Performance (optional) -> Test Runner -> Docs/Notes.
- Performance issue: Explorer -> Performance -> (Frontend/Backend Dev) -> Test Runner -> Docs/Notes.

## Output format expectations
- Explorer: Entry points -> File list -> Notes.
- Frontend Dev: Plan -> Files -> UI risks -> Commands.
- Backend Dev: Plan -> API impact -> Migrations -> Commands.
- Debugger: Root cause options -> Fixes -> Verify.
- Test Runner: Test plan -> Commands -> Results.
- Docs/Notes: Summary -> Risks -> Next steps.
- API Contract: Contract map -> Mismatch list -> Fix suggestions.
- Performance: Hotspots -> Risks -> Optimization ideas -> Verify.

## Guardrails
- Use read-only scans unless user requests edits.
- Avoid destructive commands unless explicitly requested.
- Run the smallest relevant tests after non-trivial changes.
- Prefer explicit, readable code over cleverness.
- @frontend-dev must preserve the current dashboard UI design/look/feel for all UI design changes; follow existing typography, color palette, spacing, and component patterns unless explicitly directed otherwise.
- After every successful change by @frontend-dev, @test-runner should run tests to verify nothing broke.
- @test-runner must use curl to test endpoints and must not run project test files.
