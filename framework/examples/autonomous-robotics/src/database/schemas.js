/**
 * Smart402 Autonomous Robotics Platform - MongoDB Schemas
 * Database models for robots, telemetry, contracts, and analytics
 */

import { MongoClient } from 'mongodb';

/**
 * Robot Schema
 * Stores robot fleet information with real-time status
 */
export const RobotSchema = {
  name: 'robots',
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['robot_id', 'type', 'status', 'location', 'contract_id'],
      properties: {
        robot_id: {
          bsonType: 'string',
          description: 'Unique robot identifier (e.g., ROB-001-2024)'
        },
        type: {
          enum: ['industrial', 'warehouse', 'service', 'mobile', 'drone', 'specialized'],
          description: 'Type of robot'
        },
        status: {
          enum: ['active', 'idle', 'maintenance', 'offline', 'error', 'charging'],
          description: 'Current robot status'
        },
        location: {
          bsonType: 'object',
          required: ['coordinates', 'facility'],
          properties: {
            coordinates: {
              bsonType: 'array',
              items: { bsonType: 'double' },
              description: '[longitude, latitude]'
            },
            facility: {
              bsonType: 'string',
              description: 'Facility name or ID'
            },
            zone: {
              bsonType: 'string',
              description: 'Specific zone within facility'
            }
          }
        },
        specifications: {
          bsonType: 'object',
          properties: {
            model: { bsonType: 'string' },
            manufacturer: { bsonType: 'string' },
            serial_number: { bsonType: 'string' },
            max_payload: { bsonType: 'double' },
            battery_capacity: { bsonType: 'double' },
            sensors: { bsonType: 'array' }
          }
        },
        telemetry: {
          bsonType: 'object',
          properties: {
            uptime: { bsonType: 'double', description: 'Total uptime in seconds' },
            tasks_completed: { bsonType: 'int' },
            tasks_failed: { bsonType: 'int' },
            errors: { bsonType: 'int' },
            battery_level: { bsonType: 'double' },
            temperature: { bsonType: 'double' },
            last_maintenance: { bsonType: 'date' },
            next_maintenance: { bsonType: 'date' }
          }
        },
        contract_id: {
          bsonType: 'string',
          description: 'Associated Smart402 contract ID'
        },
        blockchain_address: {
          bsonType: 'string',
          description: 'Blockchain address for payments'
        },
        owner: {
          bsonType: 'object',
          properties: {
            user_id: { bsonType: 'string' },
            email: { bsonType: 'string' },
            company: { bsonType: 'string' }
          }
        },
        created_at: { bsonType: 'date' },
        updated_at: { bsonType: 'date' }
      }
    }
  },
  indexes: [
    { key: { robot_id: 1 }, unique: true },
    { key: { status: 1 } },
    { key: { 'location.facility': 1 } },
    { key: { contract_id: 1 } },
    { key: { created_at: -1 } }
  ]
};

/**
 * Telemetry Schema
 * Real-time data from robot sensors and operations
 */
export const TelemetrySchema = {
  name: 'telemetry',
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['robot_id', 'timestamp', 'data_type', 'value'],
      properties: {
        robot_id: {
          bsonType: 'string',
          description: 'Robot that generated this telemetry'
        },
        timestamp: {
          bsonType: 'date',
          description: 'When data was collected'
        },
        data_type: {
          enum: [
            'position', 'battery', 'temperature', 'speed', 'task_status',
            'sensor_reading', 'error', 'maintenance', 'performance'
          ],
          description: 'Type of telemetry data'
        },
        value: {
          bsonType: 'object',
          description: 'Telemetry data payload (flexible schema)'
        },
        unit: {
          bsonType: 'string',
          description: 'Unit of measurement'
        },
        quality: {
          bsonType: 'double',
          minimum: 0,
          maximum: 1,
          description: 'Data quality score (0-1)'
        },
        chainlink_verified: {
          bsonType: 'bool',
          description: 'Whether verified by Chainlink oracle'
        },
        blockchain_tx: {
          bsonType: 'string',
          description: 'Transaction hash if pushed to blockchain'
        }
      }
    }
  },
  indexes: [
    { key: { robot_id: 1, timestamp: -1 } },
    { key: { data_type: 1 } },
    { key: { timestamp: -1 } },
    { key: { chainlink_verified: 1 } }
  ],
  timeseries: {
    timeField: 'timestamp',
    metaField: 'robot_id',
    granularity: 'seconds'
  }
};

/**
 * Smart402 Contracts Schema
 * Smart402 contract instances for robot services
 */
