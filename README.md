# Next Action Tracker (NAT)

A focused dashboard application designed to prevent pipeline leakage in Sales CRM systems by ensuring every sales opportunity maintains forward momentum.

## Problem Statement

Sales pipeline leakage occurs when deals are lost not because customers say "no", but because sales representatives forget to proactively plan and execute next steps. The Next Action Tracker ensures every deal has a defined next action with a due date, and forces sales reps to immediately plan the subsequent action when completing the current one.

## Architecture

- **Frontend**: React 18+ with TypeScript, React Query for server state management
- **Backend**: FastAPI with Python 3.11+, Pydantic for validation
- **Database**: PostgreSQL 15+ with timezone support
- **Deployment**: Docker Compose for local development

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Git

### Development Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd next-action-tracker
```

2. Start all services:
```bash
docker-compose up -d
```

3. Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Environment Configuration

The application uses environment variables for configuration:

#### Backend (.env)
- `DATABASE_URL`: PostgreSQL connection string
- `ENVIRONMENT`: development/production
- `LOG_LEVEL`: INFO/DEBUG/WARNING/ERROR
- `SECRET_KEY`: Application secret key
- `ALLOWED_ORIGINS`: CORS allowed origins

#### Frontend (.env)
- `REACT_APP_API_URL`: Backend API URL
- `REACT_APP_TENANT_ID`: Default tenant ID for development

## Project Structure

```
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── core/           # Core configuration
│   │   ├── models/         # Pydantic models
│   │   └── main.py         # FastAPI application
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   └── services/       # API services
│   ├── Dockerfile
│   └── package.json
├── database/
│   └── init.sql           # Database initialization
└── docker-compose.yml     # Development environment
```

## Development Workflow

1. Make changes to code
2. Services auto-reload in development mode
3. Database changes require container restart
4. Run tests before committing

## API Endpoints

### GET /api/v1/opportunities/due
Retrieve all due actions for the NAT dashboard.

**Headers**: `X-Tenant-ID: <tenant-uuid>`

### POST /api/v1/opportunities/{id}/complete_action
Complete current action and set next action.

**Headers**: `X-Tenant-ID: <tenant-uuid>`
**Body**:
```json
{
    "new_next_action_at": "2025-11-10T10:00:00Z",
    "new_next_action_details": "Send customized contract"
}
```

## Multi-Tenant Architecture

The application implements tenant isolation through:
- Required `X-Tenant-ID` header on all API requests
- Database queries filtered by `tenant_id`
- Demo tenant pre-configured for development

## Contributing

1. Create feature branch from main
2. Make changes with proper commit messages
3. Test changes locally with Docker Compose
4. Submit pull request

## License

[Add your license here]