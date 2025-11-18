/**
 * Smart402 X402 Payment Protocol
 * Automatic machine-to-machine payments with blockchain integration
 */

import { ethers } from 'ethers';
import type {
  X402Config,
  X402PaymentRequest,
  X402PaymentResult,
  X402Header
} from '../types/index.js';

export class X402Protocol {
  private provider?: ethers.JsonRpcProvider;
  private signer?: ethers.Wallet;
  private config: X402Config;
  private readonly version = '1.0.0';

  constructor(config: X402Config) {
    this.config = {
      gas_limit: 300000,
      gas_price_multiplier: 1.2,
      payment_token: 'USDC',
      chain_id: 137, // Polygon mainnet default
      ...config
    };

    if (config.private_key && config.provider_url) {
      this.initializeBlockchain();
    }
  }

  /**
   * Initialize blockchain connection
   */
  private initializeBlockchain(): void {
    try {
      this.provider = new ethers.JsonRpcProvider(this.config.provider_url);

      if (this.config.private_key) {
        this.signer = new ethers.Wallet(this.config.private_key, this.provider);
        console.log('✓ X402 Protocol initialized with wallet:', this.signer.address);
      }
    } catch (error) {
      console.error('Failed to initialize blockchain:', error);
      throw new Error('X402 blockchain initialization failed');
    }
  }

  /**
   * Generate X402 payment header
   */
  generateHeader(
    contractId: string,
    amount: string,
    currency: string = 'USDC',
    deadline?: number
  ): X402Header {
    if (!this.signer) {
      return this.generateDemoHeader(contractId, amount, currency, deadline);
    }

    const header: X402Header = {
      version: this.version,
      contract_id: contractId,
      payment_address: this.signer.address,
      payment_token: currency,
      amount,
      deadline: deadline || Math.floor(Date.now() / 1000) + 86400 // 24 hours default
    };

    // Sign the header
    const message = this.encodeHeaderForSigning(header);
    const signature = this.signMessage(message);
    header.signature = signature;

    return header;
  }

  /**
   * Execute X402 payment
   */
  async executePayment(request: X402PaymentRequest): Promise<X402PaymentResult> {
    if (!this.signer || !this.provider) {
      return this.simulatePayment(request);
    }

    try {
      console.log('Executing X402 payment:', request);

      // Check if using native token or ERC20
      const isNativeToken = this.config.payment_token === 'MATIC' || this.config.payment_token === 'ETH';

      let txHash: string;

      if (isNativeToken) {
        txHash = await this.executeNativePayment(request);
      } else {
        txHash = await this.executeTokenPayment(request);
      }

      // Wait for confirmation
      const receipt = await this.provider.waitForTransaction(txHash, 1);

      return {
        transaction_hash: txHash,
        status: receipt?.status === 1 ? 'confirmed' : 'failed',
        amount: request.amount,
        fee: this.calculateFee(receipt),
        timestamp: new Date(),
        block_number: receipt?.blockNumber,
        confirmations: 1
      };

    } catch (error) {
      console.error('Payment execution failed:', error);

      return {
        transaction_hash: '',
        status: 'failed',
        amount: request.amount,
        fee: '0',
        timestamp: new Date()
      };
    }
  }

  /**
   * Execute native token payment (MATIC, ETH)
   */
  private async executeNativePayment(request: X402PaymentRequest): Promise<string> {
    if (!this.signer) throw new Error('Signer not initialized');

    const tx = await this.signer.sendTransaction({
      to: request.recipient,
      value: ethers.parseUnits(request.amount, 18),
      gasLimit: this.config.gas_limit
    });

    return tx.hash;
  }

  /**
   * Execute ERC20 token payment (USDC, etc.)
   */
  private async executeTokenPayment(request: X402PaymentRequest): Promise<string> {
    if (!this.signer) throw new Error('Signer not initialized');

    // ERC20 transfer function signature
    const erc20Abi = [
      'function transfer(address to, uint256 amount) returns (bool)'
    ];

    // Get token contract address (you would have a registry for this)
    const tokenAddress = this.getTokenAddress(request.currency);

    const tokenContract = new ethers.Contract(tokenAddress, erc20Abi, this.signer);

    // Parse amount based on token decimals (USDC uses 6 decimals)
    const decimals = request.currency === 'USDC' ? 6 : 18;
    const amount = ethers.parseUnits(request.amount, decimals);

    const tx = await tokenContract.transfer(request.recipient, amount, {
      gasLimit: this.config.gas_limit
    });

    return tx.hash;
  }

  /**
   * Validate X402 header
   */
  async validateHeader(header: X402Header): Promise<boolean> {
    try {
      // Check version
      if (!header.version || header.version !== this.version) {
        console.warn('Invalid or unsupported X402 version');
        return false;
      }

      // Check required fields
      if (!header.contract_id || !header.payment_address || !header.amount) {
        console.warn('Missing required X402 header fields');
        return false;
      }

      // Check deadline
      if (header.deadline && header.deadline < Math.floor(Date.now() / 1000)) {
        console.warn('X402 payment deadline exceeded');
        return false;
      }

      // Verify signature if present
      if (header.signature) {
        const message = this.encodeHeaderForSigning(header);
        const recoveredAddress = this.recoverSigner(message, header.signature);

        if (recoveredAddress.toLowerCase() !== header.payment_address.toLowerCase()) {
          console.warn('X402 signature verification failed');
          return false;
        }
      }

      return true;

    } catch (error) {
      console.error('X402 header validation error:', error);
      return false;
    }
  }

