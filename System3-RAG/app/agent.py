"""
Azure AI Foundry Agent Client

Provides abstraction layer for communicating with Azure AI Foundry agents.
Handles authentication, session management, and response formatting.
"""

import os
import json
import logging
from typing import Optional, Dict, List, Any
from dataclasses import dataclass
import httpx
from azure.identity import DefaultAzureCredential, ClientSecretCredential


logger = logging.getLogger(__name__)


@dataclass
class AgentMessage:
    """Represents a message in agent conversation."""
    role: str  # "user" or "assistant"
    content: str
    citations: Optional[List[Dict[str, str]]] = None
    tools_used: Optional[List[str]] = None


@dataclass
class AgentResponse:
    """Structured response from agent."""
    message: str
    citations: List[Dict[str, str]]
    tools_used: List[str]
    reasoning: Optional[str] = None
    recommendations: Optional[Dict[str, Any]] = None


class AzureAIFoundryAgent:
    """
    Client for Azure AI Foundry Agents.
    
    Handles:
    - Authentication (Managed Identity or Service Principal)
    - Session/conversation management
    - Tool invocation and result handling
    - Response parsing and formatting
    """
    
    def __init__(
        self,
        endpoint: str,
        agent_id: str,
        api_key: Optional[str] = None,
        deployment_name: str = "gpt-4o",
        use_managed_identity: bool = True,
    ):
        """
        Initialize Azure AI Foundry Agent client.
        
        Args:
            endpoint: Azure AI Foundry endpoint (e.g., https://xxx.openai.azure.com/)
            agent_id: ID of the deployed agent
            api_key: API key (if not using managed identity)
            deployment_name: Model deployment name (default: gpt-4o)
            use_managed_identity: Use Azure AD authentication (default: True)
        """
        self.endpoint = endpoint.rstrip('/')
        self.agent_id = agent_id
        self.deployment_name = deployment_name
        self.api_version = "2024-02-15-preview"
        
        # Setup authentication
        if use_managed_identity:
            self.credential = DefaultAzureCredential()
            logger.info("Using Azure Managed Identity for authentication")
        else:
            if not api_key:
                api_key = os.getenv("AZURE_AI_FOUNDRY_KEY")
            self.api_key = api_key
            logger.info("Using API key authentication")
        
        # Session storage (in-memory; use database for production)
        self.sessions: Dict[str, List[AgentMessage]] = {}
    
    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers with authentication."""
        headers = {
            "Content-Type": "application/json",
            "api-version": self.api_version,
        }
        
        if hasattr(self, 'api_key'):
            headers["api-key"] = self.api_key
        else:
            # Use bearer token from managed identity
            token = self.credential.get_token("https://openai.azure.com/.default").token
            headers["Authorization"] = f"Bearer {token}"
        
        return headers
    
    def create_session(self, session_id: str) -> str:
        """
        Create a new conversation session.
        
        Args:
            session_id: Unique identifier for the session
            
        Returns:
            Session ID
        """
        self.sessions[session_id] = []
        logger.info(f"Created new session: {session_id}")
        return session_id
    
    def delete_session(self, session_id: str) -> None:
        """Delete a conversation session."""
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Deleted session: {session_id}")
    
    def send_message(
        self,
        session_id: str,
        content: str,
        user_id: Optional[str] = None,
    ) -> AgentResponse:
        """
        Send a message to the agent and get response.
        
        Args:
            session_id: Conversation session ID
            content: User message
            user_id: Optional user identifier
            
        Returns:
            AgentResponse with message, citations, and tools used
        """
        # Ensure session exists
        if session_id not in self.sessions:
            self.create_session(session_id)
        
        # Add user message to history
        self.sessions[session_id].append(
            AgentMessage(role="user", content=content)
        )
        
        # Call agent API
        try:
            response_data = self._call_agent_api(session_id, content, user_id)
            
            # Parse response
            agent_response = self._parse_response(response_data)
            
            # Add to history
            self.sessions[session_id].append(
                AgentMessage(
                    role="assistant",
                    content=agent_response.message,
                    citations=agent_response.citations,
                    tools_used=agent_response.tools_used,
                )
            )
            
            return agent_response
            
        except Exception as e:
            logger.error(f"Error sending message to agent: {e}")
            raise
    
    def _call_agent_api(
        self,
        session_id: str,
        content: str,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Call the Azure AI Foundry Agent API.
        
        Args:
            session_id: Conversation session
            content: User message
            user_id: Optional user ID
            
        Returns:
            JSON response from agent
        """
        url = f"{self.endpoint}/agents/{self.agent_id}/messages"
        
        headers = self._get_headers()
        
        # Build request payload
        payload = {
            "role": "user",
            "content": content,
        }
        
        if user_id:
            payload["user_id"] = user_id
        
        # Add conversation history for context
        messages = []
        for msg in self.sessions[session_id]:
            messages.append({
                "role": msg.role,
                "content": msg.content,
            })
        
        request_body = {
            "messages": messages,
            "session_id": session_id,
        }
        
        logger.debug(f"Calling agent API with {len(messages)} messages")
        
        # Make API call (synchronous for now; could be async)
        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                url,
                json=request_body,
                headers=headers,
            )
            response.raise_for_status()
            return response.json()
    
    def _parse_response(self, response_data: Dict[str, Any]) -> AgentResponse:
        """
        Parse agent API response into structured format.
        
        Args:
            response_data: Raw response from agent API
            
        Returns:
            Structured AgentResponse
        """
        # Extract message (agent API returns nested structure)
        message = response_data.get("content", "")
        
        # Extract citations if present
        citations = []
        if "citations" in response_data:
            citations = response_data["citations"]
        
        # Extract tools used
        tools_used = []
        if "tools_used" in response_data:
            tools_used = response_data["tools_used"]
        
        # Extract reasoning and recommendations if present
        reasoning = response_data.get("reasoning")
        recommendations = response_data.get("recommendations")
        
        return AgentResponse(
            message=message,
            citations=citations,
            tools_used=tools_used,
            reasoning=reasoning,
            recommendations=recommendations,
        )
    
    def get_session_history(self, session_id: str) -> List[AgentMessage]:
        """Get full conversation history for a session."""
        return self.sessions.get(session_id, [])
    
    def clear_session_history(self, session_id: str) -> None:
        """Clear conversation history (but keep session active)."""
        if session_id in self.sessions:
            self.sessions[session_id] = []
            logger.info(f"Cleared history for session: {session_id}")


