/**
 * Smart402 Dashboard Application
 * Main JavaScript application for controlling and monitoring the Smart402 system
 */

class Smart402Dashboard {
    constructor() {
        this.isRunning = false;
        this.updateInterval = null;
        this.apiBaseUrl = '/api';

        // Initialize DOM elements
        this.elements = {
            startBtn: document.getElementById('startBtn'),
            stopBtn: document.getElementById('stopBtn'),
            resetBtn: document.getElementById('resetBtn'),
            clearLogBtn: document.getElementById('clearLogBtn'),
            duration: document.getElementById('duration'),
            status: document.getElementById('status'),
            activityLog: document.getElementById('activityLog'),
            autoScroll: document.getElementById('autoScroll'),

            // Stats elements
            currentState: document.getElementById('currentState'),
            transitions: document.getElementById('transitions'),
            successRate: document.getElementById('successRate'),
            totalContracts: document.getElementById('totalContracts'),
            registrySize: document.getElementById('registrySize'),
            bestFitness: document.getElementById('bestFitness'),
            systemStatus: document.getElementById('systemStatus'),

            // Component status elements
            aeoStatus: document.getElementById('aeo-status'),
            aeoText: document.getElementById('aeo-text'),
            llmoStatus: document.getElementById('llmo-status'),
            llmoText: document.getElementById('llmo-text'),
            sccStatus: document.getElementById('scc-status'),
            sccText: document.getElementById('scc-text'),
            x402Status: document.getElementById('x402-status'),
            x402Text: document.getElementById('x402-text')
        };

        this.initializeEventListeners();
        this.logMessage('System initialized and ready', 'info');
    }

    /**
     * Initialize event listeners
     */
    initializeEventListeners() {
        this.elements.startBtn.addEventListener('click', () => this.startOrchestration());
        this.elements.stopBtn.addEventListener('click', () => this.stopOrchestration());
        this.elements.resetBtn.addEventListener('click', () => this.resetSystem());
        this.elements.clearLogBtn.addEventListener('click', () => this.clearLog());
    }

