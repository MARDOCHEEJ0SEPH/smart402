/**
 * Smart402 JavaScript SDK
 *
 * Universal Protocol for AI-Native Smart Contracts
 *
 * @example
 * ```typescript
 * import { Smart402 } from '@smart402/sdk';
 *
 * const contract = await Smart402.create({
 *   type: 'saas-subscription',
 *   parties: ['vendor@example.com', 'customer@example.com'],
 *   payment: {
 *     amount: 1000,
 *     frequency: 'monthly',
 *     token: 'USDC'
 *   }
 * });
 *
 * await contract.deploy({ network: 'polygon' });
 * ```
 */

export { Smart402 } from './core/Smart402';
export { Contract } from './core/Contract';
export { AEOEngine } from './aeo/AEOEngine';
export { LLMOEngine } from './llmo/LLMOEngine';
export { X402Client } from './x402/X402Client';

// Types
export * from './types';

// Templates
export { templates } from './core/templates';

// Utils
export { validateUCL, compileContract, formatAmount } from './utils';

// Version
export const VERSION = '1.0.0';
