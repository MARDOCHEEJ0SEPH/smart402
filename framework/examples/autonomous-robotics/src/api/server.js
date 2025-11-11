/**
 * Smart402 Autonomous Robotics Platform - API Server
 * Express + WebSocket server with real-time telemetry streaming
 */

import express from 'express';
import { WebSocketServer } from 'ws';
import http from 'http';
import cors from 'cors';
import helmet from 'helmet';
import compression from 'compression';
import morgan from 'morgan';
import dotenv from 'dotenv';
import { MongoClient } from 'mongodb';

// Import Smart402 components
import { Smart402RoboticsIntegration } from '../core/Smart402Integration.js';
import { NeuralCore } from '../ai/NeuralCore.js';
import { ChainlinkIntegration } from '../blockchain/ChainlinkIntegration.js';

dotenv.config();

export class RoboticsAPIServer {
  constructor(config = {}) {
    this.config = {
      port: config.port || process.env.PORT || 3000,
      wsPort: config.wsPort || process.env.WS_PORT || 3001,
      mongoUri: config.mongoUri || process.env.MONGODB_URI,
      dbName: config.dbName || process.env.MONGODB_DATABASE || 'smart402-robotics'
    };

    this.app = express();
    this.server = null;
    this.wss = null;
    this.mongoClient = null;
    this.db = null;

    // Smart402 components
    this.smart402 = null;
    this.neuralCore = null;
    this.chainlink = null;

    // WebSocket clients tracking
    this.wsClients = new Map();
    this.robotSubscriptions = new Map();
  }

  /**
   * Initialize all components
   */
  async initialize() {
    console.log('\n🚀 Initializing Smart402 Robotics API Server...');

    // Connect to MongoDB
    await this.connectDatabase();

    // Initialize Smart402 components
    this.smart402 = new Smart402RoboticsIntegration();
    await this.smart402.initialize();

    this.neuralCore = new NeuralCore({
      evolutionEnabled: true,
      evolutionFrequency: 3600000 // 1 hour
    });
    await this.neuralCore.initialize();

    this.chainlink = new ChainlinkIntegration();
    await this.chainlink.initialize();

    // Setup Express middleware
    this.setupMiddleware();

    // Setup routes
    this.setupRoutes();

    // Setup WebSocket server
    this.setupWebSocketServer();

    // Start evolution scheduler
    this.startEvolutionScheduler();

    console.log('✓ API Server initialized successfully');
  }

  /**
   * Connect to MongoDB
   */
  async connectDatabase() {
    try {
      this.mongoClient = new MongoClient(this.config.mongoUri);
      await this.mongoClient.connect();
      this.db = this.mongoClient.db(this.config.dbName);

      console.log('✓ Connected to MongoDB');
      console.log(`  Database: ${this.config.dbName}`);

    } catch (error) {
      console.error('✗ MongoDB connection failed:', error);
      throw error;
    }
  }

  /**
   * Setup Express middleware
   */
  setupMiddleware() {
    this.app.use(helmet());
    this.app.use(cors());
    this.app.use(compression());
    this.app.use(express.json());
    this.app.use(express.urlencoded({ extended: true }));
    this.app.use(morgan('combined'));
  }

