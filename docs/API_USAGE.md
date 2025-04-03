# S4 API Documentation

This document provides detailed information about the S4 API endpoints, authentication methods, and expected request/response formats.

## Authentication

S4 uses API key-based authentication with two types of keys:

1. **Admin API Key**: For accessing admin endpoints (tenant management, analytics)
2. **Tenant API Key**: For tenant-specific operations (document management, search)

API keys should be included in the request header:

```
X-Admin-Key: your_admin_api_key  # For admin endpoints
X-Tenant-Key: your_tenant_api_key  # For tenant endpoints
```

## Base URLs

- **Local Development**: `http://localhost:8000/api`
- **Production**: `https://your-api-endpoint.com/api`

## Admin API Endpoints

### Tenant Management

#### Create Tenant

```
POST /admin/tenants
```

Request Header:
```
X-Admin-Key: your_admin_api_key
Content-Type: application/json
```

Request Body:
```json
{
  "name": "Example Company",
  "email": "admin@example.com",
  "company": "Example Inc",
  "plan_id": "basic"
}
```

Response (200 OK):
```json
{
  "id": "tenant_123456",
  "name": "Example Company",
  "email": "admin@example.com",
  "company": "Example Inc",
  "plan_id": "basic",
  "api_key": "s4_tenant_api_key_789",
  "created_at": "2023-07-15T12:00:00Z",
  "storage_used": 0,
  "api_calls_count": 0,
  "status": "active"
}
```

#### List Tenants

```
GET /admin/tenants
```

Request Header:
```
X-Admin-Key: your_admin_api_key
```

Query Parameters:
- `page`: Page number (default: 1)
- `limit`: Results per page (default: 20)
- `status`: Filter by tenant status (optional: "active", "suspended")

Response (200 OK):
```json
{
  "tenants": [
    {
      "id": "tenant_123456",
      "name": "Example Company",
      "email": "admin@example.com",
      "company": "Example Inc",
      "plan_id": "basic",
      "created_at": "2023-07-15T12:00:00Z",
      "storage_used": 1048576,
      "api_calls_count": 150,
      "status": "active"
    },
    // More tenants...
  ],
  "total": 45,
  "page": 1,
  "limit": 20
}
```

#### Get Tenant Details

```
GET /admin/tenants/{tenant_id}
```

Request Header:
```
X-Admin-Key: your_admin_api_key
```

Response (200 OK):
```json
{
  "id": "tenant_123456",
  "name": "Example Company",
  "email": "admin@example.com",
  "company": "Example Inc",
  "plan_id": "basic",
  "api_key": "s4_tenant_api_key_789",
  "created_at": "2023-07-15T12:00:00Z",
  "storage_used": 1048576,
  "api_calls_count": 150,
  "status": "active",
  "document_count": 25,
  "last_activity": "2023-07-20T15:30:00Z"
}
```

#### Update Tenant Plan

```
PUT /admin/tenants/{tenant_id}/plan
```

Request Header:
```
X-Admin-Key: your_admin_api_key
Content-Type: application/json
```

Request Body:
```json
{
  "plan_id": "premium"
}
```

Response (200 OK):
```json
{
  "id": "tenant_123456",
  "name": "Example Company",
  "plan_id": "premium",
  "updated_at": "2023-07-21T10:15:00Z"
}
```

#### Regenerate Tenant API Key

```
POST /admin/tenants/{tenant_id}/regenerate-key
```

Request Header:
```
X-Admin-Key: your_admin_api_key
```

Response (200 OK):
```json
{
  "tenant_id": "tenant_123456",
  "api_key": "s4_tenant_api_key_new_123",
  "regenerated_at": "2023-07-21T11:30:00Z"
}
```

#### Suspend Tenant

```
POST /admin/tenants/{tenant_id}/suspend
```

Request Header:
```
X-Admin-Key: your_admin_api_key
```

Response (200 OK):
```json
{
  "id": "tenant_123456",
  "status": "suspended",
  "suspended_at": "2023-07-21T14:45:00Z"
}
```

#### Reactivate Tenant

```
POST /admin/tenants/{tenant_id}/activate
```

Request Header:
```
X-Admin-Key: your_admin_api_key
```

Response (200 OK):
```json
{
  "id": "tenant_123456",
  "status": "active",
  "activated_at": "2023-07-22T09:15:00Z"
}
```

### Analytics

#### System Analytics

```
GET /admin/analytics/system
```

Request Header:
```
X-Admin-Key: your_admin_api_key
```

Query Parameters:
- `period`: "day", "week", "month" (default: "day")
- `start_date`: ISO format date (optional)
- `end_date`: ISO format date (optional)

