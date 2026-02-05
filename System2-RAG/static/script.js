/**
 * System 2 RAG - Frontend JavaScript
 * Handles API communication with intelligent environment detection
 */

// API Base URL Detection
// Automatically determines the correct API endpoint based on environment
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
    if (host.includes('azurecontainerapps.io') || host.includes('rag-system2')) {
        const url = '/api';  // Same-origin relative path
        console.log('[API] Azure environment detected, using relative path:', url);
        return url;
    }
    
    // Fallback for other domains
    const url = `${protocol}//${host}/api`;
    console.log('[API] Generic environment, using:', url);
    return url;
}

const API_BASE_URL = getAPIBaseURL();
console.log('[APP] API Base URL configured:', API_BASE_URL);

// Tab switching functionality
function switchTab(tabName) {
    console.log('[TAB] Switching to tab:', tabName);
    
    // Hide all tabs
    const tabs = document.querySelectorAll('.tab-content');
    tabs.forEach(tab => tab.classList.remove('active'));
    
    // Remove active class from all buttons
    const buttons = document.querySelectorAll('.tab-button');
    buttons.forEach(btn => btn.classList.remove('active'));
    
    // Show selected tab
    const selectedTab = document.getElementById(tabName);
    if (selectedTab) {
        selectedTab.classList.add('active');
    }
    
    // Set active button
    event.target.classList.add('active');
}

// Tab button event listeners
document.addEventListener('DOMContentLoaded', function() {
    console.log('[APP] Initializing application...');
    
    const tabButtons = document.querySelectorAll('.tab-button');
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const tabName = this.getAttribute('data-tab');
            switchTab(tabName);
        });
    });
    
    // Initialize forms
    initializeForms();
    console.log('[APP] Application initialized');
});

// Initialize form handlers
function initializeForms() {
    const pocForm = document.getElementById('pocForm');
    if (pocForm) {
        pocForm.addEventListener('submit', handlePOCGeneration);
    }
    
    const searchForm = document.getElementById('searchForm');
    if (searchForm) {
        searchForm.addEventListener('submit', handleSearch);
    }
}

// Make API request with error handling
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
            throw new Error(errorData.error || `HTTP ${response.status}`);
        }
        
        const responseData = await response.json();
        console.log('[API] Response data received:', responseData);
        return responseData;
        
    } catch (error) {
        console.error('[API] Request failed:', error.message);
        throw error;
    }
}

// Handle POC Generation
async function handlePOCGeneration(event) {
    event.preventDefault();
    console.log('[POC] Generating POC...');
    
    const solutionArea = document.getElementById('solutionArea').value;
    const pocTitle = document.getElementById('pocTitle').value;
    const pocQuery = document.getElementById('pocQuery').value;
    const topResults = document.getElementById('topResults').value;
    
    const errorDiv = document.getElementById('pocError');
    const resultDiv = document.getElementById('pocResult');
    
    // Hide previous messages
    errorDiv.style.display = 'none';
    resultDiv.style.display = 'none';
    
    try {
        const payload = {
            solution_area: solutionArea,
            poc_title: pocTitle,
            query: pocQuery,
            top_results: parseInt(topResults)
        };
        
        const response = await makeRequest(`${API_BASE_URL}/rag/generate-poc`, 'POST', payload);
        
        console.log('[POC] Successfully generated:', response.poc_id);
        
        // Display result
        const outputDiv = document.getElementById('pocOutput');
        outputDiv.textContent = JSON.stringify(response, null, 2);
        resultDiv.style.display = 'block';
        
    } catch (error) {
        console.error('[POC] Generation failed:', error);
        const errorMsg = document.getElementById('pocErrorMsg');
        errorMsg.textContent = error.message || 'Failed to generate POC. Please check the console for details.';
        errorDiv.style.display = 'block';
    }
}