  /**
   * Setup API routes
   */
  setupRoutes() {
    // Health check
    this.app.get('/health', (req, res) => {
      res.json({
        status: 'healthy',
        timestamp: new Date().toISOString(),
        neuralCore: this.neuralCore.getStatus(),
        chainlink: this.chainlink.getStatus()
      });
    });

    // Robot management routes
    this.app.get('/api/robots', this.handleGetRobots.bind(this));
    this.app.get('/api/robots/:robotId', this.handleGetRobot.bind(this));
    this.app.post('/api/robots', this.handleCreateRobot.bind(this));
    this.app.put('/api/robots/:robotId', this.handleUpdateRobot.bind(this));
    this.app.get('/api/robots/:robotId/telemetry', this.handleGetTelemetry.bind(this));

    // Contract routes
    this.app.post('/api/contracts/create', this.handleCreateContract.bind(this));
    this.app.post('/api/contracts/:contractId/deploy', this.handleDeployContract.bind(this));
    this.app.post('/api/contracts/:contractId/payment', this.handleExecutePayment.bind(this));
    this.app.get('/api/contracts/:contractId', this.handleGetContract.bind(this));
    this.app.get('/api/contracts', this.handleGetContracts.bind(this));

    // Task management routes
    this.app.post('/api/tasks', this.handleCreateTask.bind(this));
    this.app.post('/api/tasks/:taskId/assign', this.handleAssignTask.bind(this));
    this.app.get('/api/tasks/:taskId', this.handleGetTask.bind(this));
    this.app.put('/api/tasks/:taskId/complete', this.handleCompleteTask.bind(this));

    // Neural Core routes
    this.app.get('/api/neural/status', this.handleGetNeuralStatus.bind(this));
    this.app.post('/api/neural/evolve', this.handleTriggerEvolution.bind(this));
    this.app.post('/api/neural/decision', this.handleMakeDecision.bind(this));

    // Chainlink routes
    this.app.post('/api/chainlink/verify-telemetry', this.handleVerifyTelemetry.bind(this));
    this.app.get('/api/chainlink/status/:requestId', this.handleCheckVerification.bind(this));
    this.app.post('/api/chainlink/datafeed', this.handleCreateDataFeed.bind(this));

    // Analytics routes
    this.app.get('/api/analytics/fleet', this.handleGetFleetAnalytics.bind(this));
    this.app.get('/api/analytics/performance', this.handleGetPerformanceAnalytics.bind(this));

    // Webhook endpoint for Chainlink callbacks
    this.app.post('/api/webhooks/contract-events', this.handleContractWebhook.bind(this));

    // 404 handler
    this.app.use((req, res) => {
      res.status(404).json({ error: 'Not found' });
    });

    // Error handler
    this.app.use((err, req, res, next) => {
      console.error('API Error:', err);
      res.status(500).json({ error: 'Internal server error' });
    });
  }

  /**
   * Setup WebSocket server for real-time telemetry
   */
  setupWebSocketServer() {
    this.wss = new WebSocketServer({ port: this.config.wsPort });

    this.wss.on('connection', (ws, req) => {
      const clientId = this.generateClientId();
      this.wsClients.set(clientId, ws);

      console.log(`📱 WebSocket client connected: ${clientId}`);

      ws.on('message', (message) => {
        this.handleWebSocketMessage(clientId, ws, message);
      });

      ws.on('close', () => {
        console.log(`📱 WebSocket client disconnected: ${clientId}`);
        this.wsClients.delete(clientId);
        this.cleanupSubscriptions(clientId);
      });

      ws.on('error', (error) => {
        console.error(`WebSocket error for ${clientId}:`, error);
      });

      // Send welcome message
      ws.send(JSON.stringify({
        type: 'connected',
        clientId: clientId,
        timestamp: Date.now()
      }));
    });

    console.log(`✓ WebSocket server listening on port ${this.config.wsPort}`);
  }

  /**
   * Handle WebSocket messages
   */
  handleWebSocketMessage(clientId, ws, message) {
    try {
      const data = JSON.parse(message.toString());

      switch (data.type) {
        case 'subscribe':
          this.handleSubscribe(clientId, ws, data.robotId);
          break;

        case 'unsubscribe':
          this.handleUnsubscribe(clientId, data.robotId);
          break;

        case 'ping':
          ws.send(JSON.stringify({ type: 'pong', timestamp: Date.now() }));
          break;

        default:
          ws.send(JSON.stringify({ type: 'error', message: 'Unknown message type' }));
      }
    } catch (error) {
      console.error('WebSocket message error:', error);
      ws.send(JSON.stringify({ type: 'error', message: 'Invalid message format' }));
    }
  }

  /**
   * Handle robot subscription for real-time updates
   */
  handleSubscribe(clientId, ws, robotId) {
    if (!this.robotSubscriptions.has(robotId)) {
      this.robotSubscriptions.set(robotId, new Set());
    }

    this.robotSubscriptions.get(robotId).add(clientId);

    ws.send(JSON.stringify({
      type: 'subscribed',
      robotId: robotId,
      timestamp: Date.now()
    }));

    console.log(`📡 Client ${clientId} subscribed to robot ${robotId}`);
  }

