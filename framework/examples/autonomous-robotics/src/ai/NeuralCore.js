/**
 * Smart402 Autonomous Robotics - Neural Core
 * AI-powered decision engine with self-evolution capabilities
 * Integrates with Smart402 framework for optimized contract generation
 */

import * as tf from '@tensorflow/tfjs-node';
import brain from 'brain.js';
import { SimpleLinearRegression, PolynomialRegression } from 'ml-regression';

export class NeuralCore {
  constructor(config = {}) {
    this.config = {
      learningRate: config.learningRate || 0.01,
      evolutionEnabled: config.evolutionEnabled !== false,
      evolutionFrequency: config.evolutionFrequency || 3600000, // 1 hour
      minAccuracyThreshold: config.minAccuracyThreshold || 0.85,
      autoOptimize: config.autoOptimize !== false
    };

    this.currentGeneration = 0;
    this.model = null;
    this.decisionNetwork = null;
    this.performanceHistory = [];
    this.evolutionHistory = [];
    this.isTraining = false;
  }

  /**
   * Initialize Neural Core with TensorFlow.js model
   */
  async initialize() {
    console.log('\n🧠 Initializing Neural Core...');

    // Create deep learning model for robot task assignment
    this.model = tf.sequential({
      layers: [
        tf.layers.dense({ inputShape: [15], units: 64, activation: 'relu' }),
        tf.layers.dropout({ rate: 0.2 }),
        tf.layers.dense({ units: 32, activation: 'relu' }),
        tf.layers.dropout({ rate: 0.2 }),
        tf.layers.dense({ units: 16, activation: 'relu' }),
        tf.layers.dense({ units: 8, activation: 'softmax' }) // 8 possible decisions
      ]
    });

    this.model.compile({
      optimizer: tf.train.adam(this.config.learningRate),
      loss: 'categoricalCrossentropy',
      metrics: ['accuracy']
    });

    // Initialize Brain.js neural network for real-time decisions
    this.decisionNetwork = new brain.NeuralNetwork({
      hiddenLayers: [10, 8, 6],
      activation: 'sigmoid',
      learningRate: this.config.learningRate
    });

    console.log('✓ Neural Core initialized');
    console.log(`  Learning Rate: ${this.config.learningRate}`);
    console.log(`  Evolution: ${this.config.evolutionEnabled ? 'Enabled' : 'Disabled'}`);
    console.log(`  Generation: ${this.currentGeneration}`);

    return this;
  }

  /**
   * Make intelligent decision about robot task assignment
   * Uses AI to optimize which robot should handle which task
   */
  async makeTaskAssignmentDecision(task, availableRobots) {
    const features = this.extractTaskFeatures(task, availableRobots);

    // Use TensorFlow model for complex decisions
    const inputTensor = tf.tensor2d([features], [1, 15]);
    const prediction = this.model.predict(inputTensor);
    const probabilities = await prediction.data();

    inputTensor.dispose();
    prediction.dispose();

    // Interpret probabilities to select best robot
    const decision = this.interpretDecisionProbabilities(
      probabilities,
      availableRobots,
      task
    );

    // Log decision for learning
    this.logDecision(decision, features);

    return decision;
  }

  /**
   * Extract features from task and robots for AI decision making
   */
  extractTaskFeatures(task, robots) {
    const features = [
      // Task features (normalized 0-1)
      this.normalizeTaskType(task.type),
      this.normalizeTaskPriority(task.priority),
      task.payload?.weight ? task.payload.weight / 1000 : 0,
      task.payload?.distance ? task.payload.distance / 10000 : 0,
      task.payload?.complexity ? task.payload.complexity / 100 : 0,

      // Fleet features
      robots.length / 100, // Normalized robot count
      this.calculateAverageFleetUptime(robots),
      this.calculateAverageFleetBatteryLevel(robots),

      // Environmental features
      this.getTimeOfDayFactor(),
      this.getWeekdayFactor(),
      this.getLoadFactor(robots),

      // Historical performance
      this.getHistoricalSuccessRate(),
      this.getAverageTaskDuration(),
      this.getRecentErrorRate(),

      // Random factors for exploration
      Math.random() * 0.1
    ];

    return features;
  }

