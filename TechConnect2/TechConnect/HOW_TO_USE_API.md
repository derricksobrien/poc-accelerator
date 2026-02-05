# How to Use the TechConnect API

## 🚀 Quick Start

The TechConnect API is now live and publicly accessible!

**API Base URL**: `http://techconnect-api-prod.eastus.azurecontainer.io:8000`

---

## 📝 API Endpoints

### 1. Health Check
Check if the API is running:
```bash
curl http://techconnect-api-prod.eastus.azurecontainer.io:8000/health
```

**Response** (if healthy):
```json
{
  "status": "healthy",
  "timestamp": "2026-01-21T..."
}
```

---

### 2. List Accelerators
Get available Microsoft solution accelerators:
```bash
curl http://techconnect-api-prod.eastus.azurecontainer.io:8000/accelerators
```

**Response**:
```json
{
  "count": 42,
  "accelerators": [
    {
      "id": "...",
      "title": "...",
      "description": "..."
    },
    ...
  ]
}
```

---

### 3. Get Context/Recommendations
Get context-specific recommendations based on scenario:

```bash
curl -X POST http://techconnect-api-prod.eastus.azurecontainer.io:8000/context \
  -H "Content-Type: application/json" \
  -d '{
    "scenario_title": "Digital Transformation for Retail",
    "solution_area": "AI",
    "num_results": 3
  }'
```

**Parameters**:
- `scenario_title` (string, required): The business scenario
- `solution_area` (string, optional): Filter by area (e.g., "AI", "Data")
- `num_results` (integer, optional): How many results to return (default: 1)

**Response**:
```xml
<ContextBlock>
  <Scenario>Digital Transformation for Retail</Scenario>
  <RecommendedAccelerators>
    <Accelerator>
      <Title>...</Title>
      <Description>...</Description>
    </Accelerator>
    ...
  </RecommendedAccelerators>
</ContextBlock>
```

---

## 🧪 Testing Examples

### Python
```python
import requests

# Health check
response = requests.get('http://techconnect-api-prod.eastus.azurecontainer.io:8000/health')
print(response.json())

# Get recommendations
response = requests.post(
    'http://techconnect-api-prod.eastus.azurecontainer.io:8000/context',
    json={
        'scenario_title': 'AI Automation',
        'num_results': 2
    }
)
print(response.text)
```

### JavaScript
```javascript
// Health check
fetch('http://techconnect-api-prod.eastus.azurecontainer.io:8000/health')
  .then(r => r.json())
  .then(data => console.log(data))

// Get recommendations
fetch('http://techconnect-api-prod.eastus.azurecontainer.io:8000/context', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    scenario_title: 'AI Automation',
    num_results: 2
  })
})
  .then(r => r.text())
  .then(data => console.log(data))
```

### PowerShell
```powershell
# Health check
Invoke-WebRequest -Uri 'http://techconnect-api-prod.eastus.azurecontainer.io:8000/health' | Select-Object -ExpandProperty Content

# Get recommendations
$body = @{
    scenario_title = 'AI Automation'
    num_results = 2
} | ConvertTo-Json

Invoke-WebRequest -Uri 'http://techconnect-api-prod.eastus.azurecontainer.io:8000/context' `
  -Method POST `
  -ContentType 'application/json' `
  -Body $body | Select-Object -ExpandProperty Content
```

---

## 💡 Common Scenarios

### Scenario 1: Get AI Recommendations
```bash
curl -X POST http://techconnect-api-prod.eastus.azurecontainer.io:8000/context \
  -H "Content-Type: application/json" \
  -d '{"scenario_title":"AI Automation","solution_area":"AI","num_results":3}'
```

### Scenario 2: Data Platform Recommendations
```bash
curl -X POST http://techconnect-api-prod.eastus.azurecontainer.io:8000/context \
  -H "Content-Type: application/json" \
  -d '{"scenario_title":"Build Data Platform","solution_area":"Data","num_results":2}'
```

### Scenario 3: General Cloud Migration
```bash
curl -X POST http://techconnect-api-prod.eastus.azurecontainer.io:8000/context \
  -H "Content-Type: application/json" \
  -d '{"scenario_title":"Enterprise Cloud Migration","num_results":5}'
```

---

## ⏱️ Rate Limits & Considerations

- **No authentication required** - API is public
- **No rate limiting** - Use responsibly
- **Response time** - Typically < 1 second
- **Uptime** - Container is running 24/7 (unless stopped)

---

## 🆘 Troubleshooting

### API not responding
- Check if URL is correct
- Wait a moment and try again
- Contact: [your contact info]

### Unexpected responses
- Verify JSON format in POST requests
- Check that `scenario_title` is provided
- Try with a simpler scenario

### Performance issues
- API should respond in < 1 second
- If slower, the container might be restarting
- Container auto-restarts on failure

---

## 📊 API Status

**Current Status**: ✅ Running  
**URL**: http://techconnect-api-prod.eastus.azurecontainer.io:8000  
**Last Updated**: January 21, 2026  
**Cost**: ~$0.20/hour while running

---

## 📞 Support

For issues or questions, contact the deployment team.

For technical details, see:
- [AZURE_READY_TO_DEPLOY.md](AZURE_READY_TO_DEPLOY.md) - Deployment info
- [TESTING.md](TESTING.md) - Detailed testing guide
- [.github/copilot-instructions.md](.github/copilot-instructions.md) - API specification