  /**
   * Handle unsubscribe
   */
  handleUnsubscribe(clientId, robotId) {
    if (this.robotSubscriptions.has(robotId)) {
      this.robotSubscriptions.get(robotId).delete(clientId);

      if (this.robotSubscriptions.get(robotId).size === 0) {
        this.robotSubscriptions.delete(robotId);
      }
    }
  }

  /**
   * Broadcast telemetry update to subscribed clients
   */
  broadcastTelemetry(robotId, telemetryData) {
    if (!this.robotSubscriptions.has(robotId)) {
      return;
    }

    const message = JSON.stringify({
      type: 'telemetry',
      robotId: robotId,
      data: telemetryData,
      timestamp: Date.now()
    });

    for (const clientId of this.robotSubscriptions.get(robotId)) {
      const ws = this.wsClients.get(clientId);
      if (ws && ws.readyState === ws.OPEN) {
        ws.send(message);
      }
    }
  }

  // ==================== API Route Handlers ====================

  async handleGetRobots(req, res) {
    try {
      const status = req.query.status;
      const type = req.query.type;
      const limit = parseInt(req.query.limit) || 100;
      const skip = parseInt(req.query.skip) || 0;

      const query = {};
      if (status) query.status = status;
      if (type) query.type = type;

      const robots = await this.db.collection('robots')
        .find(query)
        .limit(limit)
        .skip(skip)
        .sort({ created_at: -1 })
        .toArray();

      const total = await this.db.collection('robots').countDocuments(query);

      res.json({
        robots,
        total,
        limit,
        skip
      });

    } catch (error) {
      console.error('Error fetching robots:', error);
      res.status(500).json({ error: 'Failed to fetch robots' });
    }
  }

  async handleGetRobot(req, res) {
    try {
      const { robotId } = req.params;

      const robot = await this.db.collection('robots').findOne({ robot_id: robotId });

      if (!robot) {
        return res.status(404).json({ error: 'Robot not found' });
      }

      // Get latest telemetry
      const telemetry = await this.db.collection('telemetry')
        .find({ robot_id: robotId })
        .sort({ timestamp: -1 })
        .limit(100)
        .toArray();

      res.json({
        robot,
        telemetry
      });

    } catch (error) {
      console.error('Error fetching robot:', error);
      res.status(500).json({ error: 'Failed to fetch robot' });
    }
  }

  async handleCreateRobot(req, res) {
    try {
      const robotData = {
        robot_id: req.body.robot_id,
        type: req.body.type,
        status: 'idle',
        location: req.body.location,
        specifications: req.body.specifications || {},
        telemetry: {
          uptime: 0,
          tasks_completed: 0,
          tasks_failed: 0,
          errors: 0,
          battery_level: 100,
          temperature: 25
        },
        contract_id: null,
        blockchain_address: null,
        owner: req.body.owner || {},
        created_at: new Date(),
        updated_at: new Date()
      };

      await this.db.collection('robots').insertOne(robotData);

      res.status(201).json({
        message: 'Robot created successfully',
        robot: robotData
      });

    } catch (error) {
      console.error('Error creating robot:', error);
      res.status(500).json({ error: 'Failed to create robot' });
    }
  }

  async handleUpdateRobot(req, res) {
    try {
      const { robotId } = req.params;
      const updates = req.body;

      updates.updated_at = new Date();

      const result = await this.db.collection('robots').updateOne(
        { robot_id: robotId },
        { $set: updates }
      );

      if (result.matchedCount === 0) {
        return res.status(404).json({ error: 'Robot not found' });
      }

      res.json({ message: 'Robot updated successfully' });

    } catch (error) {
      console.error('Error updating robot:', error);
      res.status(500).json({ error: 'Failed to update robot' });
    }
  }

  async handleGetTelemetry(req, res) {
    try {
      const { robotId } = req.params;
      const limit = parseInt(req.query.limit) || 100;
      const dataType = req.query.type;

      const query = { robot_id: robotId };
      if (dataType) query.data_type = dataType;

      const telemetry = await this.db.collection('telemetry')
        .find(query)
        .sort({ timestamp: -1 })
        .limit(limit)
        .toArray();

      res.json({ robotId, telemetry, count: telemetry.length });

    } catch (error) {
      console.error('Error fetching telemetry:', error);
      res.status(500).json({ error: 'Failed to fetch telemetry' });
    }
  }

