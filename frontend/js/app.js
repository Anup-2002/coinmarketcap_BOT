// Configuration: Auto-detect Render (same origin) vs Local Dev
const isLocal = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
const API_BASE_URL = isLocal ? 'http://localhost:8000' : '';

// DOM Elements
const elements = {
    badgeStatus: document.getElementById('backend-status-badge'),
    statLogin: document.getElementById('stat-login'),
    statTotal: document.getElementById('stat-total'),
    statRemaining: document.getElementById('stat-remaining'),
    statGenerated: document.getElementById('stat-generated'),
    statPosted: document.getElementById('stat-posted'),
    statCurrentCoin: document.getElementById('stat-current-coin'),
    progressBar: document.getElementById('progress-bar'),
    progressText: document.getElementById('progress-text'),
    logContainer: document.getElementById('log-container'),
    actionButtons: document.querySelectorAll('.action-btn')
};


// Logging Utility
function addLog(message, type = 'info') {
    const time = new Date().toLocaleTimeString();
    const entry = document.createElement('div');
    entry.className = `log-entry log-${type}`;
    entry.innerHTML = `<span class="log-time">[${time}]</span> ${message}`;
    
    elements.logContainer.appendChild(entry);
    elements.logContainer.scrollTop = elements.logContainer.scrollHeight;
}

function clearLogs() {
    elements.logContainer.innerHTML = '';
}

// UI State Management
function setButtonsState(disabled) {
    elements.actionButtons.forEach(btn => {
        btn.disabled = disabled;
        if (disabled) {
            btn.classList.add('opacity-50');
        } else {
            btn.classList.remove('opacity-50');
        }
    });
}

function updateProgress(posted, total) {
    if (total === 0) return;
    const percentage = Math.round((posted / total) * 100);
    elements.progressBar.style.width = `${percentage}%`;
    elements.progressText.textContent = `${percentage}% (${posted}/${total})`;
}


// Core API Wrapper
async function apiCall(endpoint, method = "GET", body = null) {

    setButtonsState(true);

    try {

        const options = {
            method
        };

        if (body) {

            options.headers = {
                "Content-Type": "application/json"
            };

            options.body = JSON.stringify(body);

        }

        const response = await fetch(
            `${API_BASE_URL}${endpoint}`,
            options
        );
        const text = await response.text();

        let data;


        try {

            data = JSON.parse(text);

        }

        catch {

            throw new Error(
                `Backend returned invalid JSON:\n${text}`
            );

        }

        if (!response.ok) {

            throw new Error(
                data.message ||
                response.statusText
            );

        }

        // Optional status badge update (depends on backend response shape)
        if (typeof data?.status === 'string') {
            if (data.status === 'Running') {
                elements.badgeStatus.textContent = 'Running';
                elements.badgeStatus.className = 'badge bg-success';
            } else {
                elements.badgeStatus.textContent = 'Idle';
                elements.badgeStatus.className = 'badge bg-secondary';
            }
        }

        return data;



    }

    catch(error){

        addLog(
            error.message,
            "error"
        );

    }

    finally{

        setButtonsState(false);

    }

}

// Feature Functions
async function refreshStatus() {
    try {
        const res = await fetch(
            `${API_BASE_URL}/status`
        );

        if(!res.ok){
            throw new Error(`Status ${res.status}`);
        }

        const data = await res.json();

        document.getElementById("stat-total").innerText = data.total;
        document.getElementById("stat-posted").innerText = data.posted;
        document.getElementById("stat-remaining").innerText = data.remaining;
        document.getElementById("stat-current-coin").innerText = data.current_coin;
        document.getElementById("stat-login").innerText = data.login;


    } catch (err) {
        console.error("Status fetch failed:", err);
    }
}
async function checkLogin() {
    addLog('Initiating login check...', 'info');
    try {
        const data = await apiCall('/check-login', 'POST');
        elements.statLogin.textContent = data.status || 'Success';
        elements.statLogin.classList.add('text-success');
        addLog(JSON.stringify(data), 'success');
    } catch (error) {
        elements.statLogin.textContent = 'Failed';
        elements.statLogin.classList.add('text-danger');
    }
}

async function fullFlow() {
    addLog('Starting Fetch + Generate flow. This may take a while...', 'info');
    try {
        const data = await apiCall('/full-flow', 'POST');
        addLog(`Generation complete: ${JSON.stringify(data)}`, 'success');

        refreshStatus();
        // Start/continue polling for updated stats
        setInterval(refreshStatus, 5000);
    } catch (error) {
        addLog('Fetch + Generate failed.', 'error');
    }
}


async function startPosting() {
    addLog('Starting posting sequence...', 'info');
    try {
        const data = await apiCall('/post-chat', 'POST');
        addLog(`Posting complete/paused: ${JSON.stringify(data)}`, 'success');
        refreshStatus();
    } catch (error) {
        addLog('Posting sequence encountered an error.', 'error');
    }
}

async function resumePosting() {
    addLog('Resuming posting sequence...', 'info');
    try {
        const data = await apiCall('/post-chat', 'POST');
        addLog(`Resume complete: ${JSON.stringify(data)}`, 'success');
        refreshStatus();
    } catch (error) {
        addLog('Failed to resume posting.', 'error');
    }
}

// Initial Load
document.addEventListener('DOMContentLoaded', () => {
    refreshStatus();
});
