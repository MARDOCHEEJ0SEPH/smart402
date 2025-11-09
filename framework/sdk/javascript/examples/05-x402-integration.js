/**
 * Advanced Example: X402 Protocol Integration
 *
 * This example demonstrates:
 * - X402 HTTP header generation
 * - Machine-to-machine payment flow
 * - API endpoint integration
 * - Webhook handling
 * - Payment verification
 */

const { Smart402 } = require('../src/core/Smart402');
const chalk = require('chalk');
const axios = require('axios');

async function demonstrateX402Integration() {
  console.log(chalk.blue.bold('\n🌐 X402 Protocol Integration Example\n'));

  // Create API-integrated contract
  const contract = await Smart402.create({
    type: 'api-usage-payment',
    parties: [
      'api-provider@service.com',
      'api-consumer@client.com'
    ],
    payment: {
      amount: 0.10, // $0.10 per API call
      currency: 'USD',
      token: 'USDC',
      blockchain: 'polygon',
      frequency: 'per-request',
      paymentModel: 'pay-per-use'
    },
    apiConfig: {
      endpoint: 'https://api.service.com/v1/process',
      authentication: 'x402-headers',
      rateLimits: {
        requestsPerMinute: 60,
        requestsPerDay: 10000
      },
      pricing: {
        basePrice: 0.10,
        tierPricing: [
          { threshold: 1000, pricePerRequest: 0.08 },
          { threshold: 10000, pricePerRequest: 0.05 },
          { threshold: 100000, pricePerRequest: 0.03 }
        ]
      }
    },
    conditions: [
      {
        id: 'api_available',
        type: 'uptime',
        description: 'API must be available (200 response)',
        threshold: 0.999
      },
      {
        id: 'response_time',
        type: 'performance',
        description: 'Response time < 200ms',
        threshold: 200,
        unit: 'ms'
      },
      {
        id: 'rate_limit_check',
        type: 'validation',
        description: 'Request within rate limits',
        checkMethod: 'pre-request'
      }
    ],
    metadata: {
      title: 'Pay-Per-Use API Service',
      description: 'X402-enabled API with automatic per-request payments',
      category: 'api-monetization',
      tags: ['x402', 'api', 'pay-per-use', 'micropayments']
    }
  });

  console.log(chalk.green('✓ X402-enabled contract created'));
  console.log(chalk.cyan('  Contract ID:'), contract.ucl.contract_id);
  console.log(chalk.cyan('  Payment Model:'), 'Pay-per-use');
  console.log(chalk.cyan('  Base Price:'), `$${contract.ucl.payment.amount} per request`);
  console.log();

  // Deploy contract
  console.log(chalk.yellow('🚀 Deploying X402 contract...\n'));
  const deployResult = await contract.deploy({
    network: 'polygon',
    x402Enabled: true
  });

  console.log(chalk.green('✓ Contract deployed'));
  console.log(chalk.cyan('  Address:'), deployResult.address);
  console.log(chalk.cyan('  X402 Endpoint:'), deployResult.x402Endpoint || 'https://x402.smart402.io/verify');
  console.log();

  // Generate X402 headers
  console.log(chalk.yellow('📋 Generating X402 Headers:\n'));
  const headers = contract.generateX402Headers(true);

  console.log(chalk.cyan('Standard X402 Headers:'));
  Object.entries(headers).forEach(([key, value]) => {
    if (key.startsWith('X402-')) {
      console.log(chalk.gray(`  ${key}: ${value}`));
    }
  });
  console.log();

  // Simulate API requests with X402
  console.log(chalk.yellow('🔄 Simulating X402 Payment Flow:\n'));
  console.log(chalk.blue('─'.repeat(60)));

  await simulateX402Request(contract, 1);
  await simulateX402Request(contract, 2);
  await simulateX402Request(contract, 3);

  console.log(chalk.blue('─'.repeat(60)));
  console.log();

  // Demonstrate webhook handling
  console.log(chalk.yellow('🔔 Webhook Event Handling:\n'));
  await demonstrateWebhooks(contract);
  console.log();

  // Show payment summary
  console.log(chalk.yellow('💰 Payment Summary:\n'));
  const summary = {
    totalRequests: 3,
    pricePerRequest: contract.ucl.payment.amount,
    totalAmount: 3 * contract.ucl.payment.amount,
    currency: contract.ucl.payment.token
  };

  console.log(chalk.cyan('  Total API Requests:'), summary.totalRequests);
  console.log(chalk.cyan('  Price Per Request:'), `$${summary.pricePerRequest} ${summary.currency}`);
  console.log(chalk.cyan('  Total Amount:'), `$${summary.totalAmount.toFixed(2)} ${summary.currency}`);
  console.log();

  // Demonstrate batch settlement
  console.log(chalk.yellow('⚡ Batch Settlement (Gas Optimization):\n'));
  console.log(chalk.gray('Instead of 3 separate transactions, X402 can batch payments:'));
  console.log();

  const batchResult = await contract.executeBatchPayment({
    requests: [
      { requestId: 'req_1', amount: 0.10 },
      { requestId: 'req_2', amount: 0.10 },
      { requestId: 'req_3', amount: 0.10 }
    ]
  });

  console.log(chalk.green('✓ Batch payment executed'));
  console.log(chalk.cyan('  Transaction Hash:'), batchResult.transactionHash);
  console.log(chalk.cyan('  Total Amount:'), `$${batchResult.totalAmount} ${batchResult.token}`);
  console.log(chalk.cyan('  Requests Settled:'), batchResult.requestCount);
  console.log(chalk.cyan('  Gas Saved:'), `~${batchResult.gasSaved || '67'}%`);
  console.log();

  // X402 verification example
  console.log(chalk.yellow('🔐 X402 Signature Verification:\n'));
  const verificationResult = await verifyX402Signature(contract, headers);
  console.log(chalk.cyan('  Signature Valid:'), verificationResult.valid ? chalk.green('✓') : chalk.red('✗'));
  console.log(chalk.cyan('  Verified By:'), verificationResult.verifiedBy);
  console.log(chalk.cyan('  Timestamp:'), new Date(verificationResult.timestamp).toISOString());
  console.log();

  // Show X402 workflow diagram
  console.log(chalk.yellow('📊 X402 Request/Payment Workflow:\n'));
  console.log(chalk.gray(`
  Client                    Smart402                  API Provider
    │                          │                           │
    ├─(1) Generate X402────────>│                           │
    │     Headers with          │                           │
    │     signature             │                           │
    │                          │                           │
    ├─(2) HTTP Request─────────────────────────────────────>│
    │     + X402 Headers        │                           │
    │                          │                           │
    │                          │<─(3) Verify Signature─────┤
    │                          │     & Conditions          │
    │                          │                           │
    │                          ├─(4) Authorize Payment─────>│
    │                          │                           │
    │<─────────────────────────────(5) API Response────────┤
    │                          │     + X402-Payment-Receipt│
    │                          │                           │
    ├─(6) Settlement──────────>│                           │
    │     (on-chain)            │                           │
    │                          │                           │
    │                          ├─(7) Confirm & Release────>│
    │                          │                           │
  `));
  console.log();

  // Export X402 configuration
  console.log(chalk.yellow('💾 Exporting X402 Configuration:\n'));
  const fs = require('fs');
  const path = require('path');

  const x402Config = {
    contractId: contract.ucl.contract_id,
    endpoint: contract.ucl.apiConfig.endpoint,
    headers: headers,
    pricing: contract.ucl.apiConfig.pricing,
    rateLimits: contract.ucl.apiConfig.rateLimits,
    verificationEndpoint: 'https://x402.smart402.io/verify',
    webhooks: {
      paymentExecuted: 'https://api.client.com/webhooks/x402/payment',
      conditionFailed: 'https://api.client.com/webhooks/x402/failure'
    }
  };

  const outputPath = path.join(__dirname, 'output', 'x402-config.json');
  if (!fs.existsSync(path.join(__dirname, 'output'))) {
    fs.mkdirSync(path.join(__dirname, 'output'), { recursive: true });
  }
  fs.writeFileSync(outputPath, JSON.stringify(x402Config, null, 2));

  console.log(chalk.green('✓ X402 configuration exported to:'), outputPath);
  console.log();

  console.log(chalk.green.bold('✨ X402 Protocol integration demonstration complete!\n'));
  console.log(chalk.white('Key Benefits:'));
  console.log(chalk.gray('  • Automatic payments with every API call'));
  console.log(chalk.gray('  • No manual invoice/payment process'));
  console.log(chalk.gray('  • Built-in SLA enforcement'));
  console.log(chalk.gray('  • Gas-optimized batch settlements'));
  console.log(chalk.gray('  • Cryptographic payment verification'));
  console.log(chalk.gray('  • Machine-readable commercial terms\n'));

  return contract;
}

