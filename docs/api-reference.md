# API Reference

## Complete REST API Documentation

All endpoints are available at the base URL:
- **Local:** http://localhost:5000
- **Docker:** http://localhost:5000
- **Azure:** https://your-app-name.azurewebsites.net

---

## Authentication

**Current:** No authentication required (for POC)  
**Production:** Add via:
```python
@app.before_request
def check_api_key():
    key = request.headers.get('X-API-Key')
    if not key or key != os.environ.get('API_KEY'):
        return {'error': 'Unauthorized'}, 401
```

---

## Endpoints

### 1. GET `/`
**Description:** Home page with API documentation

**Response:** HTML page with links to all endpoints

---

### 2. GET `/api/health`
**Description:** Health check for monitoring and load balancers

**Response:**
```json
{
    "status": "healthy",
    "timestamp": "2024-02-06T10:30:00Z",
    "version": "1.0.0"
}
```

**Status Codes:** 
- `200 OK` - Service is healthy
- `503 Service Unavailable` - Service is down

---

### 3. GET `/api/list-scenarios`
**Description:** Get list of all 50+ available solution scenarios

**Query Parameters:** None

**Example Request:**
```bash
curl http://localhost:5000/api/list-scenarios
```

**Response:**
```json
{
    "total": 53,
    "scenarios": [
        {
            "id": "ai-001",
            "name": "AI Chatbot with Azure OpenAI",
            "area": "AI",
            "complexity": "L300",
            "description": "Build a chatbot using Azure OpenAI API...",
            "tags": ["chatbot", "llm", "azure"]
        },
        {
            "id": "sec-001",
            "name": "DevSecOps Pipeline",
            "area": "Security",
            "complexity": "L300",
            "description": "Implement security scanning in CI/CD...",
            "tags": ["security", "cicd", "scanning"]
        }
    ]
}
```

**Status Codes:**
- `200 OK` - Success
- `500 Internal Server Error` - Catalog load failure

---

### 4. GET `/api/scenario/{id}`
**Description:** Get detailed information about a specific scenario

**Path Parameters:**
- `id` (string) - Scenario ID (e.g., "ai-001")

**Example Request:**
```bash
curl http://localhost:5000/api/scenario/ai-001
```

**Response:**
```json
{
    "id": "ai-001",
    "name": "AI Chatbot with Azure OpenAI",
    "solution_area": "AI",
    "technical_complexity": "L300",
    "description": "Build a conversational chatbot using Azure OpenAI...",
    "long_description": "This solution demonstrates...",
    "tags": ["chatbot", "llm", "conversational"],
    "prerequisites": [
        "Python 3.8+",
        "Azure subscription",
        "Basic Python knowledge"
    ],
    "primary_usecase": "Customer Service Automation",
    "responsible_ai_tag": true,
    "estimated_hours": 8,
    "technologies": ["Python", "Flask", "Azure OpenAI", "Streamlit"],
    "link_to_content": "https://github.com/derricksobrien/poc-accelerator"
}
```

**Status Codes:**
- `200 OK` - Scenario found
- `404 Not Found` - Scenario ID doesn't exist
- `500 Internal Server Error` - Server error

---

### 5. POST `/api/search`
**Description:** Semantic search across all scenarios using TF-IDF matching

**Request Body:**
```json
{
    "query": "AI automation",
    "area": "AI",
    "complexity": "L300"
}
```

**Parameters:**
- `query` (string, required) - Search term(s)
- `area` (string, optional) - Filter by solution area
  - Allowed values: "AI", "Security", "Azure (Data & AI)", "Cloud & AI Platforms"
- `complexity` (string, optional) - Filter by complexity
  - Allowed values: "L200", "L300", "L400"

**Example Request:**
```bash
curl -X POST http://localhost:5000/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "machine learning",
    "area": "AI",
    "complexity": "L300"
  }'
```

