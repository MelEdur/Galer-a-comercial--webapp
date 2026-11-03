
---
name: fastapi-development
description: Guidelines for developing backend functionality with Python, FastAPI, SQLAlchemy 2.0, Pydantic 2, Alembic, PostgreSQL and Pytest. Use when creating or modifying API endpoints, business logic, request and response schemas, database models, migrations, validation, dependencies or backend tests.
---

# FastAPI Development

## 1. General Principles

- Follow the project's root AGENTS.md.
- Inspect the existing backend structure before making changes.
- Follow existing conventions instead of introducing new patterns.
- Prefer simple, readable and maintainable solutions.
- Avoid unnecessary abstractions, layers and dependencies.
- Keep business logic separate from HTTP handling.
- Do not implement functionality outside the approved scope.

## 2. Project Organization

Organize backend code by functional modules.

Separate responsibilities when they provide a clear benefit:

- Routers: HTTP endpoints and request/response handling.
- Services: business logic and application operations.
- Schemas: request and response validation.
- Models: database entities and relationships.
- Repositories: database queries and persistence when needed.

Do not create empty or unnecessary modules.

Avoid placing all application logic inside routers.

## 3. FastAPI

- Use FastAPI routers to organize endpoints.
- Use dependency injection for shared dependencies.
- Use appropriate HTTP methods and status codes.
- Keep endpoints focused on HTTP concerns.
- Avoid duplicating business rules across endpoints.
- Use asynchronous endpoints only when the underlying operations support asynchronous execution.
- Do not perform blocking operations inside async endpoints.

## 4. Pydantic 2 Schemas

- Define explicit schemas for API requests and responses.
- Separate input schemas from output schemas when their responsibilities differ.
- Validate incoming data using Pydantic 2.
- Use appropriate field constraints and types with `Field`.
- Use `model_config = ConfigDict(from_attributes=True)` when building output
  schemas from SQLAlchemy models.
- Use `field_validator` and `model_validator` for custom validation instead of
  ad-hoc validation inside endpoints.
- Use `model_validate()` and `model_dump()`; avoid the deprecated `.dict()` and
  `.json()` methods.
- Avoid exposing database models directly as API responses.
- Do not return unnecessary internal fields.

## 5. Business Logic

- Place business rules in the appropriate service or application module.
- Keep routers thin.
- Validate business constraints before persisting data.
- Avoid duplicating business logic.
- Raise meaningful exceptions for expected business errors.
- Do not mix HTTP-specific concerns with domain rules unnecessarily.

## 6. Database Integration with SQLAlchemy 2.0

- Use PostgreSQL as the project's database.
- Use SQLAlchemy 2.0 as the ORM and data access toolkit.
- Define models with the declarative mapping using `Mapped` and `mapped_column`.
- Define relationships explicitly with `relationship(back_populates=...)`.
- Use `select()` with `Session.execute()` or `Session.scalars()` instead of the
  legacy `Query` API.
- Prefer typed, explicit column references over implicit or string-based ones.
- Inject a `Session` per request through a FastAPI dependency and close it
  reliably.
- Use transactions when multiple related operations must succeed or fail
  together.
- Use `selectinload()` or `joinedload()` to avoid N+1 queries when loading
  relationships.
- Keep database access organized in repositories or data access modules.
- Avoid unnecessary database queries.
- Keep business logic in services, not in models or repositories.
- Never expose sensitive database information through API responses.

### Migrations with Alembic

- Use Alembic for all database schema changes.
- Keep one focused migration per approved change.
- Generate migrations with autogenerate and always review the generated script.
- Never modify migrations that have already been applied to a shared database.
- Keep model changes and their migrations in the same change.
- Do not create or alter tables manually outside migrations.

## 7. Authentication and Authorization

- Enforce permissions on the backend.
- Never rely exclusively on frontend validation or route protection.
- Verify resource ownership before allowing modifications.
- Merchants may only manage their assigned stores and products.
- Administrators may manage merchant accounts and store assignments.
- Public endpoints must expose only intended information.
- Never store plaintext passwords or expose credentials, tokens or secrets.

## 8. API Design

- Follow REST conventions.
- Use consistent endpoint naming.
- Use appropriate HTTP status codes.
- Maintain consistent request and response structures.
- Return meaningful validation and error responses.
- Coordinate API contract changes with the frontend agent.
- Do not assume frontend requirements without reviewing the existing API contracts.

## 9. Error Handling

- Handle expected errors explicitly.
- Avoid exposing stack traces or internal implementation details.
- Use consistent error responses.
- Do not silently swallow exceptions.
- Distinguish validation errors, missing resources and authorization failures.

## 10. Testing with Pytest

- Use Pytest as the backend testing framework.
- Add tests for new or modified functionality.
- Test successful operations and expected failures.
- Test validation and authorization.
- Verify that merchants cannot access resources belonging to other merchants.
- Organize tests by module using `test_*.py` files and `test_*` functions.
- Use fixtures for the test database, sessions, clients and authentication.
- Use FastAPI dependency overrides to isolate the database and auth in tests.
- Prefer a transactional pattern that rolls back changes after each test.
- Use `pytest.mark.parametrize` for equivalent cases with different inputs.
- Use a dedicated test database; never run tests against development or
  production data.
- Run relevant tests after implementation with `pytest`.
- Never claim tests passed unless they were actually executed.

## 11. OpenSpec Integration

Before implementation:

- Review the approved OpenSpec change.
- Read the relevant requirements and acceptance criteria.
- Inspect the existing backend implementation.
- Identify affected modules and dependencies.

During implementation:

- Follow the approved scope.
- Avoid unrelated changes.
- Report ambiguities instead of inventing requirements.

After implementation:

- Run relevant tests.
- Verify acceptance criteria.
- Report modified files and test results.
- Identify any specification updates that may be necessary.

## 12. Collaboration

- Work exclusively on backend responsibilities.
- Coordinate API contract changes with the frontend agent.
- Do not modify frontend code.
- Do not perform Git operations.
- Report integration issues to the coordinating agent.