  async handleCreateContract(req, res) {
    try {
      const { robotDetails, rentalConfig } = req.body;

      // Create Smart402 contract
      const contract = await this.smart402.createRobotRentalContract(
        robotDetails,
        rentalConfig
      );

      // Store in database
      await this.db.collection('contracts').insertOne({
        contract_id: contract.ucl.contract_id,
        type: contract.ucl.contract_type,
        status: 'pending',
        parties: contract.ucl.parties,
        payment: contract.ucl.payment,
        conditions: contract.ucl.conditions,
        ucl: contract.ucl,
        aeo_score: contract.aeo_score || 0,
        robot_ids: [robotDetails.robotId],
        created_at: new Date(),
        updated_at: new Date()
      });

      res.status(201).json({
        message: 'Contract created successfully',
        contract: {
          contractId: contract.ucl.contract_id,
          type: contract.ucl.contract_type,
          aeoScore: contract.aeo_score
        }
      });

    } catch (error) {
      console.error('Error creating contract:', error);
      res.status(500).json({ error: 'Failed to create contract' });
    }
  }

  async handleDeployContract(req, res) {
    try {
      const { contractId } = req.params;

      const contractDoc = await this.db.collection('contracts').findOne({ contract_id: contractId });

      if (!contractDoc) {
        return res.status(404).json({ error: 'Contract not found' });
      }

      // Deploy to blockchain
      // (Implementation would use Smart402 SDK)

      res.json({
        message: 'Contract deployment initiated',
        contractId: contractId
      });

    } catch (error) {
      console.error('Error deploying contract:', error);
      res.status(500).json({ error: 'Failed to deploy contract' });
    }
  }

  async handleExecutePayment(req, res) {
    try {
      const { contractId } = req.params;
      const { amount } = req.body;

      // Execute X402 payment
      // (Implementation would use Smart402 SDK)

      res.json({
        message: 'Payment executed successfully',
        contractId: contractId,
        amount: amount
      });

    } catch (error) {
      console.error('Error executing payment:', error);
      res.status(500).json({ error: 'Failed to execute payment' });
    }
  }

  async handleGetContract(req, res) {
    try {
      const { contractId } = req.params;

      const contract = await this.db.collection('contracts').findOne({ contract_id: contractId });

      if (!contract) {
        return res.status(404).json({ error: 'Contract not found' });
      }

      res.json({ contract });

    } catch (error) {
      console.error('Error fetching contract:', error);
      res.status(500).json({ error: 'Failed to fetch contract' });
    }
  }

  async handleGetContracts(req, res) {
    try {
      const status = req.query.status;
      const limit = parseInt(req.query.limit) || 50;

      const query = {};
      if (status) query.status = status;

      const contracts = await this.db.collection('contracts')
        .find(query)
        .limit(limit)
        .sort({ created_at: -1 })
        .toArray();

      res.json({ contracts, count: contracts.length });

    } catch (error) {
      console.error('Error fetching contracts:', error);
      res.status(500).json({ error: 'Failed to fetch contracts' });
    }
  }

  async handleCreateTask(req, res) {
    try {
      const taskData = {
        task_id: req.body.task_id || `TASK-${Date.now()}`,
        robot_id: req.body.robot_id || null,
        type: req.body.type,
        status: 'pending',
        priority: req.body.priority || 'medium',
        details: req.body.details || {},
        contract_id: req.body.contract_id || null,
        created_at: new Date(),
        updated_at: new Date()
      };

      await this.db.collection('tasks').insertOne(taskData);

      res.status(201).json({
        message: 'Task created successfully',
        task: taskData
      });

    } catch (error) {
      console.error('Error creating task:', error);
      res.status(500).json({ error: 'Failed to create task' });
    }
  }

