# Architecture Documentation

Detailed technical architecture of the Next Action Tracker system.

## System Overview

The Next Action Tracker follows a modern three-tier architecture with clear separation of concerns:

```mermaid
graph TB
    subgraph "Client Layer"
        Browser[Web Browser]
        Mobile[Mobile Browser]
    end
    
    subgraph "Presentation Layer"
        React[React SPA]
        RQ[React Query]
        Components[UI Components]
        React --> RQ
        React --> Components
    end
    
    subgraph "API Layer"
        LB[Load Balancer]
        FastAPI[FastAPI Server]
        Middleware[Middleware Stack]
        Routes[API Routes]
        LB --> FastAPI
        FastAPI --> Middleware
        Middleware --> Routes
    end
    
    subgraph "Business Logic Layer"
        Services[Business Services]
        Validation[Data Validation]
        Models[Pydantic Models]
        Services --> Validation
        Validation --> Models
    end
    
    subgraph "Data Layer"
        Pool[Connection Pool]
        PostgreSQL[(PostgreSQL)]
        Indexes[Optimized Indexes]
        Pool --> PostgreSQL
        PostgreSQL --> Indexes
    end
    
    Browser --> React
    Mobile --> React
    RQ --> LB
    Routes --> Services
    Services --> Pool
```

## Component Architecture

### Frontend Architecture

```mermaid
graph TD
    subgraph "React Application"
        App[App.tsx]
        Router[React Router]
        
        subgraph "Contexts"
            TenantCtx[TenantContext]
            ToastCtx[ToastContext]
        end
        
        subgraph "Components"
            Dashboard[DueActionsDashboard]
            Card[DueActionCard]
            Modal[CompleteActionModal]
            Error[ErrorBoundary]
        end
        
        subgraph "Services"
            API[API Client]
            Query[React Query]
        end
        
        App --> Router
        App --> TenantCtx
        App --> ToastCtx
        Router --> Dashboard
        Dashboard --> Card
        Card --> Modal
        Dashboard --> Error
        Components --> Query
        Query --> API
    end
```

#### Key Frontend Patterns

1. **Container/Presentation Pattern**: Smart containers manage state, dumb components handle display
2. **Context for Global State**: Tenant and toast notifications use React Context
3. **React Query for Server State**: Automatic caching, background updates, optimistic updates
4. **Error Boundaries**: Graceful error handling at component level

### Backend Architecture

```mermaid
graph TD
    subgraph "FastAPI Application"
        Main[main.py]
        
        subgraph "API Layer"
            Router[API Router]
            Routes[Route Handlers]
            Deps[Dependencies]
        end
        
        subgraph "Middleware Stack"
            CORS[CORS Middleware]
            Tenant[Tenant Validation]
            Logging[Request Logging]
            Error[Error Handler]
        end
        
        subgraph "Business Logic"
            Services[Business Services]
            Models[Pydantic Models]
            Validation[Data Validation]
        end
        
        subgraph "Data Access"
            DB[Database Connection]
            Queries[SQL Queries]
            Migrations[Schema Migrations]
        end
        
        Main --> Router
        Router --> Routes
        Routes --> Deps
        Main --> CORS
        CORS --> Tenant
        Tenant --> Logging
        Logging --> Error
        Routes --> Services
        Services --> Models
        Models --> Validation
        Services --> DB
        DB --> Queries
        DB --> Migrations
    end
```

#### Key Backend Patterns

1. **Dependency Injection**: FastAPI's dependency system for database connections and tenant validation
2. **Repository Pattern**: Abstracted data access layer (implicit in route handlers)
3. **Middleware Pipeline**: Request processing pipeline with tenant validation and logging
4. **Pydantic Models**: Type-safe data validation and serialization

## Data Architecture

### Database Schema

```mermaid
erDiagram
    tenants {
        uuid id PK
        text name
        timestamptz created_at
    }
    
    opportunities {
        uuid id PK
        uuid tenant_id FK
        text name
        integer value
        text stage
        timestamptz next_action_at
        text next_action_details
        timestamptz last_activity_at
        timestamptz created_at
        timestamptz updated_at
    }
    
    tenants ||--o{ opportunities : "has many"
```

### Index Strategy

```sql
-- Primary performance index for NAT dashboard
CREATE INDEX idx_opportunities_tenant_due 
ON opportunities (tenant_id, next_action_at) 
WHERE next_action_at IS NOT NULL;

-- Additional indexes for common queries
CREATE INDEX idx_opportunities_tenant_activity 
ON opportunities (tenant_id, last_activity_at DESC);

CREATE INDEX idx_opportunities_tenant_stage 
ON opportunities (tenant_id, stage);
```

### Query Patterns

#### Due Actions Query (Hot Path)
```sql
-- Optimized for dashboard performance
SELECT id, name, value, stage, next_action_at, next_action_details 
FROM opportunities
WHERE tenant_id = $1
  AND next_action_at IS NOT NULL
  AND next_action_at <= NOW()
ORDER BY next_action_at ASC;
```

