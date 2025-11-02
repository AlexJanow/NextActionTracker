# Design Document - Next Action Tracker (NAT)

## Overview

The Next Action Tracker (NAT) is a focused dashboard application designed to prevent pipeline leakage in Sales CRM systems. The system consists of a React frontend, FastAPI backend, and PostgreSQL database, implementing a multi-tenant architecture with tenant-based data isolation.

The core workflow ensures that every sales opportunity maintains forward momentum by requiring sales representatives to immediately define the next action when completing the current one.

## Architecture

### System Architecture

```mermaid
graph TD
    User[Sales Rep] --> Browser[React SPA]
    
    subgraph Frontend[React Frontend]
        Dashboard[DueActionsDashboard]
        Card[DueActionCard]
        Modal[CompleteActionModal]
        Dashboard --> Card
        Card --> Modal
    end
    
    subgraph Backend[FastAPI Backend]
        API[API Routes]
        Auth[Tenant Validation]
        Logic[Business Logic]
        API --> Auth
        Auth --> Logic
    end
    
    subgraph Database[PostgreSQL]
        Tenants[tenants table]
        Opportunities[opportunities table]
        Indexes[Optimized Indexes]
        Tenants --> Opportunities
        Opportunities --> Indexes
    end
    
    Browser --> API
    Logic --> Database
```

### Technology Stack

- **Frontend**: React 18+ with TypeScript, React Query for server state management
- **Backend**: FastAPI with Python 3.11+, Pydantic for validation
- **Database**: PostgreSQL 15+ with timezone support
- **Deployment**: Docker Compose for local development

## Components and Interfaces

### Database Schema

#### Tenants Table
```sql
CREATE TABLE tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

#### Opportunities Table
```sql
CREATE TABLE opportunities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    name TEXT NOT NULL,
    value INTEGER,
    stage TEXT NOT NULL,
    next_action_at TIMESTAMPTZ,
    next_action_details TEXT,
    last_activity_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Critical index for NAT dashboard performance
CREATE INDEX idx_opportunities_tenant_due 
ON opportunities (tenant_id, next_action_at) 
WHERE next_action_at IS NOT NULL;
```

### API Endpoints

#### GET /api/v1/opportunities/due
**Purpose**: Retrieve all due actions for the NAT dashboard

**Headers**: 
- `X-Tenant-ID`: UUID (required)

**Response**: Array of opportunity objects with due actions

**Query Logic**:
```sql
SELECT id, name, value, stage, next_action_at, next_action_details 
FROM opportunities
WHERE tenant_id = :tenant_id
  AND next_action_at IS NOT NULL
  AND next_action_at <= NOW()
ORDER BY next_action_at ASC;
```

#### POST /api/v1/opportunities/{opportunity_id}/complete_action
**Purpose**: Complete current action and set next action

**Headers**: 
- `X-Tenant-ID`: UUID (required)

**Request Body**:
```json
{
    "new_next_action_at": "2025-11-10T10:00:00Z",
    "new_next_action_details": "Send customized contract"
}
```

**Update Logic**:
```sql
UPDATE opportunities
SET 
    next_action_at = :new_next_action_at,
    next_action_details = :new_next_action_details,
    last_activity_at = NOW(),
    updated_at = NOW()