export const ContractsSchema = {
  name: 'contracts',
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['contract_id', 'type', 'status', 'parties', 'payment'],
      properties: {
        contract_id: {
          bsonType: 'string',
          description: 'Smart402 contract ID'
        },
        type: {
          enum: [
            'robot-rental', 'maintenance', 'data-access', 'task-execution',
            'fleet-subscription', 'api-access', 'custom'
          ],
          description: 'Contract type'
        },
        status: {
          enum: ['draft', 'pending', 'active', 'completed', 'cancelled', 'disputed'],
          description: 'Contract status'
        },
        parties: {
          bsonType: 'array',
          items: {
            bsonType: 'object',
            properties: {
              role: { enum: ['provider', 'client', 'operator'] },
              email: { bsonType: 'string' },
              wallet_address: { bsonType: 'string' }
            }
          }
        },
        payment: {
          bsonType: 'object',
          required: ['amount', 'token', 'frequency'],
          properties: {
            amount: { bsonType: 'double' },
            token: { bsonType: 'string' },
            blockchain: { bsonType: 'string' },
            frequency: { enum: ['one-time', 'hourly', 'daily', 'weekly', 'monthly'] },
            last_payment: { bsonType: 'date' },
            next_payment: { bsonType: 'date' },
            total_paid: { bsonType: 'double' }
          }
        },
        conditions: {
          bsonType: 'array',
          items: {
            bsonType: 'object',
            properties: {
              id: { bsonType: 'string' },
              type: { bsonType: 'string' },
              description: { bsonType: 'string' },
              met: { bsonType: 'bool' },
              last_checked: { bsonType: 'date' }
            }
          }
        },
        ucl: {
          bsonType: 'object',
          description: 'Universal Contract Language representation'
        },
        aeo_score: {
          bsonType: 'double',
          minimum: 0,
          maximum: 1,
          description: 'Answer Engine Optimization score'
        },
        blockchain_address: {
          bsonType: 'string',
          description: 'Deployed contract address'
        },
        blockchain_tx: {
          bsonType: 'string',
          description: 'Deployment transaction hash'
        },
        robot_ids: {
          bsonType: 'array',
          items: { bsonType: 'string' },
          description: 'Associated robots'
        },
        metadata: {
          bsonType: 'object',
          description: 'Additional contract metadata'
        },
        created_at: { bsonType: 'date' },
        updated_at: { bsonType: 'date' },
        expires_at: { bsonType: 'date' }
      }
    }
  },
  indexes: [
    { key: { contract_id: 1 }, unique: true },
    { key: { status: 1 } },
    { key: { 'parties.wallet_address': 1 } },
    { key: { blockchain_address: 1 } },
    { key: { created_at: -1 } }
  ]
};

/**
 * Tasks Schema
 * Robot task assignments and execution tracking
 */
export const TasksSchema = {
  name: 'tasks',
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['task_id', 'robot_id', 'type', 'status'],
      properties: {
        task_id: {
          bsonType: 'string',
          description: 'Unique task identifier'
        },
        robot_id: {
          bsonType: 'string',
          description: 'Assigned robot'
        },
        type: {
          enum: [
            'pickup', 'delivery', 'inspection', 'maintenance', 'monitoring',
            'assembly', 'cleaning', 'security', 'custom'
          ],
          description: 'Task type'
        },
        status: {
          enum: ['pending', 'assigned', 'in_progress', 'completed', 'failed', 'cancelled'],
          description: 'Task status'
        },
        priority: {
          enum: ['low', 'medium', 'high', 'urgent'],
          description: 'Task priority'
        },
        details: {
          bsonType: 'object',
          properties: {
            description: { bsonType: 'string' },
            location_from: { bsonType: 'object' },
            location_to: { bsonType: 'object' },
            payload: { bsonType: 'object' },
            requirements: { bsonType: 'array' }
          }
        },
        contract_id: {
          bsonType: 'string',
          description: 'Associated contract'
        },
        execution: {
          bsonType: 'object',
          properties: {
            started_at: { bsonType: 'date' },
            completed_at: { bsonType: 'date' },
            duration: { bsonType: 'int' },
            success_rate: { bsonType: 'double' },
            errors: { bsonType: 'array' }
          }
        },
        neural_decision: {
          bsonType: 'object',
          description: 'AI decision data if assigned by Neural Core'
        },
        created_at: { bsonType: 'date' },
        updated_at: { bsonType: 'date' }
      }
    }
  },
  indexes: [
    { key: { task_id: 1 }, unique: true },
    { key: { robot_id: 1, status: 1 } },
    { key: { status: 1, priority: -1 } },
    { key: { contract_id: 1 } },
    { key: { created_at: -1 } }
  ]
};

/**
 * Analytics Schema
 * Performance metrics and AI learning data
 */