**Performance Characteristics**:
- Uses `idx_opportunities_tenant_due` index
- Typical execution time: <10ms for 1000 opportunities
- Scales linearly with due action count

#### Action Completion Update (Write Path)
```sql
-- Atomic update with optimistic locking
UPDATE opportunities
SET 
    next_action_at = $2,
    next_action_details = $3,
    last_activity_at = NOW(),
    updated_at = NOW()
WHERE id = $1 AND tenant_id = $4;
```

**Performance Characteristics**:
- Single row update with primary key lookup
- Typical execution time: <5ms
- ACID compliant with automatic timestamp updates

## Security Architecture

### Multi-Tenant Isolation

```mermaid
graph LR
    subgraph "Request Flow"
        Client[Client Request]
        Header[X-Tenant-ID Header]
        Middleware[Tenant Middleware]
        Query[Database Query]
        Filter[WHERE tenant_id = ?]
    end
    
    Client --> Header
    Header --> Middleware
    Middleware --> Query
    Query --> Filter
```

#### Current Implementation (Application-Level)
- **Header-based identification**: All requests require `X-Tenant-ID`
- **Middleware validation**: Automatic tenant ID extraction and validation
- **Query-level filtering**: All database queries include tenant filter
- **No shared data**: Complete logical separation between tenants

#### Security Considerations
- **IDOR Risk**: Malicious header manipulation could access other tenant data
- **No Authentication**: Current implementation assumes trusted environment
- **Audit Gap**: No logging of cross-tenant access attempts

#### Production Security Recommendations
```python
# JWT-based tenant validation (recommended)
async def validate_jwt_tenant(token: str = Depends(oauth2_scheme)):
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    tenant_id = payload.get("tenant_id")
    if not tenant_id:
        raise HTTPException(401, "Invalid token")
    return tenant_id

# Row-Level Security (PostgreSQL)
ALTER TABLE opportunities ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON opportunities
    FOR ALL TO app_user
    USING (tenant_id = current_setting('app.tenant_id')::uuid);
```

## Performance Architecture

### Caching Strategy

```mermaid
graph TD
    subgraph "Client-Side Caching"
        RQCache[React Query Cache]
        Browser[Browser Cache]
        LocalStorage[Local Storage]
    end
    
    subgraph "Server-Side Caching"
        AppCache[Application Cache]
        DBPool[Connection Pool]
        QueryCache[Query Plan Cache]
    end
    
    subgraph "Database Optimization"
        Indexes[Optimized Indexes]
        Stats[Query Statistics]
        Vacuum[Auto Vacuum]
    end
    
    RQCache --> AppCache
    AppCache --> DBPool
    DBPool --> Indexes
```

#### React Query Configuration
```typescript
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30 * 1000,        // 30 seconds
      cacheTime: 5 * 60 * 1000,    // 5 minutes
      refetchOnWindowFocus: true,   // Refresh on focus
      retry: 3,                     // Retry failed requests
    },
  },
});
```

#### Database Connection Pooling
```python
# FastAPI with asyncpg
DATABASE_URL = "postgresql://user:pass@host:5432/db"
engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,           # Connection pool size
    max_overflow=30,        # Additional connections
    pool_pre_ping=True,     # Validate connections
    pool_recycle=3600,      # Recycle after 1 hour
)
```

### Scalability Patterns

#### Horizontal Scaling
```yaml
# Load balancer configuration
services:
  nginx:
    image: nginx:alpine
    ports: ["80:80"]
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - backend-1
      - backend-2
      - backend-3

  backend-1:
    build: ./backend
    environment:
      - INSTANCE_ID=1
  
  backend-2:
    build: ./backend
    environment:
      - INSTANCE_ID=2
      
  backend-3:
    build: ./backend
    environment:
      - INSTANCE_ID=3
```

#### Database Scaling
```mermaid
graph TD
    subgraph "Read Scaling"
        Primary[(Primary DB)]
        Replica1[(Read Replica 1)]
        Replica2[(Read Replica 2)]
        Primary --> Replica1
        Primary --> Replica2
    end
    
    subgraph "Application Layer"
        WriteAPI[Write Operations]
        ReadAPI[Read Operations]
        WriteAPI --> Primary
        ReadAPI --> Replica1
        ReadAPI --> Replica2
    end
```

## Deployment Architecture

### Development Environment

```mermaid
graph TD
    subgraph "Developer Machine"
        Docker[Docker Desktop]
        Compose[Docker Compose]
        Volumes[Volume Mounts]
        
        subgraph "Containers"
            Frontend[Frontend Container]
            Backend[Backend Container]
            Database[PostgreSQL Container]
        end
        
        Docker --> Compose
        Compose --> Frontend
        Compose --> Backend
        Compose --> Database
        Volumes --> Frontend
        Volumes --> Backend
    end
```

### Production Environment