  async handleAssignTask(req, res) {
    try {
      const { taskId } = req.params;

      const task = await this.db.collection('tasks').findOne({ task_id: taskId });

      if (!task) {
        return res.status(404).json({ error: 'Task not found' });
      }

      // Get available robots
      const robots = await this.db.collection('robots')
        .find({ status: { $in: ['active', 'idle'] } })
        .toArray();

      // Use Neural Core to make assignment decision
      const decision = await this.neuralCore.makeTaskAssignmentDecision(task, robots);

      if (decision.selectedRobot) {
        // Assign task
        await this.db.collection('tasks').updateOne(
          { task_id: taskId },
          {
            $set: {
              robot_id: decision.selectedRobot,
              status: 'assigned',
              neural_decision: decision,
              updated_at: new Date()
            }
          }
        );

        // Update robot status
        await this.db.collection('robots').updateOne(
          { robot_id: decision.selectedRobot },
          { $set: { status: 'busy', updated_at: new Date() } }
        );

        res.json({
          message: 'Task assigned successfully',
          taskId: taskId,
          robotId: decision.selectedRobot,
          decision: decision
        });
      } else {
        res.json({
          message: 'No suitable robot found',
          taskId: taskId,
          decision: decision
        });
      }

    } catch (error) {
      console.error('Error assigning task:', error);
      res.status(500).json({ error: 'Failed to assign task' });
    }
  }

  async handleGetTask(req, res) {
    try {
      const { taskId } = req.params;

      const task = await this.db.collection('tasks').findOne({ task_id: taskId });

      if (!task) {
        return res.status(404).json({ error: 'Task not found' });
      }

      res.json({ task });

    } catch (error) {
      console.error('Error fetching task:', error);
      res.status(500).json({ error: 'Failed to fetch task' });
    }
  }

  async handleCompleteTask(req, res) {
    try {
      const { taskId } = req.params;
      const { successful, duration } = req.body;

      await this.db.collection('tasks').updateOne(
        { task_id: taskId },
        {
          $set: {
            status: 'completed',
            'execution.completed_at': new Date(),
            'execution.duration': duration,
            'execution.success_rate': successful ? 1.0 : 0.0,
            updated_at: new Date()
          }
        }
      );

      res.json({ message: 'Task marked as completed', taskId });

    } catch (error) {
      console.error('Error completing task:', error);
      res.status(500).json({ error: 'Failed to complete task' });
    }
  }

  async handleGetNeuralStatus(req, res) {
    try {
      const status = this.neuralCore.getStatus();
      res.json({ neuralCore: status });

    } catch (error) {
      console.error('Error getting neural status:', error);
      res.status(500).json({ error: 'Failed to get neural status' });
    }
  }

  async handleTriggerEvolution(req, res) {
    try {
      const result = await this.neuralCore.evolve();

      res.json({
        message: 'Evolution completed',
        result: result
      });

    } catch (error) {
      console.error('Error triggering evolution:', error);
      res.status(500).json({ error: 'Failed to trigger evolution' });
    }
  }

  async handleMakeDecision(req, res) {
    try {
      const { task, robots } = req.body;

      const decision = await this.neuralCore.makeTaskAssignmentDecision(task, robots);

      res.json({ decision });

    } catch (error) {
      console.error('Error making decision:', error);
      res.status(500).json({ error: 'Failed to make decision' });
    }
  }

  async handleVerifyTelemetry(req, res) {
    try {
      const { robotId, telemetryData } = req.body;

      const result = await this.chainlink.requestRobotTelemetryVerification(robotId, telemetryData);

      res.json({
        message: 'Verification request submitted',
        result: result
      });

    } catch (error) {
      console.error('Error requesting verification:', error);
      res.status(500).json({ error: 'Failed to request verification' });
    }
  }

  async handleCheckVerification(req, res) {
    try {
      const { requestId } = req.params;

      const status = await this.chainlink.checkVerificationStatus(requestId);

      res.json({ status });

    } catch (error) {
      console.error('Error checking verification:', error);
      res.status(500).json({ error: 'Failed to check verification' });
    }
  }

  async handleCreateDataFeed(req, res) {
    try {
      const { robotId, config } = req.body;

      const feed = await this.chainlink.createDataFeed(robotId, config);

      res.json({
        message: 'Data feed created',
        feed: feed
      });

    } catch (error) {
      console.error('Error creating data feed:', error);
      res.status(500).json({ error: 'Failed to create data feed' });
    }
  }

