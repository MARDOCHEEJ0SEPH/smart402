/**
 * Smart402 API Gateway
 * Fastify-based microservices gateway with Smart402 integration
 */

import Fastify from 'fastify';
import cors from '@fastify/cors';
import helmet from '@fastify/helmet';
import rateLimit from '@fastify/rate-limit';
import compress from '@fastify/compress';
import swagger from '@fastify/swagger';
import swaggerUi from '@fastify/swagger-ui';
import postgres from '@fastify/postgres';
import redis from '@fastify/redis';

import { gatewayConfig } from './config/index.js';
import smart402Plugin from './plugins/smart402.js';
import contractRoutes from './routes/contracts.js';
import healthRoutes from './routes/health.js';
import { addX402Headers, logSmart402Metrics } from './middleware/smart402.js';

// Create Fastify instance
const fastify = Fastify({
  logger: {
    level: gatewayConfig.logger.level,
    transport: gatewayConfig.logger.prettyPrint ? {
      target: 'pino-pretty',
      options: {
        translateTime: 'HH:MM:ss Z',
        ignore: 'pid,hostname'
      }
    } : undefined
  },
  requestIdHeader: 'x-request-id',
  requestIdLogLabel: 'reqId',
  disableRequestLogging: false,
  trustProxy: true
});

/**
 * Register plugins
 */
async function registerPlugins() {
  // Security
  await fastify.register(helmet, {
    contentSecurityPolicy: {
      directives: {
        defaultSrc: ["'self'"],
        styleSrc: ["'self'", "'unsafe-inline'"],
        scriptSrc: ["'self'", "'unsafe-inline'"],
        imgSrc: ["'self'", 'data:', 'https:']
      }
    }
  });

  // CORS
  await fastify.register(cors, {
    origin: gatewayConfig.cors.origin,
    credentials: gatewayConfig.cors.credentials
  });

  // Rate Limiting
  await fastify.register(rateLimit, {
    max: gatewayConfig.rateLimit.max,
    timeWindow: gatewayConfig.rateLimit.timeWindow,
    cache: 10000,
    allowList: ['127.0.0.1'],
    redis: fastify.redis, // Will use Redis after it's registered
    skipOnError: true
  });

  // Compression
  await fastify.register(compress, {
    global: true,
    encodings: ['gzip', 'deflate']
  });

  // PostgreSQL
  await fastify.register(postgres, {
    connectionString: gatewayConfig.postgres.url,
    max: gatewayConfig.postgres.max
  });

  fastify.log.info('PostgreSQL connected');

  // Redis
  await fastify.register(redis, {
    url: gatewayConfig.redis.url,
    family: 4
  });

  fastify.log.info('Redis connected');

  // Smart402 SDK
  await fastify.register(smart402Plugin);

  // Swagger Documentation
  await fastify.register(swagger, {
    openapi: {
      info: {
        title: 'Smart402 Scalable Architecture API',
        description: 'RESTful API for Smart402 contract management with AEO, LLMO, and X402 protocols',
        version: '1.0.0'
      },
      servers: [
        {
          url: `http://localhost:${gatewayConfig.port}`,
          description: 'Development server'
        }
      ],
      tags: [
        { name: 'contracts', description: 'Smart402 contract operations' },
        { name: 'payments', description: 'X402 payment operations' },
        { name: 'health', description: 'Health check endpoints' }
      ]
    }
  });

  await fastify.register(swaggerUi, {
    routePrefix: '/docs',
    uiConfig: {
      docExpansion: 'list',
      deepLinking: true
    },
    staticCSP: true,
    transformStaticCSP: (header) => header
  });

  fastify.log.info('Swagger UI available at /docs');
}

/**
 * Register routes
 */
async function registerRoutes() {
  // Global hooks
  fastify.addHook('onRequest', addX402Headers);
  fastify.addHook('onRequest', logSmart402Metrics);

  // Health routes
  await fastify.register(healthRoutes);

  // Contract routes
  await fastify.register(contractRoutes, { prefix: '/api/v1' });

  // Root route
  fastify.get('/', async (request, reply) => {
    return {
      name: 'Smart402 Scalable Architecture Gateway',
      version: '1.0.0',
      smart402: {
        aeo_enabled: true,
        llmo_enabled: true,
        x402_enabled: fastify.smart402.isRealMode(),
        mode: fastify.smart402.isRealMode() ? 'production' : 'demo'
      },
      endpoints: {
        health: '/health',
        docs: '/docs',
        contracts: '/api/v1/contracts',
        metrics: '/metrics'
      }
    };
  });
}

/**
 * Start server
 */
async function start() {
  try {
    // Register plugins
    await registerPlugins();

    // Register routes
    await registerRoutes();

    // Initialize database tables
    await initializeDatabase();

    // Start listening
    await fastify.listen({
      port: gatewayConfig.port,
      host: gatewayConfig.host
    });

    fastify.log.info(`🚀 Smart402 Gateway started on ${gatewayConfig.host}:${gatewayConfig.port}`);
    fastify.log.info(`📚 API Documentation: http://localhost:${gatewayConfig.port}/docs`);
    fastify.log.info(`🔍 Environment: ${gatewayConfig.env}`);

  } catch (error) {
    fastify.log.error('Failed to start server:', error);
    process.exit(1);
  }
}

/**
 * Initialize database tables
 */
async function initializeDatabase() {
  try {
    // Create contracts table if not exists
    await fastify.pg.query(`
      CREATE TABLE IF NOT EXISTS contracts (
        id SERIAL PRIMARY KEY,
        contract_id VARCHAR(255) UNIQUE NOT NULL,
        ucl JSONB NOT NULL,
        aeo_score DECIMAL(3, 2) NOT NULL,
        status VARCHAR(50) NOT NULL DEFAULT 'draft',
        created_at TIMESTAMP NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
        metadata JSONB DEFAULT '{}'::jsonb
      )
    `);

    // Create index on contract_id for fast lookups
    await fastify.pg.query(`
      CREATE INDEX IF NOT EXISTS idx_contracts_contract_id ON contracts(contract_id)
    `);

    // Create index on status for filtering
    await fastify.pg.query(`
      CREATE INDEX IF NOT EXISTS idx_contracts_status ON contracts(status)
    `);

    // Create index on created_at for sorting
    await fastify.pg.query(`
      CREATE INDEX IF NOT EXISTS idx_contracts_created_at ON contracts(created_at DESC)
    `);

    // Create GIN index on metadata for JSONB queries
    await fastify.pg.query(`
      CREATE INDEX IF NOT EXISTS idx_contracts_metadata ON contracts USING GIN(metadata)
    `);

    fastify.log.info('Database tables initialized');

  } catch (error) {
    fastify.log.error('Database initialization error:', error);
    throw error;
  }
}

/**
 * Graceful shutdown
 */
async function shutdown(signal: string) {
  fastify.log.info(`Received ${signal}, shutting down gracefully...`);

  try {
    await fastify.close();
    fastify.log.info('Server closed successfully');
    process.exit(0);
  } catch (error) {
    fastify.log.error('Error during shutdown:', error);
    process.exit(1);
  }
}

// Handle shutdown signals
process.on('SIGTERM', () => shutdown('SIGTERM'));
process.on('SIGINT', () => shutdown('SIGINT'));

// Handle unhandled rejections
process.on('unhandledRejection', (reason, promise) => {
  fastify.log.error('Unhandled Rejection at:', promise, 'reason:', reason);
  process.exit(1);
});

// Start the server
start();
