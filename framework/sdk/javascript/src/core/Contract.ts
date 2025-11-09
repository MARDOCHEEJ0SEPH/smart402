/**
 * Contract Class
 *
 * Represents a Smart402 contract instance with full lifecycle management.
 */

import { X402Client } from '../x402/X402Client';
import {
  UCLContract,
  AEOMetadata,
  DeployOptions,
  DeployResult,
  ContractStatus,
  PaymentResult,
  Smart402Options
} from '../types';

export class Contract {
  public readonly id: string;
  public readonly ucl: UCLContract;
  public readonly aeo: AEOMetadata;
  private x402: X402Client;
  private options: Smart402Options;
  private _status: ContractStatus = 'draft';
  private _deployedAddress?: string;
  private _transactionHash?: string;

  constructor(config: {
    ucl: UCLContract;
    aeo: AEOMetadata;
    x402: X402Client;
    options: Smart402Options;
  }) {
    this.ucl = config.ucl;
    this.aeo = config.aeo;
    this.x402 = config.x402;
    this.options = config.options;
    this.id = config.ucl.contract_id;
  }

  /**
   * Deploy contract to blockchain
   *
   * @example
   * ```typescript
   * const result = await contract.deploy({
   *   network: 'polygon',
   *   gasLimit: 1000000
   * });
   *
   * console.log('Deployed to:', result.address);
   * console.log('Transaction:', result.transactionHash);
   * ```
   */
  async deploy(options: DeployOptions = {}): Promise<DeployResult> {
    if (this._status === 'deployed') {
      throw new Error('Contract already deployed');
    }

    this._status = 'deploying';

    try {
      // Compile UCL to Solidity
      const solidity = await this.compile('solidity');

      // Deploy to blockchain
      const deployment = await this.x402.deploy({
        code: solidity,
        network: options.network || this.options.network || 'polygon',
        gasLimit: options.gasLimit,
        gasPrice: options.gasPrice
      });

      this._deployedAddress = deployment.address;
      this._transactionHash = deployment.transactionHash;
      this._status = 'deployed';

      // Register in Smart402 registry
      await this.register();

      return {
        success: true,
        address: deployment.address,
        transactionHash: deployment.transactionHash,
        network: deployment.network,
        blockNumber: deployment.blockNumber,
        contractId: this.id
      };
    } catch (error) {
      this._status = 'failed';
      throw error;
    }
  }

  /**
   * Compile contract to target language
   *
   * @example
   * ```typescript
   * const solidity = await contract.compile('solidity');
   * const javascript = await contract.compile('javascript');
   * ```
   */
  async compile(target: 'solidity' | 'javascript' | 'rust' = 'solidity'): Promise<string> {
    const { compile } = await import('../utils/compiler');
    return compile(this.ucl, { target });
  }

  /**
   * Execute payment manually
   *
   * @example
   * ```typescript
   * const result = await contract.executePayment({
   *   amount: 99,
   *   from: '0xCustomer...',
   *   to: '0xVendor...'
   * });
   * ```
   */
  async executePayment(params?: {
    amount?: number;
    from?: string;
    to?: string;
  }): Promise<PaymentResult> {
    if (this._status !== 'deployed') {
      throw new Error('Contract must be deployed before executing payments');
    }

    const payment = await this.x402.executePayment({
      contractId: this.id,
      contractAddress: this._deployedAddress!,
      amount: params?.amount || this.ucl.payment.amount,
      token: this.ucl.payment.token,
      network: this.options.network || 'polygon',
      from: params?.from,
      to: params?.to
    });

    return payment;
  }

  /**
   * Start automatic monitoring and execution
   *
   * @example
   * ```typescript
   * await contract.startMonitoring({
   *   frequency: 'hourly',
   *   webhook: 'https://api.example.com/webhooks'
   * });
   * ```
   */
  async startMonitoring(options: {
    frequency?: 'realtime' | 'high' | 'medium' | 'low' | 'daily';
    webhook?: string;
  } = {}): Promise<void> {
    if (this._status !== 'deployed') {
      throw new Error('Contract must be deployed before monitoring');
    }

    await this.x402.startMonitoring({
      contractId: this.id,
      contractAddress: this._deployedAddress!,
      conditions: this.ucl.conditions,
      oracles: this.ucl.oracles,
      frequency: options.frequency || 'medium',
      webhook: options.webhook
    });

    console.log(`Monitoring started for contract ${this.id}`);
  }

