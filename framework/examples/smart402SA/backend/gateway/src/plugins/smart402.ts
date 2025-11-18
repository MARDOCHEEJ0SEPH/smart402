/**
 * Smart402 Fastify Plugin
 * Integrates Smart402 SDK with Fastify
 */

import fp from 'fastify-plugin';
import { Smart402 } from '@smart402sa/sdk';
import type { FastifyPluginAsync } from 'fastify';
import { gatewayConfig } from '../config/index.js';

declare module 'fastify' {
  interface FastifyInstance {
    smart402: Smart402;
  }
}

const smart402Plugin: FastifyPluginAsync = async (fastify, options) => {
  // Initialize Smart402 SDK
  const smart402 = new Smart402(
    // AEO Config
    {
      target_score: gatewayConfig.smart402.aeo_target_score,
      optimize_for: ['clarity', 'completeness', 'discoverability'],
      schema_org: true
    },
    // LLMO Config
    {
      optimization_level: gatewayConfig.smart402.llmo_optimization_level,
      validate_ucl: true,
      include_examples: true
    },
    // X402 Config (only if blockchain credentials provided)
    gatewayConfig.blockchain.private_key ? {
      provider_url: gatewayConfig.blockchain.rpc_url,
      private_key: gatewayConfig.blockchain.private_key,
      chain_id: gatewayConfig.blockchain.chain_id,
      payment_token: 'USDC'
    } : undefined
  );

  // Decorate Fastify instance
  fastify.decorate('smart402', smart402);

  fastify.log.info('Smart402 SDK initialized');

  if (smart402.isRealMode()) {
    fastify.log.info(`Smart402 wallet: ${smart402.getWalletAddress()}`);
  } else {
    fastify.log.warn('Smart402 running in DEMO mode (no blockchain credentials)');
  }
};

export default fp(smart402Plugin, {
  name: 'smart402',
  dependencies: []
});