  /**
   * Check payment status
   */
  async checkPaymentStatus(transactionHash: string): Promise<X402PaymentResult | null> {
    if (!this.provider) {
      return null;
    }

    try {
      const receipt = await this.provider.getTransactionReceipt(transactionHash);

      if (!receipt) {
        return {
          transaction_hash: transactionHash,
          status: 'pending',
          amount: '0',
          fee: '0',
          timestamp: new Date()
        };
      }

      const tx = await this.provider.getTransaction(transactionHash);
      const currentBlock = await this.provider.getBlockNumber();

      return {
        transaction_hash: transactionHash,
        status: receipt.status === 1 ? 'confirmed' : 'failed',
        amount: tx?.value ? ethers.formatEther(tx.value) : '0',
        fee: this.calculateFee(receipt),
        timestamp: new Date(),
        block_number: receipt.blockNumber,
        confirmations: currentBlock - receipt.blockNumber
      };

    } catch (error) {
      console.error('Failed to check payment status:', error);
      return null;
    }
  }

  /**
   * Estimate payment fees
   */
  async estimateFees(request: X402PaymentRequest): Promise<string> {
    if (!this.provider) {
      return '0.001'; // Demo estimate
    }

    try {
      const feeData = await this.provider.getFeeData();
      const gasPrice = feeData.gasPrice || ethers.parseUnits('50', 'gwei');

      const estimatedGas = BigInt(this.config.gas_limit || 300000);
      const totalFee = gasPrice * estimatedGas;

      return ethers.formatEther(totalFee);

    } catch (error) {
      console.error('Fee estimation failed:', error);
      return '0.001';
    }
  }

  /**
   * Encode header for signing
   */
  private encodeHeaderForSigning(header: X402Header): string {
    return ethers.solidityPackedKeccak256(
      ['string', 'string', 'address', 'string', 'string', 'uint256'],
      [
        header.version,
        header.contract_id,
        header.payment_address,
        header.payment_token,
        header.amount,
        header.deadline || 0
      ]
    );
  }

  /**
   * Sign message
   */
  private signMessage(message: string): string {
    if (!this.signer) {
      return '0x' + '0'.repeat(130); // Demo signature
    }

    // Note: This is a simplified version. In production, you'd use proper EIP-712 signing
    return 'signed:' + message.substring(0, 20);
  }

  /**
   * Recover signer from signature
   */
  private recoverSigner(message: string, signature: string): string {
    // Simplified version - in production use ethers.verifyMessage
    if (signature.startsWith('signed:')) {
      return this.signer?.address || '0x0000000000000000000000000000000000000000';
    }

    try {
      return ethers.recoverAddress(message, signature);
    } catch {
      return '0x0000000000000000000000000000000000000000';
    }
  }

  /**
   * Calculate transaction fee from receipt
   */
  private calculateFee(receipt: ethers.TransactionReceipt | null): string {
    if (!receipt) return '0';

    const gasUsed = receipt.gasUsed;
    const gasPrice = receipt.gasPrice || 0n;
    const fee = gasUsed * gasPrice;

    return ethers.formatEther(fee);
  }

  /**
   * Get token contract address
   */
  private getTokenAddress(currency: string): string {
    // Token addresses for Polygon mainnet
    const tokens: Record<string, string> = {
      'USDC': '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174',
      'USDT': '0xc2132D05D31c914a87C6611C10748AEb04B58e8F',
      'DAI': '0x8f3Cf7ad23Cd3CaDbD9735AFf958023239c6A063',
      'WETH': '0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619',
      'WBTC': '0x1BFD67037B42Cf73acF2047067bd4F2C47D9BfD6'
    };

    return tokens[currency] || tokens['USDC'];
  }

  /**
   * Generate demo header (when no wallet configured)
   */
  private generateDemoHeader(
    contractId: string,
    amount: string,
    currency: string,
    deadline?: number
  ): X402Header {
    return {
      version: this.version,
      contract_id: contractId,
      payment_address: '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb',
      payment_token: currency,
      amount,
      deadline: deadline || Math.floor(Date.now() / 1000) + 86400,
      signature: '0x' + '0'.repeat(130)
    };
  }

  /**
   * Simulate payment (demo mode)
   */
  private simulatePayment(request: X402PaymentRequest): X402PaymentResult {
    console.log('📝 Simulating X402 payment (Demo Mode)');
    console.log('   Amount:', request.amount, request.currency);
    console.log('   Recipient:', request.recipient);
    console.log('   Contract:', request.contract_id);

    const mockTxHash = '0x' + Array.from({ length: 64 }, () =>
      Math.floor(Math.random() * 16).toString(16)
    ).join('');

    return {
      transaction_hash: mockTxHash,
      status: 'confirmed',
      amount: request.amount,
      fee: '0.001',
      timestamp: new Date(),
      block_number: Math.floor(Math.random() * 1000000),
      confirmations: 1
    };
  }

  /**
   * Get wallet address
   */
  getWalletAddress(): string | undefined {
    return this.signer?.address;
  }

  /**
   * Check if real blockchain mode is active
   */
  isRealMode(): boolean {
    return this.signer !== undefined && this.provider !== undefined;
  }
}

export default X402Protocol;
