# Implementation Plan - Next Action Tracker

- [x] 1. Set up project structure and development environment

  - Create directory structure for backend (FastAPI) and frontend (React)
  - Set up Docker Compose configuration for PostgreSQL, backend, and frontend services
  - Configure environment variables and .env files for development
  - Initialize Git repository with proper .gitignore files
  - _Requirements: 6.1, 6.2, 6.3, 6.4_

- [x] 2. Implement database schema and models

  - [x] 2.1 Create PostgreSQL database schema

    - Write SQL migration scripts for tenants and opportunities tables
    - Create optimized indexes including idx_opportunities_tenant_due
    - Set up database connection and migration system
    - _Requirements: 4.2, 4.3_

  - [x] 2.2 Implement Pydantic data models

    - Create OpportunityBase, OpportunityCreate, OpportunityUpdate, and Opportunity models
    - Add tenant model and validation schemas
    - Implement proper datetime handling with timezone support
    - _Requirements: 1.1, 2.1, 3.1, 3.3_

  - [x] 2.3 Create database seed script
    - Write seed.py script to create demo tenants and opportunities
    - Include mix of due, future, and overdue actions for testing
    - Add data cleanup utilities for development
    - _Requirements: 1.1, 4.3_

- [x] 3. Build FastAPI backend with tenant isolation

  - [x] 3.1 Set up FastAPI application structure

    - Create main FastAPI app with proper middleware configuration
    - Implement tenant validation middleware for X-Tenant-ID header
    - Set up database connection pooling with asyncpg
    - Add structured logging configuration
    - _Requirements: 4.1, 4.4, 4.5_

  - [x] 3.2 Implement GET /api/v1/opportunities/due endpoint

    - Create route handler with tenant filtering
    - Implement optimized SQL query for due actions
    - Add proper error handling and validation
    - Include response serialization with Pydantic models
    - _Requirements: 1.1, 1.2, 1.3, 1.5_

  - [x] 3.3 Implement POST /api/v1/opportunities/{id}/complete_action endpoint

    - Create route handler for action completion workflow
    - Implement atomic database transaction for updates
    - Add validation for required fields (new_next_action_at, new_next_action_details)
    - Update last_activity_at timestamp automatically
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 3.1, 3.2_

  - [x]\* 3.4 Add comprehensive error handling and logging
    - Implement custom exception handlers for 400, 404, 422, 500 errors
    - Add structured logging for all action completions
    - Create error response models with consistent format
    - _Requirements: 5.2, 5.4_

- [x] 4. Create React frontend with TypeScript

  - [x] 4.1 Set up React application structure

    - Initialize React app with TypeScript and required dependencies
    - Configure React Query for server state management
    - Set up routing and basic app layout
    - Add CSS framework or styling solution
    - _Requirements: 5.1, 5.5_

  - [x] 4.2 Implement DueActionsDashboard component

    - Create main dashboard component with useQuery hook
    - Implement loading states with skeleton loaders
    - Add error boundary and error display components
    - Create empty state UI for "All done! 🎉" message
    - _Requirements: 1.1, 1.2, 1.4, 5.1, 5.2_

  - [x] 4.3 Build DueActionCard component

    - Create card component to display opportunity details
    - Format and display name, value, stage, and next action details
    - Add "Complete Action" button with proper styling
    - Implement click handler to open completion modal
    - _Requirements: 1.3, 2.1_

  - [x] 4.4 Develop CompleteActionModal component
    - Create modal with form for new action date and details
    - Implement DatePicker and TextArea with validation
    - Add useMutation hook for API calls
    - Handle loading states, error display, and success feedback
    - Implement automatic dashboard refresh after successful completion
    - _Requirements: 2.1, 2.2, 2.3, 2.5, 5.3, 5.4, 5.5_

- [x] 5. Integrate frontend and backend with proper error handling

  - [x] 5.1 Configure API client and tenant management

    - Set up axios or fetch client with X-Tenant-ID header injection
    - Create tenant context provider for React app
    - Implement API error interceptors and retry logic
    - _Requirements: 4.1, 4.4, 5.2_

  - [x] 5.2 Implement comprehensive error handling

    - Add network error handling with retry mechanisms
    - Create toast notification system for user feedback
    - Implement field-level validation error display
    - Add error boundaries for component-level error catching
    - _Requirements: 5.2, 5.4_

  - [ ]\* 5.3 Add unit tests for critical components
    - Write tests for DueActionsDashboard component behavior
    - Test CompleteActionModal form validation and submission
    - Create tests for API client error handling
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [x] 6. Set up deployment and documentation

  - [x] 6.1 Complete Docker Compose configuration

    - Finalize docker-compose.yml with all services
    - Configure proper networking between containers
    - Set up volume mounts for development
    - Add health checks for all services
    - _Requirements: 6.1, 6.2_

  - [x] 6.2 Create comprehensive README documentation

    - Document problem statement and solution approach
    - Include architecture diagrams and setup instructions
    - Add API documentation and usage examples
    - Document trade-offs, limitations, and next steps
    - _Requirements: 6.3, 6.4_

  - [ ]\* 6.3 Add integration tests and E2E testing
    - Create integration tests for API endpoints with test database
    - Write E2E tests for complete user workflows
    - Set up test data fixtures and cleanup procedures
    - _Requirements: 1.1, 1.2, 1.3, 2.1, 2.2, 2.3, 2.4, 2.5_

- [ ] 7. Final integration and testing

  - [ ] 7.1 End-to-end workflow testing

    - Test complete user journey from dashboard to action completion
    - Verify tenant isolation works correctly across all components
    - Test error scenarios and recovery mechanisms
    - Validate performance with seed data
    - _Requirements: 1.1, 1.2, 1.3, 1.5, 2.1, 2.2, 2.3, 2.4, 2.5, 4.1, 4.2, 4.3, 4.4, 4.5_

  - [ ] 7.2 Performance optimization and final polish
    - Optimize database queries and add monitoring
    - Implement React Query caching strategies
    - Add final UI polish and responsive design
    - Create production-ready build configuration
    - _Requirements: 5.1, 5.5_
