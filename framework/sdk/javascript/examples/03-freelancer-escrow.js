/**
 * Advanced Example: Freelancer Escrow Payment
 *
 * This example demonstrates:
 * - Multi-milestone payment structure
 * - Escrow-based payment release
 * - Work verification conditions
 * - Dispute resolution mechanism
 */

const { Smart402 } = require('../src/core/Smart402');
const chalk = require('chalk');

async function createFreelancerEscrow() {
  console.log(chalk.blue.bold('\n👨‍💻 Freelancer Escrow Contract Example\n'));

  // Create multi-milestone freelancer contract
  const contract = await Smart402.create({
    type: 'freelancer-escrow',
    parties: [
      'client@startup.com',
      'freelancer@dev.com'
    ],
    payment: {
      amount: 5000,
      currency: 'USD',
      token: 'USDC',
      blockchain: 'polygon',
      frequency: 'milestone-based',
      escrow: true
    },
    milestones: [
      {
        id: 'milestone_1',
        title: 'Project Setup & Architecture',
        description: 'Initial project setup, architecture design, and database schema',
        amount: 1000,
        dueDate: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(), // 7 days
        deliverables: [
          'Project repository setup',
          'Architecture documentation',
          'Database schema design',
          'Development environment configuration'
        ],
        conditions: [
          {
            id: 'github_repo',
            type: 'verification',
            description: 'GitHub repository created and accessible',
            verificationMethod: 'api'
          },
          {
            id: 'docs_submitted',
            type: 'verification',
            description: 'Architecture documentation submitted',
            verificationMethod: 'manual'
          }
        ]
      },
      {
        id: 'milestone_2',
        title: 'Core Feature Development',
        description: 'Implement core application features and API endpoints',
        amount: 2000,
        dueDate: new Date(Date.now() + 21 * 24 * 60 * 60 * 1000).toISOString(), // 21 days
        deliverables: [
          'User authentication system',
          'Core API endpoints',
          'Database integration',
          'Unit tests (>80% coverage)'
        ],
        conditions: [
          {
            id: 'tests_pass',
            type: 'api',
            description: 'All tests passing with >80% coverage',
            endpoint: 'https://ci.example.com/api/test-results',
            threshold: 0.8
          },
          {
            id: 'code_review',
            type: 'verification',
            description: 'Code review approved by client',
            verificationMethod: 'manual'
          }
        ]
      },
      {
        id: 'milestone_3',
        title: 'Frontend & Integration',
        description: 'Build frontend interface and integrate with backend',
        amount: 1500,
        dueDate: new Date(Date.now() + 35 * 24 * 60 * 60 * 1000).toISOString(), // 35 days
        deliverables: [
          'Responsive UI components',
          'Frontend-backend integration',
          'User flow implementation',
          'Cross-browser testing'
        ],
        conditions: [
          {
            id: 'ui_approved',
            type: 'verification',
            description: 'UI/UX approved by client',
            verificationMethod: 'manual'
          },
          {
            id: 'functional_tests',
            type: 'verification',
            description: 'End-to-end functional tests passing',
            verificationMethod: 'automated'
          }
        ]
      },
      {
        id: 'milestone_4',
        title: 'Deployment & Documentation',
        description: 'Deploy to production and provide documentation',
        amount: 500,
        dueDate: new Date(Date.now() + 42 * 24 * 60 * 60 * 1000).toISOString(), // 42 days
        deliverables: [
          'Production deployment',
          'User documentation',
          'API documentation',
          'Handover meeting'
        ],
        conditions: [
          {
            id: 'live_deployment',
            type: 'api',
            description: 'Application live and accessible',
            endpoint: 'https://app.startup.com/health',
            expectedStatus: 200
          },
          {
            id: 'docs_complete',
            type: 'verification',
            description: 'Documentation completed and reviewed',
            verificationMethod: 'manual'
          }
        ]
      }
    ],
    dispute: {
      enabled: true,
      arbitrator: 'arbitration@smart402.io',
      windowDays: 7,
      resolution: 'mediation-first'
    },
    metadata: {
      title: 'Full-Stack Web Application Development',
      description: 'Milestone-based freelancer contract with escrow protection',
      category: 'freelance',
      tags: ['development', 'escrow', 'milestones', 'web-app'],
      effectiveDate: new Date().toISOString(),
      projectDuration: '6 weeks'
    }
  });

  console.log(chalk.green('✓ Freelancer escrow contract created'));
  console.log(chalk.cyan('  Contract ID:'), contract.ucl.contract_id);
  console.log(chalk.cyan('  Total Value:'), `$${contract.ucl.payment.amount} ${contract.ucl.payment.token}`);
  console.log(chalk.cyan('  Milestones:'), contract.ucl.milestones.length);
  console.log(chalk.cyan('  Escrow:'), 'Enabled');
  console.log();

  // Display milestone breakdown
  console.log(chalk.yellow('📋 Milestone Breakdown:\n'));
  contract.ucl.milestones.forEach((milestone, index) => {
    console.log(chalk.cyan(`  ${index + 1}. ${milestone.title}`));
    console.log(chalk.gray(`     Amount: $${milestone.amount} | Due: ${new Date(milestone.dueDate).toLocaleDateString()}`));
    console.log(chalk.gray(`     Deliverables: ${milestone.deliverables.length} items`));
    console.log(chalk.gray(`     Conditions: ${milestone.conditions.length} checks`));
    console.log();
  });

  // Deploy contract with escrow
  console.log(chalk.yellow('🚀 Deploying escrow contract...\n'));
  const deployResult = await contract.deploy({
    network: 'polygon',
    escrowEnabled: true,
    fundEscrow: true // Client funds full amount to escrow
  });

  console.log(chalk.green('✓ Contract deployed with escrow'));
  console.log(chalk.cyan('  Contract Address:'), deployResult.address);
  console.log(chalk.cyan('  Escrow Address:'), deployResult.escrowAddress);
  console.log(chalk.cyan('  Funded Amount:'), `$${contract.ucl.payment.amount}`);
  console.log();

  // Simulate milestone completion workflow
  console.log(chalk.yellow('🎯 Milestone Completion Workflow:\n'));

  for (let i = 0; i < contract.ucl.milestones.length; i++) {
    const milestone = contract.ucl.milestones[i];

    console.log(chalk.magenta(`\n--- Milestone ${i + 1}: ${milestone.title} ---\n`));

    // Simulate freelancer working
    console.log(chalk.gray('⏳ Freelancer working on deliverables...'));
    await sleep(1000);
    console.log(chalk.gray('⏳ Submitting work for review...'));
    await sleep(1000);
    console.log();

    // Check milestone conditions
    console.log(chalk.cyan('Checking milestone conditions:'));
    const conditionResults = await checkMilestoneConditions(milestone, contract);

    let allConditionsMet = true;
    conditionResults.forEach(result => {
      const status = result.met ? chalk.green('✓') : chalk.red('✗');
      console.log(`  ${status} ${result.description}`);
      if (!result.met) allConditionsMet = false;
    });
    console.log();

    if (allConditionsMet) {
      // Release payment from escrow
      console.log(chalk.yellow('💳 Releasing payment from escrow...'));
      const paymentResult = await contract.executePayment({
        milestone: milestone.id,
        amount: milestone.amount,
        releaseFromEscrow: true
      });

      console.log(chalk.green('✓ Payment released successfully'));
      console.log(chalk.cyan('  Transaction:'), paymentResult.transactionHash);
      console.log(chalk.cyan('  Amount:'), `$${paymentResult.amount} ${paymentResult.token}`);
      console.log(chalk.cyan('  Released to:'), paymentResult.to);
      console.log(chalk.cyan('  Remaining Escrow:'), `$${contract.ucl.payment.amount - getTotalPaid(contract, i + 1)}`);
      console.log();

      console.log(chalk.green(`✨ Milestone ${i + 1} completed and paid!\n`));
    } else {
      console.log(chalk.red('✗ Conditions not met - payment held in escrow'));
      console.log(chalk.yellow('⚠️  Dispute resolution available if needed\n'));
      break;
    }
  }

  // Contract summary
  console.log(chalk.blue('─'.repeat(60)));
  console.log(chalk.yellow('\n📊 Contract Summary:\n'));

  const completedMilestones = 2; // Simulated
  const totalPaid = getTotalPaid(contract, completedMilestones);
  const remainingInEscrow = contract.ucl.payment.amount - totalPaid;

  console.log(chalk.cyan('  Progress:'));
  console.log(chalk.gray(`    Completed: ${completedMilestones}/${contract.ucl.milestones.length} milestones`));
  console.log(chalk.gray(`    Paid: $${totalPaid}/$${contract.ucl.payment.amount}`));
  console.log(chalk.gray(`    Remaining in Escrow: $${remainingInEscrow}`));
  console.log();

  console.log(chalk.cyan('  Key Features:'));
  console.log(chalk.gray('    ✓ Milestone-based payments'));
  console.log(chalk.gray('    ✓ Escrow protection for both parties'));
  console.log(chalk.gray('    ✓ Automated condition verification'));
  console.log(chalk.gray('    ✓ Dispute resolution mechanism'));
  console.log(chalk.gray('    ✓ Transparent on-chain records'));
  console.log();

  // Export contract
  const fs = require('fs');
  const path = require('path');
  const yaml = contract.exportYAML();
  const outputPath = path.join(__dirname, 'output', 'freelancer-escrow.yaml');

  if (!fs.existsSync(path.join(__dirname, 'output'))) {
    fs.mkdirSync(path.join(__dirname, 'output'), { recursive: true });
  }

  fs.writeFileSync(outputPath, yaml);
  console.log(chalk.green('✓ Contract exported to:'), outputPath);
  console.log();

  console.log(chalk.green.bold('✨ Freelancer escrow contract demonstration complete!\n'));

  return contract;
}

// Helper functions
function getTotalPaid(contract, milestoneCount) {
  return contract.ucl.milestones
    .slice(0, milestoneCount)
    .reduce((sum, m) => sum + m.amount, 0);
}

async function checkMilestoneConditions(milestone, contract) {
  // Simulate condition checking
  return milestone.conditions.map(condition => {
    // In real implementation, would check actual APIs, GitHub, etc.
    const met = Math.random() > 0.2; // 80% success rate for demo
    return {
      id: condition.id,
      description: condition.description,
      met,
      checkedAt: new Date().toISOString()
    };
  });
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// Run the example
if (require.main === module) {
  createFreelancerEscrow().catch(error => {
    console.error(chalk.red('\n❌ Error:'), error.message);
    console.error(error.stack);
    process.exit(1);
  });
}

module.exports = { createFreelancerEscrow };
