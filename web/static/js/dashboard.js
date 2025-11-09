/**
 * Smart402 Dashboard JavaScript
 * Handles real-time dashboard updates and visualizations
 */

// Dashboard state
const dashboardState = {
    charts: {},
    updateInterval: null,
    isUpdating: false
};

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    initDashboard();
    initNavigation();
    initCharts();
    startAutoUpdate();
});

/**
 * Initialize dashboard
 */
function initDashboard() {
    // Load initial data
    updateMetrics();
    updateContractsTable();

    // Setup refresh button
    const refreshBtn = document.getElementById('refreshBtn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', function() {
            this.querySelector('i').classList.add('fa-spin');
            updateMetrics();
            setTimeout(() => {
                this.querySelector('i').classList.remove('fa-spin');
            }, 1000);
        });
    }

    // Setup process contract button
    const processBtn = document.getElementById('processContractBtn');
    if (processBtn) {
        processBtn.addEventListener('click', function() {
            window.location.href = 'index.html#demo';
        });
    }
}

/**
 * Initialize navigation
 */
function initNavigation() {
    const navItems = document.querySelectorAll('.sidebar .nav-item');
    const sections = document.querySelectorAll('.main-content section');

    navItems.forEach(item => {
        item.addEventListener('click', function(e) {
            const href = this.getAttribute('href');

            // Only handle hash links
            if (href && href.startsWith('#')) {
                e.preventDefault();

                // Update active state
                navItems.forEach(i => i.classList.remove('active'));
                this.classList.add('active');

                // Show corresponding section
                const targetId = href.substring(1);
                sections.forEach(section => {
                    if (section.id === targetId) {
                        section.classList.remove('hidden');
                    } else {
                        section.classList.add('hidden');
                    }
                });
            }
        });
    });
}

/**
 * Update metrics
 */
async function updateMetrics() {
    try {
        // Simulate API call - in production, this would fetch real data
        const stats = await fetchSystemStats();

        // Update metric values
        document.getElementById('totalContracts').textContent = stats.totalContracts;
        document.getElementById('successRate').textContent = stats.successRate + '%';
        document.getElementById('avgTime').textContent = stats.avgTime + 's';
        document.getElementById('bestFitness').textContent = stats.bestFitness.toFixed(4);

        // Update progress bars
        updateProgressBar('discoveryRate', stats.discoveryRate);
        updateProgressBar('understandingRate', stats.understandingRate);
        updateProgressBar('compilationRate', stats.compilationRate);
        updateProgressBar('executionRate', stats.executionRate);

        // Update charts
        updateCharts(stats);

    } catch (error) {
        console.error('Failed to update metrics:', error);
    }
}

/**
 * Update progress bar
 */
function updateProgressBar(id, value) {
    const fillEl = document.getElementById(id);
    const textEl = document.getElementById(id + 'Text');

    if (fillEl && textEl) {
        const percentage = (value * 100).toFixed(1);
        fillEl.style.width = percentage + '%';
        textEl.textContent = percentage + '%';
    }
}

/**
 * Initialize charts
 */
