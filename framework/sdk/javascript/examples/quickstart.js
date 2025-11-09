/**
 * Smart402 Quick Start Example
 *
 * This example shows how to create, deploy, and monitor
 * a Smart402 contract in just a few lines of code.
 */

const { Smart402 } = require('@smart402/sdk');

async function main() {
  console.log('🚀 Smart402 Quick Start\n');

  // ============================================
  // 1. CREATE CONTRACT
  // ============================================
  console.log('1️⃣  Creating contract...');

  const contract = await Smart402.create({
    type: 'saas-subscription',
    parties: [
      'vendor@saas.com',
      'customer@company.com'
    ],
    payment: {
      amount: 99,
      frequency: 'monthly',
      token: 'USDC'
    },
    conditions: [
      {
        id: 'uptime_check',
        description: 'Service uptime must be >= 99%',
        source: 'monitoring_api',
        operator: 'gte',
        threshold: 0.99
      }
    ]
  });

  console.log('✅ Contract created!');
  console.log(`   ID: ${contract.id}`);
  console.log(`   Summary: ${contract.getSummary()}\n`);

  // ============================================
  // 2. DEPLOY CONTRACT
  // ============================================
  console.log('2️⃣  Deploying to Polygon...');

  const deployment = await contract.deploy({
    network: 'polygon'
  });

  console.log('✅ Deployed!');
  console.log(`   Address: ${deployment.address}`);
  console.log(`   Transaction: ${deployment.transactionHash}`);
  console.log(`   Block: ${deployment.blockNumber}`);
  console.log(`   View: ${contract.getURL()}\n`);

  // ============================================
  // 3. CHECK CONDITIONS
  // ============================================
  console.log('3️⃣  Checking conditions...');

  const conditionStatus = await contract.checkConditions();

  console.log(`   All met: ${conditionStatus.allMet}`);
  console.log('   Details:');
  for (const [id, met] of Object.entries(conditionStatus.conditions)) {
    console.log(`     ${met ? '✅' : '❌'} ${id}`);
  }
  console.log();

  // ============================================
  // 4. START MONITORING
  // ============================================
  console.log('4️⃣  Starting automatic monitoring...');

  await contract.startMonitoring({
    frequency: 'hourly',
    webhook: 'https://api.example.com/webhooks/payment'
  });

  console.log('✅ Monitoring active!');
  console.log('   Payments will execute automatically when conditions met.\n');

  // ============================================
  // 5. CONTRACT INFO
  // ============================================
  console.log('📋 Contract Information:\n');

  const terms = contract.getPaymentTerms();
  console.log(`   Amount: ${terms.amount} ${terms.token}`);
  console.log(`   Frequency: ${terms.frequency}`);
  console.log(`   Blockchain: ${terms.blockchain}`);
  console.log(`   AEO Score: ${contract.getAEOScore()}/100\n`);

  console.log('🎉 All done! Your contract is now:');
  console.log('   ✓ Discoverable by any AI (ChatGPT, Claude, Gemini)');
  console.log('   ✓ Understandable by any LLM');
  console.log('   ✓ Executing payments automatically\n');
}

// Run example
main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error('❌ Error:', error);
    process.exit(1);
  });