  /**
   * Interpret AI prediction probabilities into actionable decisions
   */
  interpretDecisionProbabilities(probabilities, robots, task) {
    // Decision types based on probability output
    const decisionTypes = [
      'assign_highest_performance',
      'assign_nearest',
      'assign_lowest_load',
      'assign_best_battery',
      'assign_specialist',
      'defer_task',
      'split_task',
      'escalate_task'
    ];

    // Get highest probability decision type
    let maxProb = 0;
    let selectedType = decisionTypes[0];

    for (let i = 0; i < probabilities.length; i++) {
      if (probabilities[i] > maxProb) {
        maxProb = probabilities[i];
        selectedType = decisionTypes[i];
      }
    }

    // Execute the decision strategy
    const decision = this.executeDecisionStrategy(selectedType, robots, task);

    return {
      type: selectedType,
      confidence: maxProb,
      selectedRobot: decision.robotId,
      reasoning: decision.reasoning,
      alternativeRobots: decision.alternatives,
      expectedDuration: decision.estimatedDuration,
      successProbability: decision.successProbability
    };
  }

  /**
   * Execute specific decision strategy
   */
  executeDecisionStrategy(strategyType, robots, task) {
    const validRobots = robots.filter(r => r.status === 'active' || r.status === 'idle');

    if (validRobots.length === 0) {
      return {
        robotId: null,
        reasoning: 'No available robots',
        alternatives: [],
        estimatedDuration: null,
        successProbability: 0
      };
    }

    switch (strategyType) {
      case 'assign_highest_performance':
        return this.assignToHighestPerformance(validRobots, task);

      case 'assign_nearest':
        return this.assignToNearest(validRobots, task);

      case 'assign_lowest_load':
        return this.assignToLowestLoad(validRobots, task);

      case 'assign_best_battery':
        return this.assignToBestBattery(validRobots, task);

      case 'assign_specialist':
        return this.assignToSpecialist(validRobots, task);

      case 'defer_task':
        return {
          robotId: null,
          reasoning: 'Task deferred - better conditions expected later',
          alternatives: validRobots.map(r => r.robot_id),
          estimatedDuration: null,
          successProbability: 0.5
        };

      case 'split_task':
        return this.splitTaskAcrossRobots(validRobots, task);

      case 'escalate_task':
        return {
          robotId: null,
          reasoning: 'Task complexity requires human intervention',
          alternatives: [],
          estimatedDuration: null,
          successProbability: 0
        };

      default:
        return this.assignToHighestPerformance(validRobots, task);
    }
  }

  /**
   * Assign task to robot with highest performance score
   */
  assignToHighestPerformance(robots, task) {
    let bestRobot = robots[0];
    let bestScore = this.calculateRobotPerformanceScore(bestRobot, task);

    for (const robot of robots.slice(1)) {
      const score = this.calculateRobotPerformanceScore(robot, task);
      if (score > bestScore) {
        bestScore = score;
        bestRobot = robot;
      }
    }

    return {
      robotId: bestRobot.robot_id,
      reasoning: `Highest performance score: ${(bestScore * 100).toFixed(1)}%`,
      alternatives: robots
        .filter(r => r.robot_id !== bestRobot.robot_id)
        .slice(0, 3)
        .map(r => r.robot_id),
      estimatedDuration: this.estimateTaskDuration(bestRobot, task),
      successProbability: bestScore
    };
  }

  /**
   * Assign task to nearest robot (by location)
   */
  assignToNearest(robots, task) {
    if (!task.details?.location_from?.coordinates) {
      return this.assignToHighestPerformance(robots, task);
    }

    let nearestRobot = robots[0];
    let shortestDistance = this.calculateDistance(
      nearestRobot.location.coordinates,
      task.details.location_from.coordinates
    );

    for (const robot of robots.slice(1)) {
      const distance = this.calculateDistance(
        robot.location.coordinates,
        task.details.location_from.coordinates
      );
      if (distance < shortestDistance) {
        shortestDistance = distance;
        nearestRobot = robot;
      }
    }

    return {
      robotId: nearestRobot.robot_id,
      reasoning: `Nearest robot: ${shortestDistance.toFixed(2)}m away`,
      alternatives: robots
        .filter(r => r.robot_id !== nearestRobot.robot_id)
        .slice(0, 3)
        .map(r => r.robot_id),
      estimatedDuration: this.estimateTaskDuration(nearestRobot, task),
      successProbability: 0.85
    };
  }

