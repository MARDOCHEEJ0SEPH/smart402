/**
 * Chainlink Oracle Integration for Smart402 Robotics Platform
 * Provides verified, real-time telemetry data from robots to blockchain
 */

import { ethers } from 'ethers';
import axios from 'axios';
import dotenv from 'dotenv';

dotenv.config();

export class ChainlinkIntegration {
  constructor(config = {}) {
    this.config = {
      nodeUrl: config.nodeUrl || process.env.CHAINLINK_NODE_URL,
      apiKey: config.apiKey || process.env.CHAINLINK_API_KEY,
      jobId: config.jobId || process.env.CHAINLINK_JOB_ID,
      linkTokenAddress: config.linkTokenAddress,
      oracleAddress: config.oracleAddress,
      rpcUrl: config.rpcUrl || process.env.BLOCKCHAIN_RPC_URL,
      privateKey: config.privateKey || process.env.PRIVATE_KEY
    };

    this.provider = null;
    this.signer = null;
    this.linkContract = null;
    this.oracleContract = null;
    this.pendingRequests = new Map();
  }

  /**
   * Initialize Chainlink connection
   */
  async initialize() {
    console.log('\n🔗 Initializing Chainlink Oracle Integration...');

    // Setup blockchain connection
    this.provider = new ethers.JsonRpcProvider(this.config.rpcUrl);
    this.signer = new ethers.Wallet(this.config.privateKey, this.provider);

    console.log('✓ Chainlink integration initialized');
    console.log(`  Oracle Node: ${this.config.nodeUrl}`);
    console.log(`  Wallet: ${this.signer.address}`);

    return this;
  }

  /**
   * Request verified telemetry data for a robot
   * This pushes real-time robot data to blockchain via Chainlink oracle
   */
  async requestRobotTelemetryVerification(robotId, telemetryData) {
    console.log(`\n📡 Requesting Chainlink verification for robot ${robotId}...`);

    const requestId = this.generateRequestId(robotId);

    // Prepare telemetry payload
    const payload = {
      robotId: robotId,
      timestamp: Date.now(),
      telemetry: {
        position: telemetryData.position,
        battery: telemetryData.battery,
        temperature: telemetryData.temperature,
        status: telemetryData.status,
        uptime: telemetryData.uptime,
        tasksCompleted: telemetryData.tasksCompleted
      },
      dataHash: this.hashTelemetryData(telemetryData)
    };

    try {
      // Send request to Chainlink node
      const response = await axios.post(
        `${this.config.nodeUrl}/jobs/${this.config.jobId}/runs`,
        {
          data: payload
        },
        {
          headers: {
            'Content-Type': 'application/json',
            'X-Chainlink-EA-AccessKey': this.config.apiKey,
            'X-Chainlink-EA-Secret': this.config.apiKey
          }
        }
      );

      console.log('✓ Chainlink request submitted');
      console.log(`  Request ID: ${requestId}`);
      console.log(`  Job Run ID: ${response.data.data?.id || 'pending'}`);

      // Store pending request
      this.pendingRequests.set(requestId, {
        robotId,
        telemetryData,
        payload,
        timestamp: Date.now(),
        status: 'pending'
      });

      return {
        requestId,
        chainlinkJobRunId: response.data.data?.id,
        status: 'pending',
        dataHash: payload.dataHash
      };

    } catch (error) {
      console.error('✗ Chainlink request failed:', error.message);
      throw error;
    }
  }

  /**
   * Request uptime verification for SLA monitoring
   */
  async requestUptimeVerification(robotId, startTime, endTime) {
    console.log(`\n⏱️  Requesting uptime verification for ${robotId}...`);

    const requestId = this.generateRequestId(`${robotId}-uptime`);

    const payload = {
      robotId: robotId,
      verificationType: 'uptime',
      timeRange: {
        start: startTime,
        end: endTime
      },
      timestamp: Date.now()
    };

    try {
      const response = await axios.post(
        `${this.config.nodeUrl}/jobs/${this.config.jobId}/runs`,
        {
          data: payload
        },
        {
          headers: {
            'Content-Type': 'application/json',
            'X-Chainlink-EA-AccessKey': this.config.apiKey
          }
        }
      );

      this.pendingRequests.set(requestId, {
        robotId,
        payload,
        timestamp: Date.now(),
        status: 'pending'
      });

      console.log('✓ Uptime verification request submitted');
      console.log(`  Request ID: ${requestId}`);

      return {
        requestId,
        chainlinkJobRunId: response.data.data?.id,
        status: 'pending'
      };

    } catch (error) {
      console.error('✗ Uptime verification request failed:', error.message);
      throw error;
    }
  }