**Response:**
```json
{
    "query": "machine learning",
    "filters": {
        "area": "AI",
        "complexity": "L300"
    },
    "total_results": 8,
    "query_time_ms": 45,
    "results": [
        {
            "id": "ai-005",
            "name": "Machine Learning Model Training",
            "similarity_score": 0.94,
            "area": "AI",
            "complexity": "L300",
            "description": "...",
            "tags": ["ml", "training", "azure"]
        }
    ]
}
```

**Status Codes:**
- `200 OK` - Search completed (results may be empty)
- `400 Bad Request` - Missing required query parameter
- `500 Internal Server Error` - Search engine error

---

### 6. POST `/api/generate-poc`
**Description:** Auto-generate POC code and deployment instructions

**Request Body:**
```json
{
    "title": "Build an E-commerce AI Recommendation Engine",
    "description": "Create a recommendation system for products",
    "azure_config": {
        "openai_key": "sk-...",
        "openai_base": "https://instance.openai.azure.com",
        "openai_version": "2024-02-15-preview"
    }
}
```

**Parameters:**
- `title` (string, required) - POC title/goal
- `description` (string, optional) - Detailed description
- `azure_config` (object, optional) - Azure service configuration
  - `openai_key` - Azure OpenAI API key
  - `openai_base` - Azure OpenAI endpoint
  - `openai_version` - API version

**Example Request:**
```bash
curl -X POST http://localhost:5000/api/generate-poc \
  -H "Content-Type: application/json" \
  -d '{
    "title": "AI Product Recommendation System",
    "description": "For e-commerce platform",
    "azure_config": {
        "openai_key": "sk-...",
        "openai_base": "https://myinstance.openai.azure.com",
        "openai_version": "2024-02-15-preview"
    }
  }'
```

**Response:**
```json
{
    "poc_id": "poc-20240206-001",
    "title": "AI Product Recommendation System",
    "status": "generated",
    "generated_at": "2024-02-06T10:30:00Z",
    "code_snippet": "import azure.ai.openai\nfrom azure.identity import DefaultAzureCredential\n...",
    "full_code": "# Complete Python implementation\n...",
    "deployment_steps": [
        "1. Create Azure Container Registry",
        "2. Build Docker image",
        "3. Push to registry",
        "4. Deploy to Container Apps"
    ],
    "required_services": [
        "Azure OpenAI",
        "Azure Container Apps",
        "Azure Container Registry"
    ],
    "estimated_time_hours": 3,
    "estimated_cost": "$15-30",
    "recommended_reading": [
        {
            "title": "Azure OpenAI Documentation",
            "url": "https://learn.microsoft.com/..."
        }
    ]
}
```

**Status Codes:**
- `200 OK` - POC generated successfully
- `400 Bad Request` - Missing required parameters
- `401 Unauthorized` - Invalid API key
- `500 Internal Server Error` - Generation failed

---

### 7. POST `/api/validate-azure`
**Description:** Validate Azure connectivity and credentials

**Request Body:**
```json
{
    "openai_key": "sk-...",
    "openai_base": "https://instance.openai.azure.com"
}
```

**Example Request:**
```bash
curl -X POST http://localhost:5000/api/validate-azure \
  -H "Content-Type: application/json" \
  -d '{
    "openai_key": "sk-...",
    "openai_base": "https://myinstance.openai.azure.com"
  }'
```

**Response (Success):**
```json
{
    "valid": true,
    "message": "Azure OpenAI connection successful",
    "service": "Azure OpenAI",
    "model": "gpt-4",
    "region": "eastus",
    "deployment_name": "gpt-4"
}
```

**Response (Failure):**
```json
{
    "valid": false,
    "message": "Invalid API key",
    "error_code": "invalid_credentials",
    "suggestion": "Check OPENAI_API_KEY environment variable"
}
```

**Status Codes:**
- `200 OK` - Validation completed
- `400 Bad Request` - Missing parameters
- `401 Unauthorized` - Invalid credentials
- `503 Service Unavailable` - Azure service unreachable

---

### 8. GET `/api/azure-services-check`
**Description:** List available Azure services and their status