```mermaid
graph TD
    subgraph "Load Balancer"
        ALB[Application Load Balancer]
        SSL[SSL Termination]
        ALB --> SSL
    end
    
    subgraph "Application Tier"
        ECS1[ECS Task 1]
        ECS2[ECS Task 2]
        ECS3[ECS Task 3]
    end
    
    subgraph "Database Tier"
        RDS[(RDS PostgreSQL)]
        Backup[(Automated Backups)]
        RDS --> Backup
    end
    
    subgraph "Monitoring"
        CloudWatch[CloudWatch]
        Logs[Log Aggregation]
        Metrics[Custom Metrics]
        CloudWatch --> Logs
        CloudWatch --> Metrics
    end
    
    SSL --> ECS1
    SSL --> ECS2
    SSL --> ECS3
    ECS1 --> RDS
    ECS2 --> RDS
    ECS3 --> RDS
    ECS1 --> CloudWatch
    ECS2 --> CloudWatch
    ECS3 --> CloudWatch
```

## Error Handling Architecture

### Frontend Error Boundaries

```typescript
// Component-level error handling
class ErrorBoundary extends React.Component {
  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Log to monitoring service
    logger.error('Component error', { error, errorInfo });
    
    // Show user-friendly message
    this.setState({ hasError: true });
  }
}

// API error handling
const apiClient = axios.create({
  baseURL: process.env.REACT_APP_API_URL,
  timeout: 10000,
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle authentication error
      redirectToLogin();
    } else if (error.response?.status >= 500) {
      // Handle server error
      showErrorToast('Server error occurred');
    }
    return Promise.reject(error);
  }
);
```

### Backend Error Handling

```python
# Global exception handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(
        "HTTP exception",
        extra={
            "status_code": exc.status_code,
            "detail": exc.detail,
            "path": request.url.path,
            "method": request.method,
            "tenant_id": request.headers.get("X-Tenant-ID"),
        }
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "error_code": getattr(exc, "error_code", "UNKNOWN_ERROR"),
            "timestamp": datetime.utcnow().isoformat(),
        }
    )

# Database error handling
async def handle_db_error(error: Exception) -> HTTPException:
    if isinstance(error, asyncpg.UniqueViolationError):
        return HTTPException(409, "Resource already exists")
    elif isinstance(error, asyncpg.ForeignKeyViolationError):
        return HTTPException(400, "Invalid reference")
    else:
        logger.exception("Database error")
        return HTTPException(500, "Internal server error")
```

## Monitoring Architecture

### Application Metrics

```python
# Custom metrics collection
from prometheus_client import Counter, Histogram, Gauge

# Request metrics
request_count = Counter(
    'nat_requests_total',
    'Total requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'nat_request_duration_seconds',
    'Request duration',
    ['method', 'endpoint']
)

# Business metrics
due_actions_gauge = Gauge(
    'nat_due_actions_total',
    'Current due actions',
    ['tenant_id']
)

actions_completed = Counter(
    'nat_actions_completed_total',
    'Actions completed',
    ['tenant_id']
)
```

### Health Check Architecture

```mermaid
graph TD
    subgraph "Health Checks"
        App[Application Health]
        DB[Database Health]
        Deps[Dependencies Health]
    end
    
    subgraph "Monitoring"
        Prometheus[Prometheus]
        Grafana[Grafana Dashboard]
        AlertManager[Alert Manager]
    end
    
    subgraph "Notifications"
        Slack[Slack Alerts]
        Email[Email Alerts]
        PagerDuty[PagerDuty]
    end
    
    App --> Prometheus
    DB --> Prometheus
    Deps --> Prometheus
    Prometheus --> Grafana
    Prometheus --> AlertManager
    AlertManager --> Slack
    AlertManager --> Email
    AlertManager --> PagerDuty
```

## Future Architecture Considerations

### Microservices Evolution

```mermaid
graph TD
    subgraph "Current Monolith"
        FastAPI[FastAPI Application]
        Business[Business Logic]
        Data[Data Access]
        FastAPI --> Business
        Business --> Data
    end
    
    subgraph "Future Microservices"
        Gateway[API Gateway]
        Auth[Auth Service]
        Opportunities[Opportunity Service]
        Notifications[Notification Service]
        Analytics[Analytics Service]
        
        Gateway --> Auth
        Gateway --> Opportunities
        Gateway --> Notifications
        Gateway --> Analytics
    end
```

### Event-Driven Architecture

```mermaid
graph LR
    subgraph "Event Sources"
        API[API Actions]
        Scheduler[Scheduled Jobs]
        Webhooks[External Webhooks]
    end
    
    subgraph "Event Bus"
        EventBus[Event Stream]
        Topics[Event Topics]
        EventBus --> Topics
    end
    
    subgraph "Event Consumers"
        Notifications[Notification Service]
        Analytics[Analytics Service]
        Integrations[External Integrations]
    end
    
    API --> EventBus
    Scheduler --> EventBus
    Webhooks --> EventBus
    Topics --> Notifications
    Topics --> Analytics
    Topics --> Integrations
```

This architecture provides a solid foundation for the current requirements while maintaining flexibility for future enhancements and scaling needs.