  /**
   * Stop automatic monitoring
   */
  async stopMonitoring(): Promise<void> {
    await this.x402.stopMonitoring(this.id);
    console.log(`Monitoring stopped for contract ${this.id}`);
  }

  /**
   * Check if conditions are met
   *
   * @example
   * ```typescript
   * const status = await contract.checkConditions();
   * console.log('Conditions met:', status.allMet);
   * ```
   */
  async checkConditions(): Promise<{
    allMet: boolean;
    conditions: Record<string, boolean>;
    timestamp: Date;
  }> {
    const result = await this.x402.checkConditions({
      contractId: this.id,
      conditions: this.ucl.conditions,
      oracles: this.ucl.oracles
    });

    return result;
  }

  /**
   * Get contract status
   */
  get status(): ContractStatus {
    return this._status;
  }

  /**
   * Get deployed address
   */
  get address(): string | undefined {
    return this._deployedAddress;
  }

  /**
   * Get deployment transaction hash
   */
  get transactionHash(): string | undefined {
    return this._transactionHash;
  }

  /**
   * Export contract to various formats
   *
   * @example
   * ```typescript
   * const yaml = await contract.export('yaml');
   * const json = await contract.export('json');
   * ```
   */
  async export(format: 'yaml' | 'json' | 'ucl' = 'yaml'): Promise<string> {
    const { exportContract } = await import('../utils/export');
    return exportContract(this.ucl, format);
  }

  /**
   * Get natural language summary
   *
   * @example
   * ```typescript
   * const summary = contract.getSummary();
   * console.log(summary);
   * // "This contract charges $99/month for SaaS service..."
   * ```
   */
  getSummary(): string {
    return this.ucl.summary?.plain_english || 'No summary available';
  }

  /**
   * Get AEO score
   */
  getAEOScore(): number {
    return this.aeo.score || 0;
  }

  /**
   * Get contract parties
   */
  getParties(): Array<{ role: string; identifier: string; name?: string }> {
    return this.ucl.metadata.parties;
  }

  /**
   * Get payment terms
   */
  getPaymentTerms(): {
    amount: number;
    frequency: string;
    token: string;
    blockchain: string;
  } {
    return {
      amount: this.ucl.payment.amount,
      frequency: this.ucl.payment.frequency,
      token: this.ucl.payment.token,
      blockchain: this.ucl.payment.blockchain
    };
  }

  /**
   * Validate contract structure
   */
  async validate(): Promise<{
    valid: boolean;
    errors: string[];
  }> {
    const { validateUCL } = await import('../utils/validator');
    return validateUCL(this.ucl);
  }

  /**
   * Register contract in Smart402 registry
   */
  private async register(): Promise<void> {
    // This would register with the on-chain registry
    // For now, it's a placeholder
    console.log(`Registering contract ${this.id} in registry...`);
  }

  /**
   * Convert contract to JSON
   */
  toJSON(): any {
    return {
      id: this.id,
      ucl: this.ucl,
      aeo: this.aeo,
      status: this._status,
      address: this._deployedAddress,
      transactionHash: this._transactionHash
    };
  }

  /**
   * Get contract URL for viewing
   */
  getURL(): string {
    if (this._deployedAddress) {
      const network = this.options.network || 'polygon';
      const explorer = this.getExplorerURL(network);
      return `${explorer}/address/${this._deployedAddress}`;
    }
    return `https://smart402.io/contracts/${this.id}`;
  }

  private getExplorerURL(network: string): string {
    const explorers: Record<string, string> = {
      ethereum: 'https://etherscan.io',
      polygon: 'https://polygonscan.com',
      arbitrum: 'https://arbiscan.io',
      optimism: 'https://optimistic.etherscan.io',
      base: 'https://basescan.org'
    };
    return explorers[network] || explorers.polygon;
  }
}
