/**
 * Smart402 JavaScript SDK Tests
 *
 * Comprehensive test suite for Smart402 SDK functionality
 */

const { Smart402 } = require('../src/core/Smart402');
const { Contract } = require('../src/core/Contract');

describe('Smart402 SDK', () => {
  describe('Contract Creation', () => {
    test('should create a basic SaaS subscription contract', async () => {
      const contract = await Smart402.create({
        type: 'saas-subscription',
        parties: ['vendor@example.com', 'customer@example.com'],
        payment: {
          amount: 99,
          token: 'USDC',
          blockchain: 'polygon',
          frequency: 'monthly'
        }
      });

      expect(contract).toBeInstanceOf(Contract);
      expect(contract.ucl.contract_id).toContain('smart402:');
      expect(contract.ucl.payment.amount).toBe(99);
      expect(contract.ucl.payment.token).toBe('USDC');
      expect(contract.ucl.metadata.parties).toHaveLength(2);
    });

    test('should create contract from template', async () => {
      const contract = await Smart402.fromTemplate('saas-subscription', {
        vendor_email: 'vendor@test.com',
        customer_email: 'customer@test.com',
        amount: 49
      });

      expect(contract).toBeInstanceOf(Contract);
      expect(contract.ucl.payment.amount).toBe(49);
    });

    test('should validate required fields', async () => {
      await expect(Smart402.create({
        type: 'invalid',
        parties: []
      })).rejects.toThrow();
    });

    test('should generate unique contract IDs', async () => {
      const contract1 = await Smart402.create({
        type: 'test',
        parties: ['a@test.com', 'b@test.com'],
        payment: { amount: 10, token: 'USDC', blockchain: 'polygon', frequency: 'monthly' }
      });

      const contract2 = await Smart402.create({
        type: 'test',
        parties: ['a@test.com', 'b@test.com'],
        payment: { amount: 10, token: 'USDC', blockchain: 'polygon', frequency: 'monthly' }
      });

      expect(contract1.ucl.contract_id).not.toBe(contract2.ucl.contract_id);
    });
  });

  describe('AEO (Answer Engine Optimization)', () => {
    let contract;

    beforeEach(async () => {
      contract = await Smart402.create({
        type: 'saas-subscription',
        parties: ['vendor@example.com', 'customer@example.com'],
        payment: {
          amount: 99,
          token: 'USDC',
          blockchain: 'polygon',
          frequency: 'monthly'
        },
        metadata: {
          title: 'Monthly SaaS Subscription',
          description: 'Automated monthly payment for software service',
          category: 'saas'
        }
      });
    });

    test('should calculate AEO score', () => {
      const score = contract.getAEOScore();

      expect(score).toHaveProperty('total');
      expect(score).toHaveProperty('semantic_richness');
      expect(score).toHaveProperty('citation_friendliness');
      expect(score).toHaveProperty('findability');
      expect(score).toHaveProperty('authority_signals');
      expect(score).toHaveProperty('citation_presence');

      expect(score.total).toBeGreaterThanOrEqual(0);
      expect(score.total).toBeLessThanOrEqual(1);
    });

    test('should generate JSON-LD markup', () => {
      const jsonld = contract.generateJSONLD();

      expect(jsonld).toContain('@context');
      expect(jsonld).toContain('https://schema.org/');
      expect(jsonld).toContain('SmartContract');
      expect(jsonld).toContain(contract.ucl.contract_id);
    });

    test('should improve score with better metadata', async () => {
      const basicContract = await Smart402.create({
        type: 'test',
        parties: ['a@test.com', 'b@test.com'],
        payment: { amount: 10, token: 'USDC', blockchain: 'polygon', frequency: 'monthly' }
      });

      const richContract = await Smart402.create({
        type: 'test',
        parties: ['a@test.com', 'b@test.com'],
        payment: { amount: 10, token: 'USDC', blockchain: 'polygon', frequency: 'monthly' },
        metadata: {
          title: 'Comprehensive Test Contract',
          description: 'Detailed description with rich metadata',
          category: 'testing',
          tags: ['test', 'example', 'smart402']
        }
      });

      const basicScore = basicContract.getAEOScore();
      const richScore = richContract.getAEOScore();

      expect(richScore.total).toBeGreaterThanOrEqual(basicScore.total);
    });
  });

  describe('LLMO (Large Language Model Optimization)', () => {
    let contract;

    beforeEach(async () => {
      contract = await Smart402.create({
        type: 'saas-subscription',
        parties: ['vendor@example.com', 'customer@example.com'],
        payment: {
          amount: 99,
          token: 'USDC',
          blockchain: 'polygon',
          frequency: 'monthly'
        }
      });
    });

    test('should validate contract', () => {
      const validation = contract.validate();

      expect(validation).toHaveProperty('valid');
      expect(validation).toHaveProperty('errors');
      expect(validation).toHaveProperty('warnings');
      expect(validation.valid).toBe(true);
      expect(validation.errors).toHaveLength(0);
    });

    test('should generate human-readable explanation', () => {
      const explanation = contract.explain();

      expect(explanation).toContain('contract');
      expect(explanation).toContain('payment');
      expect(typeof explanation).toBe('string');
      expect(explanation.length).toBeGreaterThan(0);
    });

    test('should compile to Solidity', async () => {
      const solidity = await contract.compile('solidity');

      expect(solidity).toContain('pragma solidity');
      expect(solidity).toContain('contract');
      expect(solidity).toContain('function');
    });

    test('should compile to JavaScript', async () => {
      const javascript = await contract.compile('javascript');

      expect(javascript).toContain('class');
      expect(javascript).toContain('async');
      expect(javascript).toContain('executePayment');
    });

    test('should compile to Rust', async () => {
      const rust = await contract.compile('rust');

      expect(rust).toContain('pub struct');
      expect(rust).toContain('impl');
      expect(rust).toContain('execute_payment');
    });

    test('should detect validation errors', async () => {
      const invalidContract = await Smart402.create({
        type: 'test',
        parties: [],  // Invalid: no parties
        payment: { amount: -10, token: 'USDC', blockchain: 'polygon', frequency: 'monthly' }  // Invalid: negative amount
      });

      const validation = invalidContract.validate();

      expect(validation.valid).toBe(false);
      expect(validation.errors.length).toBeGreaterThan(0);
    });
  });

  describe('X402 Protocol', () => {
    let contract;

    beforeEach(async () => {
      contract = await Smart402.create({
        type: 'api-payment',
        parties: ['provider@api.com', 'consumer@client.com'],
        payment: {
          amount: 0.10,
          token: 'USDC',
          blockchain: 'polygon',
          frequency: 'per-request'
        }
      });
    });

    test('should generate X402 headers', () => {
      const headers = contract.generateX402Headers(true);

      expect(headers).toHaveProperty('X402-Contract-ID');
      expect(headers).toHaveProperty('X402-Payment-Amount');
      expect(headers).toHaveProperty('X402-Payment-Token');
      expect(headers).toHaveProperty('X402-Settlement-Network');
      expect(headers).toHaveProperty('X402-Conditions-Met');
      expect(headers).toHaveProperty('X402-Signature');
      expect(headers).toHaveProperty('X402-Nonce');

      expect(headers['X402-Contract-ID']).toBe(contract.ucl.contract_id);
      expect(headers['X402-Payment-Amount']).toBe('0.10');
      expect(headers['X402-Payment-Token']).toBe('USDC');
    });

    test('should include nonce in headers', () => {
      const headers1 = contract.generateX402Headers(true);
      const headers2 = contract.generateX402Headers(true);

      expect(headers1['X402-Nonce']).not.toBe(headers2['X402-Nonce']);
    });

    test('should generate signature', () => {
      const headers = contract.generateX402Headers(true);

      expect(headers['X402-Signature']).toBeDefined();
      expect(headers['X402-Signature'].length).toBeGreaterThan(0);
    });
  });

  describe('Contract Deployment', () => {
    let contract;

    beforeEach(async () => {
      contract = await Smart402.create({
        type: 'test',
        parties: ['a@test.com', 'b@test.com'],
        payment: {
          amount: 10,
          token: 'USDC',
          blockchain: 'polygon-mumbai',
          frequency: 'one-time'
        }
      });
    });

    test('should deploy to testnet', async () => {
      const result = await contract.deploy({ network: 'polygon-mumbai' });

      expect(result).toHaveProperty('address');
      expect(result).toHaveProperty('transactionHash');
      expect(result).toHaveProperty('network');
      expect(result.network).toBe('polygon-mumbai');
      expect(result.address).toMatch(/^0x[a-fA-F0-9]{40}$/);
    });

    test('should deploy to mainnet', async () => {
      const result = await contract.deploy({ network: 'polygon' });

      expect(result.network).toBe('polygon');
      expect(result.address).toMatch(/^0x[a-fA-F0-9]{40}$/);
    });

    test('should return deployment receipt', async () => {
      const result = await contract.deploy({ network: 'polygon-mumbai' });

      expect(result).toHaveProperty('blockNumber');
      expect(result).toHaveProperty('gasUsed');
    });
  });

  describe('Contract Monitoring', () => {
    let contract;

    beforeEach(async () => {
      contract = await Smart402.create({
        type: 'saas-subscription',
        parties: ['vendor@example.com', 'customer@example.com'],
        payment: {
          amount: 99,
          token: 'USDC',
          blockchain: 'polygon',
          frequency: 'monthly'
        },
        conditions: [
          {
            id: 'uptime_check',
            type: 'api',
            description: 'Service uptime > 99%',
            threshold: 0.99
          }
        ]
      });
    });

    test('should start monitoring', async () => {
      const result = await contract.startMonitoring({ frequency: 'hourly' });

      expect(result).toHaveProperty('monitoringId');
      expect(result).toHaveProperty('frequency');
      expect(result.frequency).toBe('hourly');
    });

    test('should check conditions', async () => {
      const result = await contract.checkConditions();

      expect(result).toHaveProperty('allMet');
      expect(result).toHaveProperty('conditions');
      expect(result).toHaveProperty('timestamp');
      expect(Array.isArray(result.conditions)).toBe(true);
    });

    test('should execute payment when conditions met', async () => {
      const result = await contract.executePayment();

      expect(result).toHaveProperty('success');
      expect(result).toHaveProperty('transactionHash');
      expect(result).toHaveProperty('amount');
      expect(result).toHaveProperty('token');
      expect(result.amount).toBe(99);
      expect(result.token).toBe('USDC');
    });
  });

  describe('Export and Import', () => {
    let contract;

    beforeEach(async () => {
      contract = await Smart402.create({
        type: 'test',
        parties: ['a@test.com', 'b@test.com'],
        payment: {
          amount: 10,
          token: 'USDC',
          blockchain: 'polygon',
          frequency: 'monthly'
        }
      });
    });

    test('should export to YAML', () => {
      const yaml = contract.exportYAML();

      expect(yaml).toContain('contract_id:');
      expect(yaml).toContain('payment:');
      expect(yaml).toContain('amount: 10');
    });

    test('should export to JSON', () => {
      const json = contract.exportJSON();
      const parsed = JSON.parse(json);

      expect(parsed).toHaveProperty('contract_id');
      expect(parsed).toHaveProperty('payment');
      expect(parsed.payment.amount).toBe(10);
    });

    test('should load from exported YAML', () => {
      const yaml = contract.exportYAML();
      const loaded = Smart402.loadFromYAML(yaml);

      expect(loaded.contract_id).toBe(contract.ucl.contract_id);
      expect(loaded.payment.amount).toBe(contract.ucl.payment.amount);
    });

    test('should load from exported JSON', () => {
      const json = contract.exportJSON();
      const loaded = Smart402.loadFromJSON(json);

      expect(loaded.contract_id).toBe(contract.ucl.contract_id);
      expect(loaded.payment.amount).toBe(contract.ucl.payment.amount);
    });
  });

  describe('Templates', () => {
    test('should list available templates', () => {
      const templates = Smart402.getTemplates();

      expect(Array.isArray(templates)).toBe(true);
      expect(templates.length).toBeGreaterThan(0);
    });

    test('should create from SaaS template', async () => {
      const contract = await Smart402.fromTemplate('saas-subscription', {
        vendor_email: 'vendor@test.com',
        customer_email: 'customer@test.com',
        amount: 99
      });

      expect(contract.ucl.metadata.contract_type).toBe('saas-subscription');
      expect(contract.ucl.payment.amount).toBe(99);
    });

    test('should create from freelancer template', async () => {
      const contract = await Smart402.fromTemplate('freelancer-payment', {
        freelancer_email: 'dev@freelance.com',
        client_email: 'client@company.com',
        amount: 5000
      });

      expect(contract.ucl.metadata.contract_type).toBe('freelancer-payment');
      expect(contract.ucl.payment.amount).toBe(5000);
    });
  });

  describe('Error Handling', () => {
    test('should throw error for invalid contract type', async () => {
      await expect(Smart402.create({
        type: '',
        parties: ['a@test.com'],
        payment: { amount: 10, token: 'USDC', blockchain: 'polygon', frequency: 'monthly' }
      })).rejects.toThrow();
    });

    test('should throw error for invalid payment amount', async () => {
      await expect(Smart402.create({
        type: 'test',
        parties: ['a@test.com', 'b@test.com'],
        payment: { amount: -100, token: 'USDC', blockchain: 'polygon', frequency: 'monthly' }
      })).rejects.toThrow();
    });

    test('should throw error for missing required fields', async () => {
      await expect(Smart402.create({
        type: 'test'
        // Missing parties and payment
      })).rejects.toThrow();
    });
  });

  describe('Contract Summary', () => {
    test('should generate readable summary', async () => {
      const contract = await Smart402.create({
        type: 'saas-subscription',
        parties: ['vendor@example.com', 'customer@example.com'],
        payment: {
          amount: 99,
          token: 'USDC',
          blockchain: 'polygon',
          frequency: 'monthly'
        }
      });

      const summary = contract.getSummary();

      expect(summary).toContain('99');
      expect(summary).toContain('USDC');
      expect(summary).toContain('monthly');
    });
  });
});

// Run tests
if (require.main === module) {
  console.log('Running Smart402 SDK Tests...\n');
  // Test execution handled by test runner (Jest, Mocha, etc.)
}
