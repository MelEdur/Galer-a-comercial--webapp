
# AGENTS.md

## 1. Project Overview

Web application designed to promote commercial stores within a shopping gallery and improve visitors' shopping experience.

The application allows visitors to discover stores, search and explore products, browse categories, view product details, and locate stores using an interactive map.

Merchants can manage their store information and product catalogs through an administration panel.

The system has three user roles:

- Visitor: Can browse public information about stores and products.
- Merchant: Can manage their assigned store and its products.
- Administrator: Can manage merchant accounts and assign them to stores.

## 2. Technology Stack

The following technologies are the project's definitive stack.

### Backend

- Python
- FastAPI
- SQLAlchemy 2.0
- Pydantic 2
- Alembic
- PostgreSQL
- Pytest

### Frontend

- React
- TypeScript
- Vite
- Tailwind CSS
- React Router
- Fetch API for HTTP requests
- TanStack Query
- Vitest
- React Testing Library

### Infrastructure

- Docker
- Docker Compose

Technologies explicitly excluded for now:

- Axios (use Fetch API instead)
- shadcn/ui
- ESLint
- Prettier
- Ruff

Respect the existing project configuration and dependencies.

Do not introduce new technologies or dependencies without a clear justification. Use the technologies listed above instead of alternatives.

## 3. Architecture

### General

- Use a modular monolithic architecture.
- Organize application code by functionality.
- Keep responsibilities clearly separated.
- Avoid unnecessary abstractions, layers, and design patterns.
- Prefer simple and maintainable solutions.
- Do not introduce microservices.

### Backend

- Organize backend code by functional modules.
- Separate API handling, business logic, and data access.
- Keep business rules outside HTTP controllers.
- Use explicit schemas for API requests and responses.
- Avoid exposing database models directly through API responses.
- Keep database access and persistence logic organized.

### Frontend

- Organize frontend code by functionality.
- Separate presentation components from API communication.
- Reuse components when they provide a clear benefit.
- Use TypeScript types to define data structures and API contracts.
- Avoid unnecessary global state and abstractions.

### Integration

- Backend is responsible for defining and maintaining API contracts.
- Frontend consumes the existing API contracts.
- Coordinate changes affecting both applications.
- Avoid duplicating business rules between frontend and backend.
- Backend always enforces business rules and permissions.

## 4. Development Principles

- Follow existing project conventions.
- Use clear and descriptive names.
- Keep functions and modules focused on a single responsibility.
- Avoid duplicated code and business logic.
- Prefer focused and incremental changes.
- Do not implement functionality beyond the requested scope.
- Inspect existing code before modifying it.
- Do not make architectural decisions without considering the existing project structure.

## 5. Security

- Enforce authentication and authorization on the backend.
- Never rely exclusively on frontend validation or permissions.
- Merchants can only manage their assigned stores and products.
- Verify resource ownership in protected operations.
- Never expose passwords, credentials, tokens, or sensitive information.
- Never commit secrets or environment-specific credentials.

## 6. Testing and Quality

- Add or update tests for modified functionality.
- Cover successful operations, validation errors, and authorization failures.
- Run relevant tests after implementation.
- Verify that existing functionality has not been unintentionally broken.
- Report tests that could not be executed.
- Never claim tests passed unless they were actually executed.

## 7. OpenSpec Workflow

Use OpenSpec to organize meaningful functional changes.

Follow the OpenSpec workflow:

- Explore: Investigate ideas or requirements when the solution is not yet clear.
- Propose: Define the proposed change, specifications, design, and implementation tasks.
- Apply: Implement an approved change.
- Verify: Check the implementation against the specifications and acceptance criteria.
- Archive: Archive a completed change.

Do not create unnecessary OpenSpec changes for trivial modifications.

Always review relevant existing specifications before implementing functionality.

Keep specifications aligned with approved requirements and architectural decisions.

Do not silently change approved requirements during implementation.

## 8. Agent Workflow

The project uses OpenCode's built-in Plan and Build agents, along with specialized subagents.

### Plan Agent

The Plan agent is responsible for analysis and planning.

It should:

- Understand the user's request.
- Inspect the existing project structure and implementation.
- Review relevant OpenSpec specifications.
- Explore uncertain requirements when necessary.
- Use OpenSpec to propose meaningful changes.
- Identify affected modules and components.
- Define implementation steps and acceptance criteria.
- Identify dependencies between backend and frontend tasks.
- Present the plan for review before implementation.

The Plan agent should not implement application functionality.

Do not create a separate coordinator agent. The built-in Plan agent fulfills the planning responsibility.

### Build Agent

The Build agent is responsible for implementing approved plans.

It should:

- Review the approved plan and relevant specifications.
- Break down the implementation into manageable tasks.
- Delegate specialized work to the appropriate subagents.
- Coordinate dependencies between agents.
- Review their results.
- Integrate the implementation.
- Execute relevant tests.
- Verify acceptance criteria.

The Build agent should not attempt to implement every specialized task itself when an appropriate subagent is available.

### Specialized Agents

#### Backend Agent

Responsible for:

- Python and FastAPI development.
- API endpoints and business logic.
- Database access and persistence.
- Request and response schemas.
- Authentication and authorization.
- Backend tests.

#### Frontend Agent

Responsible for:

- React and TypeScript development.
- Pages and components.
- User interactions and application state.
- API integration.
- Frontend tests and usability.

#### Git Agent

Responsible for:

- Git branches and repository management.
- Reviewing changes before commits.
- Creating commits.
- Pushing archived changes to `origin`.
- Managing merges and resolving Git conflicts.

All Git operations should be delegated to this agent.

#### Publicación después de archivar

Cuando un cambio OpenSpec se archiva y el usuario aprueba el cierre:

- Delegar al Git Agent la revisión final, el commit y el push a `origin`.
- Publicar en la rama actual; no crear ni cambiar de rama salvo pedido explícito.
- Usar Conventional Commits y excluir cambios ajenos al cambio archivado.
- Verificar con el MCP de GitHub que el commit y la rama remota existen.
- No usar `push_files` ni `create_or_update_file` del MCP para reemplazar el push de la historia local, salvo pedido explícito.

## 9. Delegation and Collaboration

- Delegate backend tasks to the Backend Agent.
- Delegate frontend tasks to the Frontend Agent.
- Delegate Git operations to the Git Agent.
- Do not delegate tasks unnecessarily.
- Coordinate API contracts before implementing dependent frontend functionality.
- Share relevant requirements and implementation context with each agent.
- Avoid assigning conflicting modifications to multiple agents.
- Review delegated results before considering a task complete.

For full-stack functionality, coordinate backend and frontend implementation.

When tasks are independent, agents may work in parallel.

The Build agent must not assume that delegation guarantees successful integration. It is responsible for reviewing and verifying the combined result.

## 10. Git Safety

- Do not overwrite or discard existing user changes.
- Never perform destructive Git operations without explicit approval.
- Do not commit unrelated changes.
- Do not commit automatically after every implementation task.
- After archiving an OpenSpec change, delegate the commit and push to the Git Agent, then verify the remote commit with the GitHub MCP.
- Ask for approval when an operation could discard work or rewrite shared history.

## 11. Definition of Done

A task is considered complete when:

- Requested functionality has been implemented.
- The implementation follows the project architecture.
- Relevant tests have been executed.
- Security and authorization requirements are respected.
- Acceptance criteria have been verified.
- Related OpenSpec specifications have been updated when necessary.
- No unrelated changes have been introduced.
- Remaining issues and limitations have been reported.
