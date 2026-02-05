# TechConnect API - Interactive Testing Guide

## Access the API Documentation

**URL**: `http://localhost:8000/docs`

The Swagger UI provides an interactive interface to test all endpoints.

---

## Testing Endpoints in the Browser

### 1. Try the Health Check
1. Scroll down to the `/health` endpoint
2. Click **"Try it out"**
3. Click **"Execute"**
4. See the `200` response with `{"status": "healthy", ...}`

---

### 2. List All Accelerators
1. Find the `GET /accelerators` endpoint
2. Click **"Try it out"**
3. Click **"Execute"**
4. View all 3 indexed accelerators with their metadata

---

### 3. Get a Specific Accelerator
1. Find the `GET /accelerators/{accelerator_id}` endpoint
2. Click **"Try it out"**
3. In the `accelerator_id` field, enter: `multi-agent-automation`
4. Click **"Execute"**
5. See the full ContextBlock with:
   - Architecture summary (compacted to ~150 tokens)
   - Prerequisites in XML format
   - Products & services in XML format
   - RAI disclaimer (if applicable)

---

### 4. Search for Context (Main Endpoint)

This is the most important endpoint for the Instruction Agent.

#### 4a. AI Automation Scenario
1. Find the `POST /context` endpoint
2. Click **"Try it out"**
3. Replace the default request body with:

```json
{
  "scenario_title": "Build an AI agent for automating business workflows",
  "solution_area": "AI",
  "num_results": 2
}
```

4. Click **"Execute"**
5. See 2 AI solutions with RAI disclaimers

#### 4b. Document Processing Scenario
1. Click **"Try it out"** again
2. Use this request:

```json
{
  "scenario_title": "Process documents and extract information from content",
  "num_results": 3
}
```

3. Click **"Execute"**
4. See semantically relevant results (Content Processing will rank high)

#### 4c. Complexity-Based Search
1. Click **"Try it out"**
2. Use this request:

```json
{
  "scenario_title": "enterprise data platform",
  "complexity": "L400",
  "num_results": 2
}
```

3. See only L400 complexity solutions

---

## Request/Response Schema

### POST /context Request
```json
{
  "scenario_title": "string (required) - What you're trying to build",
  "solution_area": "string (optional) - Filter: 'AI', 'Security', 'Azure (Data & AI)'",
  "complexity": "string (optional) - Filter: 'L200', 'L300', 'L400'",
  "num_results": "integer (default: 3) - How many results to return"
}
```

### ContextBlock Response
```json
{
  "catalog_item_id": "string - Unique identifier",
  "solution_name": "string - Display name",
  "solution_area": "string - Category",
  "complexity_level": "string - L200/L300/L400",
  "architecture_summary": "string - Compacted description (~150 tokens)",
  "prerequisites_xml": "string - XML-formatted prerequisites",
  "products_xml": "string - XML-formatted Azure services",
  "rai_disclaimer": "string or null - Safety guardrails if AI solution",
  "repository_url": "string - GitHub link"
}
```

---

## Sample Payloads for Testing

### Payload 1: AI Automation (with RAI)
```json
{
  "scenario_title": "Delegate complex tasks to AI agents that can act on behalf of users",
  "solution_area": "AI",
  "num_results": 2
}
```

**Expected**: Multi-Agent Automation Engine (L400) with RAI disclaimer

---

### Payload 2: Content Analysis
```json
{
  "scenario_title": "Extract structured data from invoices, contracts, and documents",
  "num_results": 1
}
```

**Expected**: Content Processing Accelerator (L300)

---

### Payload 3: Data Analytics
```json
{
  "scenario_title": "Build a unified data foundation for analytics and insights",
  "solution_area": "Azure (Data & AI)",
  "num_results": 1
}
```

**Expected**: Unified Data Foundation with Fabric (L400)

---

### Payload 4: Advanced Search (L300 complexity only)
```json
{
  "scenario_title": "AI-powered solutions for mid-tier implementation",
  "complexity": "L300",
  "num_results": 5
}
```

**Expected**: Content Processing Accelerator (L300)

---

## Key Features to Observe

### 1. XML-Formatted Output
Check the `prerequisites_xml` and `products_xml` fields - they use XML tags for efficient downstream parsing:

```xml
<prerequisites>
  <item>Azure Subscription</item>
  <item>Azure OpenAI approval</item>
</prerequisites>
```

### 2. Token-Efficient Summary
The `architecture_summary` is compacted to ~150 tokens for cost efficiency in multi-agent communication.

### 3. RAI Safety Guardrails
When `rai_disclaimer` is not null, it contains mandatory safety guidance:

```
⚠️ RESPONSIBLE AI DISCLAIMER (RAI):
This AI solution must be deployed with governance guardrails including:
- Monitoring of model outputs for bias and accuracy
- Human review of high-impact decisions
- Transparency about AI capabilities and limitations
- Compliance with Microsoft Responsible AI principles
```

### 4. Semantic Search in Action
Try variations:
- "AI automation" vs "business process automation"
- "document processing" vs "invoice extraction"
- "data platform" vs "analytics foundation"

All will return relevant results based on token matching.

---

## How This Integrates with the Instruction Agent

```
[Instruction Agent]
    ↓
    Calls: POST /context
    Body: { scenario_title, solution_area, complexity, num_results }
    ↓
[TechConnect Broker]
    ↓
    ├─ Loads catalog.json
    ├─ Ingests into vector store
    ├─ Tokenizes query
    ├─ Searches semantic index
    ├─ Applies filters (area, complexity)
    ├─ Formats as ContextBlocks (XML tags)
    ├─ Injects RAI disclaimers if needed
    ↓
[Returns ContextResponse]
    {
      request_id: "req_hash",
      blocks: [...],
      count: N
    }
    ↓
[Instruction Agent]
    ↓
    Parses prerequisites_xml
    Checks for rai_disclaimer
    Retrieves products from products_xml
    Generates deployment instructions
```

---

## Testing Tips

1. **Use the Swagger UI "Try it out" feature** - It auto-validates JSON
2. **Copy sample payloads** - Use the ones provided above
3. **Check response codes** - Should be 200 for success
4. **Examine the XML** - Notice how prerequisites/products are tagged
5. **Try different queries** - See how semantic search ranks results

---

## Troubleshooting

**Getting 0 results?**
- Try removing the `solution_area` filter
- Use broader terms in `scenario_title`
- Check that the scenario matches content in the catalog

**RAI Disclaimer not showing?**
- Only appears for AI solutions (check `solution_area`)
- Must have `responsible_ai_tag: true` in catalog.json

**XML tags look malformed?**
- This is expected - they're designed for downstream parsing, not human readability
- The Instruction Agent will parse them programmatically

---

**Next**: Deploy this to Azure Container Apps or a cloud provider for production use!
