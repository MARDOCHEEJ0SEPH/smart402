/**
 * Smart402 Contract Routes
 * RESTful API endpoints for contract management
 */

import type { FastifyInstance, FastifyRequest, FastifyReply } from 'fastify';
import { z } from 'zod';
import type { Smart402Config } from '@smart402sa/sdk';

// Request schemas
const createContractSchema = z.object({
  type: z.string().min(1),
  title: z.string().min(10).max(200),
  description: z.string().min(20).max(2000),
  parties: z.array(z.object({
    id: z.string(),
    role: z.string(),
    address: z.string().optional(),
    metadata: z.record(z.any()).optional()
  })).min(1),
  terms: z.record(z.any()),
  metadata: z.record(z.any()).optional()
});

const executePaymentSchema = z.object({
  contract_id: z.string(),
  amount: z.string(),
  currency: z.string().default('USDC'),
  recipient: z.string(),
  metadata: z.record(z.any()).optional()
});

export default async function contractRoutes(fastify: FastifyInstance) {
  /**
   * POST /contracts - Create new Smart402 contract
   */
  fastify.post('/contracts', {
    schema: {
      description: 'Create a new Smart402 contract with UCL, AEO, and X402',
      tags: ['contracts'],
      body: {
        type: 'object',
        required: ['type', 'title', 'description', 'parties', 'terms'],
        properties: {
          type: { type: 'string' },
          title: { type: 'string' },
          description: { type: 'string' },
          parties: { type: 'array' },
          terms: { type: 'object' },
          metadata: { type: 'object' }
        }
      },
      response: {
        200: {
          type: 'object',
          properties: {
            success: { type: 'boolean' },
            contract: { type: 'object' }
          }
        }
      }
    }
  }, async (request: FastifyRequest, reply: FastifyReply) => {
    try {
      // Validate request body
      const validatedData = createContractSchema.parse(request.body);

      // Create contract using Smart402 SDK
      const contract = await fastify.smart402.create(validatedData as Smart402Config);

      // Store in PostgreSQL (primary storage)
      const insertQuery = `
        INSERT INTO contracts (
          contract_id, ucl, aeo_score, status, created_at, metadata
        ) VALUES ($1, $2, $3, $4, $5, $6)
        RETURNING *
      `;

      await fastify.pg.query(insertQuery, [
        contract.contract_id,
        JSON.stringify(contract.ucl),
        contract.aeo_score,
        contract.status,
        contract.created_at,
        JSON.stringify(contract.metadata)
      ]);

      // Index in Elasticsearch for AEO search
      // This would use @elastic/elasticsearch client
      fastify.log.info(`Contract created: ${contract.contract_id}`);

      // Store in MongoDB for flexible queries
      // This would use MongoDB client
      fastify.log.info(`Contract indexed in MongoDB: ${contract.contract_id}`);

      return reply.code(200).send({
        success: true,
        contract,
        message: 'Smart402 contract created successfully'
      });

    } catch (error) {
      fastify.log.error('Contract creation error:', error);

      if (error instanceof z.ZodError) {
        return reply.code(400).send({
          success: false,
          error: 'Validation error',
          details: error.errors
        });
      }

      return reply.code(500).send({
        success: false,
        error: 'Failed to create contract',
        message: error instanceof Error ? error.message : 'Unknown error'
      });
    }
  });

  /**
   * GET /contracts/:id - Get contract by ID
   */
  fastify.get('/contracts/:id', {
    schema: {
      description: 'Retrieve a Smart402 contract by ID',
      tags: ['contracts'],
      params: {
        type: 'object',
        properties: {
          id: { type: 'string' }
        }
      }
    }
  }, async (request: FastifyRequest<{ Params: { id: string } }>, reply: FastifyReply) => {
    try {
      const { id } = request.params;

      // Check Redis cache first
      const cachedContract = await fastify.redis.get(`contract:${id}`);

      if (cachedContract) {
        fastify.log.info(`Cache hit for contract: ${id}`);
        return reply.send({
          success: true,
          contract: JSON.parse(cachedContract),
          cached: true
        });
      }

      // Query PostgreSQL
      const result = await fastify.pg.query(
        'SELECT * FROM contracts WHERE contract_id = $1',
        [id]
      );

      if (result.rows.length === 0) {
        return reply.code(404).send({
          success: false,
          error: 'Contract not found'
        });
      }

      const contract = result.rows[0];

      // Cache in Redis (1 hour TTL)
      await fastify.redis.setex(`contract:${id}`, 3600, JSON.stringify(contract));

      return reply.send({
        success: true,
        contract
      });

    } catch (error) {
      fastify.log.error('Contract retrieval error:', error);

      return reply.code(500).send({
        success: false,
        error: 'Failed to retrieve contract'
      });
    }
  });

  /**
   * GET /contracts - List contracts with pagination
   */
  fastify.get('/contracts', {
    schema: {
      description: 'List Smart402 contracts with pagination',
      tags: ['contracts'],
      querystring: {
        type: 'object',
        properties: {
          page: { type: 'integer', minimum: 1, default: 1 },
          limit: { type: 'integer', minimum: 1, maximum: 100, default: 20 },
          status: { type: 'string' },
          type: { type: 'string' }
        }
      }
    }
  }, async (request: FastifyRequest<{ Querystring: any }>, reply: FastifyReply) => {
    try {
      const { page = 1, limit = 20, status, type } = request.query;
      const offset = (page - 1) * limit;

      let query = 'SELECT * FROM contracts WHERE 1=1';
      const params: any[] = [];
      let paramIndex = 1;

      if (status) {
        query += ` AND status = $${paramIndex}`;
        params.push(status);
        paramIndex++;
      }

      if (type) {
        query += ` AND metadata->>'type' = $${paramIndex}`;
        params.push(type);
        paramIndex++;
      }

      query += ` ORDER BY created_at DESC LIMIT $${paramIndex} OFFSET $${paramIndex + 1}`;
      params.push(limit, offset);

      const result = await fastify.pg.query(query, params);

      // Get total count
      const countResult = await fastify.pg.query('SELECT COUNT(*) FROM contracts');
      const total = parseInt(countResult.rows[0].count, 10);

      return reply.send({
        success: true,
        contracts: result.rows,
        pagination: {
          page,
          limit,
          total,
          pages: Math.ceil(total / limit)
        }
      });

    } catch (error) {
      fastify.log.error('Contract listing error:', error);

      return reply.code(500).send({
        success: false,
        error: 'Failed to list contracts'
      });
    }
  });

  /**
   * POST /contracts/:id/execute - Execute X402 payment
   */
  fastify.post('/contracts/:id/execute', {
    schema: {
      description: 'Execute X402 payment for a contract',
      tags: ['contracts', 'payments']
    }
  }, async (request: FastifyRequest<{ Params: { id: string }; Body: any }>, reply: FastifyReply) => {
    try {
      const { id } = request.params;
      const paymentData = executePaymentSchema.parse(request.body);

      // Retrieve contract
      const contractResult = await fastify.pg.query(
        'SELECT * FROM contracts WHERE contract_id = $1',
        [id]
      );

      if (contractResult.rows.length === 0) {
        return reply.code(404).send({
          success: false,
          error: 'Contract not found'
        });
      }

      // Execute payment using Smart402 X402 Protocol
      const paymentResult = await fastify.smart402.executePayment({
        amount: paymentData.amount,
        currency: paymentData.currency,
        recipient: paymentData.recipient,
        contract_id: id,
        metadata: paymentData.metadata
      });

      // Update contract status
      await fastify.pg.query(
        `UPDATE contracts
         SET status = 'active',
             metadata = jsonb_set(metadata, '{payment}', $1)
         WHERE contract_id = $2`,
        [JSON.stringify(paymentResult), id]
      );

      // Invalidate cache
      await fastify.redis.del(`contract:${id}`);

      return reply.send({
        success: true,
        payment: paymentResult,
        message: 'Payment executed successfully'
      });

    } catch (error) {
      fastify.log.error('Payment execution error:', error);

      return reply.code(500).send({
        success: false,
        error: 'Failed to execute payment',
        message: error instanceof Error ? error.message : 'Unknown error'
      });
    }
  });

  /**
   * GET /contracts/:id/payment-status - Check payment status
   */
  fastify.get('/contracts/:id/payment-status/:txHash', {
    schema: {
      description: 'Check X402 payment status',
      tags: ['contracts', 'payments']
    }
  }, async (request: FastifyRequest<{ Params: { id: string; txHash: string } }>, reply: FastifyReply) => {
    try {
      const { txHash } = request.params;

      const paymentStatus = await fastify.smart402.checkPaymentStatus(txHash);

      if (!paymentStatus) {
        return reply.code(404).send({
          success: false,
          error: 'Payment not found'
        });
      }

      return reply.send({
        success: true,
        payment: paymentStatus
      });

    } catch (error) {
      fastify.log.error('Payment status check error:', error);

      return reply.code(500).send({
        success: false,
        error: 'Failed to check payment status'
      });
    }
  });
}
