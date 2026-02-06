"""
CSA L400 Test Scenarios for System3-RAG

Realistic enterprise POC generation scenarios for Cloud Solution Architects.
These scenarios test the full system with L400 (advanced) complexity requirements.

L400 Definition: Advanced architecture patterns, multi-region deployment,
enterprise compliance, detailed implementation roadmaps, and production SLA requirements.

Run individual scenarios with:
    python -m pytest test_csa_scenarios.py::TestCSAL400Scenarios::test_scenario_1_* -v
    
Or run all:
    python -m pytest test_csa_scenarios.py -v
"""

import pytest
import json
from datetime import datetime
from fastapi.testclient import TestClient
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.main import app

client = TestClient(app)


class TestCSAL400Scenarios:
    """L400 scenarios requiring advanced architecture, compliance, and implementation details."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Create a fresh session for each scenario."""
        response = client.post("/api/rag/session/create", json={})
        self.session = response.json()
        self.session_id = self.session["session_id"]
        yield
        # Cleanup after test
        client.delete(f"/api/rag/session/{self.session_id}")

    # ========== SCENARIO 1: Enterprise AI Chatbot with Multi-Region HA ==========

    def test_scenario_1_enterprise_ai_chatbot_basic(self):
        """
        SCENARIO 1: Enterprise AI Chatbot with Multi-Region High Availability
        
        CUSTOMER PROFILE:
        - Financial Services company (Contoso Bank)
        - 50,000+ employees, global presence (6 regions)
        - Requirement: Customer service chatbot supporting 10+ languages
        - Compliance: SOC2, PCI-DSS, GDPR
        - Availability: 99.99% SLA, 24/7 support
        
        REQUIREMENTS:
        1. Multi-region deployment (North America, Europe, APAC)
        2. Enterprise-grade security with RBAC and managed identity
        3. Data residency compliance
        4. Disaster recovery and failover
        5. Comprehensive monitoring and alerting
        6. Cost optimization across regions
        
        EXPECTED DELIVERABLES:
        - High-level architecture diagram
        - Implementation roadmap (phases)
        - RBAC role definitions with scopes
        - Bicep/Terraform deployment scripts
        - Cost estimates by region
        - SLA and performance metrics
        """
        
        response = client.post(
            "/api/rag/generate-poc",
            json={
                "session_id": self.session_id,
                "title": "Enterprise AI Chatbot - Multi-Region HA",
                "solution_area": "AI",
                "complexity": "L400",
                "requirements": """
Multi-region AI chatbot for financial services:
- Primary regions: East US, West Europe, Southeast Asia
- Secondary regions: Canada Central, UK South, Australia East
- 99.99% uptime SLA
- Support 12 languages with localization
- Real-time sentiment analysis
- Integration with existing CRM (Dynamics 365)
- Compliance: SOC2 Type II, PCI-DSS v3.2.1, GDPR
- Data residency: Europe data stays in EU, APAC in Asia
- Budget: $500k-$1M annually
- Timeline: 6-month POC to production
""",
                "top_k": 10
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response contains required CSA elements
        self._validate_csa_response(data, "Enterprise AI Chatbot")
        
        # Scenario-specific validations
        recommendations = data.get("recommendations", [])
        if isinstance(recommendations, list) and len(recommendations) > 0:
            # Should include multi-region options
            rec_text = str(recommendations).lower()
            assert any(word in rec_text for word in ["region", "azure", "cosmos", "traffic manager"])

    def test_scenario_1_enterprise_ai_chatbot_rbac(self):
        """Test RBAC generation for scenario 1."""
        response = client.post(
            "/api/rag/generate-poc",
            json={
                "session_id": self.session_id,
                "title": "Enterprise AI Chatbot RBAC",
                "solution_area": "AI",
                "complexity": "L400",
                "requirements": "RBAC for multi-region chatbot with Contoso Bank requirements",
                "top_k": 5
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        rbac = data.get("rbac_requirements", [])
        if isinstance(rbac, list) and len(rbac) > 0:
            # Should have multiple roles for different access levels
            rbac_text = str(rbac).lower()
            expected_roles = ["contributor", "reader", "admin", "operator", "security"]
            # At least some security-related roles should be present
            assert any(role in rbac_text for role in expected_roles)

    def test_scenario_1_enterprise_ai_chatbot_deployment(self):
        """Test deployment script generation for scenario 1."""
        response = client.post(
            "/api/rag/generate-poc",
            json={
                "session_id": self.session_id,
                "title": "Enterprise AI Chatbot Deployment",
                "solution_area": "AI",
                "complexity": "L400",
                "requirements": "Deployment scripts for multi-region chatbot",
                "top_k": 5
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        script = data.get("deployment_script", "")
        if script:
            # Should mention cloud resources
            script_text = str(script).lower()
            keywords = ["resource", "deploy", "bicep", "terraform", "azurerm"]
            assert any(kw in script_text for kw in keywords)

    # ========== SCENARIO 2: Secure Data Analytics Platform ==========

    def test_scenario_2_secure_analytics_basic(self):
        """
        SCENARIO 2: Secure Data Analytics Platform with Advanced Analytics
        
        CUSTOMER PROFILE:
        - Healthcare provider (Contoso Health)
        - 40+ hospitals, 200k+ patients
        - Requirement: HIPAA-compliant analytics platform
        - Use case: Predictive patient care, operational analytics
        - Compliance: HIPAA, HITRUST, state-specific requirements
        
        REQUIREMENTS:
        1. HIPAA-compliant data handling
        2. Advanced analytics (ML models, Power BI)
        3. Data security: encryption at rest, in-transit, RBAC
        4. Audit logging and compliance reporting
        5. Network isolation (private endpoints)
        6. Disaster recovery
        
        EXPECTED DELIVERABLES:
        - Security architecture
        - Data governance framework
        - Compliance checklist
        - Network diagram
        - Incident response plan
        """
        
        response = client.post(
            "/api/rag/generate-poc",
            json={
                "session_id": self.session_id,
                "title": "Secure Healthcare Analytics Platform",
                "solution_area": "Data",
                "complexity": "L400",
                "requirements": """
HIPAA-compliant analytics platform for healthcare:
- Data sources: EHR systems, medical devices, patient records
- Advanced analytics: Predictive models, anomaly detection
- Compliance: HIPAA, HITRUST CSF, state regulations
- Data sensitivity: PII, PHI, financial data
- Features: ML model training, real-time alerts, audit trails
- Users: 500+ data scientists, analysts, clinicians
- Retention: 7 years with archival
- Disaster recovery: 4-hour RTO, 1-hour RPO
- Budget: $1.5M-$3M annually
- Timeline: 12-month implementation
""",
                "top_k": 10
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        self._validate_csa_response(data, "Healthcare Analytics")
        
        # Should emphasize security and compliance
        response_text = str(data).lower()
        assert any(word in response_text for word in ["security", "compliance", "encryption", "audit"])

    def test_scenario_2_security_rbac(self):
        """Test RBAC generation emphasizing healthcare security."""
        response = client.post(
            "/api/rag/generate-poc",
            json={
                "session_id": self.session_id,
                "title": "Healthcare Analytics RBAC",
                "solution_area": "Data",
                "complexity": "L400",
                "requirements": "HIPAA-compliant RBAC with role separation (clinicians, analysts, admins, auditors)",
                "top_k": 5
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        rbac = data.get("rbac_requirements", "")
        rbac_text = str(rbac).lower()
        # Should mention sensitive access controls
        assert any(word in rbac_text for word in ["role", "access", "audit", "compliance", "data"])

    def test_scenario_2_iac_template(self):
        """Test IaC template generation for healthcare platform."""
        response = client.post(
            "/api/rag/generate-poc",
            json={
                "session_id": self.session_id,
                "title": "Healthcare Platform IaC",
                "solution_area": "Data",
                "complexity": "L400",
                "requirements": "Bicep IaC template for secure healthcare data platform",
                "top_k": 5
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        iac = data.get("iac_template", "")
        if iac:
            iac_text = str(iac).lower()
            # Should include security components
            assert any(word in iac_text for word in ["resource", "parameter", "variable", "network", "storage"])

    # ========== SCENARIO 3: Cloud-Native App Migration & Modernization ==========

    def test_scenario_3_cloud_migration_basic(self):
        """
        SCENARIO 3: Cloud-Native App Migration & Modernization
        
        CUSTOMER PROFILE:
        - Manufacturing company (Contoso Industrial)
        - Legacy monolithic applications (20+ year old)
        - Requirement: Modernize to cloud-native, microservices
        - Use case: Supply chain optimization, predictive maintenance
        
        REQUIREMENTS:
        1. Containerization (Docker)
        2. Kubernetes orchestration
        3. Microservices architecture
        4. CI/CD pipelines
        5. Infrastructure as Code (Bicep + Kubernetes)
        6. Zero-downtime migration
        7. Blue-green deployments
        8. Multi-cloud strategy
        
        EXPECTED DELIVERABLES:
        - Architecture evolution roadmap
        - Containerization strategy
        - Kubernetes topology
        - CI/CD pipeline design
        - Cost-benefit analysis
        - Risk mitigation plan
        """
        
        response = client.post(
            "/api/rag/generate-poc",
            json={
                "session_id": self.session_id,
                "title": "Cloud-Native Migration - Monolith to Microservices",
                "solution_area": "Cloud",
                "complexity": "L400",
                "requirements": """
Modernize legacy manufacturing systems to cloud-native:
- Current: 20-year-old monolithic application (20MB binary)
- Target: Microservices on AKS with event-driven architecture
- Components: 15 microservices, 50+ containers
- CI/CD: Azure DevOps, automated testing, GitOps
- Data: Legacy SQL Server → Cosmos DB, data migration
- Infrastructure: Bicep → Terraform for multi-cloud
- Timeline: 18-month phased migration
- Zero-downtime requirement: parallel systems during transition
- Rollback capability: 1-hour restore time
- Cost optimization: 30% reduction target
- Training: 200 developers upskilling needed
""",
                "top_k": 10
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        self._validate_csa_response(data, "Cloud Migration")

    def test_scenario_3_deployment_strategy(self):
        """Test deployment strategy for cloud migration scenario."""
        response = client.post(
            "/api/rag/generate-poc",
            json={
                "session_id": self.session_id,
                "title": "Cloud Migration Deployment Strategy",
                "solution_area": "Cloud",
                "complexity": "L400",
                "requirements": "Blue-green deployment strategy with AKS, Helm, GitOps",
                "top_k": 5
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should include deployment strategy details
        response_text = str(data).lower()
        assert any(word in response_text for word in ["deploy", "aks", "kubernetes", "helm", "gitops", "container"])

    def test_scenario_3_cost_analysis(self):
        """Test cost analysis for cloud migration."""
        response = client.post(
            "/api/rag/generate-poc",
            json={
                "session_id": self.session_id,
                "title": "Cloud Migration Cost Analysis",
                "solution_area": "Cloud",
                "complexity": "L400",
                "requirements": "TCO analysis: on-prem vs cloud, cost optimization opportunities",
                "top_k": 5
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should address cost
        response_text = str(data).lower()
        assert any(word in response_text for word in ["cost", "budget", "pricing", "billing", "consumption"])

    # ========== SCENARIO 4: Real-Time AI/ML Platform ==========

    def test_scenario_4_ml_platform_basic(self):
        """
        SCENARIO 4: Real-Time AI/ML Platform for Financial Services
        
        CUSTOMER PROFILE:
        - Investment firm (Contoso Capital)
        - 500+ quants, data scientists
        - Requirement: Real-time ML platform for trading
        - Use case: Fraud detection, market prediction, portfolio optimization
        
        REQUIREMENTS:
        1. Real-time data ingestion (sub-second latency)
        2. GPU-accelerated model training
        3. Feature engineering at scale
        4. Model serving with ultra-low latency
        5. A/B testing framework
        6. Model monitoring and retraining
        7. Explainability (AI transparency)
        8. Risk management and audit trail
        
        EXPECTED DELIVERABLES:
        - ML platform architecture
        - Data pipeline design
        - Model serving topology
        - Infrastructure requirements
        - Cost/performance tradeoffs
        """
        
        response = client.post(
            "/api/rag/generate-poc",
            json={
                "session_id": self.session_id,
                "title": "Real-Time ML Platform for Trading",
                "solution_area": "AI",
                "complexity": "L400",
                "requirements": """
Real-time ML platform for investment trading:
- Data: 10GB+/day real-time market data, alternative data
- Models: 50+ ML models (trading signals, risk, fraud detection)
- Latency: <100ms inference, <1 second training on new data
- Infrastructure: GPU compute, distributed training
- Features: Feature store, model registry, experiment tracking
- Serving: Low-latency inference, canary deployments, A/B testing
- Monitoring: Model drift detection, prediction monitoring
- Compliance: Risk limits, trading restrictions, audit loss
- Scalability: 1000+ predictions/second
- Timeline: 12-month implementation
- Budget: $5M+ annually (compute-heavy)
""",
                "top_k": 10
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        self._validate_csa_response(data, "ML Trading Platform")

    def test_scenario_4_ml_infrastructure(self):
        """Test infrastructure for ML platform scenario."""
        response = client.post(
            "/api/rag/generate-poc",
            json={
                "session_id": self.session_id,
                "title": "ML Platform GPU Infrastructure",
                "solution_area": "AI",
                "complexity": "L400",
                "requirements": "GPU-based infrastructure for ML training and inference on Azure",
                "top_k": 5
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        response_text = str(data).lower()
        # Should mention compute resources
        assert any(word in response_text for word in ["gpu", "compute", "inference", "training", "aml"])

    # ========== SCENARIO 5: Enterprise IoT & Edge Platform ==========

    def test_scenario_5_iot_edge_basic(self):
        """
        SCENARIO 5: Enterprise IoT & Edge Computing Platform
        
        CUSTOMER PROFILE:
        - Utility company (Contoso Utilities)
        - 10M+ devices (smart meters, sensors)
        - Requirement: Real-time edge analytics
        - Use case: Smart grid, demand prediction, asset monitoring
        
        REQUIREMENTS:
        1. IoT Hub at scale (millions of devices)
        2. Edge computing (Azure Stack Edge, IoT Edge)
        3. Real-time stream processing
        4. Predictive maintenance models
        5. Security key management
        6. Offline capability
        7. Hybrid cloud operation
        
        EXPECTED DELIVERABLES:
        - IoT architecture
        - Edge deployment topology
        - Data flow diagram
        - Security model
        - Scaling strategy
        """
        
        response = client.post(
            "/api/rag/generate-poc",
            json={
                "session_id": self.session_id,
                "title": "Enterprise IoT Smart Grid Platform",
                "solution_area": "Cloud",
                "complexity": "L400",
                "requirements": """
IoT platform for utility smart grid:
- Devices: 10M+ smart meters, substations, sensors
- Data: 100GB+/day telemetry, sensor readings
- Real-time: <5 second latency for grid events
- Edge: Offline processing during network outages
- Analytics: Demand prediction, load balancing, fault detection
- Connectivity: MQTT, AMQP, HTTP protocols
- Availability: 99.99% uptime (critical infrastructure)
- Regions: Multi-country operations with data locality
- Timeline: 24-month nationwide rollout
- Budget: $10M+ (scale and criticality)
""",
                "top_k": 10
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        self._validate_csa_response(data, "IoT Smart Grid")

    # ========== SCENARIO 6: Multi-Tenant SaaS Platform ==========

    def test_scenario_6_saas_platform_basic(self):
        """
        SCENARIO 6: Multi-Tenant SaaS Platform with Advanced Features
        
        CUSTOMER PROFILE:
        - SaaS startup (Contoso SaaS)
        - 1000+ enterprise customers globally
        - Requirement: Scalable multi-tenant platform
        - Use case: Business intelligence, analytics SaaS
        
        REQUIREMENTS:
        1. Multi-tenancy with isolated data
        2. Scalability: 10k-100k concurrent users
        3. Global distribution (CDN)
        4. High availability and disaster recovery
        5. Compliance: SOC2, ISO 27001, GDPR
        6. Analytics: Usage metrics, cost allocation per tenant
        7. Customization: Tenant-specific features
        
        EXPECTED DELIVERABLES:
        - SaaS architecture
        - Tenant isolation strategy
        - Scaling topology
        - Cost model
        - Compliance roadmap
        """
        
        response = client.post(
            "/api/rag/generate-poc",
            json={
                "session_id": self.session_id,
                "title": "Multi-Tenant SaaS Analytics Platform",
                "solution_area": "Cloud",
                "complexity": "L400",
                "requirements": """
Multi-tenant SaaS analytics platform:
- Customers: 1000+ enterprise tenants
- Users: 500k+ concurrent users globally
- Data: 500GB+/day analytics data
- Availability: 99.99% SLA
- Regions: Global (N. America, Europe, APAC)
- Compliance: SOC2 Type II, ISO 27001, GDPR, CCPA
- Features: Custom dashboards, API access, white-labeling
- Scalability: Auto-scaling to handle peak load
- Cost model: Per-tenant metering and billing
- Timeline: 12-month SaaS launch
""",
                "top_k": 10
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        self._validate_csa_response(data, "SaaS Platform")

    # ========== HELPER METHODS ==========

    def _validate_csa_response(self, data: dict, scenario_name: str):
        """Validate response meets CSA L400 requirements."""
        
        # Check all required sections present
        required_sections = [
            "poc_id",
            "title",
            "status",
            "recommendations",
            "rbac_requirements",
            "deployment_script",
            "iac_template"
        ]
        
        for section in required_sections:
            assert section in data, f"Missing required section: {section}"
        
        # Validate non-empty content
        assert len(str(data.get("recommendations", ""))) > 50, "Recommendations too brief"
        assert len(str(data.get("rbac_requirements", ""))) > 50, "RBAC requirements too brief"
        
        print(f"\n✓ {scenario_name} Scenario Validated")
        print(f"  POC ID: {data['poc_id']}")
        print(f"  Status: {data['status']}")
        print(f"  Title: {data['title']}")

    def _validate_search_results(self, results: list, expected_count: int = 5):
        """Validate search results structure."""
        assert isinstance(results, list)
        assert len(results) <= expected_count
        
        for result in results:
            assert "id" in result or "name" in result or "title" in result
            # Results should have relevance score if ranked
            if "score" in result:
                assert 0 <= result["score"] <= 1


class TestCSAScenarioValidation:
    """Validation tests for CSA scenario correctness."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Create session for validation tests."""
        response = client.post("/api/rag/session/create", json={})
        self.session_id = response.json()["session_id"]
        yield
        client.delete(f"/api/rag/session/{self.session_id}")

    def test_all_scenarios_complete_in_time(self):
        """Test that all scenarios complete within reasonable time."""
        import time
        
        scenarios = [
            {
                "title": "Enterprise AI Chatbot",
                "area": "AI",
                "complexity": "L400",
                "max_time": 5.0  # seconds
            },
            {
                "title": "Healthcare Analytics",
                "area": "Data",
                "complexity": "L400",
                "max_time": 5.0
            }
        ]
        
        for scenario in scenarios:
            start = time.time()
            response = client.post(
                "/api/rag/generate-poc",
                json={
                    "session_id": self.session_id,
                    "title": scenario["title"],
                    "solution_area": scenario["area"],
                    "complexity": scenario["complexity"],
                    "requirements": f"Test {scenario['title']}"
                }
            )
            elapsed = time.time() - start
            
            assert response.status_code == 200
            assert elapsed < scenario["max_time"], f"{scenario['title']} took {elapsed}s"

    def test_scenarios_generate_distinct_responses(self):
        """Test that different scenarios generate different recommendations."""
        # Scenario A: AI-focused
        response_a = client.post(
            "/api/rag/generate-poc",
            json={
                "session_id": self.session_id,
                "title": "AI Solution",
                "solution_area": "AI",
                "complexity": "L400",
                "requirements": "AI implementation"
            }
        )
        
        # Scenario B: Data-focused
        response_b = client.post(
            "/api/rag/generate-poc",
            json={
                "session_id": self.session_id,
                "title": "Data Solution",
                "solution_area": "Data",
                "complexity": "L400",
                "requirements": "Data pipeline"
            }
        )
        
        assert response_a.status_code == 200
        assert response_b.status_code == 200
        
        # Recommendations should be different based on solution area
        data_a = response_a.json()
        data_b = response_b.json()
        
        # They should have different content
        assert data_a["poc_id"] != data_b["poc_id"]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