  /**
   * Assign to robot with lowest current workload
   */
  assignToLowestLoad(robots, task) {
    let bestRobot = robots[0];
    let lowestLoad = this.calculateRobotLoad(bestRobot);

    for (const robot of robots.slice(1)) {
      const load = this.calculateRobotLoad(robot);
      if (load < lowestLoad) {
        lowestLoad = load;
        bestRobot = robot;
      }
    }

    return {
      robotId: bestRobot.robot_id,
      reasoning: `Lowest workload: ${(lowestLoad * 100).toFixed(1)}%`,
      alternatives: robots
        .filter(r => r.robot_id !== bestRobot.robot_id)
        .slice(0, 3)
        .map(r => r.robot_id),
      estimatedDuration: this.estimateTaskDuration(bestRobot, task),
      successProbability: 0.88
    };
  }

  /**
   * Assign to robot with best battery level
   */
  assignToBestBattery(robots, task) {
    let bestRobot = robots[0];
    let bestBattery = bestRobot.telemetry?.battery_level || 0;

    for (const robot of robots.slice(1)) {
      const battery = robot.telemetry?.battery_level || 0;
      if (battery > bestBattery) {
        bestBattery = battery;
        bestRobot = robot;
      }
    }

    return {
      robotId: bestRobot.robot_id,
      reasoning: `Best battery: ${bestBattery.toFixed(1)}%`,
      alternatives: robots
        .filter(r => r.robot_id !== bestRobot.robot_id)
        .slice(0, 3)
        .map(r => r.robot_id),
      estimatedDuration: this.estimateTaskDuration(bestRobot, task),
      successProbability: 0.90
    };
  }

  /**
   * Assign to robot that specializes in this task type
   */
  assignToSpecialist(robots, task) {
    const specialists = robots.filter(r => r.type.toLowerCase() === task.type.toLowerCase());

    if (specialists.length === 0) {
      return this.assignToHighestPerformance(robots, task);
    }

    return this.assignToHighestPerformance(specialists, task);
  }

  /**
   * Split complex task across multiple robots
   */
  splitTaskAcrossRobots(robots, task) {
    const topRobots = robots
      .map(r => ({
        robot: r,
        score: this.calculateRobotPerformanceScore(r, task)
      }))
      .sort((a, b) => b.score - a.score)
      .slice(0, Math.min(3, robots.length));

    return {
      robotId: topRobots[0].robot.robot_id,
      reasoning: `Task split across ${topRobots.length} robots for parallel execution`,
      alternatives: topRobots.slice(1).map(r => r.robot.robot_id),
      estimatedDuration: this.estimateTaskDuration(topRobots[0].robot, task) / topRobots.length,
      successProbability: topRobots[0].score
    };
  }

  /**
   * Calculate robot performance score for specific task
   */
  calculateRobotPerformanceScore(robot, task) {
    const weights = {
      uptime: 0.25,
      successRate: 0.30,
      recentPerformance: 0.20,
      battery: 0.15,
      load: 0.10
    };

    const uptime = (robot.telemetry?.uptime || 0) / 86400; // Normalize to days
    const uptimeScore = Math.min(uptime / 30, 1); // Max 30 days

    const tasksCompleted = robot.telemetry?.tasks_completed || 0;
    const tasksFailed = robot.telemetry?.tasks_failed || 0;
    const successRate = tasksCompleted > 0
      ? tasksCompleted / (tasksCompleted + tasksFailed)
      : 0.5;

    const recentScore = (robot.telemetry?.reputation_score || 5000) / 10000;

    const batteryScore = (robot.telemetry?.battery_level || 50) / 100;

    const loadScore = 1 - this.calculateRobotLoad(robot);

    const totalScore =
      uptimeScore * weights.uptime +
      successRate * weights.successRate +
      recentScore * weights.recentPerformance +
      batteryScore * weights.battery +
      loadScore * weights.load;

    return Math.max(0, Math.min(1, totalScore));
  }