WHERE id = :opportunity_id AND tenant_id = :tenant_id;
```

### Frontend Components

#### DueActionsDashboard Component
- **State Management**: Uses React Query `useQuery` for server state
- **Loading States**: Skeleton loader during data fetch
- **Error Handling**: Error boundary with retry functionality
- **Empty State**: "All done! 🎉" when no due actions

#### DueActionCard Component
- **Props**: Opportunity data (id, name, value, stage, next_action_details, next_action_at)
- **Actions**: "Complete Action" button that opens modal
- **Display**: Formatted opportunity information with clear action details
- **Visual Prioritization**: 
  - Urgency calculation function: `getUrgencyColor(next_action_at: string): string`
  - Color logic based on days overdue:
    - `> 3 days`: red (#ef4444) - high urgency
    - `1-3 days`: yellow (#eab308) - medium urgency
    - `today`: blue (#3b82f6) - low urgency
  - Visual indicator: colored left border (4px width) on card

#### CompleteActionModal Component
- **Form Fields**: 
  - DatePicker for new action date (required, must be today or future)
  - TextArea for action description (required)
- **Quick-Select Buttons**: 
  - Three buttons: "+1 Week", "+2 Weeks", "+1 Month"
  - Positioned directly below DatePicker
  - Click handler: `handleQuickSelect(interval: 'week' | '2weeks' | 'month')`
  - Automatically populates DatePicker with calculated future date
- **Validation**: 
  - Client-side validation before submission
  - DatePicker min date set to today (prevents past date selection)
  - Form validation: `new_next_action_at >= today`
  - Error message: "Next action date must be today or in the future"
- **Mutation**: Uses React Query `useMutation` for API call
- **UX**: Disabled submit during loading, error display on failure

## Data Models

### Opportunity Model (Pydantic)
```python
class OpportunityBase(BaseModel):
    name: str
    value: Optional[int] = None
    stage: str
    next_action_at: Optional[datetime] = None
    next_action_details: Optional[str] = None

class OpportunityCreate(OpportunityBase):
    pass

class OpportunityUpdate(BaseModel):
    new_next_action_at: datetime
    new_next_action_details: str

class Opportunity(OpportunityBase):
    id: UUID
    tenant_id: UUID
    last_activity_at: datetime
    created_at: datetime
    updated_at: datetime
```

### Tenant Isolation Strategy

**Light Implementation Approach**:
- All API endpoints require `X-Tenant-ID` header
- Database queries filtered by `tenant_id` in WHERE clauses
- No row-level security (RLS) for simplicity
- Validation middleware ensures tenant_id presence

**Security Considerations**:
- Current approach is demo-suitable but IDOR-vulnerable
- Production would require JWT-based authentication
- Consider PostgreSQL RLS for additional security layer

## Error Handling

### Backend Error Responses
- **400 Bad Request**: Invalid input data (Pydantic validation)
- **404 Not Found**: Opportunity not found or wrong tenant
- **422 Unprocessable Entity**: Business logic violations
- **500 Internal Server Error**: Database or system errors

### Frontend Error Handling
- **Network Errors**: Retry mechanism with exponential backoff
- **Validation Errors**: Field-level error display
- **API Errors**: Toast notifications with error details
- **Loading States**: Skeleton loaders and disabled buttons

### Error Logging
```python
# Structured logging for action completions
logger.info(
    "Action completed",
    extra={
        "tenant_id": tenant_id,
        "opportunity_id": opportunity_id,
        "action_type": "complete_action",
        "timestamp": datetime.utcnow().isoformat()
    }
)
```

## Testing Strategy

### Backend Testing
- **Unit Tests**: Business logic validation, data model tests
- **Integration Tests**: API endpoint testing with test database
- **Database Tests**: Query performance and constraint validation

### Frontend Testing
- **Component Tests**: React Testing Library for UI components
- **Integration Tests**: User workflow testing with MSW mocking
- **E2E Tests**: Critical path testing with Playwright

### Test Data Strategy
- **Seed Script**: Creates demo tenants and opportunities with varied urgency levels
  - 1 opportunity: 7 days overdue (high urgency, red indicator)
  - 1 opportunity: 2 days overdue (medium urgency, yellow indicator)
  - 1 opportunity: due today (low urgency, blue indicator)
  - 1 opportunity: 1 day overdue (for demo completion workflow)
  - 1 opportunity: 3 days in future (should not appear on dashboard)
  - Total: 5-6 opportunities, 4 visible on dashboard
- **Test Fixtures**: Reusable test data for consistent testing
- **Database Cleanup**: Automated cleanup between test runs

## Performance Considerations

### Database Optimization
- **Primary Index**: `idx_opportunities_tenant_due` for dashboard queries
- **Query Optimization**: Filtered index excludes NULL next_action_at
- **Connection Pooling**: FastAPI with asyncpg for efficient connections

### Frontend Optimization
- **React Query Caching**: Automatic background refetch and caching
- **Component Optimization**: React.memo for expensive renders
- **Bundle Optimization**: Code splitting for reduced initial load

### Scalability Bottlenecks
- **Current Limitation**: No pagination on /due endpoint
- **Mitigation Strategy**: Cursor-based pagination for >1000 opportunities
- **Monitoring**: Track P95 latency on critical endpoints

## Demo Enhancement Features

### Visual Urgency Indicators

**Implementation Approach**:
```typescript
// Utility function in DueActionCard.tsx
function getUrgencyColor(nextActionAt: string): string {
  const actionDate = new Date(nextActionAt);
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  actionDate.setHours(0, 0, 0, 0);
  
  const daysOverdue = Math.floor((today.getTime() - actionDate.getTime()) / (1000 * 60 * 60 * 24));
  
  if (daysOverdue > 3) return '#ef4444'; // red - high urgency
  if (daysOverdue >= 1) return '#eab308'; // yellow - medium urgency
  return '#3b82f6'; // blue - due today
}
```

**CSS Application**:
```css
.due-action-card {
  border-left: 4px solid var(--urgency-color);
}
```

### Quick-Select Date Buttons

**Implementation Approach**:
```typescript
// In CompleteActionModal.tsx
function handleQuickSelect(interval: 'week' | '2weeks' | 'month') {
  const today = new Date();
  let futureDate: Date;
  
  switch (interval) {
    case 'week':
      futureDate = new Date(today.setDate(today.getDate() + 7));
      break;
    case '2weeks':
      futureDate = new Date(today.setDate(today.getDate() + 14));
      break;
    case 'month':
      futureDate = new Date(today.setMonth(today.getMonth() + 1));
      break;
  }
  
  setNewNextActionAt(futureDate);
}
```

**Date Validation**:
```typescript
// Validation function
function validateFutureDate(date: Date): boolean {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  date.setHours(0, 0, 0, 0);
  return date >= today;
}
```

### Enhanced Seed Data

**Seed Script Structure**:
```python
# backend/app/database/seed.py
from datetime import datetime, timedelta

