
This product specification is designed for an Agentic Context Broker—the "bridge" between raw GitHub repository data and your existing instruction-generating agent.

By feeding this into GitHub Copilot in VS Code, you can prompt it to scaffold the architecture, define data models, and generate the RAG pipeline.

Product Specification: The Contextual Broker Agent
1. System Overview
The Contextual Broker is a Python-based RAG system that transforms unstructured GitHub repository data into high-fidelity "context blocks" for the Skillable learner agent. It must provide authoritative architectural patterns, prerequisites, and governance metadata to ensure "Gold Standard" POC delivery.

2. Core Components (The Atomic Pipeline)
Break your build into these five testable modules:

Module A: The Scraper (Data Ingestion)

Purpose: Fetch repository content (READMEs, /docs, deployment scripts).

Tooling: PyGithub or requests for API interaction; firecrawl for converting web-based repository pages to clean Markdown.

Atomic Test: Run a script that inputs a URL and outputs a raw_content.md file for that repo.

Module B: The Metadata Extractor (LLM Processing)

Purpose: Use an LLM to parse raw Markdown into the structured catalog.json schema (Solution Area, Complexity, Prerequisites).

Tooling: OpenAI or Azure OpenAI with Pydantic for "Structured Outputs" to ensure the JSON matches your schema exactly.

Atomic Test: Input a README and verify the output is a valid JSON object with the solution_area field populated.

Module C: The Vector Store (RAG Memory)

Purpose: Index the extracted metadata and repo descriptions for semantic search.

Recommendations:

ChromaDB: Best for local, lightweight Python development and rapid prototyping.

Pinecone: Best if you need a fully managed, production-grade serverless solution for TechConnect '26 scale.

Qdrant: Excellent for strong filtering (e.g., searching specifically for "Security" + "L400").

Atomic Test: Query the store for "AI automation" and ensure the "Multi-Agent Automation" repo is the top result.

Module D: The Context Provider (A2A Interface)

Purpose: Expose an API endpoint that the existing "Instruction Agent" can call.

Tooling: FastAPI to create a lightweight REST service.

Atomic Test: Send a POST request with a scenario title and receive the full "Context Block" (Architecture + Prerequisites).

Module E: The Governance Guardrails (RAI Injection)

Purpose: Automatically append mandatory Responsible AI (RAI) prompts if the responsible_ai_tag is true.

Atomic Test: Verify that any "AI" solution area result includes the standard RAI safety disclaimer in its final output.

3. Suggested Architecture Diagram
4. Implementation Steps for GitHub Copilot
Use these specific prompts in VS Code to get started:

Scaffolding: "Create a Python project structure for a RAG agent using FastAPI. Include directories for 'ingestion', 'models', and 'vector_store'."

Data Modeling: "Using Pydantic, define a CatalogItem class that includes solution_area (Enum), complexity (int), and prerequisites (List)."

RAG Logic: "Write a function using LangChain and ChromaDB to index a folder of Markdown files and perform a similarity search with metadata filtering."

Integration: "Create a FastAPI endpoint that takes a user scenario, searches the vector store, and returns a formatted prompt for another AI agent."

5. What you may have overlooked:
Context Compaction: If a repository has a massive README, your broker shouldn't send the whole thing. Implement a "compaction" layer that summarizes the README into a 500-token summary before sending it to the next agent.

Token Efficiency: Multi-agent communication can become expensive. Use XML tagging (e.g., <prerequisites>...</prerequisites>) in the broker's output so the instruction agent can parse the context more efficiently.

Regional Constraints: Ensure your metadata includes "Azure Regions." If a POC requires a specific AI model only available in eastus2, your agent should warn the user immediately.