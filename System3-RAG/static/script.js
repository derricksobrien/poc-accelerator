/**
 * System3-RAG Frontend JavaScript
 * Agent-Based POC Generator with Session Support
 * Integrates with Azure AI Foundry agents for intelligent responses
 */

// ============================================================================
// Configuration & Initialization
// ============================================================================

// API Base URL Detection
function getAPIBaseURL() {
    const host = window.location.hostname;
    const protocol = window.location.protocol;
    
    console.log('[API] Detecting environment...');
    console.log('[API] Hostname:', host);
    
    // Local development
    if (host === 'localhost' || host === '127.0.0.1') {
        const url = 'http://localhost:8000/api';
        console.log('[API] Local environment detected, using:', url);
        return url;
    }
    
    // Azure Container Apps environment
    if (host.includes('azurecontainerapps.io') || host.includes('system3')) {
        const url = '/api';
        console.log('[API] Azure environment detected, using relative path:', url);
        return url;
    }
    
    // Fallback
    const url = `${protocol}//${host}/api`;
    console.log('[API] Generic environment, using:', url);
    return url;
}

const API_BASE_URL = getAPIBaseURL();
let CURRENT_SESSION_ID = localStorage.getItem('system3_session_id') || null;

console.log('[APP] API Base URL configured:', API_BASE_URL);
console.log('[APP] Current Session:', CURRENT_SESSION_ID);

// ============================================================================
// Session Management
// ============================================================================

async function createNewSession() {
    console.log('[SESSION] Creating new session...');
    
    try {
        const response = await makeRequest(`${API_BASE_URL}/rag/session/create`, 'POST', {
            metadata: {
                created_from: 'System3-RAG frontend',
                timestamp: new Date().toISOString()
            }
        });
        
        CURRENT_SESSION_ID = response.session_id;
        localStorage.setItem('system3_session_id', CURRENT_SESSION_ID);
        
        document.getElementById('sessionId').textContent = `Session: ${CURRENT_SESSION_ID.substring(0, 8)}...`;
        
        console.log('[SESSION] New session created:', CURRENT_SESSION_ID);
        showNotification('New session created', 'success');
        
    } catch (error) {
        console.error('[SESSION] Failed to create session:', error);
        showNotification('Failed to create session: ' + error.message, 'error');
    }
}

async function exportSessionData() {
    if (!CURRENT_SESSION_ID) {
        showNotification('No active session', 'error');
        return;
    }
    
    console.log('[SESSION] Exporting session data...');
    
    try {
        const response = await makeRequest(
            `${API_BASE_URL}/rag/session/${CURRENT_SESSION_ID}/export`,
            'GET'
        );
        
        const blob = new Blob([JSON.stringify(response, null, 2)], { type: 'application/json' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `system3-session-${CURRENT_SESSION_ID.substring(0, 8)}-${Date.now()}.json`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        console.log('[SESSION] Session exported');
        
    } catch (error) {
        console.error('[SESSION] Export failed:', error);
        showNotification('Export failed: ' + error.message, 'error');
    }
}

// ============================================================================
// Tab Navigation
// ============================================================================

function switchTab(tabName) {
    console.log('[TAB] Switching to tab:', tabName);
    
    // Hide all tabs
    const tabs = document.querySelectorAll('.tab-content');
    tabs.forEach(tab => tab.classList.remove('active'));
    
    // Remove active class from buttons
    const buttons = document.querySelectorAll('.tab-button');
    buttons.forEach(btn => btn.classList.remove('active'));
    
    // Show selected tab and mark button active
    const selectedTab = document.getElementById(tabName);
    if (selectedTab) {
        selectedTab.classList.add('active');
    }
    
    event.target.classList.add('active');
}

// ============================================================================
// Form Initialization
// ============================================================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('[APP] Initializing System3-RAG...');
    
    // Initialize session
    if (!CURRENT_SESSION_ID) {
        createNewSession();
    } else {
        document.getElementById('sessionId').textContent = `Session: ${CURRENT_SESSION_ID.substring(0, 8)}...`;
    }
    
    // Tab buttons
    const tabButtons = document.querySelectorAll('.tab-button');
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const tabName = this.getAttribute('data-tab');
            switchTab(tabName);
        });
    });
    
    // Forms
    const pocForm = document.getElementById('pocForm');
    if (pocForm) pocForm.addEventListener('submit', handlePOCGeneration);
    
    const searchForm = document.getElementById('searchForm');
    if (searchForm) searchForm.addEventListener('submit', handleSearch);
    
    const chatForm = document.getElementById('chatForm');
    if (chatForm) chatForm.addEventListener('submit', handleChatMessage);
    
    console.log('[APP] System3-RAG initialized');
});