Response (200 OK):
```json
{
  "period": "day",
  "start_date": "2023-07-15T00:00:00Z",
  "end_date": "2023-07-15T23:59:59Z",
  "total_api_calls": 12500,
  "total_storage_used": 1073741824,
  "total_documents": 1250,
  "active_tenants": 45,
  "new_tenants": 3,
  "hourly_breakdown": [
    {
      "hour": "00:00",
      "api_calls": 250,
      "document_uploads": 12
    },
    // More hours...
  ]
}
```

#### Tenant Analytics

```
GET /admin/analytics/tenants
```

Request Header:
```
X-Admin-Key: your_admin_api_key
```

Query Parameters:
- `period`: "day", "week", "month" (default: "day")
- `limit`: Number of top tenants to return (default: 10)
- `sort_by`: "api_calls", "storage" (default: "api_calls")

Response (200 OK):
```json
{
  "period": "day",
  "top_tenants_by_api_calls": [
    {
      "tenant_id": "tenant_123456",
      "name": "Example Company",
      "api_calls": 1500,
      "percent_of_total": 12
    },
    // More tenants...
  ],
  "top_tenants_by_storage": [
    {
      "tenant_id": "tenant_789012",
      "name": "Another Company",
      "storage_used": 104857600,
      "percent_of_total": 10
    },
    // More tenants...
  ]
}
```

## Tenant API Endpoints

### Document Management

#### Upload Document

```
POST /documents
```

Request Header:
```
X-Tenant-Key: your_tenant_api_key
```

Request Body (multipart/form-data):
- `file`: The document file
- `metadata`: JSON string with document metadata (optional)

Example curl command:
```bash
curl -X POST http://localhost:8000/api/documents \
  -H "X-Tenant-Key: your_tenant_api_key" \
  -F "file=@/path/to/document.pdf" \
  -F 'metadata={"title": "Example Document", "category": "Report"}'
```

Response (201 Created):
```json
{
  "document_id": "doc_123456",
  "filename": "document.pdf",
  "content_type": "application/pdf",
  "size": 1048576,
  "metadata": {
    "title": "Example Document",
    "category": "Report"
  },
  "uploaded_at": "2023-07-15T12:00:00Z",
  "status": "processing"
}
```

#### List Documents

```
GET /documents
```

Request Header:
```
X-Tenant-Key: your_tenant_api_key
```

Query Parameters:
- `page`: Page number (default: 1)
- `limit`: Results per page (default: 20)
- `category`: Filter by category (optional)
- `status`: Filter by processing status (optional: "processing", "ready", "failed")

Response (200 OK):
```json
{
  "documents": [
    {
      "document_id": "doc_123456",
      "filename": "document.pdf",
      "content_type": "application/pdf",
      "size": 1048576,
      "metadata": {
        "title": "Example Document",
        "category": "Report"
      },
      "uploaded_at": "2023-07-15T12:00:00Z",
      "status": "ready"
    },
    // More documents...
  ],
  "total": 25,
  "page": 1,
  "limit": 20
}
```

#### Get Document

```
GET /documents/{document_id}
```

Request Header:
```
X-Tenant-Key: your_tenant_api_key
```

Response (200 OK):
```json
{
  "document_id": "doc_123456",
  "filename": "document.pdf",
  "content_type": "application/pdf",
  "size": 1048576,
  "metadata": {
    "title": "Example Document",
    "category": "Report"
  },
  "uploaded_at": "2023-07-15T12:00:00Z",
  "status": "ready",
  "chunks": 15,
  "last_accessed": "2023-07-16T10:30:00Z"
}
```

#### Download Document

```
GET /documents/{document_id}/download
```

Request Header:
```
X-Tenant-Key: your_tenant_api_key
```

Response (200 OK):
The document file with appropriate Content-Type header.

#### Update Document Metadata

```
PATCH /documents/{document_id}/metadata
```

Request Header:
```
X-Tenant-Key: your_tenant_api_key
Content-Type: application/json
```

Request Body:
```json
{
  "title": "Updated Document Title",
  "category": "Updated Category",
  "custom_field": "Custom Value"
}
```

Response (200 OK):
```json
{
  "document_id": "doc_123456",
  "metadata": {
    "title": "Updated Document Title",
    "category": "Updated Category",
    "custom_field": "Custom Value"
  },
  "updated_at": "2023-07-16T14:20:00Z"
}
```

#### Delete Document

```
DELETE /documents/{document_id}
```

Request Header:
```
X-Tenant-Key: your_tenant_api_key
```

Response (204 No Content)

### Search

#### Semantic Search

```
POST /search
```

Request Header:
```
X-Tenant-Key: your_tenant_api_key
Content-Type: application/json
```

