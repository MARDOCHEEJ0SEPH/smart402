/**
 * Smart402 JavaScript SDK - Quickstart Example
 *
 * This example demonstrates the complete workflow:
 * 1. Creating a contract
 * 2. Deploying to blockchain
 * 3. Monitoring and auto-execution
 */

const { Smart402 } = require('../src/core/Smart402');
const chalk = require('chalk');

async function main() {
  console.log(chalk.blue.bold('\n🚀 Smart402 Quickstart Example\n'));

  try {
    // Step 1: Create Contract
    console.log(chalk.cyan('1️⃣  Creating SaaS subscription contract...'));

    const contract = await Smart402.create({
      type: 'saas-subscription',
      parties: [
        'vendor@example.com',
        'customer@example.com'
      ],
      payment: {
        amount: 99,
        currency: 'USD',
        token: 'USDC',
        blockchain: 'polygon',
        frequency: 'monthly'
      },
      metadata: {
        title: 'Monthly SaaS Subscription',
        description: 'Automatic monthly payment for software service'
      }
    });

    console.log(chalk.green('   ✓ Contract created:'), contract.ucl.contract_id);
    console.log(chalk.green('   ✓ Summary:'), contract.getSummary());
    console.log();

    // Step 2: Get AEO Score
    console.log(chalk.cyan('2️⃣  Calculating AEO Score...'));
    const aeoScore = contract.getAEOScore();
    console.log(chalk.green(`   ✓ AEO Score: ${aeoScore.total.toFixed(2)}/1.0`));
    console.log(chalk.gray(`     - Semantic Richness: ${aeoScore.semantic_richness.toFixed(2)}`));
    console.log(chalk.gray(`     - Citation Friendliness: ${aeoScore.citation_friendliness.toFixed(2)}`));
    console.log(chalk.gray(`     - Findability: ${aeoScore.findability.toFixed(2)}`));
    console.log();

    // Step 3: Validate Contract
    console.log(chalk.cyan('3️⃣  Validating contract...'));
    const validation = contract.validate();
    if (validation.valid) {
      console.log(chalk.green('   ✓ Contract is valid'));
    } else {
      console.log(chalk.red('   ✗ Validation errors:'), validation.errors);
    }
    if (validation.warnings.length > 0) {
      console.log(chalk.yellow('   ⚠ Warnings:'), validation.warnings);
    }
    console.log();

    // Step 4: Generate Explanation
    console.log(chalk.cyan('4️⃣  Generating plain-English explanation...'));
    const explanation = contract.explain();
    console.log(chalk.white(explanation));
    console.log();

    // Step 5: Compile to Target Languages
    console.log(chalk.cyan('5️⃣  Compiling to target languages...'));

    const solidity = await contract.compile('solidity');
    console.log(chalk.green(`   ✓ Solidity code generated (${solidity.length} bytes)`));

    const javascript = await contract.compile('javascript');
    console.log(chalk.green(`   ✓ JavaScript code generated (${javascript.length} bytes)`));

    const rust = await contract.compile('rust');
    console.log(chalk.green(`   ✓ Rust code generated (${rust.length} bytes)`));
    console.log();

    // Step 6: Deploy Contract
    console.log(chalk.cyan('6️⃣  Deploying to Polygon...'));
    const deployResult = await contract.deploy({ network: 'polygon' });
    console.log(chalk.green('   ✓ Contract deployed!'));
    console.log(chalk.gray(`     - Address: ${deployResult.address}`));
    console.log(chalk.gray(`     - Transaction: ${deployResult.transactionHash}`));
    console.log(chalk.gray(`     - Network: ${deployResult.network}`));
    if (deployResult.blockNumber) {
      console.log(chalk.gray(`     - Block: ${deployResult.blockNumber}`));
    }
    console.log();

    // Step 7: Generate X402 Headers
    console.log(chalk.cyan('7️⃣  Generating X402 payment headers...'));
    const headers = contract.generateX402Headers(true);
    console.log(chalk.green('   ✓ X402 headers generated:'));
    console.log(chalk.gray(`     - X402-Contract-ID: ${headers['X402-Contract-ID']}`));
    console.log(chalk.gray(`     - X402-Payment-Amount: ${headers['X402-Payment-Amount']}`));
    console.log(chalk.gray(`     - X402-Payment-Token: ${headers['X402-Payment-Token']}`));
    console.log(chalk.gray(`     - X402-Conditions-Met: ${headers['X402-Conditions-Met']}`));
    console.log();

    // Step 8: Check Conditions
    console.log(chalk.cyan('8️⃣  Checking contract conditions...'));
    const conditions = await contract.checkConditions();
    console.log(chalk.green('   ✓ Conditions checked:'));
    console.log(chalk.gray(`     - All Met: ${conditions.allMet}`));
    console.log(chalk.gray(`     - Timestamp: ${conditions.timestamp}`));
    console.log();

    // Step 9: Execute Payment
    if (conditions.allMet) {
      console.log(chalk.cyan('9️⃣  Executing payment...'));
      const paymentResult = await contract.executePayment();
      console.log(chalk.green('   ✓ Payment executed!'));
      console.log(chalk.gray(`     - Success: ${paymentResult.success}`));
      console.log(chalk.gray(`     - Transaction: ${paymentResult.transactionHash}`));
      console.log(chalk.gray(`     - Amount: ${paymentResult.amount}`));
      console.log(chalk.gray(`     - Token: ${paymentResult.token}`));
      console.log(chalk.gray(`     - From: ${paymentResult.from}`));
      console.log(chalk.gray(`     - To: ${paymentResult.to}`));
      console.log();
    }

    // Step 10: Export Contract
    console.log(chalk.cyan('🔟 Exporting contract...'));
    const yaml = contract.exportYAML();
    console.log(chalk.green(`   ✓ YAML export generated (${yaml.length} bytes)`));

    const json = contract.exportJSON();
    console.log(chalk.green(`   ✓ JSON export generated (${json.length} bytes)`));

    console.log(chalk.green.bold('\n✨ Quickstart complete! All systems operational.\n'));
    console.log(chalk.white('Next steps:'));
    console.log(chalk.gray('  • Start monitoring: smart402 monitor contract.yaml'));
    console.log(chalk.gray(`  • Check status: smart402 status ${contract.ucl.contract_id}`));
    console.log(chalk.gray('  • View templates: smart402 templates\n'));

  } catch (error) {
    console.error(chalk.red('\n❌ Error:'), error.message);
    console.error(error.stack);
    process.exit(1);
  }
}

// Run the example
if (require.main === module) {
  main();
}

module.exports = { main };
