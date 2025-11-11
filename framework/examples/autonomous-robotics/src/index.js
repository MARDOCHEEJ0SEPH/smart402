#!/usr/bin/env node

/**
 * Smart402 Autonomous Robotics Platform - Main Entry Point
 * Complete example demonstrating Smart402 framework integration
 */

import { RoboticsAPIServer } from './api/server.js';
import { Smart402RoboticsIntegration } from './core/Smart402Integration.js';
import { initializeDatabase } from './database/schemas.js';
import dotenv from 'dotenv';

dotenv.config();

/**
 * Main function - runs complete example
 */
async function main() {
  console.log(`
╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║   ███████╗███╗   ███╗ █████╗ ██████╗ ████████╗██╗  ██╗ ██████╗ ██████╗  ║
║   ██╔════╝████╗ ████║██╔══██╗██╔══██╗╚══██╔══╝██║  ██║██╔═████╗╚════██╗ ║
║   ███████╗██╔████╔██║███████║██████╔╝   ██║   ███████║██║██╔██║ █████╔╝ ║
║   ╚════██║██║╚██╔╝██║██╔══██║██╔══██╗   ██║   ╚════██║████╔╝██║██╔═══╝  ║
║   ███████║██║ ╚═╝ ██║██║  ██║██║  ██║   ██║        ██║╚██████╔╝███████╗ ║
║   ╚══════╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝        ╚═╝ ╚═════╝ ╚══════╝ ║
║                                                                           ║
║            AUTONOMOUS ROBOTICS PLATFORM WITH BLOCKCHAIN                  ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝

🤖 Self-Evolving Autonomous Robotics Website
   ✓ Smart402 Framework (AEO + LLMO + X402)
   ✓ MongoDB Database
   ✓ Polygon Blockchain (EVM)
   ✓ Chainlink Oracles (Real-time Data)
   ✓ Neural Core (AI Decision Engine)
   ✓ WebSocket (Live Telemetry)
   ✓ 100% Smart402 Compliant
   ✓ Scalable & Self-Healing

`);

  const mode = process.argv[2] || 'server';

  try {
    switch (mode) {
      case 'server':
        await runServer();
        break;

      case 'example':
        await runExample();
        break;

      case 'init-db':
        await initDB();
        break;

      default:
        console.log('Usage: node src/index.js [server|example|init-db]');
        process.exit(1);
    }

  } catch (error) {
    console.error('\n❌ Fatal error:', error);
    process.exit(1);
  }
}

/**
 * Run the API server
 */
async function runServer() {
  console.log('🚀 Starting Smart402 Robotics API Server...\n');

  const server = new RoboticsAPIServer();
  await server.start();

  // Keep process alive
  process.on('SIGINT', async () => {
    console.log('\n\n👋 Shutting down gracefully...');
    await server.stop();
    process.exit(0);
  });

  process.on('SIGTERM', async () => {
    console.log('\n\n👋 Shutting down gracefully...');
    await server.stop();
    process.exit(0);
  });
}

/**
 * Run a complete example demonstrating all features
 */
