#!/usr/bin/env node

/**
 * Smart402 CLI
 *
 * Command-line interface for creating, deploying, and monitoring
 * AI-native smart contracts.
 *
 * Usage:
 *   smart402 create         Create a new contract
 *   smart402 deploy         Deploy contract to blockchain
 *   smart402 monitor        Monitor contract conditions
 *   smart402 status         Check contract status
 *   smart402 templates      List available templates
 */

const { Command } = require('commander');
const chalk = require('chalk');
const ora = require('ora');
const inquirer = require('inquirer');
const fs = require('fs').promises;
const path = require('path');
const { Smart402 } = require('../dist/index');

const program = new Command();

program
  .name('smart402')
  .description('CLI for Smart402 - Universal Protocol for AI-Native Smart Contracts')
  .version('1.0.0');

// ============================================
// CREATE COMMAND
// ============================================

program
  .command('create')
  .description('Create a new Smart402 contract')
  .option('-t, --template <name>', 'Use a contract template')
  .option('-o, --output <file>', 'Output file path', './contract.yaml')
  .option('-i, --interactive', 'Interactive mode', true)
  .action(async (options) => {
    console.log(chalk.blue.bold('\n🚀 Smart402 Contract Creator\n'));

    try {
      let contractConfig;

      if (options.template) {
        // Use template
        contractConfig = await createFromTemplate(options.template);
      } else if (options.interactive) {
        // Interactive mode
        contractConfig = await createInteractive();
      } else {
        console.log(chalk.red('Please specify --template or use interactive mode'));
        process.exit(1);
      }

      // Create contract
      const spinner = ora('Creating contract...').start();
      const contract = await Smart402.create(contractConfig);
      spinner.succeed('Contract created!');

      // Export to file
      const yaml = await contract.export('yaml');
      await fs.writeFile(options.output, yaml);

      console.log(chalk.green(`\n✅ Contract saved to ${options.output}`));
      console.log(chalk.gray(`Contract ID: ${contract.id}`));
      console.log(chalk.gray(`\nNext steps:`));
      console.log(chalk.gray(`  1. Review the contract: cat ${options.output}`));
      console.log(chalk.gray(`  2. Deploy: smart402 deploy ${options.output}`));
      console.log(chalk.gray(`  3. Monitor: smart402 monitor ${contract.id}\n`));

    } catch (error) {
      console.error(chalk.red('\n❌ Error creating contract:'), error.message);
      process.exit(1);
    }
  });

async function createInteractive() {
  const answers = await inquirer.prompt([
    {
      type: 'list',
      name: 'type',
      message: 'What type of contract do you want to create?',
      choices: [
        { name: 'SaaS Subscription', value: 'saas-subscription' },
        { name: 'Freelancer Milestone', value: 'freelancer-milestone' },
        { name: 'Supply Chain', value: 'supply-chain' },
        { name: 'Affiliate Commission', value: 'affiliate-commission' },
        { name: 'Vendor SLA', value: 'vendor-sla' },
        { name: 'One-Time Payment', value: 'one-time-payment' }
      ]
    },
    {
      type: 'input',
      name: 'vendor',
      message: 'Vendor address or email:',
      validate: (input) => input.length > 0
    },
    {
      type: 'input',
      name: 'customer',
      message: 'Customer address or email:',
      validate: (input) => input.length > 0
    },
    {
      type: 'number',
      name: 'amount',
      message: 'Payment amount:',
      validate: (input) => input > 0
    },
    {
      type: 'list',
      name: 'token',
      message: 'Payment token:',
      choices: ['USDC', 'USDT', 'DAI', 'ETH']
    },
    {
      type: 'list',
      name: 'frequency',
      message: 'Payment frequency:',
      choices: ['one-time', 'monthly', 'weekly', 'yearly']
    },
    {
      type: 'list',
      name: 'network',
      message: 'Blockchain network:',
      choices: ['Polygon', 'Ethereum', 'Arbitrum', 'Optimism', 'Base'],
      default: 'Polygon'
    }
  ]);

  return {
    type: answers.type,
    parties: [answers.vendor, answers.customer],
    payment: {
      amount: answers.amount,
      token: answers.token,
      frequency: answers.frequency,
      blockchain: answers.network.toLowerCase()
    }
  };
}

async function createFromTemplate(templateName) {
  const templates = Smart402.getTemplates();

  if (!templates.includes(templateName)) {
    console.log(chalk.red(`\nTemplate '${templateName}' not found.`));
    console.log(chalk.gray('\nAvailable templates:'));
    templates.forEach(t => console.log(chalk.gray(`  - ${t}`)));
    process.exit(1);
  }

  // Get template variables
  const templateDoc = Smart402.getTemplateDoc(templateName);
  const variables = {};

  console.log(chalk.cyan(`\nUsing template: ${templateDoc.title}\n`));

  for (const variable of templateDoc.variables) {
    const answer = await inquirer.prompt([{
      type: variable.type === 'enum' ? 'list' : 'input',
      name: variable.name,
      message: variable.description,
      choices: variable.options,
      default: variable.default,
      validate: (input) => variable.required ? input && input.length > 0 : true
    }]);

    variables[variable.name] = answer[variable.name];
  }

  return Smart402.fromTemplate(templateName, variables);
}