  /**
   * Evolution Engine - Self-improving AI
   */
  async evolve() {
    if (!this.config.evolutionEnabled) {
      return;
    }

    console.log('\n🧬 Neural Core Evolution initiated...');
    console.log(`  Current Generation: ${this.currentGeneration}`);

    const performance = this.evaluateCurrentPerformance();
    console.log(`  Current Performance: ${(performance.accuracy * 100).toFixed(1)}%`);

    if (performance.accuracy >= this.config.minAccuracyThreshold) {
      console.log('  ✓ Performance meets threshold - evolution unnecessary');
      return;
    }

    // Train model with recent decision history
    await this.retrainModel();

    // Adjust hyperparameters
    await this.optimizeHyperparameters();

    // Create new generation
    this.currentGeneration++;

    const newPerformance = this.evaluateCurrentPerformance();
    const improvement = newPerformance.accuracy - performance.accuracy;

    console.log(`  New Performance: ${(newPerformance.accuracy * 100).toFixed(1)}%`);
    console.log(`  Improvement: ${improvement >= 0 ? '+' : ''}${(improvement * 100).toFixed(2)}%`);
    console.log(`  ✓ Evolution complete - Generation ${this.currentGeneration}`);

    // Store evolution history
    this.evolutionHistory.push({
      generation: this.currentGeneration,
      timestamp: new Date(),
      performance: newPerformance,
      improvement: improvement
    });

    return {
      generation: this.currentGeneration,
      performance: newPerformance,
      improvement: improvement
    };
  }

  /**
   * Retrain model with recent performance data
   */
  async retrainModel() {
    if (this.performanceHistory.length < 10) {
      return; // Not enough data
    }

    this.isTraining = true;

    // Prepare training data from performance history
    const recentHistory = this.performanceHistory.slice(-1000); // Last 1000 decisions

    const xs = recentHistory.map(h => h.features);
    const ys = recentHistory.map(h => h.outcome);

    // Convert to tensors
    const xTrain = tf.tensor2d(xs);
    const yTrain = tf.tensor2d(ys);

    // Train model
    await this.model.fit(xTrain, yTrain, {
      epochs: 50,
      batchSize: 32,
      validationSplit: 0.2,
      callbacks: {
        onEpochEnd: (epoch, logs) => {
          if (epoch % 10 === 0) {
            console.log(`    Epoch ${epoch}: loss = ${logs.loss.toFixed(4)}, acc = ${logs.acc.toFixed(4)}`);
          }
        }
      }
    });

    // Cleanup tensors
    xTrain.dispose();
    yTrain.dispose();

    this.isTraining = false;
  }

  /**
   * Optimize hyperparameters based on performance
   */
  async optimizeHyperparameters() {
    const performance = this.evaluateCurrentPerformance();

    if (performance.accuracy < 0.7) {
      // Performance is poor - increase learning rate
      this.config.learningRate = Math.min(this.config.learningRate * 1.2, 0.1);
      console.log(`    Increased learning rate to ${this.config.learningRate.toFixed(4)}`);
    } else if (performance.accuracy > 0.95) {
      // Performance is excellent - decrease learning rate for fine-tuning
      this.config.learningRate = Math.max(this.config.learningRate * 0.8, 0.001);
      console.log(`    Decreased learning rate to ${this.config.learningRate.toFixed(4)}`);
    }

    // Re-compile model with new learning rate
    this.model.compile({
      optimizer: tf.train.adam(this.config.learningRate),
      loss: 'categoricalCrossentropy',
      metrics: ['accuracy']
    });
  }

  /**
   * Evaluate current model performance
   */
  evaluateCurrentPerformance() {
    if (this.performanceHistory.length === 0) {
      return { accuracy: 0.5, avgDuration: 0, successRate: 0.5 };
    }

    const recent = this.performanceHistory.slice(-100);

    const successfulDecisions = recent.filter(h => h.successful).length;
    const accuracy = successfulDecisions / recent.length;

    const avgDuration = recent.reduce((sum, h) => sum + (h.duration || 0), 0) / recent.length;

    const successRate = recent.reduce((sum, h) => sum + (h.successProbability || 0.5), 0) / recent.length;

    return { accuracy, avgDuration, successRate };
  }

  /**
   * Log decision for learning and evolution
   */
  logDecision(decision, features) {
    this.performanceHistory.push({
      timestamp: new Date(),
      decision: decision.type,
      robotId: decision.selectedRobot,
      confidence: decision.confidence,
      successProbability: decision.successProbability,
      features: features,
      successful: null, // Will be updated when task completes
      duration: null
    });

    // Keep only recent history (last 10,000 decisions)
    if (this.performanceHistory.length > 10000) {
      this.performanceHistory = this.performanceHistory.slice(-10000);
    }
  }