  async handleGetFleetAnalytics(req, res) {
    try {
      const totalRobots = await this.db.collection('robots').countDocuments();
      const activeRobots = await this.db.collection('robots').countDocuments({ status: 'active' });
      const totalTasks = await this.db.collection('tasks').countDocuments();
      const completedTasks = await this.db.collection('tasks').countDocuments({ status: 'completed' });

      res.json({
        fleet: {
          totalRobots,
          activeRobots,
          idleRobots: totalRobots - activeRobots,
          utilization: activeRobots / totalRobots
        },
        tasks: {
          totalTasks,
          completedTasks,
          successRate: completedTasks / totalTasks
        }
      });

    } catch (error) {
      console.error('Error fetching fleet analytics:', error);
      res.status(500).json({ error: 'Failed to fetch analytics' });
    }
  }

  async handleGetPerformanceAnalytics(req, res) {
    try {
      const analytics = await this.db.collection('analytics')
        .find({ metric_type: 'fleet_performance' })
        .sort({ timestamp: -1 })
        .limit(100)
        .toArray();

      res.json({ analytics });

    } catch (error) {
      console.error('Error fetching performance analytics:', error);
      res.status(500).json({ error: 'Failed to fetch performance analytics' });
    }
  }

  async handleContractWebhook(req, res) {
    try {
      const event = req.body;

      console.log('📥 Received contract webhook:', event);

      // Process event based on type
      switch (event.type) {
        case 'condition_check':
          // Handle condition check result
          break;

        case 'payment_executed':
          // Handle payment execution
          break;

        case 'contract_completed':
          // Handle contract completion
          break;

        default:
          console.log('Unknown event type:', event.type);
      }

      res.json({ message: 'Webhook received' });

    } catch (error) {
      console.error('Error handling webhook:', error);
      res.status(500).json({ error: 'Webhook processing failed' });
    }
  }

  // ==================== Utility Functions ====================

  startEvolutionScheduler() {
    // Schedule Neural Core evolution every hour
    setInterval(async () => {
      console.log('\n⏰ Scheduled evolution check...');
      try {
        await this.neuralCore.evolve();
      } catch (error) {
        console.error('Evolution failed:', error);
      }
    }, this.neuralCore.config.evolutionFrequency);
  }

  generateClientId() {
    return `client-${Date.now()}-${Math.random().toString(36).substring(7)}`;
  }

  cleanupSubscriptions(clientId) {
    for (const [robotId, clients] of this.robotSubscriptions.entries()) {
      clients.delete(clientId);
      if (clients.size === 0) {
        this.robotSubscriptions.delete(robotId);
      }
    }
  }

  /**
   * Start the server
   */
  async start() {
    await this.initialize();

    this.server = http.createServer(this.app);

    this.server.listen(this.config.port, () => {
      console.log('\n═'.repeat(60));
      console.log('🤖 Smart402 Autonomous Robotics Platform - ONLINE');
      console.log('═'.repeat(60));
      console.log(`📡 API Server:       http://localhost:${this.config.port}`);
      console.log(`🌐 WebSocket Server: ws://localhost:${this.config.wsPort}`);
      console.log(`🧠 Neural Core:      Generation ${this.neuralCore.currentGeneration}`);
      console.log(`🔗 Chainlink:        ${this.chainlink.config.nodeUrl}`);
      console.log(`💾 MongoDB:          ${this.config.dbName}`);
      console.log('═'.repeat(60));
      console.log('\n✨ Server ready to accept connections\n');
    });
  }

  /**
   * Stop the server
   */
  async stop() {
    console.log('\n🛑 Shutting down server...');

    // Close WebSocket connections
    if (this.wss) {
      for (const ws of this.wsClients.values()) {
        ws.close();
      }
      this.wss.close();
    }

    // Close HTTP server
    if (this.server) {
      this.server.close();
    }

    // Close MongoDB connection
    if (this.mongoClient) {
      await this.mongoClient.close();
    }

    console.log('✓ Server stopped');
  }
}

export default RoboticsAPIServer;

// Run server if executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
  const server = new RoboticsAPIServer();
  server.start().catch(error => {
    console.error('Failed to start server:', error);
    process.exit(1);
  });

  // Handle graceful shutdown
  process.on('SIGINT', async () => {
    await server.stop();
    process.exit(0);
  });
}