  /**
   * Request task completion verification
   */
  async requestTaskVerification(taskId, robotId, taskData) {
    console.log(`\n✅ Requesting task completion verification...`);

    const requestId = this.generateRequestId(`task-${taskId}`);

    const payload = {
      taskId: taskId,
      robotId: robotId,
      verificationType: 'task_completion',
      taskData: {
        type: taskData.type,
        status: taskData.status,
        completedAt: taskData.completedAt,
        duration: taskData.duration,
        successMetrics: taskData.successMetrics
      },
      timestamp: Date.now()
    };

    try {
      const response = await axios.post(
        `${this.config.nodeUrl}/jobs/${this.config.jobId}/runs`,
        {
          data: payload
        },
        {
          headers: {
            'Content-Type': 'application/json',
            'X-Chainlink-EA-AccessKey': this.config.apiKey
          }
        }
      );

      this.pendingRequests.set(requestId, {
        taskId,
        robotId,
        payload,
        timestamp: Date.now(),
        status: 'pending'
      });

      console.log('✓ Task verification request submitted');
      console.log(`  Request ID: ${requestId}`);
      console.log(`  Task ID: ${taskId}`);

      return {
        requestId,
        chainlinkJobRunId: response.data.data?.id,
        status: 'pending'
      };

    } catch (error) {
      console.error('✗ Task verification request failed:', error.message);
      throw error;
    }
  }

  /**
   * Check verification status
   */
  async checkVerificationStatus(requestId) {
    const request = this.pendingRequests.get(requestId);

    if (!request) {
      throw new Error(`Request ${requestId} not found`);
    }

    try {
      // Check Chainlink job run status
      const response = await axios.get(
        `${this.config.nodeUrl}/runs/${request.chainlinkJobRunId}`,
        {
          headers: {
            'X-Chainlink-EA-AccessKey': this.config.apiKey
          }
        }
      );

      const status = response.data.data?.attributes?.status || 'unknown';

      if (status === 'completed') {
        request.status = 'verified';
        request.result = response.data.data?.attributes?.result;

        console.log(`✓ Verification completed for ${requestId}`);
        console.log(`  Result: ${JSON.stringify(request.result)}`);

        return {
          requestId,
          status: 'verified',
          verified: true,
          result: request.result,
          timestamp: Date.now()
        };
      } else if (status === 'errored') {
        request.status = 'failed';

        console.error(`✗ Verification failed for ${requestId}`);

        return {
          requestId,
          status: 'failed',
          verified: false,
          error: response.data.data?.attributes?.error,
          timestamp: Date.now()
        };
      } else {
        return {
          requestId,
          status: 'pending',
          verified: null,
          timestamp: Date.now()
        };
      }

    } catch (error) {
      console.error(`✗ Error checking status for ${requestId}:`, error.message);
      return {
        requestId,
        status: 'error',
        verified: false,
        error: error.message,
        timestamp: Date.now()
      };
    }
  }

  /**
   * Create Chainlink data feed for continuous monitoring
   */
  async createDataFeed(robotId, config = {}) {
    console.log(`\n📊 Creating Chainlink data feed for ${robotId}...`);

    const feedConfig = {
      robotId: robotId,
      updateInterval: config.updateInterval || 300, // 5 minutes
      telemetryFields: config.fields || [
        'position',
        'battery',
        'temperature',
        'status',
        'uptime'
      ],
      thresholds: config.thresholds || {
        battery: { min: 20, critical: 10 },
        temperature: { max: 80, critical: 90 },
        uptime: { min: 0.95 }
      },
      webhook: config.webhook,
      autoVerify: config.autoVerify !== false
    };

    try {
      // Create Chainlink job spec for continuous monitoring
      const jobSpec = this.generateJobSpec(feedConfig);

      const response = await axios.post(
        `${this.config.nodeUrl}/jobs`,
        jobSpec,
        {
          headers: {
            'Content-Type': 'application/json',
            'X-Chainlink-EA-AccessKey': this.config.apiKey
          }
        }
      );

      console.log('✓ Data feed created');
      console.log(`  Feed ID: ${response.data.data?.id}`);
      console.log(`  Update Interval: ${feedConfig.updateInterval}s`);

      return {
        feedId: response.data.data?.id,
        robotId: robotId,
        config: feedConfig,
        status: 'active'
      };

    } catch (error) {
      console.error('✗ Failed to create data feed:', error.message);
      throw error;
    }
  }

