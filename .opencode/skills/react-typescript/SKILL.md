---
name: react-typescript
description: Guidelines for developing frontend functionality with React, TypeScript, Vite and Tailwind CSS. Use when creating or modifying pages, components, layouts, routing, forms, API integration, state management or frontend tests.
---

# React and TypeScript Development

## 1. General Principles

- Follow the project instructions defined in the root `AGENTS.md`.
- Use React with TypeScript.
- Use Vite as the frontend development and build tool.
- Use Tailwind CSS for styling.
- Prioritize simplicity, readability and maintainability.
- Inspect the existing frontend structure before making changes.
- Reuse existing components and conventions when appropriate.
- Avoid unnecessary abstractions, dependencies and premature optimization.
- Implement only functionality included in the approved OpenSpec change.

## 2. React Components

- Prefer functional components.
- Use hooks for state and lifecycle-related behavior.
- Keep components focused on a clear responsibility.
- Extract reusable components when they provide real value.
- Avoid excessively large components.
- Keep business rules out of presentation components when appropriate.
- Use props to communicate between components.
- Avoid unnecessary prop drilling; introduce shared state only when justified.

## 3. TypeScript

- Use explicit types for component props, function parameters and important data structures.
- Avoid `any`.
- Prefer interfaces or types that clearly represent application concepts.
- Use type-safe API responses.
- Handle optional and nullable values explicitly.
- Avoid unnecessary type assertions.
- Reuse shared types when appropriate.
- Do not duplicate types that should be shared across the application.

## 4. Styling with Tailwind CSS

- Use Tailwind CSS utility classes for component styling.
- Follow consistent spacing, typography and color conventions.
- Prefer responsive layouts.
- Avoid excessive conditional class logic.
- Extract reusable components when styling patterns repeat.
- Avoid adding another CSS framework.
- Use custom CSS only when Tailwind utilities are insufficient or when it improves clarity.

## 5. Routing

- Use React Router for client-side navigation.
- Organize routes clearly.
- Protect restricted routes according to the application's authentication and authorization flow.
- Handle unknown routes with an appropriate not-found page.
- Avoid duplicating route definitions.

## 6. API Integration

- Use the native Fetch API for HTTP requests.
- Do not introduce Axios.
- Centralize shared request behavior when useful.
- Handle HTTP errors explicitly.
- Handle loading, success and error states.
- Validate and type API responses appropriately.
- Keep API communication separate from presentation components.
- Coordinate API contracts with the backend agent.
- Do not assume endpoints or response structures that have not been defined.

## 7. Data Fetching and State Management

- Use TanStack Query for server state.
- Configure query keys consistently.
- Use queries for retrieving server data.
- Use mutations for operations that modify server data.
- Invalidate or update relevant queries after mutations.
- Avoid duplicating server state unnecessarily in local component state.
- Use React state for local UI interactions.
- Do not introduce additional state management libraries without a clear need.

## 8. Forms and Validation

- Use controlled inputs when appropriate.
- Provide clear validation feedback.
- Prevent duplicate submissions when necessary.
- Handle loading and error states.
- Keep form logic understandable.
- Coordinate validation expectations with the backend.
- Never rely exclusively on frontend validation for security or business rules.

## 9. Authentication and Authorization

- Follow the authentication flow established by the backend.
- Do not store passwords or sensitive credentials in frontend code.
- Do not expose secrets or private configuration.
- Handle expired or invalid sessions appropriately.
- Hide or disable restricted actions in the interface when appropriate.
- Never treat frontend restrictions as a substitute for backend authorization.

## 10. Accessibility and Responsive Design

- Use semantic HTML elements.
- Provide labels for form controls.
- Ensure interactive elements are keyboard accessible.
- Use appropriate alternative text for meaningful images.
- Maintain sufficient contrast.
- Design interfaces for different screen sizes.
- Avoid relying exclusively on color to communicate information.

## 11. Testing

- Use Vitest for frontend tests.
- Use React Testing Library for component behavior tests.
- Test meaningful user interactions.
- Test loading, success and error states when relevant.
- Test form validation and conditional rendering.
- Avoid tests that depend excessively on implementation details.
- Do not claim tests passed if they were not executed.

## 12. OpenSpec

When implementing an approved OpenSpec change:

- Review its requirements and acceptance criteria.
- Identify affected pages, components, routes and API contracts.
- Implement only the approved scope.
- Coordinate backend dependencies with the backend agent.
- Verify the implementation against the requirements.
- Report unresolved design or integration decisions.

## 13. Collaboration

- Focus on frontend implementation.
- Coordinate API contracts with the backend agent.
- Do not modify backend code.
- Do not perform Git operations.
- Report integration issues and relevant technical decisions.