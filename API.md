# API Documentation

Complete API reference for the Next Action Tracker backend.

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://your-domain.com/api`

## Authentication

All API endpoints require tenant identification via headers:

```http
X-Tenant-ID: <tenant-uuid>
Content-Type: application/json
```

## Error Handling

### Standard Error Response

```json
{
  "detail": "Error description",
  "error_code": "ERROR_CODE",
  "timestamp": "2025-10-29T10:00:00Z"
}
```

### HTTP Status Codes

| Code | Description | When Used |
|------|-------------|-----------|
| `200` | Success | Successful GET requests |
| `201` | Created | Successful POST requests |
| `400` | Bad Request | Invalid input data |
| `404` | Not Found | Resource not found |
| `422` | Unprocessable Entity | Validation errors |
| `500` | Internal Server Error | Server errors |

## Endpoints

### Health Check

#### GET /health

Health check endpoint for monitoring.

**Headers**: None required

**Response**:
```json
{
  "status": "healthy",
  "service": "next-action-tracker-api"
}
```

### Opportunities

#### GET /api/v1/opportunities/due

Retrieve all opportunities with due actions for the specified tenant.

**Headers**:
- `X-Tenant-ID`: UUID (required)

**Query Parameters**: None

**Response**:
```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "name": "Acme Corp Enterprise Deal",
    "value": 75000,
    "stage": "Proposal",
    "next_action_at": "2025-10-29T10:00:00Z",
    "next_action_details": "Follow up on technical questions from evaluation team"
  },
  {
    "id": "987fcdeb-51d2-43a1-b456-426614174001",
    "name": "StartupXYZ SaaS Contract",
    "value": 25000,
    "stage": "Negotiation",
    "next_action_at": "2025-10-28T14:30:00Z",
    "next_action_details": "Send revised contract with updated pricing"
  }
]
```

**Empty Response** (no due actions):
```json
[]
```

**Error Responses**:

Missing tenant header:
```json
{
  "detail": "Missing X-Tenant-ID header",
  "error_code": "MISSING_TENANT_ID"
}
```

Invalid tenant:
```json
{
  "detail": "Invalid tenant ID format",
  "error_code": "INVALID_TENANT_ID"
}
```

#### POST /api/v1/opportunities/{opportunity_id}/complete_action

Complete the current action and set the next action for an opportunity.

**Headers**:
- `X-Tenant-ID`: UUID (required)
- `Content-Type`: application/json

**Path Parameters**:
- `opportunity_id`: UUID of the opportunity

**Request Body**:
```json
{
  "new_next_action_at": "2025-11-05T14:00:00Z",
  "new_next_action_details": "Send technical documentation and schedule demo"
}
```

**Field Validation**:
- `new_next_action_at`: Required, must be a valid ISO 8601 datetime
- `new_next_action_details`: Required, non-empty string, max 500 characters

**Response**:
```json
{
  "message": "Action completed successfully",
  "opportunity_id": "123e4567-e89b-12d3-a456-426614174000",
  "updated_at": "2025-10-29T10:15:00Z"
}
```

**Error Responses**:

Opportunity not found or wrong tenant:
```json
{
  "detail": "Opportunity not found or access denied",
  "error_code": "OPPORTUNITY_NOT_FOUND"
}
```

Validation errors:
```json
{
  "detail": [
    {
      "loc": ["body", "new_next_action_at"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ],
  "error_code": "VALIDATION_ERROR"
}
```

Invalid date format:
```json
{
  "detail": [
    {
      "loc": ["body", "new_next_action_at"],
      "msg": "invalid datetime format",
      "type": "value_error.datetime"
    }
  ],
  "error_code": "VALIDATION_ERROR"
}
```

## Data Models

### Opportunity

```typescript
interface Opportunity {
  id: string;                    // UUID
  name: string;                  // Opportunity name
  value: number | null;          // Deal value in cents
  stage: string;                 // Current sales stage
  next_action_at: string | null; // ISO 8601 datetime
  next_action_details: string | null; // Action description
}
```

### Complete Action Request

```typescript
interface CompleteActionRequest {
  new_next_action_at: string;    // ISO 8601 datetime (required)
  new_next_action_details: string; // Action description (required)
}
```

### Complete Action Response