  /**
   * Generate Chainlink job specification
   */
  generateJobSpec(config) {
    return {
      initiators: [
        {
          type: 'cron',
          params: {
            schedule: `@every ${config.updateInterval}s`
          }
        }
      ],
      tasks: [
        {
          type: 'httpget',
          params: {
            get: `https://robotics.smart402.io/api/robots/${config.robotId}/telemetry`,
            headers: {
              'Authorization': `Bearer ${process.env.API_KEY}`
            }
          }
        },
        {
          type: 'jsonparse',
          params: {
            path: config.telemetryFields
          }
        },
        {
          type: 'multiply',
          params: {
            times: 100 // Convert percentages
          }
        },
        {
          type: 'ethuint256'
        },
        {
          type: 'ethtx',
          params: {
            address: this.config.oracleAddress,
            functionSelector: 'fulfillOracleRequest(bytes32,uint256)'
          }
        }
      ]
    };
  }

  /**
   * Subscribe to Chainlink events for real-time updates
   */
  async subscribeToVerifications(callback) {
    console.log('\n🔔 Subscribing to Chainlink verification events...');

    // In production, this would listen to blockchain events
    // For now, we'll use polling

    setInterval(async () => {
      for (const [requestId, request] of this.pendingRequests.entries()) {
        if (request.status === 'pending') {
          const status = await this.checkVerificationStatus(requestId);

          if (status.status !== 'pending' && callback) {
            callback({
              requestId,
              robotId: request.robotId,
              status: status.status,
              verified: status.verified,
              result: status.result,
              timestamp: status.timestamp
            });

            // Remove from pending if completed or failed
            if (status.status === 'verified' || status.status === 'failed') {
              this.pendingRequests.delete(requestId);
            }
          }
        }
      }
    }, 30000); // Check every 30 seconds

    console.log('✓ Subscribed to verification events');
  }

  /**
   * Get verification history for a robot
   */
  getVerificationHistory(robotId) {
    const history = [];

    for (const [requestId, request] of this.pendingRequests.entries()) {
      if (request.robotId === robotId) {
        history.push({
          requestId,
          timestamp: request.timestamp,
          status: request.status,
          payload: request.payload
        });
      }
    }

    return history.sort((a, b) => b.timestamp - a.timestamp);
  }

  /**
   * Get real-time data feed for robot
   */
  async getRobotDataFeed(robotId) {
    try {
      // Fetch latest verified telemetry from Chainlink
      const response = await axios.get(
        `${this.config.nodeUrl}/feeds/${robotId}`,
        {
          headers: {
            'X-Chainlink-EA-AccessKey': this.config.apiKey
          }
        }
      );

      return {
        robotId,
        data: response.data.data,
        verified: true,
        timestamp: Date.now()
      };

    } catch (error) {
      console.error(`✗ Failed to fetch data feed for ${robotId}:`, error.message);
      return null;
    }
  }

  // ==================== Helper Functions ====================

  generateRequestId(identifier) {
    return ethers.id(`chainlink-${identifier}-${Date.now()}`).substring(0, 42);
  }

  hashTelemetryData(telemetryData) {
    const dataString = JSON.stringify(telemetryData);
    return ethers.id(dataString);
  }

  /**
   * Get integration status
   */
  getStatus() {
    return {
      connected: this.provider !== null,
      nodeUrl: this.config.nodeUrl,
      pendingRequests: this.pendingRequests.size,
      walletAddress: this.signer?.address
    };
  }
}

export default ChainlinkIntegration;
