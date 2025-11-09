/**
 * Advanced Example: SaaS Subscription with Uptime Conditions
 *
 * This example demonstrates:
 * - Creating a SaaS subscription contract
 * - Adding uptime monitoring conditions
 * - Implementing automatic payment with SLA enforcement
 * - Webhook notifications for payment events
 */

const { Smart402 } = require('../src/core/Smart402');
const chalk = require('chalk');

async function createSaaSContract() {
  console.log(chalk.blue.bold('\n💼 SaaS Subscription Contract Example\n'));

  // Create contract with detailed conditions
  const contract = await Smart402.create({
    type: 'saas-subscription',
    parties: [
      'saas-provider@example.com',
      'enterprise-customer@example.com'
    ],
    payment: {
      amount: 999,
      currency: 'USD',
      token: 'USDC',
      blockchain: 'polygon',
      frequency: 'monthly',
      dueDay: 1 // 1st of every month
    },
    conditions: [
      {
        id: 'uptime_check',
        type: 'api',
        description: 'Service must maintain 99.9% uptime',
        endpoint: 'https://status.saas-provider.com/api/uptime',
        threshold: 0.999,
        checkFrequency: 'hourly'
      },
      {
        id: 'support_response',
        type: 'metric',
        description: 'Support ticket response time < 4 hours',
        metric: 'avg_response_time',
        threshold: 4,
        unit: 'hours',
        checkFrequency: 'daily'
      },
      {
        id: 'data_backup',
        type: 'verification',
        description: 'Daily data backups verified',
        checkFrequency: 'daily'
      }
    ],
    metadata: {
      title: 'Enterprise SaaS Subscription with SLA',
      description: 'Monthly subscription with automated payment based on SLA compliance',
      category: 'saas',
      tags: ['subscription', 'enterprise', 'sla', 'automated'],
      effectiveDate: new Date().toISOString(),
      duration: '12 months',
      autoRenew: true
    },
    penalties: {
      uptimeBreach: {
        threshold: 0.999,
        penalty: 100, // $100 credit
        description: 'Service credit if uptime falls below 99.9%'
      },
      supportResponseBreach: {
        threshold: 4, // hours
        penalty: 50,
        description: 'Service credit if avg support response exceeds 4 hours'
      }
    }
  });

  console.log(chalk.green('✓ SaaS contract created'));
  console.log(chalk.cyan('  Contract ID:'), contract.ucl.contract_id);
  console.log(chalk.cyan('  Parties:'), contract.ucl.metadata.parties.join(' ↔ '));
  console.log(chalk.cyan('  Payment:'), `$${contract.ucl.payment.amount} ${contract.ucl.payment.token} ${contract.ucl.payment.frequency}`);
  console.log();

  // Display contract explanation
  console.log(chalk.yellow('📋 Contract Summary:\n'));
  console.log(contract.explain());
  console.log();

  // Check AEO score for AI discoverability
  console.log(chalk.yellow('🤖 AI Discoverability (AEO Score):\n'));
  const aeoScore = contract.getAEOScore();
  console.log(chalk.cyan(`  Total Score: ${(aeoScore.total * 100).toFixed(1)}%`));
  console.log(chalk.gray(`  - Semantic Richness: ${(aeoScore.semantic_richness * 100).toFixed(1)}%`));
  console.log(chalk.gray(`  - Citation Friendliness: ${(aeoScore.citation_friendliness * 100).toFixed(1)}%`));
  console.log(chalk.gray(`  - Findability: ${(aeoScore.findability * 100).toFixed(1)}%`));
  console.log(chalk.gray(`  - Authority Signals: ${(aeoScore.authority_signals * 100).toFixed(1)}%`));
  console.log(chalk.gray(`  - Citation Presence: ${(aeoScore.citation_presence * 100).toFixed(1)}%`));
  console.log();

  // Generate JSON-LD for SEO
  console.log(chalk.yellow('🔍 JSON-LD Markup for Search Engines:\n'));
  const jsonld = contract.generateJSONLD();
  console.log(chalk.gray(JSON.stringify(JSON.parse(jsonld), null, 2)));
  console.log();

  // Deploy contract
  console.log(chalk.yellow('🚀 Deploying to Polygon...\n'));
  const deployResult = await contract.deploy({
    network: 'polygon',
    gasLimit: 500000
  });

  console.log(chalk.green('✓ Deployment successful'));
  console.log(chalk.cyan('  Address:'), deployResult.address);
  console.log(chalk.cyan('  Transaction:'), deployResult.transactionHash);
  console.log(chalk.cyan('  Gas Used:'), deployResult.gasUsed || 'N/A');
  console.log();

  // Setup monitoring with webhooks
  console.log(chalk.yellow('👁️  Setting up monitoring...\n'));
  await contract.startMonitoring({
    frequency: 'hourly',
    webhook: 'https://api.example.com/webhooks/smart402',
    events: ['condition_check', 'payment_due', 'payment_executed', 'sla_breach'],
    autoExecute: true
  });

  console.log(chalk.green('✓ Monitoring configured'));
  console.log(chalk.cyan('  Check Frequency:'), 'hourly');
  console.log(chalk.cyan('  Auto-Execute:'), 'enabled');
  console.log(chalk.cyan('  Webhook Events:'), 'condition_check, payment_due, payment_executed, sla_breach');
  console.log();

  // Simulate condition check
  console.log(chalk.yellow('🔍 Checking SLA conditions...\n'));
  const conditionResult = await contract.checkConditions();

  console.log(chalk.cyan('Condition Check Results:'));
  conditionResult.conditions.forEach(cond => {
    const status = cond.met ? chalk.green('✓') : chalk.red('✗');
    console.log(`  ${status} ${cond.description}`);
    if (cond.currentValue !== undefined) {
      console.log(chalk.gray(`    Current: ${cond.currentValue}, Threshold: ${cond.threshold}`));
    }
  });
  console.log();

  if (conditionResult.allMet) {
    console.log(chalk.green('✓ All SLA conditions met - payment authorized\n'));

    // Execute payment
    console.log(chalk.yellow('💳 Executing monthly payment...\n'));
    const paymentResult = await contract.executePayment();

    console.log(chalk.green('✓ Payment executed successfully'));
    console.log(chalk.cyan('  Transaction Hash:'), paymentResult.transactionHash);
    console.log(chalk.cyan('  Amount:'), `${paymentResult.amount} ${paymentResult.token}`);
    console.log(chalk.cyan('  From:'), paymentResult.from);
    console.log(chalk.cyan('  To:'), paymentResult.to);
    console.log(chalk.cyan('  Timestamp:'), new Date(paymentResult.timestamp).toLocaleString());
    console.log();
  } else {
    console.log(chalk.red('✗ SLA conditions not met - payment will be adjusted\n'));

    // Calculate penalty adjustments
    const penalties = conditionResult.conditions
      .filter(c => !c.met)
      .map(c => ({ condition: c.id, penalty: contract.ucl.penalties?.[c.id]?.penalty || 0 }));

    const totalPenalty = penalties.reduce((sum, p) => sum + p.penalty, 0);
    const adjustedAmount = contract.ucl.payment.amount - totalPenalty;

    console.log(chalk.yellow('Penalty Adjustments:'));
    penalties.forEach(p => {
      console.log(chalk.gray(`  - ${p.condition}: -$${p.penalty}`));
    });
    console.log(chalk.cyan(`  Adjusted Payment: $${adjustedAmount} (original: $${contract.ucl.payment.amount})`));
    console.log();
  }

  // Export contract for records
  console.log(chalk.yellow('💾 Exporting contract...\n'));
  const fs = require('fs');
  const path = require('path');

  const yaml = contract.exportYAML();
  const outputPath = path.join(__dirname, 'output', 'saas-contract.yaml');

  // Ensure output directory exists
  if (!fs.existsSync(path.join(__dirname, 'output'))) {
    fs.mkdirSync(path.join(__dirname, 'output'), { recursive: true });
  }

  fs.writeFileSync(outputPath, yaml);
  console.log(chalk.green('✓ Contract exported to:'), outputPath);
  console.log();

  console.log(chalk.green.bold('✨ SaaS subscription contract setup complete!\n'));
  console.log(chalk.white('The contract will now:'));
  console.log(chalk.gray('  1. Monitor SLA conditions hourly'));
  console.log(chalk.gray('  2. Automatically execute payments on the 1st of each month'));
  console.log(chalk.gray('  3. Apply penalties if SLA thresholds are not met'));
  console.log(chalk.gray('  4. Send webhook notifications for all events'));
  console.log(chalk.gray('  5. Auto-renew after 12 months if conditions are favorable\n'));

  return contract;
}

// Run the example
if (require.main === module) {
  createSaaSContract().catch(error => {
    console.error(chalk.red('\n❌ Error:'), error.message);
    console.error(error.stack);
    process.exit(1);
  });
}

module.exports = { createSaaSContract };
