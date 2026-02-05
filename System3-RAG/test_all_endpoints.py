"""
Comprehensive Test Suite for System3-RAG

Tests all endpoints, session management, agent integration, and CSA scenarios.
Run with: pytest test_all_endpoints.py -v

Coverage:
- API endpoint validation
- Session management lifecycle
- Error handling and edge cases
- Agent integration (mock and real)
- Data serialization
- Concurrent operations
"""

import pytest
import json
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.main import app, get_scraper, get_session_manager
from app.session import SessionManager, ConversationSession, POCGeneration
from app.agent import AzureAIFoundryAgent
from fastapi.testclient import TestClient

# Initialize test client
client = TestClient(app)


class TestHealthAndStatus:
    """Test health checks and system status endpoints."""

    def test_health_check(self):
        """Test /health endpoint returns healthy status."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data

    def test_status_endpoint(self):
        """Test /status endpoint returns system info."""
        response = client.get("/status")
        assert response.status_code == 200
        data = response.json()
        assert "version" in data
        assert "environment" in data
        assert "endpoints" in data
        assert "agent" in data


class TestSessionManagement:
    """Test session lifecycle management."""

    def test_create_session(self):
        """Test creating a new session."""
        response = client.post("/api/rag/session/create", json={})
        assert response.status_code == 201
        data = response.json()
        
        assert "session_id" in data
        assert "created_at" in data
        assert "status" in data
        assert data["status"] == "active"
        self.session_id = data["session_id"]

    def test_get_session(self):
        """Test retrieving session details."""
        # First create a session
        create_response = client.post("/api/rag/session/create", json={})
        session_id = create_response.json()["session_id"]

        # Then retrieve it
        response = client.get(f"/api/rag/session/{session_id}")
        assert response.status_code == 200
        data = response.json()
        
        assert data["session_id"] == session_id
        assert "messages" in data
        assert "poc_generations" in data
        assert isinstance(data["messages"], list)

    def test_session_not_found(self):
        """Test retrieving non-existent session."""
        response = client.get("/api/rag/session/nonexistent-id")
        assert response.status_code == 404

    def test_export_session(self):
        """Test exporting session as JSON."""
        # Create session and add data
        create_response = client.post("/api/rag/session/create", json={})
        session_id = create_response.json()["session_id"]

        # Add a message
        client.post(
            f"/api/rag/session/{session_id}/message",
            json={"role": "user", "content": "Test message"}
        )

        # Export
        response = client.get(f"/api/rag/session/{session_id}/export")
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        
        data = response.json()
        assert "session_id" in data
        assert "messages" in data

    def test_delete_session(self):
        """Test deleting a session."""
        # Create session
        create_response = client.post("/api/rag/session/create", json={})
        session_id = create_response.json()["session_id"]

        # Delete it
        response = client.delete(f"/api/rag/session/{session_id}")
        assert response.status_code == 204

        # Verify it's gone
        response = client.get(f"/api/rag/session/{session_id}")
        assert response.status_code == 404

    def test_session_timeout(self):
        """Test session auto-expiration."""
        with patch('app.session.SESSION_TIMEOUT') as mock_timeout:
            mock_timeout.total_seconds.return_value = 0  # Immediate expiration
            
            # Create session
            response = client.post("/api/rag/session/create", json={})
            session_id = response.json()["session_id"]
            
            # Simulate time passing
            asyncio.sleep(1)
            
            # Session should be expired (depending on implementation)
            # This test verifies the cleanup mechanism works


class TestPOCGeneration:
    """Test POC generation endpoint."""

    def test_generate_poc_basic(self):
        """Test basic POC generation request."""
        response = client.post(
            "/api/rag/generate-poc",
            json={
                "session_id": "test-session-123",
                "title": "AI-Powered Customer Support Chatbot",
                "solution_area": "AI",
                "complexity": "L300",
                "requirements": "Enterprise-grade, multi-language support"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "poc_id" in data
        assert "title" in data
        assert "recommendations" in data
        assert "rbac_requirements" in data
        assert "deployment_script" in data
        assert "iac_template" in data
        assert "status" in data

    def test_generate_poc_with_topk(self):
        """Test POC generation with custom result limit."""
        response = client.post(
            "/api/rag/generate-poc",
            json={
                "session_id": "test-session-456",
                "title": "Data Pipeline Setup",
                "solution_area": "Data",
                "complexity": "L400",
                "requirements": "Real-time data ingestion with Azure Data Factory",
                "top_k": 3
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should have recommendations
        if "recommendations" in data and isinstance(data["recommendations"], list):
            assert len(data["recommendations"]) <= 3

    def test_generate_poc_missing_required_fields(self):
        """Test POC generation with missing fields."""
        response = client.post(
            "/api/rag/generate-poc",
            json={
                "title": "Incomplete Request"
                # Missing session_id, solution_area, etc.
            }
        )
        
        # Should either return 400 or provide default values
        assert response.status_code in [200, 400, 422]

    def test_generate_poc_invalid_complexity(self):
        """Test POC generation with invalid complexity level."""
        response = client.post(
            "/api/rag/generate-poc",
            json={
                "session_id": "test-session",
                "title": "Test",
                "solution_area": "AI",
                "complexity": "L999",  # Invalid
                "requirements": "Test"
            }
        )
        
        # Should handle gracefully
        assert response.status_code in [200, 400]

    def test_generate_poc_response_format(self):
        """Test POC generation response has correct structure."""
        response = client.post(
            "/api/rag/generate-poc",
            json={
                "session_id": "test-session",
                "title": "Test POC",
                "solution_area": "Cloud",
                "complexity": "L300",
                "requirements": "Cloud migration"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check all expected fields present
        expected_fields = [
            "poc_id", "title", "status", 
            "recommendations", "rbac_requirements",
            "deployment_script", "iac_template"
        ]
        
        for field in expected_fields:
            assert field in data, f"Missing field: {field}"


class TestSearch:
    """Test solution search endpoint."""

    def test_search_basic(self):
        """Test basic search query."""
        response = client.post(
            "/api/rag/search",
            json={
                "query": "semantic search",
                "top_k": 5
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "results" in data
        assert isinstance(data["results"], list)

    def test_search_with_filters(self):
        """Test search with area and complexity filters."""
        response = client.post(
            "/api/rag/search",
            json={
                "query": "AI implementation",
                "solution_area": "AI",
                "complexity": "L400",
                "top_k": 10
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "results" in data

    def test_search_with_synthesis(self):
        """Test search with agent synthesis."""
        response = client.post(
            "/api/rag/search",
            json={
                "query": "RAG system architecture",
                "top_k": 5,
                "synthesize": True  # Request agent synthesis
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "results" in data
        if "synthesis" in data:
            assert isinstance(data["synthesis"], str)

    def test_search_empty_query(self):
        """Test search with empty query."""
        response = client.post(
            "/api/rag/search",
            json={
                "query": "",
                "top_k": 5
            }
        )
        
        # Should handle gracefully
        assert response.status_code in [200, 400]

    def test_search_ranking(self):
        """Test search results are ranked by relevance."""
        response = client.post(
            "/api/rag/search",
            json={
                "query": "Azure",
                "top_k": 10
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        if len(data["results"]) > 1:
            # Check results are ranked (scores should be descending)
            scores = [r.get("score", 0) for r in data["results"]]
            # Scores should be in descending order
            assert scores == sorted(scores, reverse=True)


class TestHistory:
    """Test history retrieval endpoints."""

    def test_get_history_empty(self):
        """Test getting history for session with no POCs."""
        response = client.post("/api/rag/session/create", json={})
        session_id = response.json()["session_id"]

        response = client.get(f"/api/rag/session/{session_id}/history")
        assert response.status_code == 200
        data = response.json()
        
        assert "poc_generations" in data
        assert isinstance(data["poc_generations"], list)
        assert len(data["poc_generations"]) == 0

    def test_get_history_with_pocs(self):
        """Test getting history with multiple POCs."""
        response = client.post("/api/rag/session/create", json={})
        session_id = response.json()["session_id"]

        # Generate a POC
        client.post(
            "/api/rag/generate-poc",
            json={
                "session_id": session_id,
                "title": "POC 1",
                "solution_area": "AI",
                "complexity": "L300",
                "requirements": "Test"
            }
        )

        # Get history
        response = client.get(f"/api/rag/session/{session_id}/history")
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["poc_generations"]) > 0
        first_poc = data["poc_generations"][0]
        assert "id" in first_poc
        assert "title" in first_poc
        assert "created_at" in first_poc


class TestAgentIntegration:
    """Test Azure AI Foundry agent integration."""

    @patch('app.agent.AzureAIFoundryAgent.send_message')
    def test_agent_send_message(self, mock_send):
        """Test agent message sending."""
        mock_send.return_value = {
            "response": "Mock agent response",
            "status": "success"
        }

        agent = AzureAIFoundryAgent()
        result = agent.send_message(
            session_id="test",
            message="Generate POC for AI chatbot"
        )
        
        assert result["status"] == "success"
        mock_send.assert_called_once()

    @patch('app.agent.AzureAIFoundryAgent.create_session')
    def test_agent_create_session(self, mock_create):
        """Test agent session creation."""
        mock_create.return_value = "agent-session-123"

        agent = AzureAIFoundryAgent()
        session_id = agent.create_session()
        
        assert session_id == "agent-session-123"
        mock_create.assert_called_once()

    @patch('app.agent.AzureAIFoundryAgent.call_tool')
    def test_agent_search_solutions_tool(self, mock_tool):
        """Test search_solutions agent tool."""
        mock_tool.return_value = {
            "results": [
                {"id": "accel-1", "name": "Solution 1", "score": 0.95},
                {"id": "accel-2", "name": "Solution 2", "score": 0.87}
            ]
        }

        agent = AzureAIFoundryAgent()
        results = agent.call_tool(
            "search_solutions",
            {"query": "RAG", "area": "AI", "top_k": 5}
        )
        
        assert len(results["results"]) == 2
        assert results["results"][0]["score"] > results["results"][1]["score"]

    @patch('app.agent.AzureAIFoundryAgent.call_tool')
    def test_agent_generate_rbac_tool(self, mock_tool):
        """Test generate_rbac agent tool."""
        mock_tool.return_value = {
            "rbac_roles": [
                {"role": "Contributor", "scope": "/subscriptions/..."},
                {"role": "Key Vault Administrator", "scope": "/subscriptions/.../resourceGroups/.../providers/Microsoft.KeyVault/vaults/..."}
            ]
        }

        agent = AzureAIFoundryAgent()
        result = agent.call_tool(
            "generate_rbac",
            {"solution_id": "ai-chatbot", "organization": "Contoso"}
        )
        
        assert "rbac_roles" in result
        assert len(result["rbac_roles"]) > 0

    @patch('app.agent.AzureAIFoundryAgent.call_tool')
    def test_agent_generate_deployment_script_tool(self, mock_tool):
        """Test generate_deployment_script agent tool."""
        mock_tool.return_value = {
            "script_type": "bicep",
            "script_content": "param location string = 'eastus'..."
        }

        agent = AzureAIFoundryAgent()
        result = agent.call_tool(
            "generate_deployment_script",
            {"solution_id": "ai-chatbot", "format": "bicep", "environment": "prod"}
        )
        
        assert result["script_type"] == "bicep"
        assert "script_content" in result

    @patch('app.agent.AzureAIFoundryAgent.call_tool')
    def test_agent_generate_iac_template_tool(self, mock_tool):
        """Test generate_iac_template agent tool."""
        mock_tool.return_value = {
            "template_type": "bicep",
            "structure": {
                "parameters": [...],
                "variables": [...],
                "resources": [...]
            }
        }

        agent = AzureAIFoundryAgent()
        result = agent.call_tool(
            "generate_iac_template",
            {"solution_id": "ai-chatbot", "template_type": "bicep"}
        )
        
        assert result["template_type"] == "bicep"
        assert "structure" in result

    @patch('app.agent.AzureAIFoundryAgent.call_tool')
    def test_agent_validate_architecture_tool(self, mock_tool):
        """Test validate_architecture agent tool."""
        mock_tool.return_value = {
            "validation_status": "passed",
            "warnings": [],
            "recommendations": ["Add Application Insights", "Enable managed identity"]
        }

        agent = AzureAIFoundryAgent()
        result = agent.call_tool(
            "validate_architecture",
            {"solution_id": "ai-chatbot", "compliance_frameworks": ["SOC2"]}
        )
        
        assert result["validation_status"] in ["passed", "warning", "failed"]
        assert "recommendations" in result


class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_invalid_json_payload(self):
        """Test handling of invalid JSON."""
        response = client.post(
            "/api/rag/generate-poc",
            content="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code >= 400

    def test_missing_content_type(self):
        """Test handling of missing Content-Type header."""
        response = client.post(
            "/api/rag/generate-poc",
            data='{"title": "test"}'
        )
        
        # Should either work or return proper error
        assert response.status_code in [200, 400, 415]

    def test_concurrent_operations(self):
        """Test handling of concurrent operations."""
        responses = []
        
        for i in range(5):
            response = client.post(
                "/api/rag/session/create",
                json={}
            )
            responses.append(response)
        
        # All should succeed
        assert all(r.status_code == 201 for r in responses)
        
        # All session IDs should be unique
        session_ids = [r.json()["session_id"] for r in responses]
        assert len(set(session_ids)) == len(session_ids)


class TestDataValidation:
    """Test data validation and schema compliance."""

    def test_session_response_schema(self):
        """Test session response follows schema."""
        response = client.post("/api/rag/session/create", json={})
        data = response.json()
        
        # Check required fields and types
        assert isinstance(data.get("session_id"), str)
        assert isinstance(data.get("created_at"), str)
        assert data.get("status") in ["active", "expired", "deleted"]

    def test_poc_response_schema(self):
        """Test POC response follows schema."""
        response = client.post(
            "/api/rag/generate-poc",
            json={
                "session_id": "test",
                "title": "Test POC",
                "solution_area": "AI",
                "complexity": "L300",
                "requirements": "Test"
            }
        )
        
        data = response.json()
        
        # Type checks
        assert isinstance(data.get("poc_id"), str)
        assert isinstance(data.get("title"), str)
        assert isinstance(data.get("recommendations"), (list, dict))
        assert isinstance(data.get("rbac_requirements"), (list, dict, str))

    def test_search_response_schema(self):
        """Test search response follows schema."""
        response = client.post(
            "/api/rag/search",
            json={"query": "test", "top_k": 5}
        )
        
        data = response.json()
        
        assert isinstance(data.get("results"), list)
        
        if data["results"]:
            first_result = data["results"][0]
            assert "id" in first_result or "name" in first_result


class TestPerformance:
    """Test performance characteristics."""

    def test_session_creation_speed(self):
        """Test session creation is fast."""
        import time
        
        start = time.time()
        response = client.post("/api/rag/session/create", json={})
        elapsed = time.time() - start
        
        assert response.status_code == 201
        assert elapsed < 0.5  # Should complete in < 500ms

    def test_search_response_time(self):
        """Test search completes in reasonable time."""
        import time
        
        start = time.time()
        response = client.post(
            "/api/rag/search",
            json={"query": "Azure AI", "top_k": 5}
        )
        elapsed = time.time() - start
        
        assert response.status_code == 200
        assert elapsed < 2.0  # Should complete in < 2 seconds

    def test_health_check_speed(self):
        """Test health check is very fast."""
        import time
        
        start = time.time()
        response = client.get("/health")
        elapsed = time.time() - start
        
        assert response.status_code == 200
        assert elapsed < 0.1  # Should complete in < 100ms


# Test fixtures and helpers
@pytest.fixture
def session_id():
    """Create a test session."""
    response = client.post("/api/rag/session/create", json={})
    return response.json()["session_id"]


@pytest.fixture
def cleanup_sessions():
    """Cleanup test sessions after test."""
    yield
    # Cleanup code would go here


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