class AgentToolDefinitions:
    """
    Tool definitions for the agent.
    
    The agent can invoke these tools to:
    - Search solution catalog
    - Generate RBAC assignments
    - Generate deployment scripts
    - Generate IaC templates
    """
    
    SEARCH_SOLUTIONS = {
        "name": "search_solutions",
        "description": "Search the solution accelerators catalog by keyword or area",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query (keyword or solution area)"
                },
                "top_k": {
                    "type": "integer",
                    "description": "Number of results to return (default: 5)",
                    "default": 5
                },
                "area": {
                    "type": "string",
                    "description": "Filter by solution area (optional)",
                    "enum": ["AI", "Security", "Data", "Cloud", "Fabric"]
                }
            },
            "required": ["query"]
        }
    }
    
    GENERATE_RBAC = {
        "name": "generate_rbac_requirements",
        "description": "Generate RBAC role assignments for a given solution",
        "input_schema": {
            "type": "object",
            "properties": {
                "solution_id": {
                    "type": "string",
                    "description": "ID of the solution accelerator"
                },
                "scenario": {
                    "type": "string",
                    "description": "Use case scenario for RBAC mapping"
                }
            },
            "required": ["solution_id"]
        }
    }
    
    GENERATE_DEPLOYMENT_SCRIPT = {
        "name": "generate_deployment_script",
        "description": "Generate PowerShell or Bash deployment script for a solution",
        "input_schema": {
            "type": "object",
            "properties": {
                "solution_id": {
                    "type": "string",
                    "description": "ID of the solution accelerator"
                },
                "script_language": {
                    "type": "string",
                    "description": "PowerShell or Bash",
                    "enum": ["powershell", "bash"]
                },
                "target_environment": {
                    "type": "string",
                    "description": "Target deployment environment",
                    "enum": ["local", "dev", "staging", "production"]
                }
            },
            "required": ["solution_id", "script_language"]
        }
    }
    
    GENERATE_IAC = {
        "name": "generate_iac_template",
        "description": "Generate Infrastructure-as-Code (Bicep/Terraform) template",
        "input_schema": {
            "type": "object",
            "properties": {
                "solution_id": {
                    "type": "string",
                    "description": "ID of the solution accelerator"
                },
                "template_language": {
                    "type": "string",
                    "description": "Bicep or Terraform",
                    "enum": ["bicep", "terraform"]
                },
                "resource_group": {
                    "type": "string",
                    "description": "Target Azure resource group (optional)"
                }
            },
            "required": ["solution_id", "template_language"]
        }
    }
    
    VALIDATE_ARCHITECTURE = {
        "name": "validate_architecture",
        "description": "Validate proposed architecture against best practices",
        "input_schema": {
            "type": "object",
            "properties": {
                "architecture_description": {
                    "type": "string",
                    "description": "Description of the proposed architecture"
                },
                "checklist_items": {
                    "type": "array",
                    "description": "Specific items to validate",
                    "items": {"type": "string"}
                }
            },
            "required": ["architecture_description"]
        }
    }
    
    @classmethod
    def get_all_tools(cls) -> List[Dict[str, Any]]:
        """Return list of all available tools."""
        return [
            cls.SEARCH_SOLUTIONS,
            cls.GENERATE_RBAC,
            cls.GENERATE_DEPLOYMENT_SCRIPT,
            cls.GENERATE_IAC,
            cls.VALIDATE_ARCHITECTURE,
        ]


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    agent = AzureAIFoundryAgent(
        endpoint=os.getenv("AI_FOUNDRY_ENDPOINT", "https://example.openai.azure.com/"),
        agent_id=os.getenv("AI_FOUNDRY_AGENT_ID", "agent-123"),
    )
    
    # Create session
    session_id = "user-123-session-1"
    agent.create_session(session_id)
    
    # Send message (example)
    try:
        response = agent.send_message(
            session_id=session_id,
            content="What solutions do you have for enterprise AI automation?",
        )
        
        print(f"Agent: {response.message}")
        if response.citations:
            print(f"Citations: {response.citations}")
        if response.tools_used:
            print(f"Tools used: {response.tools_used}")
            
    except Exception as e:
        print(f"Error: {e}")