  /**
   * Update decision outcome after task completion
   */
  updateDecisionOutcome(decisionIndex, successful, duration) {
    if (this.performanceHistory[decisionIndex]) {
      this.performanceHistory[decisionIndex].successful = successful;
      this.performanceHistory[decisionIndex].duration = duration;
    }
  }

  // ==================== Helper Functions ====================

  normalizeTaskType(type) {
    const types = ['pickup', 'delivery', 'inspection', 'maintenance', 'monitoring', 'assembly', 'cleaning', 'security'];
    return types.indexOf(type) / types.length;
  }

  normalizeTaskPriority(priority) {
    const priorities = { low: 0.25, medium: 0.5, high: 0.75, urgent: 1.0 };
    return priorities[priority] || 0.5;
  }

  calculateAverageFleetUptime(robots) {
    if (robots.length === 0) return 0;
    const totalUptime = robots.reduce((sum, r) => sum + (r.telemetry?.uptime || 0), 0);
    return Math.min(totalUptime / robots.length / 86400 / 30, 1); // Normalize to 30 days
  }

  calculateAverageFleetBatteryLevel(robots) {
    if (robots.length === 0) return 0;
    const totalBattery = robots.reduce((sum, r) => sum + (r.telemetry?.battery_level || 50), 0);
    return totalBattery / robots.length / 100;
  }

  getTimeOfDayFactor() {
    const hour = new Date().getHours();
    return hour / 24;
  }

  getWeekdayFactor() {
    const day = new Date().getDay();
    return day / 7;
  }

  getLoadFactor(robots) {
    if (robots.length === 0) return 0;
    const busyRobots = robots.filter(r => r.status === 'busy').length;
    return busyRobots / robots.length;
  }

  getHistoricalSuccessRate() {
    if (this.performanceHistory.length === 0) return 0.5;
    const recent = this.performanceHistory.slice(-50);
    const successful = recent.filter(h => h.successful === true).length;
    return successful / recent.length;
  }

  getAverageTaskDuration() {
    if (this.performanceHistory.length === 0) return 0.5;
    const recent = this.performanceHistory.slice(-50).filter(h => h.duration);
    if (recent.length === 0) return 0.5;
    const avgDuration = recent.reduce((sum, h) => sum + h.duration, 0) / recent.length;
    return Math.min(avgDuration / 3600, 1); // Normalize to 1 hour
  }

  getRecentErrorRate() {
    if (this.performanceHistory.length === 0) return 0;
    const recent = this.performanceHistory.slice(-50);
    const errors = recent.filter(h => h.successful === false).length;
    return errors / recent.length;
  }

  calculateRobotLoad(robot) {
    // Simple load calculation based on status
    switch (robot.status) {
      case 'busy': return 1.0;
      case 'active': return 0.3;
      case 'idle': return 0.0;
      case 'charging': return 0.5;
      case 'maintenance': return 0.8;
      default: return 0.5;
    }
  }

  calculateDistance(coord1, coord2) {
    if (!coord1 || !coord2) return Infinity;
    const [lon1, lat1] = coord1;
    const [lon2, lat2] = coord2;

    // Haversine formula
    const R = 6371e3; // Earth radius in meters
    const φ1 = lat1 * Math.PI / 180;
    const φ2 = lat2 * Math.PI / 180;
    const Δφ = (lat2 - lat1) * Math.PI / 180;
    const Δλ = (lon2 - lon1) * Math.PI / 180;

    const a = Math.sin(Δφ / 2) * Math.sin(Δφ / 2) +
              Math.cos(φ1) * Math.cos(φ2) *
              Math.sin(Δλ / 2) * Math.sin(Δλ / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

    return R * c;
  }

  estimateTaskDuration(robot, task) {
    // Simple estimation based on robot performance and task complexity
    const baseTime = 1800; // 30 minutes base
    const performanceScore = this.calculateRobotPerformanceScore(robot, task);
    return baseTime / performanceScore;
  }

  /**
   * Get Neural Core status and statistics
   */
  getStatus() {
    return {
      generation: this.currentGeneration,
      isTraining: this.isTraining,
      evolutionEnabled: this.config.evolutionEnabled,
      learningRate: this.config.learningRate,
      decisionsMade: this.performanceHistory.length,
      currentPerformance: this.evaluateCurrentPerformance(),
      lastEvolution: this.evolutionHistory.length > 0
        ? this.evolutionHistory[this.evolutionHistory.length - 1]
        : null
    };
  }
}

export default NeuralCore;