// ============================================================================
// API Communication
// ============================================================================

async function makeRequest(endpoint, method = 'GET', data = null) {
    try {
        console.log(`[API] ${method} request to: ${endpoint}`);
        
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            },
            mode: 'cors',
            credentials: 'same-origin'
        };
        
        if (data) {
            options.body = JSON.stringify(data);
            console.log('[API] Request payload:', data);
        }
        
        const response = await fetch(endpoint, options);
        
        console.log(`[API] Response status: ${response.status}`);
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ error: response.statusText }));
            console.error('[API] Error response:', errorData);
            throw new Error(errorData.error || errorData.detail || `HTTP ${response.status}`);
        }
        
        const responseData = await response.json();
        console.log('[API] Response data received');
        return responseData;
        
    } catch (error) {
        console.error('[API] Request failed:', error.message);
        throw error;
    }
}

// ============================================================================
// POC Generation Handler
// ============================================================================

async function handlePOCGeneration(event) {
    event.preventDefault();
    console.log('[POC] Generating POC...');
    
    const solutionArea = document.getElementById('solutionArea').value;
    const pocTitle = document.getElementById('pocTitle').value;
    const pocQuery = document.getElementById('pocQuery').value;
    const topResults = document.getElementById('topResults').value;
    
    const errorDiv = document.getElementById('pocError');
    const resultDiv = document.getElementById('pocResult');
    
    errorDiv.style.display = 'none';
    resultDiv.style.display = 'none';
    
    try {
        const response = await makeRequest(
            `${API_BASE_URL}/rag/generate-poc?session_id=${CURRENT_SESSION_ID}`,
            'POST',
            {
                solution_area: solutionArea,
                poc_title: pocTitle,
                query: pocQuery,
                top_results: parseInt(topResults)
            }
        );
        
        console.log('[POC] Successfully generated:', response.poc.id);
        
        // Display result
        const outputDiv = document.getElementById('pocOutput');
        displayPOCResult(response.details, outputDiv);
        resultDiv.style.display = 'block';
        
        showNotification('POC generated successfully', 'success');
        
    } catch (error) {
        console.error('[POC] Generation failed:', error);
        const errorMsg = document.getElementById('pocErrorMsg');
        errorMsg.textContent = error.message;
        errorDiv.style.display = 'block';
        showNotification('POC generation failed', 'error');
    }
}

function displayPOCResult(pocData, container) {
    let html = '';
    
    if (pocData.recommendations) {
        html += '<h4>📚 Solution Recommendations</h4>';
        html += '<ul>';
        pocData.recommendations.forEach(rec => {
            html += `<li><strong>${rec.solution}</strong> (${(rec.relevance * 100).toFixed(0)}% match) - ${rec.why}</li>`;
        });
        html += '</ul>';
    }
    
    if (pocData.rbac_requirements) {
        html += '<h4>🔐 RBAC Requirements</h4>';
        html += '<pre>' + JSON.stringify(pocData.rbac_requirements, null, 2) + '</pre>';
    }
    
    if (pocData.deployment_script) {
        html += '<h4>🚀 Deployment Script</h4>';
        html += '<pre>' + pocData.deployment_script + '</pre>';
    }
    
    if (pocData.iac_template) {
        html += '<h4>🏗️ Infrastructure as Code</h4>';
        html += '<pre>' + JSON.stringify(pocData.iac_template, null, 2) + '</pre>';
    }
    
    if (pocData.architecture_summary) {
        html += '<h4>🏛️ Architecture Summary</h4>';
        html += '<p>' + pocData.architecture_summary + '</p>';
    }
    
    if (pocData.estimated_setup_time_hours) {
        html += `<p><strong>⏱️ Estimated Setup Time:</strong> ${pocData.estimated_setup_time_hours} hours</p>`;
    }
    
    if (pocData.cost_estimate) {
        html += `<p><strong>💰 Cost Estimate:</strong> ${pocData.cost_estimate}</p>`;
    }
    
    container.innerHTML = html;
}