// ============================================
// DEPLOY COMMAND
// ============================================

program
  .command('deploy <contract-file>')
  .description('Deploy contract to blockchain')
  .option('-n, --network <name>', 'Network to deploy to', 'polygon')
  .option('-k, --key <privateKey>', 'Private key for deployment')
  .option('--gas-limit <limit>', 'Gas limit')
  .action(async (contractFile, options) => {
    console.log(chalk.blue.bold('\n📡 Smart402 Deployment\n'));

    try {
      // Load contract
      const spinner = ora('Loading contract...').start();
      const yaml = await fs.readFile(contractFile, 'utf-8');
      const contract = await Smart402.fromYAML(yaml);
      spinner.succeed('Contract loaded');

      // Validate
      spinner.start('Validating contract...');
      const validation = await contract.validate();
      if (!validation.valid) {
        spinner.fail('Validation failed');
        console.log(chalk.red('\nErrors:'));
        validation.errors.forEach(err => console.log(chalk.red(`  - ${err}`)));
        process.exit(1);
      }
      spinner.succeed('Contract validated');

      // Confirm deployment
      const confirm = await inquirer.prompt([{
        type: 'confirm',
        name: 'deploy',
        message: `Deploy to ${options.network}?`,
        default: false
      }]);

      if (!confirm.deploy) {
        console.log(chalk.yellow('\nDeployment cancelled'));
        process.exit(0);
      }

      // Deploy
      spinner.start(`Deploying to ${options.network}...`);

      const result = await contract.deploy({
        network: options.network,
        gasLimit: options.gasLimit ? parseInt(options.gasLimit) : undefined
      });

      spinner.succeed('Deployment successful!');

      console.log(chalk.green('\n✅ Contract deployed!\n'));
      console.log(chalk.gray(`Contract Address: ${result.address}`));
      console.log(chalk.gray(`Transaction: ${result.transactionHash}`));
      console.log(chalk.gray(`Network: ${result.network}`));
      console.log(chalk.gray(`Block: ${result.blockNumber}`));
      console.log(chalk.gray(`\nView on explorer: ${contract.getURL()}`));
      console.log(chalk.gray(`\nStart monitoring: smart402 monitor ${contract.id}\n`));

      // Save deployment info
      const deploymentInfo = {
        contractId: contract.id,
        address: result.address,
        network: result.network,
        transactionHash: result.transactionHash,
        deployedAt: new Date().toISOString()
      };

      await fs.writeFile(
        `${contractFile}.deployed.json`,
        JSON.stringify(deploymentInfo, null, 2)
      );

    } catch (error) {
      console.error(chalk.red('\n❌ Deployment failed:'), error.message);
      process.exit(1);
    }
  });

// ============================================
// MONITOR COMMAND
// ============================================

program
  .command('monitor <contract-id>')
  .description('Monitor contract conditions and auto-execute payments')
  .option('-f, --frequency <freq>', 'Monitoring frequency', 'medium')
  .option('-w, --webhook <url>', 'Webhook URL for notifications')
  .option('--dry-run', 'Check conditions once without starting monitor')
  .action(async (contractId, options) => {
    console.log(chalk.blue.bold('\n👀 Smart402 Monitoring\n'));

    try {
      // Load contract
      const spinner = ora('Loading contract...').start();
      const contract = await Smart402.load(contractId);
      spinner.succeed('Contract loaded');

      if (options.dryRun) {
        // Just check conditions once
        spinner.start('Checking conditions...');
        const status = await contract.checkConditions();
        spinner.stop();

        console.log(chalk.cyan('\n📊 Condition Status:\n'));
        for (const [id, met] of Object.entries(status.conditions)) {
          const icon = met ? '✅' : '❌';
          console.log(`  ${icon} ${id}: ${met ? 'Met' : 'Not met'}`);
        }
        console.log(chalk.gray(`\nAll conditions met: ${status.allMet ? 'Yes' : 'No'}`));
        console.log(chalk.gray(`Checked at: ${status.timestamp}\n`));

        if (status.allMet) {
          const confirm = await inquirer.prompt([{
            type: 'confirm',
            name: 'execute',
            message: 'All conditions met. Execute payment now?',
            default: false
          }]);

          if (confirm.execute) {
            spinner.start('Executing payment...');
            const payment = await contract.executePayment();
            spinner.succeed('Payment executed!');
            console.log(chalk.green(`\n✅ Payment completed: ${payment.transactionHash}\n`));
          }
        }

      } else {
        // Start continuous monitoring
        console.log(chalk.cyan(`Starting continuous monitoring...`));
        console.log(chalk.gray(`Frequency: ${options.frequency}`));
        if (options.webhook) {
          console.log(chalk.gray(`Webhook: ${options.webhook}`));
        }

        await contract.startMonitoring({
          frequency: options.frequency,
          webhook: options.webhook
        });

        console.log(chalk.green('\n✅ Monitoring active!'));
        console.log(chalk.gray('\nPress Ctrl+C to stop\n'));

        // Keep process alive
        process.on('SIGINT', async () => {
          console.log(chalk.yellow('\n\nStopping monitoring...'));
          await contract.stopMonitoring();
          console.log(chalk.green('Monitoring stopped.\n'));
          process.exit(0);
        });

        // Keep alive
        await new Promise(() => {});
      }

    } catch (error) {
      console.error(chalk.red('\n❌ Monitoring failed:'), error.message);
      process.exit(1);
    }
  });