function initCharts() {
    // Pipeline Chart
    const pipelineCtx = document.getElementById('pipelineChart');
    if (pipelineCtx) {
        dashboardState.charts.pipeline = new Chart(pipelineCtx, {
            type: 'funnel',
            data: {
                labels: ['Discovered', 'Understood', 'Compiled', 'Verified', 'Executed'],
                datasets: [{
                    label: 'Contract Pipeline',
                    data: [100, 92, 85, 83, 81],
                    backgroundColor: [
                        'rgba(102, 126, 234, 0.8)',
                        'rgba(240, 147, 251, 0.8)',
                        'rgba(79, 172, 254, 0.8)',
                        'rgba(67, 233, 123, 0.8)',
                        'rgba(254, 202, 87, 0.8)'
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }

    // Performance Chart
    const performanceCtx = document.getElementById('performanceChart');
    if (performanceCtx) {
        dashboardState.charts.performance = new Chart(performanceCtx, {
            type: 'line',
            data: {
                labels: generateTimeLabels(12),
                datasets: [
                    {
                        label: 'Success Rate',
                        data: generateRandomData(12, 85, 95),
                        borderColor: 'rgba(102, 126, 234, 1)',
                        backgroundColor: 'rgba(102, 126, 234, 0.1)',
                        tension: 0.4
                    },
                    {
                        label: 'Efficiency',
                        data: generateRandomData(12, 75, 90),
                        borderColor: 'rgba(67, 233, 123, 1)',
                        backgroundColor: 'rgba(67, 233, 123, 0.1)',
                        tension: 0.4
                    }
                ]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        labels: {
                            color: '#a0a0b8'
                        }
                    }
                },
                scales: {
                    x: {
                        grid: {
                            color: '#2a2a3e'
                        },
                        ticks: {
                            color: '#a0a0b8'
                        }
                    },
                    y: {
                        grid: {
                            color: '#2a2a3e'
                        },
                        ticks: {
                            color: '#a0a0b8'
                        }
                    }
                }
            }
        });
    }

    // Efficiency Chart
    const efficiencyCtx = document.getElementById('efficiencyChart');
    if (efficiencyCtx) {
        dashboardState.charts.efficiency = new Chart(efficiencyCtx, {
            type: 'radar',
            data: {
                labels: ['AEO', 'LLMO', 'SCC', 'X402', 'Overall'],
                datasets: [{
                    label: 'Component Efficiency',
                    data: [0.87, 0.92, 0.85, 0.89, 0.88],
                    borderColor: 'rgba(102, 126, 234, 1)',
                    backgroundColor: 'rgba(102, 126, 234, 0.2)',
                    pointBackgroundColor: 'rgba(102, 126, 234, 1)',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: 'rgba(102, 126, 234, 1)'
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        labels: {
                            color: '#a0a0b8'
                        }
                    }
                },
                scales: {
                    r: {
                        angleLines: {
                            color: '#2a2a3e'
                        },
                        grid: {
                            color: '#2a2a3e'
                        },
                        pointLabels: {
                            color: '#a0a0b8'
                        },
                        ticks: {
                            color: '#a0a0b8',
                            backdropColor: 'transparent'
                        }
                    }
                }
            }
        });
    }

    // State Chart
    const stateCtx = document.getElementById('stateChart');
    if (stateCtx) {
        dashboardState.charts.state = new Chart(stateCtx, {
            type: 'doughnut',
            data: {
                labels: ['Discovery', 'Understanding', 'Compilation', 'Verification', 'Execution', 'Settlement', 'Completed'],
                datasets: [{
                    data: [15, 12, 18, 10, 20, 10, 15],
                    backgroundColor: [
                        'rgba(102, 126, 234, 0.8)',
                        'rgba(118, 75, 162, 0.8)',
                        'rgba(240, 147, 251, 0.8)',
                        'rgba(79, 172, 254, 0.8)',
                        'rgba(67, 233, 123, 0.8)',
                        'rgba(254, 202, 87, 0.8)',
                        'rgba(56, 249, 215, 0.8)'
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: {
                            color: '#a0a0b8'
                        }
                    }
                }
            }
        });
    }

    // Network Chart
    const networkCtx = document.getElementById('networkChart');
    if (networkCtx) {
        dashboardState.charts.network = new Chart(networkCtx, {
            type: 'scatter',
            data: {
                datasets: [{
                    label: 'Network Value Growth',
                    data: generateNetworkData(20),
                    backgroundColor: 'rgba(102, 126, 234, 0.5)',
                    borderColor: 'rgba(102, 126, 234, 1)'
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        labels: {
                            color: '#a0a0b8'
                        }
                    }
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Number of Contracts (n)',
                            color: '#a0a0b8'
                        },
                        grid: {
                            color: '#2a2a3e'
                        },
                        ticks: {
                            color: '#a0a0b8'
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Network Value',
                            color: '#a0a0b8'
                        },
                        grid: {
                            color: '#2a2a3e'
                        },
                        ticks: {
                            color: '#a0a0b8'
                        }
                    }
                }
            }
        });
    }

    // Optimization Chart
    const optimizationCtx = document.getElementById('optimizationChart');
    if (optimizationCtx) {
        dashboardState.charts.optimization = new Chart(optimizationCtx, {
            type: 'line',
            data: {
                labels: Array.from({length: 100}, (_, i) => i),
                datasets: [{
                    label: 'Fitness Score',
                    data: generateOptimizationData(100),
                    borderColor: 'rgba(67, 233, 123, 1)',
                    backgroundColor: 'rgba(67, 233, 123, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        labels: {
                            color: '#a0a0b8'
                        }
                    }
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Iteration',
                            color: '#a0a0b8'
                        },
                        grid: {
                            color: '#2a2a3e'
                        },
                        ticks: {
                            color: '#a0a0b8'
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Fitness F(C)',
                            color: '#a0a0b8'
                        },
                        grid: {
                            color: '#2a2a3e'
                        },
                        ticks: {
                            color: '#a0a0b8'
                        }
                    }
                }
            }
        });
    }
}