function downloadPOC() {
    const pocOutput = document.getElementById('pocOutput').textContent;
    const blob = new Blob([pocOutput], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `poc-${Date.now()}.txt`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
    console.log('[DOWNLOAD] POC downloaded');
}

// ============================================================================
// Chat Handler
// ============================================================================

async function handleChatMessage(event) {
    event.preventDefault();
    console.log('[CHAT] Sending message to agent...');
    
    const chatInput = document.getElementById('chatInput');
    const messageContent = chatInput.value.trim();
    
    if (!messageContent) return;
    
    // Display user message
    addChatMessage('user', messageContent);
    chatInput.value = '';
    
    const errorDiv = document.getElementById('chatError');
    errorDiv.style.display = 'none';
    
    try {
        // TODO: Call agent endpoint when available
        // For now, show mock response
        addChatMessage('assistant', 'Agent response - This will be powered by Azure AI Foundry agents.');
        
    } catch (error) {
        console.error('[CHAT] Failed:', error);
        const errorMsg = document.getElementById('chatErrorMsg');
        errorMsg.textContent = error.message;
        errorDiv.style.display = 'block';
    }
}

function addChatMessage(role, content) {
    const messagesDiv = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message chat-${role}`;
    messageDiv.innerHTML = `<div class="chat-content">${escapeHtml(content)}</div>`;
    messagesDiv.appendChild(messageDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

// ============================================================================
// Search Handler
// ============================================================================

async function handleSearch(event) {
    event.preventDefault();
    console.log('[SEARCH] Executing search...');
    
    const searchQuery = document.getElementById('searchQuery').value;
    const topK = document.getElementById('topK').value;
    const includeSynthesis = document.getElementById('includeSynthesis').checked;
    
    const errorDiv = document.getElementById('searchError');
    const resultDiv = document.getElementById('searchResult');
    
    errorDiv.style.display = 'none';
    resultDiv.style.display = 'none';
    
    try {
        const response = await makeRequest(
            `${API_BASE_URL}/rag/search?session_id=${CURRENT_SESSION_ID}`,
            'POST',
            {
                query: searchQuery,
                top_k: parseInt(topK),
                include_synthesis: includeSynthesis
            }
        );
        
        console.log('[SEARCH] Found results');
        
        // Display results
        const outputDiv = document.getElementById('searchOutput');
        if (response.results && response.results.length > 0) {
            let html = '<div class="results-list">';
            response.results.forEach((result, index) => {
                html += `
                    <div class="result-item">
                        <h4>${index + 1}. ${result.title}</h4>
                        <p><strong>Area:</strong> ${result.solution_area}</p>
                        <p><strong>Level:</strong> ${result.level}</p>
                        <p><strong>Description:</strong> ${result.description}</p>
                        <p><strong>Relevance:</strong> ${(result.relevance * 100).toFixed(1)}%</p>
                    </div>
                `;
            });
            html += '</div>';
            outputDiv.innerHTML = html;
        } else {
            outputDiv.innerHTML = '<p>No results found.</p>';
        }
        
        // Display synthesis
        if (response.synthesis) {
            const synthesisDiv = document.getElementById('searchSynthesis');
            let html = '<h4>Agent Synthesis</h4>';
            html += `<p><strong>${response.synthesis.summary}</strong></p>`;
            html += `<p>${response.synthesis.recommendations}</p>`;
            if (response.synthesis.next_steps) {
                html += '<p><strong>Next Steps:</strong></p><ul>';
                response.synthesis.next_steps.forEach(step => {
                    html += `<li>${step}</li>`;
                });
                html += '</ul>';
            }
            synthesisDiv.innerHTML = html;
        }
        
        resultDiv.style.display = 'block';
        showNotification('Search completed', 'success');
        
    } catch (error) {
        console.error('[SEARCH] Failed:', error);
        const errorMsg = document.getElementById('searchErrorMsg');
        errorMsg.textContent = error.message;
        errorDiv.style.display = 'block';
        showNotification('Search failed', 'error');
    }
}

// ============================================================================
// History Handler
// ============================================================================

async function loadHistory() {
    if (!CURRENT_SESSION_ID) {
        showNotification('No active session', 'error');
        return;
    }
    
    console.log('[HISTORY] Loading POC history...');
    
    try {
        const response = await makeRequest(
            `${API_BASE_URL}/rag/history?session_id=${CURRENT_SESSION_ID}`,
            'GET'
        );
        
        console.log('[HISTORY] Loaded POCs');
        
        const resultDiv = document.getElementById('historyResult');
        const emptyDiv = document.getElementById('historyEmpty');
        const outputDiv = document.getElementById('historyOutput');
        
        if (response.poc_generations && response.poc_generations.length > 0) {
            let html = '<div class="history-list">';
            response.poc_generations.forEach((poc, index) => {
                html += `
                    <div class="history-item">
                        <h4>${index + 1}. ${poc.title}</h4>
                        <p><strong>ID:</strong> <code>${poc.id}</code></p>
                        <p><strong>Area:</strong> ${poc.solution_area}</p>
                        <p><strong>Status:</strong> <span class="status-${poc.status}">${poc.status}</span></p>
                        <p><strong>Created:</strong> ${new Date(poc.created_at).toLocaleString()}</p>
                    </div>
                `;
            });
            html += '</div>';
            outputDiv.innerHTML = html;
            resultDiv.style.display = 'block';
            emptyDiv.style.display = 'none';
        } else {
            resultDiv.style.display = 'none';
            emptyDiv.style.display = 'block';
        }
        
    } catch (error) {
        console.error('[HISTORY] Failed:', error);
        const emptyDiv = document.getElementById('historyEmpty');
        emptyDiv.innerHTML = `<p style="color: red;">Error loading history: ${error.message}</p>`;
    }
}

// ============================================================================
// Status Check
// ============================================================================

async function checkSystemStatus() {
    console.log('[STATUS] Checking system status...');
    
    try {
        const response = await makeRequest(`${API_BASE_URL.replace('/api', '')}/status`, 'GET');
        
        console.log('[STATUS] System status retrieved');
        
        const resultDiv = document.getElementById('statusResult');
        const outputDiv = document.getElementById('statusOutput');
        
        outputDiv.textContent = JSON.stringify(response, null, 2);
        resultDiv.style.display = 'block';
        
        // Update system info table
        document.getElementById('apiEndpoint').textContent = API_BASE_URL;
        document.getElementById('environment').textContent = 
            window.location.hostname.includes('azurecontainerapps.io') ? 'Azure Cloud' : 'Local Development';
        document.getElementById('agentStatus').textContent = 
            response.agent_configured ? '✅ Configured' : '⚠️ Not Configured';
        document.getElementById('healthStatus').textContent = '✅ Healthy';
        document.getElementById('healthStatus').style.color = 'green';
        
    } catch (error) {
        console.error('[STATUS] Failed:', error);
        document.getElementById('healthStatus').textContent = '❌ Unhealthy';
        document.getElementById('healthStatus').style.color = 'red';
        document.getElementById('healthStatus').innerHTML += ` (${error.message})`;
    }
}

// ============================================================================
// Utility Functions
// ============================================================================

function copyToClipboard(elementId) {
    const element = document.getElementById(elementId);
    const text = element.textContent;
    navigator.clipboard.writeText(text).then(() => {
        showNotification('Copied to clipboard', 'success');
    }).catch(err => {
        console.error('[COPY] Failed:', err);
        showNotification('Copy failed', 'error');
    });
}

function showNotification(message, type = 'info') {
    console.log(`[NOTIFICATION] ${type.toUpperCase()}: ${message}`);
    // Could be enhanced with a toast notification library
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

console.log('[SCRIPT] script.js loaded successfully');
