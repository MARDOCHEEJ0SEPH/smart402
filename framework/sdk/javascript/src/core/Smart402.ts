/**
 * Smart402 Main Class
 *
 * Entry point for creating and managing AI-native smart contracts.
 */

import { Contract } from './Contract';
import { AEOEngine } from '../aeo/AEOEngine';
import { LLMOEngine } from '../llmo/LLMOEngine';
import { X402Client } from '../x402/X402Client';
import { templates } from './templates';
import {
  ContractConfig,
  DeployOptions,
  NetworkConfig,
  Smart402Options
} from '../types';

export class Smart402 {
  private aeo: AEOEngine;
  private llmo: LLMOEngine;
  private x402: X402Client;
  private options: Smart402Options;

  constructor(options: Smart402Options = {}) {
    this.options = {
      network: options.network || 'polygon',
      apiKey: options.apiKey,
      rpcUrl: options.rpcUrl,
      privateKey: options.privateKey,
      ...options
    };

    this.aeo = new AEOEngine(this.options);
    this.llmo = new LLMOEngine(this.options);
    this.x402 = new X402Client(this.options);
  }

  /**
   * Create a new Smart402 contract
   *
   * @example
   * ```typescript
   * const contract = await Smart402.create({
   *   type: 'saas-subscription',
   *   parties: ['vendor@example.com', 'customer@example.com'],
   *   payment: {
   *     amount: 99,
   *     frequency: 'monthly',
   *     token: 'USDC'
   *   }
   * });
   * ```
   */
  static async create(config: ContractConfig): Promise<Contract> {
    const instance = new Smart402();
    return instance.createContract(config);
  }

  /**
   * Create a contract from template
   *
   * @example
   * ```typescript
   * const contract = await Smart402.fromTemplate('saas-subscription', {
   *   vendor: '0xVendor...',
   *   customer: '0xCustomer...',
   *   monthlyPrice: 99
   * });
   * ```
   */
  static async fromTemplate(
    templateName: string,
    variables: Record<string, any>
  ): Promise<Contract> {
    const instance = new Smart402();
    return instance.createFromTemplate(templateName, variables);
  }

  /**
   * Load existing contract by ID
   *
   * @example
   * ```typescript
   * const contract = await Smart402.load('smart402:saas:abc123');
   * ```
   */
  static async load(contractId: string): Promise<Contract> {
    const instance = new Smart402();
    return instance.loadContract(contractId);
  }

  /**
   * Create contract instance
   */
  async createContract(config: ContractConfig): Promise<Contract> {
    // Generate contract structure using LLMO
    const uclContract = await this.llmo.generateUCL(config);

    // Optimize for AI discovery using AEO
    const aeoMetadata = await this.aeo.optimize(uclContract);

    // Create contract instance
    const contract = new Contract({
      ucl: uclContract,
      aeo: aeoMetadata,
      x402: this.x402,
      options: this.options
    });

    return contract;
  }

  /**
   * Create from template
   */
  async createFromTemplate(
    templateName: string,
    variables: Record<string, any>
  ): Promise<Contract> {
    const template = templates[templateName];
    if (!template) {
      throw new Error(`Template '${templateName}' not found`);
    }

    const config = template.instantiate(variables);
    return this.createContract(config);
  }

  /**
   * Load existing contract
   */
  async loadContract(contractId: string): Promise<Contract> {
    // Fetch contract from registry
    const uclContract = await this.llmo.fetchContract(contractId);
    const aeoMetadata = await this.aeo.fetchMetadata(contractId);

    const contract = new Contract({
      ucl: uclContract,
      aeo: aeoMetadata,
      x402: this.x402,
      options: this.options
    });

    return contract;
  }

  /**
   * Get available templates
   */
  static getTemplates(): string[] {
    return Object.keys(templates);
  }

  /**
   * Get template documentation
   */
  static getTemplateDoc(templateName: string): any {
    const template = templates[templateName];
    if (!template) {
      throw new Error(`Template '${templateName}' not found`);
    }
    return template.documentation;
  }

  /**
   * Access AEO engine directly
   */
  get aeoEngine(): AEOEngine {
    return this.aeo;
  }

  /**
   * Access LLMO engine directly
   */
  get llmoEngine(): LLMOEngine {
    return this.llmo;
  }

  /**
   * Access X402 client directly
   */
  get x402Client(): X402Client {
    return this.x402;
  }
}

// Convenience exports
export const create = Smart402.create;
export const fromTemplate = Smart402.fromTemplate;
export const load = Smart402.load;