Request Body:
```json
{
  "query": "What is semantic search?",
  "limit": 5,
  "categories": ["Report", "Article"],
  "min_score": 0.7,
  "include_metadata": true,
  "include_chunks": true
}
```

Response (200 OK):
```json
{
  "results": [
    {
      "document_id": "doc_123456",
      "score": 0.92,
      "metadata": {
        "title": "Introduction to Semantic Search",
        "category": "Article"
      },
      "chunks": [
        {
          "text": "Semantic search is a search technique that understands the contextual meaning of terms...",
          "score": 0.94
        }
      ]
    },
    // More results...
  ],
  "query": "What is semantic search?",
  "total_results": 12,
  "execution_time_ms": 150
}
```

### Tenant Profile

#### Get Tenant Profile

```
GET /profile
```

Request Header:
```
X-Tenant-Key: your_tenant_api_key
```

Response (200 OK):
```json
{
  "tenant_id": "tenant_123456",
  "name": "Example Company",
  "email": "admin@example.com",
  "company": "Example Inc",
  "plan": {
    "id": "basic",
    "name": "Basic Plan",
    "storage_limit": 104857600,
    "api_calls_limit": 10000,
    "features": ["basic_search", "metadata_filtering"]
  },
  "usage": {
    "storage_used": 51200000,
    "storage_used_percent": 48.8,
    "api_calls_count": 5000,
    "api_calls_percent": 50.0,
    "document_count": 25,
    "last_activity": "2023-07-20T15:30:00Z"
  },
  "created_at": "2023-07-15T12:00:00Z",
  "status": "active"
}
```

## Error Responses

All API errors follow a consistent format:

```json
{
  "error": {
    "code": "error_code",
    "message": "Human-readable error message",
    "details": {
      // Optional additional details about the error
    }
  }
}
```

Common error codes:

| Status Code | Error Code | Description |
|-------------|------------|-------------|
| 400 | invalid_request | The request was invalid or improperly formatted |
| 401 | unauthorized | Invalid or missing API key |
| 403 | forbidden | Valid API key but insufficient permissions |
| 404 | not_found | The requested resource was not found |
| 409 | conflict | The request conflicts with current state |
| 413 | payload_too_large | The uploaded file exceeds size limits |
| 429 | rate_limited | Too many requests, rate limit exceeded |
| 500 | server_error | Internal server error |
| 503 | service_unavailable | Service temporarily unavailable |

## Rate Limiting

API requests are rate-limited based on the tenant's subscription plan. Rate limit headers are included in all responses:

```
X-Rate-Limit-Limit: 10000
X-Rate-Limit-Remaining: 9990
X-Rate-Limit-Reset: 1626379200
```

When a rate limit is exceeded, a 429 response is returned.

## Webhook Notifications

S4 can send webhook notifications for important events. Configure webhooks in the Admin Portal or via the API.

### Register Webhook

```
POST /admin/tenants/{tenant_id}/webhooks
```

Request Header:
```
X-Admin-Key: your_admin_api_key
Content-Type: application/json
```

Request Body:
```json
{
  "url": "https://your-server.com/webhook",
  "events": ["document.processed", "storage.limit_approaching"],
  "secret": "your_webhook_secret"
}
```

Response (201 Created):
```json
{
  "webhook_id": "webhook_123456",
  "url": "https://your-server.com/webhook",
  "events": ["document.processed", "storage.limit_approaching"],
  "created_at": "2023-07-15T12:00:00Z",
  "status": "active"
}
```

### Webhook Payload

When an event occurs, S4 sends a POST request to your webhook URL with the following payload:

```json
{
  "event": "document.processed",
  "tenant_id": "tenant_123456",
  "timestamp": "2023-07-15T12:05:00Z",
  "data": {
    "document_id": "doc_123456",
    "status": "ready",
    "processing_time_ms": 2500
  }
}
```

The request includes a signature header for verification:

```
X-S4-Signature: sha256=...
```

## SDKs and Client Libraries

Official client libraries for popular programming languages:

- JavaScript/TypeScript: [s4-client-js](https://github.com/your-org/s4-client-js)
- Python: [s4-client-python](https://github.com/your-org/s4-client-python)
- Java: [s4-client-java](https://github.com/your-org/s4-client-java)

## API Versioning

The API version is included in the response headers:

```
X-S4-API-Version: 1.0.0
```

Major versions are accessible via URL:

```
https://your-api-endpoint.com/api/v1/...
```

## Further Resources

- [Swagger Documentation](https://your-api-endpoint.com/docs)
- [OpenAPI Specification](https://your-api-endpoint.com/openapi.json)
- [Deployment Guide](./DEPLOYMENT.md)
- [Code Examples](https://github.com/your-org/s4-examples) 