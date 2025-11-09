/**
 * Smart402 Demo Functionality
 * Handles contract processing demonstration
 */

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('contractForm');
    if (!form) return;

    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        // Get form data
        const contract = {
            id: 'demo_' + Date.now(),
            type: document.getElementById('contractType').value,
            amount: parseFloat(document.getElementById('contractAmount').value),
            parties: document.getElementById('contractParties').value.split(',').map(p => p.trim()),
            terms: document.getElementById('contractTerms').value,
            target_query: 'smart contract payment'
        };

        // Process contract through pipeline
        await processContractPipeline(contract);
    });
});

/**
 * Process contract through all stages
 */
async function processContractPipeline(contract) {
    const stages = ['aeo', 'llmo', 'scc', 'x402'];

    for (const stage of stages) {
        await processStage(stage, contract);
        await sleep(800); // Delay for visual effect
    }
}

/**
 * Process individual stage
 */
async function processStage(stageName, contract) {
    const stageEl = document.querySelector(`[data-stage="${stageName}"]`);
    const statusEl = document.getElementById(`status-${stageName}`);
    const contentEl = document.getElementById(`content-${stageName}`);

    // Set processing state
    stageEl.classList.add('active');
    statusEl.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';

    // Simulate processing
    await sleep(1500);

    // Generate results based on stage
    const result = generateStageResult(stageName, contract);

    // Update UI
    stageEl.classList.remove('active');
    stageEl.classList.add('success');
    statusEl.innerHTML = '<i class="fas fa-check-circle" style="color: var(--success)"></i>';
    contentEl.innerHTML = result;
    contentEl.style.display = 'block';
}

/**
 * Generate stage-specific results
 */
function generateStageResult(stage, contract) {
    switch (stage) {
        case 'aeo':
            const aeoScore = (Math.random() * 0.3 + 0.7).toFixed(3);
            return `
                <div class="result-item">
                    <strong>AEO Score:</strong> ${aeoScore}
                </div>
                <div class="result-item">
                    <strong>Semantic Relevance:</strong> ${(Math.random() * 0.2 + 0.8).toFixed(3)}
                </div>
                <div class="result-item">
                    <strong>Content Freshness:</strong> ${(Math.random() * 0.2 + 0.75).toFixed(3)}
                </div>
                <div class="result-item">
                    <strong>Cross-Platform Score:</strong> ${(Math.random() * 0.3 + 0.65).toFixed(3)}
                </div>
                <div class="result-success">
                    ✓ Contract optimized for AI discovery
                </div>
            `;

        case 'llmo':
            const understandingScore = (Math.random() * 0.2 + 0.75).toFixed(3);
            return `
                <div class="result-item">
                    <strong>Understanding Score:</strong> ${understandingScore}
                </div>
                <div class="result-item">
                    <strong>Perplexity:</strong> ${(Math.random() * 20 + 30).toFixed(2)}
                </div>
                <div class="result-item">
                    <strong>Semantic Components:</strong>
                    <ul style="margin-left: 20px; margin-top: 8px;">
                        <li>Parties: ${contract.parties.length}</li>
                        <li>Obligations: ${Math.floor(Math.random() * 3 + 2)}</li>
                        <li>Conditions: ${Math.floor(Math.random() * 2 + 1)}</li>
                    </ul>
                </div>
                <div class="result-success">
                    ✓ Contract structure parsed and encoded
                </div>
            `;

        case 'scc':
            const gasEstimate = Math.floor(Math.random() * 100000 + 50000);
            return `
                <div class="result-item">
                    <strong>Compilation Status:</strong> Success
                </div>
                <div class="result-item">
                    <strong>Gas Estimate:</strong> ${gasEstimate.toLocaleString()}
                </div>
                <div class="result-item">
                    <strong>Bytecode:</strong>
                    <code style="font-size: 0.75rem; color: var(--accent);">
                        0x60806040523480156100105760...
                    </code>
                </div>
                <div class="result-item">
                    <strong>Verification:</strong> Passed (3/3 properties)
                </div>
                <div class="result-item">
                    <strong>Security Score:</strong> ${(Math.random() * 0.15 + 0.85).toFixed(3)}
                </div>
                <div class="result-success">
                    ✓ Smart contract compiled and verified
                </div>
            `;

        case 'x402':
            const txHash = '0x' + Array.from({length: 64}, () =>
                Math.floor(Math.random() * 16).toString(16)).join('');
            return `
                <div class="result-item">
                    <strong>Execution Status:</strong> Success
                </div>
                <div class="result-item">
                    <strong>Transaction Hash:</strong><br>
                    <code style="font-size: 0.75rem; color: var(--success); word-break: break-all;">
                        ${txHash}
                    </code>
                </div>
                <div class="result-item">
                    <strong>Amount Transferred:</strong> ${Smart402.utils.formatCurrency(contract.amount)}
                </div>
                <div class="result-item">
                    <strong>Gas Used:</strong> ${Math.floor(Math.random() * 50000 + 71000).toLocaleString()}
                </div>
                <div class="result-item">
                    <strong>Consensus Votes:</strong> ${Math.floor(Math.random() * 2 + 5)}/7
                </div>
                <div class="result-item">
                    <strong>Execution Time:</strong> ${(Math.random() * 1.5 + 0.5).toFixed(3)}s
                </div>
                <div class="result-success">
                    ✓ Payment executed with Byzantine consensus
                </div>
            `;

        default:
            return '';
    }
}

/**
 * Utility: Sleep function
 */
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Add CSS for result items
 */
const style = document.createElement('style');
style.textContent = `
    .result-item {
        padding: 8px 0;
        color: var(--text-secondary);
        border-bottom: 1px solid var(--border);
    }

    .result-item:last-of-type {
        border-bottom: none;
    }

    .result-item strong {
        color: var(--text-primary);
    }

    .result-success {
        margin-top: 12px;
        padding: 12px;
        background: rgba(67, 233, 123, 0.1);
        border-left: 3px solid var(--success);
        border-radius: 4px;
        color: var(--success);
    }
`;
document.head.appendChild(style);
