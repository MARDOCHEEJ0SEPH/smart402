/**
 * Smart402 Autonomous Robotics - Neural Core (Simplified)
 * AI-powered decision engine with self-evolution capabilities
 * Simplified version without heavy ML dependencies for easy testing
 */

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
    this.performanceHistory = [];
    this.evolutionHistory = [];
    this.isTraining = false;
    this.weights = this.initializeWeights();
  }

  /**
   * Initialize Neural Core with decision weights
   */
  async initialize() {
    console.log('\n🧠 Initializing Neural Core...');
    console.log('✓ Neural Core initialized');
    console.log(`  Learning Rate: ${this.config.learningRate}`);
    console.log(`  Evolution: ${this.config.evolutionEnabled ? 'Enabled' : 'Disabled'}`);
    console.log(`  Generation: ${this.currentGeneration}`);

    return this;
  }

  /**
   * Initialize decision weights
   */
  initializeWeights() {
    return {
      uptime: 0.25,
      successRate: 0.30,
      recentPerformance: 0.20,
      battery: 0.15,
      load: 0.10
    };
  }

  /**
   * Make intelligent decision about robot task assignment
   */
  async makeTaskAssignmentDecision(task, availableRobots) {
    const features = this.extractTaskFeatures(task, availableRobots);

    // Use weighted scoring to make decision
    const probabilities = this.calculateDecisionProbabilities(features, availableRobots);

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
   * Calculate decision probabilities based on features
   */
  calculateDecisionProbabilities(features, robots) {
    // Simulate neural network output with weighted heuristics
    const scores = {
      assign_highest_performance: 0.3 + features.historicalSuccessRate * 0.3,
      assign_nearest: features.avgFleetUptime * 0.25,
      assign_lowest_load: (1 - features.loadFactor) * 0.25,
      assign_best_battery: features.avgFleetBattery * 0.2,
      assign_specialist: 0.15,
      defer_task: features.loadFactor > 0.8 ? 0.3 : 0.05,
      split_task: robots.length > 3 ? 0.2 : 0.05,
      escalate_task: features.errorRate > 0.5 ? 0.4 : 0.05
    };

    return Object.values(scores);
  }

  /**
   * Extract features from task and robots for AI decision making
   */
  extractTaskFeatures(task, robots) {
    const features = {
      taskType: this.normalizeTaskType(task.type),
      taskPriority: this.normalizeTaskPriority(task.priority),
      weight: task.payload?.weight ? task.payload.weight / 1000 : 0,
      distance: task.payload?.distance ? task.payload.distance / 10000 : 0,
      complexity: task.payload?.complexity ? task.payload.complexity / 100 : 0,
      robotCount: robots.length / 100,
      avgFleetUptime: this.calculateAverageFleetUptime(robots),
      avgFleetBattery: this.calculateAverageFleetBatteryLevel(robots),
      timeOfDay: this.getTimeOfDayFactor(),
      weekday: this.getWeekdayFactor(),
      loadFactor: this.getLoadFactor(robots),
      historicalSuccessRate: this.getHistoricalSuccessRate(),
      avgTaskDuration: this.getAverageTaskDuration(),
      errorRate: this.getRecentErrorRate(),
      random: Math.random() * 0.1
    };

    return features;
  }

  /**
   * Interpret AI prediction probabilities into actionable decisions
   */
  interpretDecisionProbabilities(probabilities, robots, task) {
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

    let maxProb = 0;
    let selectedType = decisionTypes[0];

    for (let i = 0; i < probabilities.length; i++) {
      if (probabilities[i] > maxProb) {
        maxProb = probabilities[i];
        selectedType = decisionTypes[i];
      }
    }

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
    const uptime = (robot.telemetry?.uptime || 0) / 86400;
    const uptimeScore = Math.min(uptime / 30, 1);

    const tasksCompleted = robot.telemetry?.tasks_completed || 0;
    const tasksFailed = robot.telemetry?.tasks_failed || 0;
    const successRate = tasksCompleted > 0
      ? tasksCompleted / (tasksCompleted + tasksFailed)
      : 0.5;

    const recentScore = (robot.telemetry?.reputation_score || 5000) / 10000;
    const batteryScore = (robot.telemetry?.battery_level || 50) / 100;
    const loadScore = 1 - this.calculateRobotLoad(robot);

    const totalScore =
      uptimeScore * this.weights.uptime +
      successRate * this.weights.successRate +
      recentScore * this.weights.recentPerformance +
      batteryScore * this.weights.battery +
      loadScore * this.weights.load;

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

    // Adjust weights based on recent performance
    this.optimizeWeights();

    // Create new generation
    this.currentGeneration++;

    const newPerformance = this.evaluateCurrentPerformance();
    const improvement = newPerformance.accuracy - performance.accuracy;

    console.log(`  New Performance: ${(newPerformance.accuracy * 100).toFixed(1)}%`);
    console.log(`  Improvement: ${improvement >= 0 ? '+' : ''}${(improvement * 100).toFixed(2)}%`);
    console.log(`  ✓ Evolution complete - Generation ${this.currentGeneration}`);

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
   * Optimize weights based on performance
   */
  optimizeWeights() {
    const performance = this.evaluateCurrentPerformance();

    if (performance.accuracy < 0.7) {
      // Increase learning rate
      this.config.learningRate = Math.min(this.config.learningRate * 1.2, 0.1);

      // Adjust weights randomly for exploration
      Object.keys(this.weights).forEach(key => {
        this.weights[key] += (Math.random() - 0.5) * this.config.learningRate;
        this.weights[key] = Math.max(0, Math.min(1, this.weights[key]));
      });

      // Normalize weights
      const sum = Object.values(this.weights).reduce((a, b) => a + b, 0);
      Object.keys(this.weights).forEach(key => {
        this.weights[key] /= sum;
      });

      console.log(`    Increased learning rate to ${this.config.learningRate.toFixed(4)}`);
    } else if (performance.accuracy > 0.95) {
      // Decrease learning rate for fine-tuning
      this.config.learningRate = Math.max(this.config.learningRate * 0.8, 0.001);
      console.log(`    Decreased learning rate to ${this.config.learningRate.toFixed(4)}`);
    }
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
      successful: null,
      duration: null
    });

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
    return Math.min(totalUptime / robots.length / 86400 / 30, 1);
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
    return Math.min(avgDuration / 3600, 1);
  }

  getRecentErrorRate() {
    if (this.performanceHistory.length === 0) return 0;
    const recent = this.performanceHistory.slice(-50);
    const errors = recent.filter(h => h.successful === false).length;
    return errors / recent.length;
  }

  calculateRobotLoad(robot) {
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

    const R = 6371e3;
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
    const baseTime = 1800;
    const performanceScore = this.calculateRobotPerformanceScore(robot, task);
    return baseTime / performanceScore;
  }

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
        : null,
      weights: this.weights
    };
  }
}

export default NeuralCore;
