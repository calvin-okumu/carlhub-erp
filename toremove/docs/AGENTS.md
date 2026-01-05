# DjangoCRM Agent Guidelines

## Build/Lint/Test Commands

### Backend (Django)
- **Run all tests**: `cd backend && python manage.py test`
- **Run single test**: `cd backend && python manage.py test <app>.<TestClass>.<test_method>`
- **Run app tests**: `cd backend && python manage.py test <app>`
- **Lint**: `cd backend && black . && isort . && ruff check --fix .`
- **Type check**: `cd backend && mypy .`

### Frontend (Next.js/React)
- **Run tests**: `cd frontend && npm test` (currently no test script configured)
- **Lint**: `cd frontend && npm run lint`
- **Build**: `cd frontend && npm run build`
- **Dev server**: `cd frontend && npm run dev`

### Full Project
- **All tests**: `make test`
- **Backend tests**: `make test-backend`
- **Frontend tests**: `make test-frontend`
- **Build all**: `make build`
- **Lint all**: `make lint`

## Code Style Guidelines

### Python (Django)
- **Imports**: Standard library first, then third-party, then local imports. One import per line.
- **Naming**: snake_case for variables/functions, PascalCase for classes, UPPER_CASE for constants
- **Error handling**: Use try/except blocks, raise ValidationError for model validation
- **Docstrings**: Use triple quotes for module/class/function docs
- **Line length**: No explicit limit, follow PEP 8 conventions

### TypeScript/React
- **Strict mode**: Enabled - all variables must be typed
- **Imports**: Use path aliases (`@/components/*`, `@/api/*`, etc.)
- **Naming**: PascalCase for components/interfaces, camelCase for variables/functions
- **Types**: Define interfaces for API responses and component props
- **Error handling**: Use try/catch in async functions, proper error states in components
- **Components**: Functional components with hooks, TypeScript interfaces for props

### General
- **Commits**: Use conventional commits (feat:, fix:, docs:, etc.)
- **Security**: Never commit secrets, use environment variables
- **Testing**: Write unit tests for business logic, integration tests for APIs
- **Access Control**: Frontend folder access is restricted - only authorized developers should modify frontend code
- **RESTRICTION**: opencode is NOT allowed to make any changes to files in the frontend/ folder