/**
 * Update charts with new data
 */
function updateCharts(stats) {
    // Update pipeline chart
    if (dashboardState.charts.pipeline) {
        const pipeline = dashboardState.charts.pipeline;
        pipeline.data.datasets[0].data = [
            100,
            stats.understandingRate * 100,
            stats.compilationRate * 100,
            stats.verificationRate * 100,
            stats.executionRate * 100
        ];
        pipeline.update();
    }
}

/**
 * Update contracts table
 */
function updateContractsTable() {
    const tbody = document.getElementById('contractsTableBody');
    if (!tbody) return;

    // Generate sample data
    const contracts = generateSampleContracts(10);

    tbody.innerHTML = contracts.map(contract => `
        <tr>
            <td><code>${contract.id}</code></td>
            <td>${contract.type}</td>
            <td>${Smart402.utils.formatCurrency(contract.amount)}</td>
            <td><span class="status-badge ${contract.status}">${contract.status}</span></td>
            <td>${contract.aeoScore.toFixed(3)}</td>
            <td>${contract.understandingScore.toFixed(3)}</td>
            <td>${contract.gasEstimate.toLocaleString()}</td>
            <td>
                <button class="action-btn" onclick="viewContract('${contract.id}')">
                    <i class="fas fa-eye"></i> View
                </button>
            </td>
        </tr>
    `).join('');
}

/**
 * Generate sample contracts
 */
function generateSampleContracts(count) {
    const types = ['payment', 'service', 'escrow', 'multi-party'];
    const statuses = ['success', 'pending', 'error'];

    return Array.from({length: count}, (_, i) => ({
        id: `contract_${1000 + i}`,
        type: types[Math.floor(Math.random() * types.length)],
        amount: Math.random() * 50000 + 1000,
        status: statuses[Math.floor(Math.random() * statuses.length)],
        aeoScore: Math.random() * 0.3 + 0.7,
        understandingScore: Math.random() * 0.2 + 0.75,
        gasEstimate: Math.floor(Math.random() * 100000 + 50000)
    }));
}

/**
 * Fetch system stats (simulated)
 */
async function fetchSystemStats() {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 500));

    return {
        totalContracts: Math.floor(Math.random() * 500 + 1000),
        successRate: (Math.random() * 10 + 88).toFixed(1),
        avgTime: (Math.random() * 1 + 1.5).toFixed(2),
        bestFitness: Math.random() * 0.2 + 0.75,
        discoveryRate: Math.random() * 0.1 + 0.85,
        understandingRate: Math.random() * 0.1 + 0.88,
        compilationRate: Math.random() * 0.1 + 0.82,
        verificationRate: Math.random() * 0.05 + 0.93,
        executionRate: Math.random() * 0.08 + 0.90
    };
}

/**
 * Helper functions for chart data generation
 */
function generateTimeLabels(count) {
    const labels = [];
    for (let i = count - 1; i >= 0; i--) {
        labels.push(`${i}h ago`);
    }
    return labels;
}

function generateRandomData(count, min, max) {
    return Array.from({length: count}, () => Math.random() * (max - min) + min);
}

function generateNetworkData(count) {
    return Array.from({length: count}, (_, i) => ({
        x: i + 1,
        y: Math.pow(i + 1, 1.5) + Math.random() * 10
    }));
}

function generateOptimizationData(count) {
    const data = [];
    let value = 0.3;

    for (let i = 0; i < count; i++) {
        value += (0.7 - value) * 0.05 + (Math.random() - 0.5) * 0.02;
        data.push(value);
    }

    return data;
}

/**
 * Start auto-update
 */
function startAutoUpdate() {
    // Update every 10 seconds
    dashboardState.updateInterval = setInterval(() => {
        if (!dashboardState.isUpdating) {
            updateMetrics();
        }
    }, 10000);
}

/**
 * View contract details
 */
function viewContract(contractId) {
    alert(`Viewing contract: ${contractId}\n\nThis would open a detailed view in production.`);
}