// Simulate X402 API request
async function simulateX402Request(contract, requestNumber) {
  console.log(chalk.magenta(`\n→ API Request #${requestNumber}:`));

  // Generate fresh headers with nonce
  const headers = contract.generateX402Headers(true);
  headers['X402-Request-ID'] = `req_${requestNumber}`;
  headers['X402-Nonce'] = Date.now().toString();

  console.log(chalk.gray(`  Request ID: ${headers['X402-Request-ID']}`));
  console.log(chalk.gray(`  Nonce: ${headers['X402-Nonce']}`));

  // Simulate API call
  await sleep(300);

  // Check conditions
  console.log(chalk.cyan('  Checking conditions...'));
  const conditionsCheck = await contract.checkConditions();

  if (conditionsCheck.allMet) {
    console.log(chalk.green('  ✓ Conditions met'));
    console.log(chalk.green('  ✓ API request processed'));
    console.log(chalk.green(`  ✓ Payment authorized: $${contract.ucl.payment.amount} ${contract.ucl.payment.token}`));
  } else {
    console.log(chalk.red('  ✗ Conditions failed'));
    console.log(chalk.red('  ✗ Request rejected'));
  }
}

// Demonstrate webhook events
async function demonstrateWebhooks(contract) {
  const webhookEvents = [
    {
      event: 'x402.payment.authorized',
      data: {
        contractId: contract.ucl.contract_id,
        requestId: 'req_1',
        amount: contract.ucl.payment.amount,
        token: contract.ucl.payment.token,
        timestamp: new Date().toISOString()
      }
    },
    {
      event: 'x402.payment.executed',
      data: {
        contractId: contract.ucl.contract_id,
        requestId: 'req_1',
        transactionHash: '0xabc123...',
        amount: contract.ucl.payment.amount,
        timestamp: new Date().toISOString()
      }
    },
    {
      event: 'x402.settlement.completed',
      data: {
        contractId: contract.ucl.contract_id,
        batchId: 'batch_1',
        requestCount: 3,
        totalAmount: 0.30,
        transactionHash: '0xdef456...',
        timestamp: new Date().toISOString()
      }
    }
  ];

  webhookEvents.forEach(webhook => {
    const emoji = webhook.event.includes('completed') ? '✅' : '📡';
    console.log(chalk.cyan(`  ${emoji} ${webhook.event}`));
    console.log(chalk.gray(`     ${JSON.stringify(webhook.data, null, 6).replace(/\n/g, '\n     ')}`));
    console.log();
  });
}

// Verify X402 signature
async function verifyX402Signature(contract, headers) {
  await sleep(200);

  return {
    valid: true,
    verifiedBy: 'Smart402 X402 Verifier',
    timestamp: Date.now(),
    signature: headers['X402-Signature'],
    nonce: headers['X402-Nonce']
  };
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// Run the example
if (require.main === module) {
  demonstrateX402Integration().catch(error => {
    console.error(chalk.red('\n❌ Error:'), error.message);
    console.error(error.stack);
    process.exit(1);
  });
}

module.exports = { demonstrateX402Integration };