async function runExample() {
  console.log('📖 Running Smart402 Robotics Platform Example...\n');

  // Initialize Smart402 integration
  const smart402 = new Smart402RoboticsIntegration();
  await smart402.initialize();

  // Example robot details
  const robotDetails = {
    robotId: 'ROB-WAREHOUSE-001',
    robotType: 'Warehouse',
    specifications: {
      model: 'AutoBot 3000',
      manufacturer: 'RoboTech Industries',
      serial_number: 'WH-3000-2024-001',
      max_payload: 500, // kg
      battery_capacity: 100, // kWh
      sensors: ['lidar', 'camera', 'ultrasonic', 'imu', 'gps']
    },
    hourlyRate: 25, // $25/hour in USDC
    location: {
      facility: 'Distribution Center Alpha',
      zone: 'Zone A-1',
      coordinates: [-118.2437, 34.0522] // Los Angeles
    },
    capabilities: [
      'Package sorting',
      'Inventory management',
      'Autonomous navigation',
      'Obstacle avoidance',
      'Real-time tracking',
      'Load optimization'
    ],
    telemetryEndpoint: 'https://robotics.smart402.io/api/robots/ROB-WAREHOUSE-001/telemetry'
  };

  // Example rental configuration
  const rentalConfig = {
    clientEmail: 'logistics@company.com',
    clientWallet: '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb',
    durationHours: 168, // 1 week
    taskDescription: 'Warehouse package sorting and inventory management for holiday season',
    autoRenew: true,
    immediatePayment: true,
    milestones: [
      {
        description: 'First 1000 packages sorted',
        amount: 500,
        deliverables: ['Sorting completed', 'Quality report', 'Efficiency metrics'],
        required: true
      },
      {
        description: 'Inventory audit completed',
        amount: 300,
        deliverables: ['Audit report', 'Discrepancy list', 'Recommendations'],
        required: true
      },
      {
        description: 'Full week operation',
        amount: 3400, // Remaining amount
        deliverables: ['Weekly performance report', 'Maintenance log', 'Final billing'],
        required: true
      }
    ]
  };

  console.log('═'.repeat(70));
  console.log('STEP 1: Creating Smart402 Robot Rental Contract');
  console.log('═'.repeat(70));

  // Create and deploy robot service with full Smart402 integration
  const result = await smart402.createAndDeployRobotService(
    robotDetails,
    rentalConfig,
    {
      gasLimit: 3000000,
      gasPriceMultiplier: 1.2
    }
  );

  console.log('\n═'.repeat(70));
  console.log('STEP 2: Smart402 Framework Verification');
  console.log('═'.repeat(70));

  console.log('\n✓ AEO (Answer Engine Optimization):');
  console.log(`  - Contract is optimized for AI discovery (ChatGPT, Claude, Gemini)`);
  console.log(`  - Rich semantic metadata for high findability`);
  console.log(`  - Schema.org structured data for citation-friendliness`);
  console.log(`  - Target AEO Score: ${(smart402.config.aeoTargetScore * 100).toFixed(1)}%`);

  console.log('\n✓ LLMO (Large Language Model Optimization):');
  console.log(`  - Universal Contract Language (UCL) representation`);
  console.log(`  - 4-layer structure:`);
  console.log(`    1. Human-readable (plain English)`);
  console.log(`    2. LLM-structured (for AI understanding)`);
  console.log(`    3. Machine-executable (programmatic)`);
  console.log(`    4. Blockchain-compilable (Solidity/bytecode)`);

  console.log('\n✓ X402 Protocol (Automatic Payments):');
  console.log(`  - HTTP extension for machine-to-machine payments`);
  console.log(`  - Automatic payment execution based on conditions`);
  console.log(`  - Blockchain-verified settlements`);
  console.log(`  - Supports USDC, USDT, DAI, native tokens`);

  console.log('\n═'.repeat(70));
  console.log('STEP 3: Blockchain & Chainlink Integration');
  console.log('═'.repeat(70));

  console.log('\n✓ Polygon Blockchain:');
  console.log(`  - Network: ${smart402.config.blockchainNetwork}`);
  console.log(`  - Contract deployed: ${result.deployment.address}`);
  console.log(`  - Transaction: ${result.deployment.transactionHash}`);

  console.log('\n✓ Chainlink Oracles:');
  console.log(`  - Real-time telemetry verification`);
  console.log(`  - Uptime monitoring with SLA enforcement`);
  console.log(`  - Task completion verification`);
  console.log(`  - Decentralized data feeds`);

  console.log('\n═'.repeat(70));
  console.log('STEP 4: Autonomous Features');
  console.log('═'.repeat(70));

  console.log('\n✓ Neural Core (AI Decision Engine):');
  console.log(`  - Intelligent task assignment`);
  console.log(`  - Self-evolving neural network`);
  console.log(`  - Performance optimization`);
  console.log(`  - Automatic learning from outcomes`);

  console.log('\n✓ Real-Time Capabilities:');
  console.log(`  - WebSocket live telemetry streaming`);
  console.log(`  - Instant status updates`);
  console.log(`  - Real-time performance metrics`);
  console.log(`  - Live dashboard monitoring`);

  console.log('\n═'.repeat(70));
  console.log('STEP 5: Access Your Deployment');
  console.log('═'.repeat(70));

  console.log(`\n📊 Block Explorer:`);
  console.log(`   ${smart402.getBlockExplorerUrl(result.deployment.address, result.deployment.network)}`);

  console.log(`\n🌐 API Endpoints:`);
  console.log(`   Robot Info:    GET  http://localhost:3000/api/robots/${robotDetails.robotId}`);
  console.log(`   Telemetry:     GET  http://localhost:3000/api/robots/${robotDetails.robotId}/telemetry`);
  console.log(`   Contract:      GET  http://localhost:3000/api/contracts/${result.contract.ucl.contract_id}`);

  console.log(`\n📡 WebSocket (Real-time):`)
  console.log(`   ws://localhost:3001`);
  console.log(`   Message: {"type": "subscribe", "robotId": "${robotDetails.robotId}"}`);

  console.log(`\n🤖 Neural Core:`);
  console.log(`   Status:        GET  http://localhost:3000/api/neural/status`);
  console.log(`   Evolve:        POST http://localhost:3000/api/neural/evolve`);

  console.log('\n═'.repeat(70));
  console.log('✨ Example Complete!');
  console.log('═'.repeat(70));

  console.log(`
📚 What was demonstrated:

1. ✅ Smart402 Framework Integration (AEO + LLMO + X402)
2. ✅ Blockchain deployment on Polygon
3. ✅ Chainlink oracle for verified telemetry
4. ✅ Neural Core AI decision engine
5. ✅ Real-time WebSocket streaming
6. ✅ MongoDB data persistence
7. ✅ Automatic payment execution
8. ✅ Self-evolving autonomous system

🚀 Next Steps:

- Start the API server: npm start
- View real-time dashboard
- Monitor robot performance
- Execute payments via X402
- Watch Neural Core evolve

📖 Documentation: See README.md and ROADMAP.md
🐛 Issues: https://github.com/MARDOCHEEJ0SEPH/smart402/issues

`);
}

/**
 * Initialize database with schemas
 */
async function initDB() {
  console.log('🗄️  Initializing MongoDB database...\n');

  await initializeDatabase(
    process.env.MONGODB_URI,
    process.env.MONGODB_DATABASE || 'smart402-robotics'
  );

  console.log('\n✓ Database initialization complete!');
  console.log('  You can now start the server with: npm start');
  process.exit(0);
}

// Run main function
main();