    /**
     * Start the orchestration
     */
    async startOrchestration() {
        const duration = parseInt(this.elements.duration.value);

        if (duration < 1) {
            this.showStatus('Please enter a valid duration (minimum 1 second)', 'error');
            return;
        }

        this.logMessage(`Starting orchestration for ${duration} seconds...`, 'info');
        this.showStatus(`Starting orchestration for ${duration} seconds...`, 'info');

        try {
            const response = await fetch(`${this.apiBaseUrl}/start`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ duration: duration })
            });

            const data = await response.json();

            if (data.success) {
                this.isRunning = true;
                this.elements.startBtn.disabled = true;
                this.elements.stopBtn.disabled = false;
                this.elements.duration.disabled = true;
                this.showStatus('Orchestration started successfully', 'success');
                this.logMessage('Orchestration started', 'success');

                // Start polling for updates
                this.startUpdates();

                // Activate all components
                this.setComponentStatus('aeo', 'active', 'Processing');
                this.setComponentStatus('llmo', 'active', 'Processing');
                this.setComponentStatus('scc', 'active', 'Processing');
                this.setComponentStatus('x402', 'active', 'Processing');

                this.elements.systemStatus.textContent = 'Running';
                this.elements.systemStatus.style.color = 'var(--success-color)';
            } else {
                throw new Error(data.error || 'Failed to start orchestration');
            }
        } catch (error) {
            this.showStatus(`Error: ${error.message}`, 'error');
            this.logMessage(`Error starting orchestration: ${error.message}`, 'error');
        }
    }

    /**
     * Stop the orchestration
     */
    async stopOrchestration() {
        this.logMessage('Stopping orchestration...', 'warning');

        try {
            const response = await fetch(`${this.apiBaseUrl}/stop`, {
                method: 'POST'
            });

            const data = await response.json();

            if (data.success) {
                this.isRunning = false;
                this.stopUpdates();
                this.elements.startBtn.disabled = false;
                this.elements.stopBtn.disabled = true;
                this.elements.duration.disabled = false;
                this.showStatus('Orchestration stopped', 'info');
                this.logMessage('Orchestration stopped by user', 'warning');

                // Deactivate all components
                this.setComponentStatus('aeo', 'ready', 'Ready');
                this.setComponentStatus('llmo', 'ready', 'Ready');
                this.setComponentStatus('scc', 'ready', 'Ready');
                this.setComponentStatus('x402', 'ready', 'Ready');

                this.elements.systemStatus.textContent = 'Stopped';
                this.elements.systemStatus.style.color = 'var(--warning-color)';
            }
        } catch (error) {
            this.showStatus(`Error: ${error.message}`, 'error');
            this.logMessage(`Error stopping orchestration: ${error.message}`, 'error');
        }
    }

    /**
     * Reset the system
     */
    async resetSystem() {
        this.logMessage('Resetting system...', 'info');

        try {
            const response = await fetch(`${this.apiBaseUrl}/reset`, {
                method: 'POST'
            });

            const data = await response.json();

            if (data.success) {
                this.showStatus('System reset successfully', 'success');
                this.logMessage('System reset complete', 'success');

                // Reset all displays
                this.elements.currentState.textContent = '-';
                this.elements.transitions.textContent = '0';
                this.elements.successRate.textContent = '0%';
                this.elements.totalContracts.textContent = '0';
                this.elements.registrySize.textContent = '0';
                this.elements.bestFitness.textContent = '0.0000';
                this.elements.systemStatus.textContent = 'Idle';
                this.elements.systemStatus.style.color = 'var(--text-primary)';

                // Reset all state nodes
                document.querySelectorAll('.state-node').forEach(node => {
                    node.classList.remove('active');
                });

                // Reset component status
                this.setComponentStatus('aeo', 'ready', 'Ready');
                this.setComponentStatus('llmo', 'ready', 'Ready');
                this.setComponentStatus('scc', 'ready', 'Ready');
                this.setComponentStatus('x402', 'ready', 'Ready');
            }
        } catch (error) {
            this.showStatus(`Error: ${error.message}`, 'error');
            this.logMessage(`Error resetting system: ${error.message}`, 'error');
        }
    }

    /**
     * Start periodic updates
     */
    startUpdates() {
        this.updateInterval = setInterval(() => {
            this.fetchStatistics();
        }, 1000); // Update every second
    }

    /**
     * Stop periodic updates
     */
    stopUpdates() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
    }

    /**
     * Fetch statistics from the API
     */
    async fetchStatistics() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/stats`);
            const data = await response.json();

            if (data.success) {
                this.updateStatistics(data.stats);

                // Check if orchestration is complete
                if (data.stats.is_complete && this.isRunning) {
                    this.logMessage('Orchestration completed', 'success');
                    this.showStatus('Orchestration completed successfully', 'success');
                    this.isRunning = false;
                    this.stopUpdates();
                    this.elements.startBtn.disabled = false;
                    this.elements.stopBtn.disabled = true;
                    this.elements.duration.disabled = false;

                    this.elements.systemStatus.textContent = 'Complete';
                    this.elements.systemStatus.style.color = 'var(--success-color)';

                    // Deactivate all components
                    this.setComponentStatus('aeo', 'complete', 'Complete');
                    this.setComponentStatus('llmo', 'complete', 'Complete');
                    this.setComponentStatus('scc', 'complete', 'Complete');
                    this.setComponentStatus('x402', 'complete', 'Complete');
                }
            }
        } catch (error) {
            console.error('Error fetching statistics:', error);
            // Don't show error message for every failed poll
        }
    }

    /**
     * Update statistics display
     */
    updateStatistics(stats) {
        // Update state machine stats
        if (stats.state_machine) {
            this.elements.currentState.textContent = stats.state_machine.current_state || '-';
            this.elements.transitions.textContent = stats.state_machine.total_transitions || 0;
            this.elements.successRate.textContent =
                ((stats.state_machine.success_rate || 0) * 100).toFixed(1) + '%';

            // Highlight current state
            document.querySelectorAll('.state-node').forEach(node => {
                node.classList.remove('active');
            });

            const currentStateNode = document.querySelector(
                `[data-state="${stats.state_machine.current_state}"]`
            );
            if (currentStateNode) {
                currentStateNode.classList.add('active');
            }
        }

        // Update contract stats
        this.elements.totalContracts.textContent = stats.total_contracts || 0;
        this.elements.registrySize.textContent = stats.registry_size || 0;

        // Update optimization stats
        this.elements.bestFitness.textContent = (stats.best_fitness || 0).toFixed(4);
    }

    /**
     * Set component status
     */
    setComponentStatus(component, status, text) {
        const statusIndicator = this.elements[`${component}Status`];
        const statusText = this.elements[`${component}Text`];
        const card = document.querySelector(`[data-component="${component}"]`);

        // Update indicator
        switch (status) {
            case 'ready':
                statusIndicator.textContent = '⚪';
                card.classList.remove('active');
                break;
            case 'active':
                statusIndicator.textContent = '🟢';
                card.classList.add('active');
                break;
            case 'complete':
                statusIndicator.textContent = '✅';
                card.classList.remove('active');
                break;
            case 'error':
                statusIndicator.textContent = '🔴';
                card.classList.remove('active');
                break;
        }

        statusText.textContent = text;
    }

    /**
     * Show status message
     */
    showStatus(message, type) {
        this.elements.status.textContent = message;
        this.elements.status.className = `status-message show ${type}`;

        // Auto-hide after 5 seconds
        setTimeout(() => {
            this.elements.status.classList.remove('show');
        }, 5000);
    }

    /**
     * Log message to activity log
     */
    logMessage(message, type = 'info') {
        const timestamp = new Date().toLocaleTimeString();
        const logEntry = document.createElement('div');
        logEntry.className = `log-entry ${type} slide-in`;
        logEntry.innerHTML = `
            <span class="log-timestamp">[${timestamp}]</span>
            <span class="log-message">${message}</span>
        `;

        this.elements.activityLog.appendChild(logEntry);

        // Auto-scroll if enabled
        if (this.elements.autoScroll.checked) {
            this.elements.activityLog.scrollTop = this.elements.activityLog.scrollHeight;
        }

        // Limit log entries to 100
        while (this.elements.activityLog.children.length > 100) {
            this.elements.activityLog.removeChild(this.elements.activityLog.firstChild);
        }
    }

    /**
     * Clear activity log
     */
    clearLog() {
        this.elements.activityLog.innerHTML = '';
        this.logMessage('Activity log cleared', 'info');
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new Smart402Dashboard();
    console.log('Smart402 Dashboard initialized');
});