// ============================================
// STATUS COMMAND
// ============================================

program
  .command('status <contract-id>')
  .description('Check contract status')
  .action(async (contractId) => {
    console.log(chalk.blue.bold('\n📋 Contract Status\n'));

    try {
      const spinner = ora('Loading contract...').start();
      const contract = await Smart402.load(contractId);
      spinner.succeed('Contract loaded');

      console.log(chalk.cyan('\nContract Information:\n'));
      console.log(chalk.gray(`ID: ${contract.id}`));
      console.log(chalk.gray(`Status: ${contract.status}`));
      console.log(chalk.gray(`Type: ${contract.ucl.metadata.type}`));

      if (contract.address) {
        console.log(chalk.gray(`Address: ${contract.address}`));
        console.log(chalk.gray(`Network: ${contract.getPaymentTerms().blockchain}`));
        console.log(chalk.gray(`URL: ${contract.getURL()}`));
      }

      console.log(chalk.cyan('\nParties:\n'));
      contract.getParties().forEach(party => {
        console.log(chalk.gray(`  ${party.role}: ${party.name || party.identifier}`));
      });

      const payment = contract.getPaymentTerms();
      console.log(chalk.cyan('\nPayment Terms:\n'));
      console.log(chalk.gray(`  Amount: ${payment.amount} ${payment.token}`));
      console.log(chalk.gray(`  Frequency: ${payment.frequency}`));
      console.log(chalk.gray(`  Blockchain: ${payment.blockchain}`));

      console.log(chalk.cyan('\nSummary:\n'));
      console.log(chalk.gray(contract.getSummary()));

      console.log(chalk.cyan('\nAEO Score:\n'));
      console.log(chalk.gray(`  ${contract.getAEOScore()}/100 - Discoverability rating\n`));

    } catch (error) {
      console.error(chalk.red('\n❌ Error:'), error.message);
      process.exit(1);
    }
  });

// ============================================
// TEMPLATES COMMAND
// ============================================

program
  .command('templates')
  .description('List available contract templates')
  .action(() => {
    console.log(chalk.blue.bold('\n📚 Available Templates\n'));

    const templates = Smart402.getTemplates();

    templates.forEach(name => {
      const doc = Smart402.getTemplateDoc(name);
      console.log(chalk.cyan(`\n${doc.title}`));
      console.log(chalk.gray(`  ${doc.description}`));
      console.log(chalk.gray(`  Usage: smart402 create --template ${name}`));
    });

    console.log();
  });

// ============================================
// INIT COMMAND
// ============================================

program
  .command('init')
  .description('Initialize Smart402 configuration')
  .action(async () => {
    console.log(chalk.blue.bold('\n⚙️  Smart402 Initialization\n'));

    const answers = await inquirer.prompt([
      {
        type: 'list',
        name: 'network',
        message: 'Default network:',
        choices: ['Polygon', 'Ethereum', 'Arbitrum', 'Optimism', 'Base'],
        default: 'Polygon'
      },
      {
        type: 'password',
        name: 'privateKey',
        message: 'Private key (optional, can set later):',
        mask: '*'
      },
      {
        type: 'input',
        name: 'rpcUrl',
        message: 'Custom RPC URL (optional):'
      }
    ]);

    const config = {
      network: answers.network.toLowerCase(),
      privateKey: answers.privateKey,
      rpcUrl: answers.rpcUrl
    };

    // Save config
    const configPath = path.join(process.cwd(), '.smart402.json');
    await fs.writeFile(configPath, JSON.stringify(config, null, 2));

    console.log(chalk.green(`\n✅ Configuration saved to .smart402.json`));
    console.log(chalk.yellow(`\n⚠️  Add .smart402.json to .gitignore to keep keys secret\n`));
  });

// Parse arguments
program.parse();
