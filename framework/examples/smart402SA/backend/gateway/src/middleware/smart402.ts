/**
 * Smart402 Middleware
 * Request/Response middleware for Smart402 integration
 */

import type { FastifyRequest, FastifyReply, HookHandlerDoneFunction } from 'fastify';

/**
 * Add X402 headers to response
 */
export async function addX402Headers(
  request: FastifyRequest,
  reply: FastifyReply
) {
  // Add X402 protocol version header
  reply.header('X-Smart402-Version', '1.0.0');

  // Add AEO optimization hint
  reply.header('X-Smart402-AEO-Enabled', 'true');

  // If response includes contract, add X402 payment header
  reply.addHook('onSend', async (request, reply, payload) => {
    try {
      const data = JSON.parse(payload as string);

      if (data?.contract?.x402_header) {
        reply.header('X-Smart402-Payment-Address', data.contract.x402_header.payment_address);
        reply.header('X-Smart402-Payment-Token', data.contract.x402_header.payment_token);
        reply.header('X-Smart402-Payment-Amount', data.contract.x402_header.amount);
      }
    } catch {
      // Not JSON or doesn't have contract - skip
    }

    return payload;
  });
}

/**
 * Validate X402 payment header in request
 */
export async function validateX402Header(
  request: FastifyRequest,
  reply: FastifyReply
) {
  const x402Header = request.headers['x-smart402-payment'];

  if (!x402Header) {
    return; // Optional header
  }

  try {
    const header = JSON.parse(x402Header as string);
    const isValid = await request.server.smart402.validateX402Header(header);

    if (!isValid) {
      reply.code(400).send({
        error: 'Invalid X402 payment header',
        message: 'The provided X402 header is invalid or expired'
      });
      return;
    }

    // Attach validated header to request
    (request as any).x402Header = header;
  } catch (error) {
    reply.code(400).send({
      error: 'Malformed X402 header',
      message: 'Could not parse X402 payment header'
    });
  }
}

/**
 * Log Smart402 metrics
 */
export async function logSmart402Metrics(
  request: FastifyRequest,
  reply: FastifyReply,
  done: HookHandlerDoneFunction
) {
  const startTime = Date.now();

  reply.addHook('onSend', async (request, reply) => {
    const duration = Date.now() - startTime;

    request.log.info({
      smart402: {
        duration_ms: duration,
        aeo_enabled: true,
        x402_enabled: request.server.smart402.isRealMode(),
        route: request.url
      }
    });
  });

  done();
}

/**
 * Rate limiting for Smart402 operations
 */
export async function smart402RateLimit(
  request: FastifyRequest,
  reply: FastifyReply
) {
  // Custom rate limiting logic for expensive Smart402 operations
  const rateLimitKey = `smart402:${request.ip}:${request.url}`;

  // This would typically use Redis
  // For now, it's a placeholder for the pattern
}

/**
 * AEO optimization middleware
 * Optimizes response for Answer Engine discoverability
 */
export async function aeoOptimize(
  request: FastifyRequest,
  reply: FastifyReply
) {
  reply.addHook('onSend', async (request, reply, payload) => {
    try {
      const data = JSON.parse(payload as string);

      // Add AEO metadata to response
      if (data && typeof data === 'object') {
        data.aeo_optimized = true;
        data.aeo_timestamp = new Date().toISOString();

        return JSON.stringify(data);
      }
    } catch {
      // Not JSON - skip optimization
    }

    return payload;
  });
}