def create_demo_opportunities(tenant_id: UUID):
    opportunities = [
        {
            "name": "Enterprise Deal - Acme Corp",
            "value": 50000,
            "stage": "Proposal",
            "next_action_at": datetime.now() - timedelta(days=7),  # High urgency
            "next_action_details": "Follow up on proposal feedback"
        },
        {
            "name": "Mid-Market - TechStart Inc",
            "value": 25000,
            "stage": "Negotiation",
            "next_action_at": datetime.now() - timedelta(days=2),  # Medium urgency
            "next_action_details": "Send revised pricing"
        },
        {
            "name": "SMB Deal - Local Business",
            "value": 5000,
            "stage": "Discovery",
            "next_action_at": datetime.now(),  # Due today
            "next_action_details": "Schedule demo call"
        },
        {
            "name": "Renewal - Existing Customer",
            "value": 15000,
            "stage": "Closed Won",
            "next_action_at": datetime.now() - timedelta(days=1),  # For demo flow
            "next_action_details": "Send renewal contract"
        },
        {
            "name": "Future Opportunity",
            "value": 30000,
            "stage": "Qualification",
            "next_action_at": datetime.now() + timedelta(days=3),  # Future (not shown)
            "next_action_details": "Initial discovery call"
        }
    ]
    return opportunities
```

## Deployment Architecture

### Development Environment
```yaml
# docker-compose.yml structure
services:
  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=nat_dev
  
  backend:
    build: ./backend
    depends_on: [db]
    environment:
      - DATABASE_URL=postgresql://...
  
  frontend:
    build: ./frontend
    depends_on: [backend]
    ports: ["3000:3000"]
```

### Environment Configuration
- **Database**: PostgreSQL with timezone support
- **Backend**: FastAPI with uvicorn ASGI server
- **Frontend**: React development server with proxy to backend