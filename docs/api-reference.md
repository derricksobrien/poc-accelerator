# API Reference

REST API endpoints for POC Accelerator.

## Generate POC

```
POST /api/generate
Content-Type: application/json

{
  "scenario": "AI Automation for Sales",
  "area": "AI",
  "complexity": "L300"
}
```

Response: `{ "poc_id": "...", "instructions": "..." }`

## List POCs

```
GET /api/pocs
```

Response: Array of POC objects

## Get POC Details

```
GET /api/pocs/{id}
```

Response: Full POC object

## Search Data Sources

```
GET /api/search?q=query&area=AI&complexity=L300
```

Response: Array of search results

## Save to GitHub

```
POST /api/save-github
Content-Type: application/json

{
  "poc_id": "...",
  "github_token": "...",
  "repo": "my-pocs"
}
```

Response: `{ "status": "success", "url": "..." }`

## Response Codes

- **200**: Success
- **400**: Bad request
- **401**: Unauthorized
- **404**: Not found
- **500**: Server error

---

## Next Steps

- [Getting Started](getting-started.html) - Quick start
- [Deployment Guide](deployment.html) - Deploy to production
- [Back to Home](index.html) - Return to documentation

---

[View on GitHub](https://github.com/derricksobrien/poc-accelerator)
