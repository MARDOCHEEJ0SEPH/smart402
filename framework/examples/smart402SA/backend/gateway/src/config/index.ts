/**
 * Gateway Configuration
 * Environment-based configuration for the API Gateway
 */

import { config } from 'dotenv';

config();

export const gatewayConfig = {
  // Server
  env: process.env.NODE_ENV || 'development',
  port: parseInt(process.env.PORT || '4000', 10),
  host: process.env.HOST || '0.0.0.0',

  // Database - PostgreSQL
  postgres: {
    url: process.env.POSTGRES_URL || 'postgresql://smart402:smart402_dev_password@localhost:5432/smart402sa',
    max: parseInt(process.env.POSTGRES_POOL_SIZE || '20', 10)
  },

  // Database - MongoDB
  mongodb: {
    url: process.env.MONGODB_URL || 'mongodb://smart402:smart402_dev_password@localhost:27017/smart402sa'
  },

  // Cache - Redis
  redis: {
    url: process.env.REDIS_URL || 'redis://localhost:6379',
    ttl: parseInt(process.env.REDIS_TTL || '3600', 10) // 1 hour default
  },

  // Search - Elasticsearch
  elasticsearch: {
    url: process.env.ELASTICSEARCH_URL || 'http://localhost:9200',
    index_prefix: process.env.ES_INDEX_PREFIX || 'smart402sa'
  },

  // Blockchain
  blockchain: {
    rpc_url: process.env.BLOCKCHAIN_RPC_URL || 'https://rpc-mumbai.maticvigil.com',
    private_key: process.env.PRIVATE_KEY,
    chain_id: parseInt(process.env.CHAIN_ID || '80001', 10) // Mumbai testnet
  },

  // JWT
  jwt: {
    secret: process.env.JWT_SECRET || 'smart402-dev-secret-change-in-production',
    expiresIn: process.env.JWT_EXPIRES_IN || '24h'
  },

  // Rate Limiting
  rateLimit: {
    max: parseInt(process.env.RATE_LIMIT_MAX || '100', 10),
    timeWindow: process.env.RATE_LIMIT_WINDOW || '1 minute'
  },

  // CORS
  cors: {
    origin: process.env.CORS_ORIGIN || '*',
    credentials: process.env.CORS_CREDENTIALS === 'true'
  },

  // Smart402
  smart402: {
    aeo_target_score: parseFloat(process.env.AEO_TARGET_SCORE || '0.85'),
    llmo_optimization_level: (process.env.LLMO_OPTIMIZATION_LEVEL || 'high') as 'basic' | 'standard' | 'high' | 'maximum'
  },

  // Logging
  logger: {
    level: process.env.LOG_LEVEL || 'info',
    prettyPrint: process.env.NODE_ENV === 'development'
  },

  // Monitoring
  monitoring: {
    enabled: process.env.MONITORING_ENABLED === 'true',
    prometheus_port: parseInt(process.env.PROMETHEUS_PORT || '9090', 10)
  }
};

export default gatewayConfig;
