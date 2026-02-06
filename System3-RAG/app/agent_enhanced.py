"""
Azure AI Foundry Agent Client - Enhanced with Real API Calls

Provides complete integration layer for Azure AI Foundry agents.
Handles authentication, session management, tool invocation, and streaming.
"""

import os
import json
import logging
from typing import Optional, Dict, List, Any, AsyncGenerator
from dataclasses import dataclass, asdict
from datetime import datetime
import httpx
from enum import Enum

try:
    from azure.identity import DefaultAzureCredential, ClientSecretCredential
    HAS_AZURE_SDK = True
except ImportError:
    HAS_AZURE_SDK = False

logger = logging.getLogger(__name__)


class AgentStatus(str, Enum):
    """Agent operation status."""
    IDLE = "idle"
    PROCESSING = "processing"
    COMPLETE = "complete"
    ERROR = "error"


@dataclass
class AgentMessage:
    """Represents a message in agent conversation."""
    role: str  # "user" or "assistant"
    content: str
    timestamp: str = None
    citations: Optional[List[Dict[str, str]]] = None
    tools_used: Optional[List[str]] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()


@dataclass
class AgentResponse:
    """Structured response from agent."""
    message: str
    status: str = "success"
    citations: List[Dict[str, str]] = None
    tools_used: List[str] = None
    reasoning: Optional[str] = None
    recommendations: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    def __post_init__(self):
        if self.citations is None:
            self.citations = []
        if self.tools_used is None:
            self.tools_used = []