```typescript
interface CompleteActionResponse {
  message: string;               // Success message
  opportunity_id: string;        // UUID of updated opportunity
  updated_at: string;           // ISO 8601 datetime of update
}
```

## Rate Limiting

Currently no rate limiting is implemented. For production use, consider:

- **Per-tenant limits**: 1000 requests per hour
- **Per-endpoint limits**: 100 requests per minute for POST endpoints
- **Burst allowance**: 10 requests per second

## Caching

### Response Caching

- `GET /api/v1/opportunities/due`: No caching (real-time data)
- `GET /health`: Cache for 60 seconds

### Client-Side Caching

Recommended client-side caching strategy:
- Cache due opportunities for 30 seconds
- Invalidate cache after successful action completion
- Use optimistic updates for better UX

## Webhooks (Future)

Planned webhook support for external integrations:

```json
{
  "event": "action.completed",
  "tenant_id": "demo-tenant-1",
  "opportunity_id": "123e4567-e89b-12d3-a456-426614174000",
  "timestamp": "2025-10-29T10:15:00Z",
  "data": {
    "previous_action": "Follow up on technical questions",
    "new_action": "Send technical documentation",
    "new_action_due": "2025-11-05T14:00:00Z"
  }
}
```

## SDK Examples

### JavaScript/TypeScript

```typescript
class NATClient {
  constructor(
    private baseUrl: string,
    private tenantId: string
  ) {}

  private get headers() {
    return {
      'Content-Type': 'application/json',
      'X-Tenant-ID': this.tenantId
    };
  }

  async getDueActions(): Promise<Opportunity[]> {
    const response = await fetch(
      `${this.baseUrl}/api/v1/opportunities/due`,
      { headers: this.headers }
    );
    return response.json();
  }

  async completeAction(
    opportunityId: string,
    nextAction: CompleteActionRequest
  ): Promise<CompleteActionResponse> {
    const response = await fetch(
      `${this.baseUrl}/api/v1/opportunities/${opportunityId}/complete_action`,
      {
        method: 'POST',
        headers: this.headers,
        body: JSON.stringify(nextAction)
      }
    );
    return response.json();
  }
}

// Usage
const client = new NATClient('http://localhost:8000', 'demo-tenant-1');
const dueActions = await client.getDueActions();
```

### Python

```python
import requests
from typing import List, Dict, Any
from datetime import datetime

class NATClient:
    def __init__(self, base_url: str, tenant_id: str):
        self.base_url = base_url
        self.tenant_id = tenant_id
        self.headers = {
            'Content-Type': 'application/json',
            'X-Tenant-ID': tenant_id
        }

    def get_due_actions(self) -> List[Dict[str, Any]]:
        response = requests.get(
            f"{self.base_url}/api/v1/opportunities/due",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def complete_action(
        self, 
        opportunity_id: str, 
        new_action_at: datetime,
        new_action_details: str
    ) -> Dict[str, Any]:
        data = {
            'new_next_action_at': new_action_at.isoformat(),
            'new_next_action_details': new_action_details
        }
        response = requests.post(
            f"{self.base_url}/api/v1/opportunities/{opportunity_id}/complete_action",
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json()

# Usage
client = NATClient('http://localhost:8000', 'demo-tenant-1')
due_actions = client.get_due_actions()
```

## Testing

### Manual Testing with curl

Get due actions:
```bash
curl -X GET "http://localhost:8000/api/v1/opportunities/due" \
  -H "X-Tenant-ID: demo-tenant-1"
```

Complete an action:
```bash
curl -X POST "http://localhost:8000/api/v1/opportunities/{id}/complete_action" \
  -H "X-Tenant-ID: demo-tenant-1" \
  -H "Content-Type: application/json" \
  -d '{
    "new_next_action_at": "2025-11-05T14:00:00Z",
    "new_next_action_details": "Send follow-up email with contract"
  }'
```

### Automated Testing

The API includes comprehensive test coverage:

```bash
# Run API tests
docker-compose exec backend python -m pytest tests/api/

# Run with coverage
docker-compose exec backend python -m pytest --cov=app tests/
```

## OpenAPI Specification

The complete OpenAPI specification is available at:
- **Interactive docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **JSON spec**: http://localhost:8000/openapi.json

This provides:
- Interactive API testing
- Request/response examples
- Schema validation
- Code generation support