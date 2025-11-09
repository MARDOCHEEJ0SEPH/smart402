/**
 * Advanced Example: Supply Chain Payment
 *
 * This example demonstrates:
 * - Multi-party supply chain contract
 * - IoT sensor integration for verification
 * - GPS tracking conditions
 * - Temperature and humidity monitoring
 * - Automatic payment upon delivery confirmation
 */

const { Smart402 } = require('../src/core/Smart402');
const chalk = require('chalk');

async function createSupplyChainContract() {
  console.log(chalk.blue.bold('\n📦 Supply Chain Payment Contract Example\n'));

  // Create supply chain contract with IoT conditions
  const contract = await Smart402.create({
    type: 'supply-chain-payment',
    parties: [
      'supplier@pharma-corp.com',
      'distributor@logistics.com',
      'retailer@pharmacy-chain.com'
    ],
    payment: {
      amount: 50000,
      currency: 'USD',
      token: 'USDC',
      blockchain: 'polygon',
      frequency: 'on-delivery',
      splitPayment: true,
      splits: [
        { party: 'supplier@pharma-corp.com', percentage: 60 },
        { party: 'distributor@logistics.com', percentage: 40 }
      ]
    },
    shipment: {
      id: 'SHIP-2024-001234',
      origin: {
        address: '123 Pharma Way, Manufacturing City, MC 12345',
        coordinates: { lat: 40.7128, lon: -74.0060 }
      },
      destination: {
        address: '456 Retail Blvd, Distribution Hub, DH 67890',
        coordinates: { lat: 34.0522, lon: -118.2437 }
      },
      expectedDepartureDate: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(),
      expectedArrivalDate: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(),
      cargo: {
        type: 'pharmaceutical',
        description: 'Temperature-sensitive vaccines',
        quantity: 10000,
        unit: 'doses',
        value: 50000
      }
    },
    conditions: [
      {
        id: 'temperature_control',
        type: 'iot-sensor',
        description: 'Maintain temperature between 2°C and 8°C',
        sensorType: 'temperature',
        minValue: 2,
        maxValue: 8,
        unit: 'celsius',
        checkFrequency: 'continuous',
        alertThreshold: 1, // Alert if out of range for >1 minute
        critical: true
      },
      {
        id: 'humidity_control',
        type: 'iot-sensor',
        description: 'Keep humidity below 60%',
        sensorType: 'humidity',
        maxValue: 60,
        unit: 'percentage',
        checkFrequency: 'continuous',
        critical: false
      },
      {
        id: 'gps_tracking',
        type: 'iot-sensor',
        description: 'Continuous GPS tracking within expected route',
        sensorType: 'gps',
        checkFrequency: 'real-time',
        geofencing: {
          enabled: true,
          allowedDeviation: 50, // km
          routeOptimized: true
        },
        critical: true
      },
      {
        id: 'tamper_detection',
        type: 'iot-sensor',
        description: 'No tampering or unauthorized access',
        sensorType: 'seal-integrity',
        checkFrequency: 'continuous',
        critical: true
      },
      {
        id: 'delivery_confirmation',
        type: 'verification',
        description: 'Delivery confirmed by authorized recipient',
        verificationMethod: 'digital-signature',
        requiredSignatures: ['retailer@pharmacy-chain.com'],
        critical: true
      },
      {
        id: 'quality_inspection',
        type: 'verification',
        description: 'Quality inspection passed upon arrival',
        verificationMethod: 'manual',
        inspector: 'quality@pharmacy-chain.com',
        critical: true
      }
    ],
    penalties: {
      temperatureBreach: {
        severity: 'critical',
        penalty: 10000,
        description: 'Full or partial product loss due to temperature violation'
      },
      deliveryDelay: {
        severity: 'moderate',
        penaltyPerDay: 500,
        gracePeriod: 1, // days
        description: 'Penalty for late delivery beyond grace period'
      },
      tamperingDetected: {
        severity: 'critical',
        penalty: 50000,
        description: 'Contract void if tampering detected'
      }
    },
    metadata: {
      title: 'Pharmaceutical Cold Chain Delivery',
      description: 'Temperature-controlled supply chain payment with IoT verification',
      category: 'supply-chain',
      tags: ['pharmaceuticals', 'cold-chain', 'iot', 'multi-party'],
      compliance: ['FDA', 'WHO-GDP', 'HACCP'],
      effectiveDate: new Date().toISOString()
    }
  });

  console.log(chalk.green('✓ Supply chain contract created'));
  console.log(chalk.cyan('  Contract ID:'), contract.ucl.contract_id);
  console.log(chalk.cyan('  Shipment ID:'), contract.ucl.shipment.id);
  console.log(chalk.cyan('  Value:'), `$${contract.ucl.payment.amount} ${contract.ucl.payment.token}`);
  console.log(chalk.cyan('  Parties:'), contract.ucl.metadata.parties.length);
  console.log(chalk.cyan('  IoT Sensors:'), contract.ucl.conditions.filter(c => c.type === 'iot-sensor').length);
  console.log();

  // Display shipment details
  console.log(chalk.yellow('📍 Shipment Details:\n'));
  console.log(chalk.cyan('  Cargo:'), `${contract.ucl.shipment.cargo.quantity} ${contract.ucl.shipment.cargo.unit} of ${contract.ucl.shipment.cargo.description}`);
  console.log(chalk.cyan('  Origin:'), contract.ucl.shipment.origin.address);
  console.log(chalk.cyan('  Destination:'), contract.ucl.shipment.destination.address);
  console.log(chalk.cyan('  Expected Transit:'), `${Math.round((new Date(contract.ucl.shipment.expectedArrivalDate) - new Date(contract.ucl.shipment.expectedDepartureDate)) / (1000 * 60 * 60 * 24))} days`);
  console.log();

  // Display monitoring conditions
  console.log(chalk.yellow('🔍 Monitoring Conditions:\n'));
  contract.ucl.conditions.forEach(condition => {
    const criticalBadge = condition.critical ? chalk.red('[CRITICAL]') : chalk.gray('[STANDARD]');
    console.log(chalk.cyan(`  ${criticalBadge} ${condition.description}`));
    if (condition.minValue !== undefined || condition.maxValue !== undefined) {
      const range = condition.minValue !== undefined
        ? `${condition.minValue}${condition.unit} - ${condition.maxValue}${condition.unit}`
        : `< ${condition.maxValue}${condition.unit}`;
      console.log(chalk.gray(`    Range: ${range} | Frequency: ${condition.checkFrequency}`));
    }
  });
  console.log();

  // Deploy contract
  console.log(chalk.yellow('🚀 Deploying supply chain contract...\n'));
  const deployResult = await contract.deploy({
    network: 'polygon',
    iotIntegration: true,
    webhooks: {
      enabled: true,
      endpoints: [
        'https://api.supplier.com/webhooks/smart402',
        'https://api.distributor.com/webhooks/smart402',
        'https://api.retailer.com/webhooks/smart402'
      ]
    }
  });

  console.log(chalk.green('✓ Contract deployed'));
  console.log(chalk.cyan('  Address:'), deployResult.address);
  console.log(chalk.cyan('  IoT Endpoints:'), deployResult.iotEndpoints || 'Configured');
  console.log();

  // Simulate shipment tracking
  console.log(chalk.yellow('🚛 Shipment Tracking Simulation:\n'));
  console.log(chalk.blue('─'.repeat(60)));

  await simulateShipment(contract);

  console.log(chalk.blue('─'.repeat(60)));
  console.log();

  // Final delivery and payment
  console.log(chalk.yellow('📦 Delivery Verification:\n'));

  console.log(chalk.cyan('Running final checks:'));
  const finalCheck = await contract.checkConditions();

  finalCheck.conditions.forEach(condition => {
    const status = condition.met ? chalk.green('✓') : chalk.red('✗');
    console.log(`  ${status} ${condition.description}`);
    if (condition.violations) {
      console.log(chalk.red(`    ⚠️  Violations: ${condition.violations}`));
    }
  });
  console.log();

  if (finalCheck.allMet) {
    console.log(chalk.green('✓ All conditions met - proceeding with payment\n'));

    // Execute split payment
    console.log(chalk.yellow('💳 Executing split payment...\n'));
    const paymentResult = await contract.executePayment({
      splitPayment: true
    });

    console.log(chalk.green('✓ Payment executed successfully'));
    console.log();
    paymentResult.splits.forEach(split => {
      console.log(chalk.cyan(`  ${split.party}:`));
      console.log(chalk.gray(`    Amount: $${split.amount} ${split.token}`));
      console.log(chalk.gray(`    Transaction: ${split.transactionHash}`));
      console.log(chalk.gray(`    Percentage: ${split.percentage}%`));
      console.log();
    });

    console.log(chalk.green.bold('✨ Supply chain contract completed successfully!\n'));
  } else {
    console.log(chalk.red('✗ Conditions violated - calculating penalties\n'));

    const penalties = calculatePenalties(finalCheck, contract);
    console.log(chalk.yellow('Penalty Assessment:'));
    penalties.forEach(penalty => {
      console.log(chalk.red(`  - ${penalty.type}: -$${penalty.amount}`));
      console.log(chalk.gray(`    ${penalty.description}`));
    });

    const adjustedAmount = contract.ucl.payment.amount - penalties.reduce((sum, p) => sum + p.amount, 0);
    console.log(chalk.cyan(`\n  Adjusted Payment: $${adjustedAmount} (original: $${contract.ucl.payment.amount})`));
    console.log();
  }

  // Export detailed report
  const fs = require('fs');
  const path = require('path');

  const report = {
    contract: contract.exportJSON(),
    shipment: contract.ucl.shipment,
    tracking: 'See tracking log for detailed sensor data',
    finalConditions: finalCheck,
    timestamp: new Date().toISOString()
  };

  const outputPath = path.join(__dirname, 'output', 'supply-chain-report.json');
  if (!fs.existsSync(path.join(__dirname, 'output'))) {
    fs.mkdirSync(path.join(__dirname, 'output'), { recursive: true });
  }
  fs.writeFileSync(outputPath, JSON.stringify(report, null, 2));

  console.log(chalk.green('✓ Supply chain report exported to:'), outputPath);
  console.log();

  return contract;
}