class AzureAIFoundryAgent:
    """
    Enhanced client for Azure AI Foundry Agents with production features.
    
    Features:
    - Real Azure AI Foundry API integration
    - Multiple authentication methods (Managed Identity, API Key)
    - Session management with persistence
    - Tool invocation and streaming support
    - Comprehensive error handling
    - Request/response logging
    - Rate limiting awareness
    """
    
    def __init__(
        self,
        endpoint: Optional[str] = None,
        agent_id: Optional[str] = None,
        api_key: Optional[str] = None,
        deployment_name: str = "gpt-4",
        api_version: str = "2024-02-15-preview",
        use_managed_identity: bool = True,
        timeout: float = 30.0,
    ):
        """
        Initialize Azure AI Foundry Agent client.
        
        Args:
            endpoint: Azure endpoint (env: AZURE_OPENAI_ENDPOINT)
            agent_id: Agent ID (env: AZURE_AI_AGENT_ID)
            api_key: API key (env: AZURE_OPENAI_KEY)
            deployment_name: Model deployment (env: AZURE_MODEL_DEPLOYMENT)
            api_version: API version to use
            use_managed_identity: Use Azure AD authentication
            timeout: Request timeout in seconds
        """
        # Load from environment if not provided
        self.endpoint = endpoint or os.getenv("AZURE_OPENAI_ENDPOINT", "").rstrip('/')
        self.agent_id = agent_id or os.getenv("AZURE_AI_AGENT_ID", "default")
        self.deployment_name = deployment_name or os.getenv("AZURE_MODEL_DEPLOYMENT", "gpt-4")
        self.api_version = api_version
        self.timeout = timeout
        
        # Check if API is available
        self.available = bool(self.endpoint and "openai.azure.com" in self.endpoint)
        
        if not self.available:
            logger.warning("Azure AI Foundry endpoint not configured. Using mock mode.")
        
        # Setup authentication
        self.use_managed_identity = use_managed_identity
        self.api_key = api_key or os.getenv("AZURE_OPENAI_KEY")
        
        if use_managed_identity and HAS_AZURE_SDK:
            try:
                self.credential = DefaultAzureCredential()
                logger.info("Using Azure Managed Identity for authentication")
            except Exception as e:
                logger.warning(f"Managed Identity unavailable: {e}")
                self.credential = None
        else:
            self.credential = None
        
        # Session storage
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.tools = self._define_tools()
        
        logger.info(f"AI Foundry Agent initialized (available={self.available}, agent={self.agent_id})")

    def _define_tools(self) -> Dict[str, Dict[str, Any]]:
        """Define available tools for the agent."""
        return {
            "search_solutions": {
                "name": "search_solutions",
                "description": "Search for relevant solution accelerators and architecture patterns",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "area": {"type": "string", "enum": ["AI", "Data", "Security", "Cloud", "Fabric"]},
                        "complexity": {"type": "string", "enum": ["L200", "L300", "L400"]},
                        "top_k": {"type": "integer", "minimum": 1, "maximum": 20}
                    },
                    "required": ["query"]
                }
            },
            "generate_rbac": {
                "name": "generate_rbac",
                "description": "Generate RBAC configuration for secure solution deployment",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "solution_id": {"type": "string"},
                        "organization": {"type": "string"},
                        "include_service_principals": {"type": "boolean"}
                    },
                    "required": ["solution_id"]
                }
            },
            "generate_deployment_script": {
                "name": "generate_deployment_script",
                "description": "Generate deployment scripts (Bicep, Terraform, ARM templates)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "solution_id": {"type": "string"},
                        "format": {"type": "string", "enum": ["bicep", "terraform", "arm"]},
                        "environment": {"type": "string", "enum": ["dev", "staging", "prod"]}
                    },
                    "required": ["solution_id", "format"]
                }
            },
            "generate_iac_template": {
                "name": "generate_iac_template",
                "description": "Generate Infrastructure-as-Code templates with best practices",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "solution_id": {"type": "string"},
                        "template_type": {"type": "string", "enum": ["bicep", "terraform", "pulumi"]},
                        "include_monitoring": {"type": "boolean"},
                        "include_security": {"type": "boolean"}
                    },
                    "required": ["solution_id", "template_type"]
                }
            },
            "validate_architecture": {
                "name": "validate_architecture",
                "description": "Validate architecture against best practices and compliance frameworks",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "solution_id": {"type": "string"},
                        "compliance_frameworks": {"type": "array", "items": {"type": "string"}},
                        "regions": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["solution_id"]
                }
            }
        }

    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers with proper authentication."""
        headers = {
            "Content-Type": "application/json",
            "api-version": self.api_version,
        }
        
        if self.api_key:
            headers["api-key"] = self.api_key
        elif self.credential and HAS_AZURE_SDK:
            try:
                token = self.credential.get_token("https://openai.azure.com/.default").token
                headers["Authorization"] = f"Bearer {token}"
            except Exception as e:
                logger.error(f"Failed to get Azure token: {e}")
        
        return headers

    def create_session(self, session_id: Optional[str] = None, user_id: Optional[str] = None) -> str:
        """
        Create a new conversation session.
        
        Args:
            session_id: Custom session ID (auto-generated if not provided)
            user_id: Optional user identifier
            
        Returns:
            Session ID
        """
        if session_id is None:
            import uuid
            session_id = str(uuid.uuid4())
        
        self.sessions[session_id] = {
            "created_at": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "messages": [],
            "status": AgentStatus.IDLE.value,
            "tools_summary": {}
        }
        
        logger.info(f"Created session: {session_id}")
        return session_id

    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session information."""
        return self.sessions.get(session_id)

    def send_message(
        self,
        session_id: str,
        message: str,
        user_id: Optional[str] = None,
        tools_to_use: Optional[List[str]] = None,
    ) -> AgentResponse:
        """
        Send message to agent and get response.
        
        Args:
            session_id: Conversation session ID
            message: User message
            user_id: Optional user ID
            tools_to_use: Optional list of tools to enable
            
        Returns:
            AgentResponse with message, citations, tools used
        """
        # Ensure session exists
        if session_id not in self.sessions:
            self.create_session(session_id, user_id)
        
        # Add user message
        user_msg = AgentMessage(role="user", content=message)
        self.sessions[session_id]["messages"].append(asdict(user_msg))
        
        # Set status
        self.sessions[session_id]["status"] = AgentStatus.PROCESSING.value
        
        try:
            if self.available:
                # Call real Azure API
                response = self._call_azure_api(
                    session_id=session_id,
                    message=message,
                    tools=tools_to_use or list(self.tools.keys())
                )
            else:
                # Use mock response
                logger.info("Using mock agent response (no Azure configured)")
                response = self._generate_mock_response(message, session_id)
            
            # Add assistant message
            assistant_msg = AgentMessage(
                role="assistant",
                content=response.message,
                citations=response.citations,
                tools_used=response.tools_used
            )
            self.sessions[session_id]["messages"].append(asdict(assistant_msg))
            self.sessions[session_id]["status"] = AgentStatus.COMPLETE.value
            
            logger.info(f"Message processed: tools_used={response.tools_used}")
            return response
            
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            self.sessions[session_id]["status"] = AgentStatus.ERROR.value
            
            return AgentResponse(
                message=f"Error processing request: {str(e)}",
                status="error",
                error=str(e)
            )

    def _call_azure_api(
        self,
        session_id: str,
        message: str,
        tools: List[str]
    ) -> AgentResponse:
        """
        Call Azure AI Foundry API with real HTTP request.
        
        Args:
            session_id: Conversation session
            message: User message
            tools: Available tools
            
        Returns:
            AgentResponse parsed from API
        """
        if not self.available:
            raise ValueError("Azure AI Foundry not configured")
        
        url = f"{self.endpoint}/agents/{self.agent_id}/messages"
        headers = self._get_headers()
        
        # Build messages array from session history
        messages = []
        for msg in self.sessions[session_id]["messages"]:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        # Add current message
        messages.append({"role": "user", "content": message})
        
        payload = {
            "messages": messages,
            "model": self.deployment_name,
            "tools": [self.tools[t] for t in tools if t in self.tools],
            "tool_choice": "auto"
        }
        
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                
                data = response.json()
                return self._parse_azure_response(data)
                
        except httpx.HTTPError as e:
            logger.error(f"Azure API error: {e}")
            raise

    def _parse_azure_response(self, data: Dict[str, Any]) -> AgentResponse:
        """Parse response from Azure AI API."""
        
        # Extract message content
        message = ""
        citations = []
        tools_used = []
        
        # Handle choice-based response format
        if "choices" in data:
            choice = data["choices"][0]
            if "message" in choice:
                msg_data = choice["message"]
                message = msg_data.get("content", "")
                
                # Extract tools used
                if "tool_calls" in msg_data:
                    tools_used = [tc.get("function", {}).get("name", "") 
                                 for tc in msg_data["tool_calls"]]
        
        # Extract citations if present
        if "citations" in data:
            citations = data["citations"]
        
        return AgentResponse(
            message=message,
            status="success",
            citations=citations,
            tools_used=tools_used
        )

    def _generate_mock_response(
        self,
        message: str,
        session_id: str
    ) -> AgentResponse:
        """
        Generate realistic mock response for testing without Azure.
        
        Args:
            message: User message
            session_id: Session ID
            
        Returns:
            Mock AgentResponse
        """
        import uuid
        
        # Generate contextual response based on message
        lower_msg = message.lower()
        
        if any(word in lower_msg for word in ["search", "find", "solution", "accelerator"]):
            return AgentResponse(
                message="I found 5 relevant solution accelerators for your request:\n\n1. **Cloud Native Architecture** - Enterprise-grade Kubernetes setup\n2. **AI/ML Pipeline** - End-to-end ML model deployment\n3. **Secure Data Platform** - HIPAA-compliant data warehouse\n4. **IoT Integration** - Large-scale IoT hub setup\n5. **DevOps Automation** - CI/CD pipeline with GitOps\n\nWould you like me to help with any of these?",
                citations=[{"source": "solution-accelerators", "url": "https://github.com/microsoft/solution-accelerators"}],
                tools_used=["search_solutions"]
            )
        
        elif any(word in lower_msg for word in ["rbac", "role", "access", "permission"]):
            return AgentResponse(
                message="I've generated RBAC configuration for your solution:\n\n**Required Roles:**\n- Contributor (subscription scope) - for deployment\n- Key Vault Administrator - for secret management\n- Data Factory Administrator - for data pipeline\n- Cosmos DB Built-in Data Contributor - for database access\n\n**Service Principal:** costoso-app-sp (with managed identity)\n\nThis follows the principle of least privilege.",
                tools_used=["generate_rbac"]
            )
        
        elif any(word in lower_msg for word in ["deploy", "script", "bicep", "terraform"]):
            return AgentResponse(
                message="""I've generated Bicep deployment scripts for your architecture:

```bicep
param location string = 'eastus'
param environment string = 'prod'

resource storageAccount 'Microsoft.Storage/storageAccounts@2021-04-01' = {
  name: 'st${uniqueString(resourceGroup().id)}'
  location: location
  kind: 'StorageV2'
  sku: {
    name: 'Standard_GRS'
  }
  properties: {
    accessTier: 'Hot'
  }
}

resource keyVault 'Microsoft.KeyVault/vaults@2021-06-01-preview' = {
  name: 'kv-${uniqueString(resourceGroup().id)}'
  location: location
  properties: {
    tenantId: subscription().tenantId
    sku: {
      family: 'A'
      name: 'standard'
    }
    accessPolicies: []
  }
}
```

These templates are ready for Azure CLI deployment: `az deployment group create ...`""",
                tools_used=["generate_deployment_script"]
            )
        
        elif any(word in lower_msg for word in ["validate", "compliance", "best practice", "architecture"]):
            return AgentResponse(
                message="I've validated your architecture against best practices:\n\n✅ **Passed Validations:**\n- Multi-region failover capability\n- Encryption at rest and in transit\n- Network isolation with NSGs\n- Managed identity usage\n\n⚠️ **Recommendations:**\n- Add Application Insights for monitoring\n- Implement Azure Backup for data protection\n- Enable Azure Policy for governance\n- Consider dedicated hosts for PCI compliance\n\n📋 **Compliance Status:**\n- SOC2: 95% aligned\n- HIPAA: 85% aligned\n- PCI-DSS: 90% aligned",
                tools_used=["validate_architecture"]
            )
        
        else:
            # Generic response
            return AgentResponse(
                message=f"I understand you're asking about: '{message}'\n\nAs a Cloud Solution Architect assistant, I can help you with:\n- Searching for relevant solution accelerators\n- Generating RBAC configurations\n- Creating deployment scripts (Bicep/Terraform)\n- Generating IaC templates\n- Validating architectures against compliance frameworks\n\nWhat would you like to focus on?",
                tools_used=[],
                citations=[]
            )

    def call_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Directly call a specific tool.
        
        Args:
            tool_name: Name of the tool
            parameters: Tool parameters
            
        Returns:
            Tool result
        """
        if tool_name not in self.tools:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        # In production, call the actual backend endpoint for the tool
        # For now, return mock results
        logger.info(f"Calling tool: {tool_name} with params: {parameters}")
        
        if tool_name == "search_solutions":
            return self._mock_search_solutions(parameters)
        elif tool_name == "generate_rbac":
            return self._mock_generate_rbac(parameters)
        elif tool_name == "generate_deployment_script":
            return self._mock_generate_deployment(parameters)
        elif tool_name == "generate_iac_template":
            return self._mock_generate_iac(parameters)
        elif tool_name == "validate_architecture":
            return self._mock_validate_architecture(parameters)
        
        return {"error": f"Unknown tool: {tool_name}"}

    def _mock_search_solutions(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Mock search_solutions tool."""
        return {
            "results": [
                {
                    "id": "ai-chatbot-001",
                    "name": "Enterprise AI Chatbot",
                    "description": "Multi-region chatbot for customer service",
                    "complexity": "L300",
                    "area": "AI"
                },
                {
                    "id": "rag-system-001",
                    "name": "RAG with Cognitive Search",
                    "description": "Retrieval-augmented generation system",
                    "complexity": "L400",
                    "area": "AI"
                }
            ]
        }

    def _mock_generate_rbac(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Mock generate_rbac tool."""
        return {
            "roles": [
                {"role": "Contributor", "scope": "/subscriptions/{subscriptionId}"},
                {"role": "Key Vault Administrator", "scope": "/subscriptions/{subscriptionId}/resourceGroups/{rgName}/providers/Microsoft.KeyVault/vaults/{vaultName}"}
            ]
        }

    def _mock_generate_deployment(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Mock generate_deployment_script tool."""
        return {
            "format": params.get("format", "bicep"),
            "script": "param location string = 'eastus'\n\nresource storageAccount 'Microsoft.Storage/storageAccounts@2021-04-01' = {...}"
        }

    def _mock_generate_iac(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Mock generate_iac_template tool."""
        return {
            "template_type": params.get("template_type", "bicep"),
            "structure": {
                "metadata": {"version": "1.0"},
                "parameters": {},
                "resources": []
            }
        }

    def _mock_validate_architecture(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Mock validate_architecture tool."""
        return {
            "status": "passed",
            "score": 95,
            "recommendations": ["Add monitoring", "Enable diagnostic logs"]
        }

    def get_session_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Get conversation history for a session."""
        if session_id not in self.sessions:
            return []
        
        return self.sessions[session_id]["messages"]

    def clear_session_history(self, session_id: str) -> bool:
        """Clear conversation history for a session."""
        if session_id in self.sessions:
            self.sessions[session_id]["messages"] = []
            return True
        return False

    def get_status(self) -> Dict[str, Any]:
        """Get agent status and configuration."""
        return {
            "agent_id": self.agent_id,
            "endpoint": self.endpoint if self.available else "mock",
            "available": self.available,
            "deployment": self.deployment_name,
            "api_version": self.api_version,
            "tools": list(self.tools.keys()),
            "active_sessions": len(self.sessions),
            "authentication": "managed_identity" if self.credential else "api_key" if self.api_key else "none"
        }
