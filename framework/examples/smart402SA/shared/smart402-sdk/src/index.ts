/**
 * Smart402 SDK - Universal Contract Language Framework
 * Complete TypeScript implementation with AEO, LLMO, and X402 Protocol
 *
 * @packageDocumentation
 */

import { AEOEngine } from './aeo/index.js';
import { LLMOEngine } from './llmo/index.js';
import { X402Protocol } from './x402/index.js';

import type {
  Smart402Config,
  Smart402Contract,
  AEOConfig,
  AEOResult,
  LLMOConfig,
  LLMOResult,
  X402Config,
  X402PaymentRequest,
  X402PaymentResult,
  X402Header,
  UCLLayer,
  ValidationResult,
  ContractStatus
} from './types/index.js';

// Re-export all types
export * from './types/index.js';

// Re-export engines
export { AEOEngine } from './aeo/index.js';
export { LLMOEngine } from './llmo/index.js';
export { X402Protocol } from './x402/index.js';

/**
 * Main Smart402 SDK class
 * Orchestrates AEO, LLMO, and X402 engines to create complete smart contracts
 */
export class Smart402 {
  private aeoEngine: AEOEngine;
  private llmoEngine: LLMOEngine;
  private x402Protocol?: X402Protocol;

  constructor(
    aeoConfig?: AEOConfig,
    llmoConfig?: LLMOConfig,
    x402Config?: X402Config
  ) {
    this.aeoEngine = new AEOEngine(aeoConfig);
    this.llmoEngine = new LLMOEngine(llmoConfig);

    if (x402Config) {
      this.x402Protocol = new X402Protocol(x402Config);
    }
  }

  /**
   * Create a complete Smart402 contract with all layers
   */
  async create(config: Smart402Config): Promise<Smart402Contract> {
    console.log('🚀 Creating Smart402 Contract:', config.title);

    // Step 1: Generate UCL using LLMO Engine
    console.log('📝 Generating Universal Contract Language (UCL)...');
    const llmoResult = await this.llmoEngine.generateUCL(config);

    if (!llmoResult.validation.is_valid) {
      console.error('❌ UCL validation failed');
      throw new Error('UCL validation failed: ' + JSON.stringify(llmoResult.validation.errors));
    }

    console.log('✓ UCL generated and validated');
    console.log('  - Optimization Score:', (llmoResult.optimization_score * 100).toFixed(1) + '%');
    console.log('  - Token Efficiency:', llmoResult.token_efficiency.toFixed(0), 'chars/unit');

    // Step 2: Calculate AEO score
    console.log('🔍 Calculating AEO (Answer Engine Optimization) score...');
    const aeoResult = await this.aeoEngine.calculateScore(config, llmoResult.ucl);

    console.log('✓ AEO analysis complete');
    console.log('  - AEO Score:', (aeoResult.score * 100).toFixed(1) + '%');

    if (aeoResult.recommendations.length > 0) {
      console.log('  - Recommendations:', aeoResult.recommendations.length);
      aeoResult.recommendations.slice(0, 3).forEach(rec => {
        console.log(`    • [${rec.priority}] ${rec.message}`);
      });
    }

    // Step 3: Generate X402 payment header (if X402 enabled)
    let x402Header: X402Header | undefined;

    if (this.x402Protocol) {
      console.log('💰 Generating X402 payment header...');

      const contractId = this.generateContractId(config);
      const amount = config.terms?.amount || '0';
      const currency = config.terms?.currency || 'USDC';

      x402Header = this.x402Protocol.generateHeader(contractId, amount, currency);

      console.log('✓ X402 header generated');
      console.log('  - Payment Address:', x402Header.payment_address);
      console.log('  - Amount:', x402Header.amount, x402Header.payment_token);
    }

    // Step 4: Construct final contract
    const contractId = this.generateContractId(config);
    const contract: Smart402Contract = {
      contract_id: contractId,
      ucl: llmoResult.ucl,
      aeo_score: aeoResult.score,
      aeo_result: aeoResult,
      llmo_result: llmoResult,
      x402_header: x402Header,
      created_at: new Date(),
      updated_at: new Date(),
      status: 'validated' as ContractStatus,
      metadata: {
        ...config.metadata,
        sdk_version: '1.0.0',
        created_with: 'Smart402 SDK'
      }
    };

    console.log('✅ Smart402 Contract created successfully');
    console.log('   Contract ID:', contractId);

    return contract;
  }

  /**
   * Optimize an existing contract configuration
   */
  async optimize(config: Smart402Config): Promise<Smart402Config> {
    return this.aeoEngine.optimize(config);
  }

  /**
   * Validate a UCL structure
   */
  async validateUCL(ucl: UCLLayer): Promise<ValidationResult> {
    return this.llmoEngine.validateUCL(ucl);
  }

  /**
   * Execute payment for a contract
   */
  async executePayment(request: X402PaymentRequest): Promise<X402PaymentResult> {
    if (!this.x402Protocol) {
      throw new Error('X402 Protocol not initialized. Provide x402Config in constructor.');
    }

    return this.x402Protocol.executePayment(request);
  }

  /**
   * Check payment status
   */
  async checkPaymentStatus(transactionHash: string): Promise<X402PaymentResult | null> {
    if (!this.x402Protocol) {
      throw new Error('X402 Protocol not initialized');
    }

    return this.x402Protocol.checkPaymentStatus(transactionHash);
  }

  /**
   * Estimate payment fees
   */
  async estimatePaymentFees(request: X402PaymentRequest): Promise<string> {
    if (!this.x402Protocol) {
      return '0';
    }

    return this.x402Protocol.estimateFees(request);
  }

  /**
   * Validate X402 header
   */
  async validateX402Header(header: X402Header): Promise<boolean> {
    if (!this.x402Protocol) {
      return false;
    }

    return this.x402Protocol.validateHeader(header);
  }

  /**
   * Get wallet address (if X402 configured with private key)
   */
  getWalletAddress(): string | undefined {
    return this.x402Protocol?.getWalletAddress();
  }

  /**
   * Check if running in real blockchain mode
   */
  isRealMode(): boolean {
    return this.x402Protocol?.isRealMode() ?? false;
  }

  /**
   * Generate unique contract ID
   */
  private generateContractId(config: Smart402Config): string {
    const timestamp = Date.now();
    const random = Math.random().toString(36).substring(2, 8);
    const type = config.type.replace(/[^a-z0-9]/gi, '_').toLowerCase();

    return `smart402:${type}:${timestamp}_${random}`;
  }
}

/**
 * Factory function to create Smart402 instance
 */
export function createSmart402(
  aeoConfig?: AEOConfig,
  llmoConfig?: LLMOConfig,
  x402Config?: X402Config
): Smart402 {
  return new Smart402(aeoConfig, llmoConfig, x402Config);
}

/**
 * Quick start helper - creates a Smart402 instance with default configs
 */
export async function quickStart(x402Config?: X402Config): Promise<Smart402> {
  const defaultAEOConfig: AEOConfig = {
    target_score: 0.85,
    optimize_for: ['clarity', 'completeness', 'discoverability'],
    schema_org: true
  };

  const defaultLLMOConfig: LLMOConfig = {
    optimization_level: 'high',
    validate_ucl: true,
    include_examples: true
  };

  return new Smart402(defaultAEOConfig, defaultLLMOConfig, x402Config);
}

// Default export
export default Smart402;
