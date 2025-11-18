/**
 * Health Check Routes
 * Status and health monitoring endpoints
 */

import type { FastifyInstance } from 'fastify';

export default async function healthRoutes(fastify: FastifyInstance) {
  /**
   * GET /health - Basic health check
   */
  fastify.get('/health', async (request, reply) => {
    return {
      status: 'healthy',
      timestamp: new Date().toISOString(),
      uptime: process.uptime(),
      environment: process.env.NODE_ENV,
      smart402: {
        version: '1.0.0',
        mode: fastify.smart402.isRealMode() ? 'production' : 'demo'
      }
    };
  });

  /**
   * GET /health/ready - Readiness probe
   */
  fastify.get('/health/ready', async (request, reply) => {
    try {
      // Check PostgreSQL
      await fastify.pg.query('SELECT 1');

      // Check Redis
      await fastify.redis.ping();

      return {
        status: 'ready',
        checks: {
          postgres: 'ok',
          redis: 'ok',
          smart402: 'ok'
        }
      };
    } catch (error) {
      reply.code(503);
      return {
        status: 'not ready',
        error: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  });

  /**
   * GET /health/live - Liveness probe
   */
  fastify.get('/health/live', async (request, reply) => {
    return {
      status: 'alive',
      timestamp: new Date().toISOString()
    };
  });

  /**
   * GET /metrics - Prometheus metrics
   */
  fastify.get('/metrics', async (request, reply) => {
    // Return basic metrics in Prometheus format
    const metrics = `
# HELP smart402_gateway_uptime_seconds Gateway uptime in seconds
# TYPE smart402_gateway_uptime_seconds gauge
smart402_gateway_uptime_seconds ${process.uptime()}

# HELP smart402_gateway_memory_usage_bytes Memory usage in bytes
# TYPE smart402_gateway_memory_usage_bytes gauge
smart402_gateway_memory_usage_bytes ${process.memoryUsage().heapUsed}

# HELP smart402_gateway_requests_total Total number of requests
# TYPE smart402_gateway_requests_total counter
smart402_gateway_requests_total ${fastify.metrics?.requestCount || 0}
    `.trim();

    reply.type('text/plain');
    return metrics;
  });
}