export const AnalyticsSchema = {
  name: 'analytics',
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['metric_type', 'timestamp', 'value'],
      properties: {
        metric_type: {
          enum: [
            'fleet_performance', 'revenue', 'uptime', 'task_completion',
            'neural_accuracy', 'aeo_score', 'contract_success', 'user_satisfaction'
          ],
          description: 'Type of metric'
        },
        timestamp: {
          bsonType: 'date',
          description: 'When metric was recorded'
        },
        value: {
          bsonType: 'double',
          description: 'Metric value'
        },
        dimensions: {
          bsonType: 'object',
          description: 'Metric dimensions (facility, robot_type, etc.)'
        },
        aggregation: {
          enum: ['instant', 'hourly', 'daily', 'weekly', 'monthly'],
          description: 'Aggregation level'
        },
        metadata: {
          bsonType: 'object'
        }
      }
    }
  },
  indexes: [
    { key: { metric_type: 1, timestamp: -1 } },
    { key: { timestamp: -1 } },
    { key: { aggregation: 1 } }
  ],
  timeseries: {
    timeField: 'timestamp',
    metaField: 'metric_type',
    granularity: 'minutes'
  }
};

/**
 * Neural Evolution Schema
 * Track AI model evolution and improvements
 */
export const NeuralEvolutionSchema = {
  name: 'neural_evolution',
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['generation', 'timestamp', 'model_version', 'performance'],
      properties: {
        generation: {
          bsonType: 'int',
          description: 'Evolution generation number'
        },
        timestamp: {
          bsonType: 'date',
          description: 'When this generation was created'
        },
        model_version: {
          bsonType: 'string',
          description: 'Model version identifier'
        },
        architecture: {
          bsonType: 'object',
          description: 'Neural network architecture details'
        },
        weights: {
          bsonType: 'string',
          description: 'Model weights (stored as binary or reference)'
        },
        performance: {
          bsonType: 'object',
          required: ['accuracy', 'task_success_rate'],
          properties: {
            accuracy: { bsonType: 'double' },
            task_success_rate: { bsonType: 'double' },
            avg_task_duration: { bsonType: 'double' },
            error_rate: { bsonType: 'double' },
            energy_efficiency: { bsonType: 'double' }
          }
        },
        improvements: {
          bsonType: 'array',
          items: {
            bsonType: 'object',
            properties: {
              area: { bsonType: 'string' },
              change: { bsonType: 'string' },
              impact: { bsonType: 'double' }
            }
          }
        },
        is_deployed: {
          bsonType: 'bool',
          description: 'Whether this generation is currently in use'
        },
        parent_generation: {
          bsonType: 'int',
          description: 'Previous generation this evolved from'
        }
      }
    }
  },
  indexes: [
    { key: { generation: -1 } },
    { key: { is_deployed: 1 } },
    { key: { timestamp: -1 } }
  ]
};

/**
 * Initialize all collections with schemas and indexes
 */
export async function initializeDatabase(mongoUri, dbName) {
  const client = new MongoClient(mongoUri);

  try {
    await client.connect();
    console.log('✓ Connected to MongoDB');

    const db = client.db(dbName);

    // Define all schemas
    const schemas = [
      RobotSchema,
      TelemetrySchema,
      ContractsSchema,
      TasksSchema,
      AnalyticsSchema,
      NeuralEvolutionSchema
    ];

    // Create collections with validation
    for (const schema of schemas) {
      try {
        // Check if collection exists
        const collections = await db.listCollections({ name: schema.name }).toArray();

        if (collections.length === 0) {
          // Create collection with validation
          const options = { validator: schema.validator };

          // Add timeseries option if present
          if (schema.timeseries) {
            options.timeseries = schema.timeseries;
          }

          await db.createCollection(schema.name, options);
          console.log(`✓ Created collection: ${schema.name}`);
        } else {
          console.log(`  Collection exists: ${schema.name}`);
        }

        // Create indexes
        const collection = db.collection(schema.name);
        for (const index of schema.indexes) {
          await collection.createIndex(index.key, {
            unique: index.unique || false,
            background: true
          });
        }
        console.log(`✓ Created indexes for: ${schema.name}`);

      } catch (error) {
        console.error(`✗ Error with collection ${schema.name}:`, error.message);
      }
    }

    console.log('\n✓ Database initialization complete!');

  } catch (error) {
    console.error('✗ Database initialization failed:', error);
    throw error;
  } finally {
    await client.close();
  }
}

export default {
  RobotSchema,
  TelemetrySchema,
  ContractsSchema,
  TasksSchema,
  AnalyticsSchema,
  NeuralEvolutionSchema,
  initializeDatabase
};