**Query Parameters:** None

**Example Request:**
```bash
curl http://localhost:5000/api/azure-services-check
```

**Response:**
```json
{
    "services": {
        "azure_openai": {
            "name": "Azure OpenAI",
            "status": "available",
            "configured": true,
            "models": ["gpt-4", "gpt-3.5-turbo"],
            "regions": ["eastus", "westus", "northeurope"]
        },
        "azure_ai_search": {
            "name": "Azure AI Search",
            "status": "available",
            "configured": false,
            "note": "Configure to enable vector search"
        },
        "app_service": {
            "name": "Azure App Service",
            "status": "recommended",
            "configured": false,
            "note": "Use for web app hosting"
        }
    },
    "total_available": 3,
    "total_configured": 1
}
```

**Status Codes:**
- `200 OK` - Services checked
- `500 Internal Server Error` - Query failed

---

### 9. GET `/api/ai-services-info`
**Description:** Get current AI service configuration

**Response:**
```json
{
    "service": "Azure OpenAI",
    "provider": "Microsoft",
    "configured": true,
    "models": ["gpt-4", "gpt-3.5-turbo"],
    "default_model": "gpt-4",
    "region": "eastus",
    "api_version": "2024-02-15-preview",
    "capabilities": [
        "Text completion",
        "Chat completion",
        "Embeddings",
        "DALL-E 3"
    ]
}
```

---

### 10. GET `/docs`
**Description:** Swagger/OpenAPI interactive documentation

**Response:** HTML page with interactive API explorer

**Features:**
- Try endpoints live
- See request/response schemas
- View all parameters and options
- Download OpenAPI spec

---

### 11. GET `/openapi.json`
**Description:** OpenAPI 3.0.0 specification

**Response:** Full API specification in JSON format (Swagger 3.0)

---

## Error Responses

All errors follow this format:

```json
{
    "error": "Error code",
    "message": "Human readable message",
    "details": "Additional context if available"
}
```

### Common Error Codes

| Code | Status | Meaning |
|------|--------|---------|
| `missing_parameter` | 400 | Required parameter not provided |
| `invalid_format` | 400 | Request format invalid |
| `not_found` | 404 | Resource doesn't exist |
| `unauthorized` | 401 | Invalid credentials |
| `server_error` | 500 | Internal server error |
| `service_unavailable` | 503 | Azure service unreachable |

---

## Rate Limiting

**Current:** No rate limiting (POC phase)

**Production Recommended:**
```python
from flask_limiter import Limiter
limiter = Limiter(app, key_func=get_remote_address)
@app.route('/api/search')
@limiter.limit("100 per hour")
def search():
    ...
```

---

## CORS Configuration

**Allowed Origins:** 
- `http://localhost:*`
- `http://127.0.0.1:*`
- `https://yourdomain.com` (production)

**Methods:** GET, POST, OPTIONS

---

## Webhooks (Future)

Reserved for future enhancement:

```
POST /webhooks/poc-generated
POST /webhooks/azure-validation-failed
POST /webhooks/search-usage
```

---

## SDK Usage Examples

### Python (Requests)
```python
import requests

# Search
resp = requests.post(
    'http://localhost:5000/api/search',
    json={'query': 'AI automation', 'area': 'AI'}
)
results = resp.json()

# Generate POC
resp = requests.post(
    'http://localhost:5000/api/generate-poc',
    json={'title': 'My POC', 'azure_config': {...}}
)
poc = resp.json()
```

### JavaScript/Node.js
```javascript
// Search
const resp = await fetch('http://localhost:5000/api/search', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({query: 'AI automation'})
});
const data = await resp.json();
```

### curl
```bash
# Search
curl -X POST http://localhost:5000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query":"AI automation","area":"AI"}'

# Get health
curl http://localhost:5000/api/health
```

---

**Continue Reading:** [Architecture](ARCHITECTURE.md) | [Getting Started](GETTING-STARTED.md) | [Troubleshooting](TROUBLESHOOTING.md)