// Helper function to simulate shipment
async function simulateShipment(contract) {
  const days = 7;

  for (let day = 0; day < days; day++) {
    console.log(chalk.magenta(`\nDay ${day + 1}/${days}:`));

    // Simulate sensor readings
    const temp = 2 + Math.random() * 6; // 2-8°C
    const humidity = 40 + Math.random() * 15; // 40-55%
    const gpsStatus = 'On route';
    const sealStatus = 'Intact';

    console.log(chalk.gray(`  🌡️  Temperature: ${temp.toFixed(1)}°C`));
    console.log(chalk.gray(`  💧 Humidity: ${humidity.toFixed(1)}%`));
    console.log(chalk.gray(`  📍 GPS: ${gpsStatus}`));
    console.log(chalk.gray(`  🔒 Seal: ${sealStatus}`));

    // Check for any violations
    if (temp < 2 || temp > 8) {
      console.log(chalk.red(`  ⚠️  ALERT: Temperature violation detected!`));
    }

    if (humidity > 60) {
      console.log(chalk.yellow(`  ⚠️  WARNING: High humidity detected`));
    }

    await sleep(500); // Simulate time passing
  }

  console.log(chalk.green('\n✓ Shipment arrived at destination\n'));
}

function calculatePenalties(checkResult, contract) {
  const penalties = [];

  checkResult.conditions.forEach(condition => {
    if (!condition.met && condition.critical) {
      if (condition.id === 'temperature_control') {
        penalties.push({
          type: 'Temperature Breach',
          amount: contract.ucl.penalties.temperatureBreach.penalty,
          description: contract.ucl.penalties.temperatureBreach.description
        });
      }
      if (condition.id === 'tamper_detection') {
        penalties.push({
          type: 'Tampering Detected',
          amount: contract.ucl.penalties.tamperingDetected.penalty,
          description: contract.ucl.penalties.tamperingDetected.description
        });
      }
    }
  });

  return penalties;
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// Run the example
if (require.main === module) {
  createSupplyChainContract().catch(error => {
    console.error(chalk.red('\n❌ Error:'), error.message);
    console.error(error.stack);
    process.exit(1);
  });
}

module.exports = { createSupplyChainContract };