// Handle Search
async function handleSearch(event) {
    event.preventDefault();
    console.log('[SEARCH] Executing search...');
    
    const searchQuery = document.getElementById('searchQuery').value;
    const topK = document.getElementById('topK').value;
    const includeSynthesis = document.getElementById('includeSynthesis').checked;
    
    const errorDiv = document.getElementById('searchError');
    const resultDiv = document.getElementById('searchResult');
    
    // Hide previous messages
    errorDiv.style.display = 'none';
    resultDiv.style.display = 'none';
    
    try {
        const payload = {
            query: searchQuery,
            top_k: parseInt(topK),
            include_synthesis: includeSynthesis
        };
        
        const response = await makeRequest(`${API_BASE_URL}/rag/search`, 'POST', payload);
        
        console.log('[SEARCH] Found results:', response.count);
        
        // Display results
        const outputDiv = document.getElementById('searchOutput');
        if (response.results && response.results.length > 0) {
            let html = '<div class="results-list">';
            response.results.forEach((result, index) => {
                html += `
                    <div class="result-item">
                        <h4>${index + 1}. ${result.title}</h4>
                        <p><strong>Area:</strong> ${result.area}</p>
                        <p><strong>Description:</strong> ${result.description}</p>
                        <p><strong>Relevance:</strong> ${(result.relevance_score * 100).toFixed(1)}%</p>
                    </div>
                `;
            });
            html += '</div>';
            outputDiv.innerHTML = html;
        } else {
            outputDiv.innerHTML = '<p>No results found for your search.</p>';
        }
        
        resultDiv.style.display = 'block';
        
    } catch (error) {
        console.error('[SEARCH] Search failed:', error);
        const errorMsg = document.getElementById('searchErrorMsg');
        errorMsg.textContent = error.message || 'Search failed. Please try again.';
        errorDiv.style.display = 'block';
    }
}

// Load POC History
async function loadHistory() {
    console.log('[HISTORY] Loading POC history...');
    
    try {
        const response = await makeRequest(`${API_BASE_URL}/rag/history`, 'GET');
        
        console.log('[HISTORY] Loaded:', response.count, 'POCs');
        
        const resultDiv = document.getElementById('historyResult');
        const emptyDiv = document.getElementById('historyEmpty');
        const outputDiv = document.getElementById('historyOutput');
        
        if (response.pocs && response.pocs.length > 0) {
            let html = '<div class="history-list">';
            response.pocs.forEach((poc, index) => {
                html += `
                    <div class="history-item">
                        <h4>${index + 1}. ${poc.poc_title}</h4>
                        <p><strong>ID:</strong> ${poc.poc_id}</p>
                        <p><strong>Area:</strong> ${poc.solution_area}</p>
                        <p><strong>Generated:</strong> ${new Date(poc.timestamp).toLocaleString()}</p>
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
        console.error('[HISTORY] Failed to load history:', error);
        const emptyDiv = document.getElementById('historyEmpty');
        emptyDiv.innerHTML = `<p style="color: red;">Error loading history: ${error.message}</p>`;
    }
}

// Check System Status
async function checkSystemStatus() {
    console.log('[STATUS] Checking system status...');
    
    try {
        const response = await makeRequest(`${API_BASE_URL.replace('/api', '')}/health`, 'GET');
        
        console.log('[STATUS] System healthy:', response.status);
        
        const resultDiv = document.getElementById('statusResult');
        const outputDiv = document.getElementById('statusOutput');
        
        outputDiv.textContent = JSON.stringify(response, null, 2);
        resultDiv.style.display = 'block';
        
        // Update system info table
        document.getElementById('apiEndpoint').textContent = API_BASE_URL;
        document.getElementById('environment').textContent = window.location.hostname.includes('azurecontainerapps.io') ? 'Azure Cloud' : 'Local Development';
        document.getElementById('healthStatus').textContent = '✅ Healthy';
        document.getElementById('healthStatus').style.color = 'green';
        
    } catch (error) {
        console.error('[STATUS] Status check failed:', error);
        document.getElementById('healthStatus').textContent = '❌ Unhealthy';
        document.getElementById('healthStatus').style.color = 'red';
    }
}

// Download POC
function downloadPOC() {
    console.log('[DOWNLOAD] Preparing POC download...');
    
    const pocOutput = document.getElementById('pocOutput').textContent;
    const blob = new Blob([pocOutput], { type: 'application/json' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `poc-${Date.now()}.json`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
    
    console.log('[DOWNLOAD] POC file downloaded');
}

// Log when script loads
console.log('[SCRIPT] script.js loaded successfully');
console.log('[CONFIG] Environment detection ready');
console.log('[CONFIG] API URL:', API_BASE_URL);
