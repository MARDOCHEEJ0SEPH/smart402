/**
 * Smart402 LLMO (Large Language Model Optimization) Engine
 * Generates and validates Universal Contract Language (UCL)
 */

import type {
  LLMOConfig,
  LLMOResult,
  UCLLayer,
  ValidationResult,
  ValidationError,
  ValidationWarning,
  Smart402Config,
  HumanReadableLayer,
  LLMStructuredLayer,
  MachineExecutableLayer,
  BlockchainCompilableLayer,
  Party,
  Intent,
  Entity,
  Action,
  ExecutableFunction,
  StateMachine
} from '../types/index.js';

export class LLMOEngine {
  private config: Required<LLMOConfig>;
  private readonly version = '1.0.0';

  constructor(config: LLMOConfig = {}) {
    this.config = {
      optimization_level: config.optimization_level ?? 'high',
      target_models: config.target_models ?? ['gpt-4', 'claude-3', 'palm-2'],
      include_examples: config.include_examples ?? true,
      validate_ucl: config.validate_ucl ?? true
    };
  }

  /**
   * Generate complete UCL from Smart402 contract configuration
   */
  async generateUCL(contractConfig: Smart402Config): Promise<LLMOResult> {
    const ucl: UCLLayer = {
      human_readable: this.generateHumanReadableLayer(contractConfig),
      llm_structured: this.generateLLMStructuredLayer(contractConfig),
      machine_executable: this.generateMachineExecutableLayer(contractConfig),
      blockchain_compilable: this.generateBlockchainCompilableLayer(contractConfig)
    };

    const validation = this.config.validate_ucl ?
      this.validateUCL(ucl) :
      this.createPassingValidation();

    const optimization_score = this.calculateOptimizationScore(ucl, contractConfig);
    const token_efficiency = this.calculateTokenEfficiency(ucl);

    return {
      ucl,
      validation,
      optimization_score,
      token_efficiency
    };
  }

  /**
   * Validate UCL structure and completeness
   */
  validateUCL(ucl: UCLLayer): ValidationResult {
    const errors: ValidationError[] = [];
    const warnings: ValidationWarning[] = [];

    // Validate Human Readable Layer
    if (!ucl.human_readable.title || ucl.human_readable.title.length === 0) {
      errors.push({
        layer: 'human_readable',
        field: 'title',
        message: 'Title is required and cannot be empty',
        severity: 'critical'
      });
    }

    if (!ucl.human_readable.description) {
      errors.push({
        layer: 'human_readable',
        field: 'description',
        message: 'Description is required',
        severity: 'error'
      });
    }

    if (!ucl.human_readable.parties || ucl.human_readable.parties.length === 0) {
      errors.push({
        layer: 'human_readable',
        field: 'parties',
        message: 'At least one party is required',
        severity: 'critical'
      });
    }

    // Validate LLM Structured Layer
    if (!ucl.llm_structured.contract_type) {
      errors.push({
        layer: 'llm_structured',
        field: 'contract_type',
        message: 'Contract type must be specified',
        severity: 'error'
      });
    }

    if (!ucl.llm_structured.intent || !ucl.llm_structured.intent.primary_goal) {
      warnings.push({
        layer: 'llm_structured',
        field: 'intent',
        message: 'Intent and primary goal should be defined for better LLM understanding',
        suggestion: 'Add a clear primary_goal describing the contract objective'
      });
    }

    if (!ucl.llm_structured.actions || ucl.llm_structured.actions.length === 0) {
      warnings.push({
        layer: 'llm_structured',
        field: 'actions',
        message: 'No actions defined - consider adding contract actions',
        suggestion: 'Define actions like transfer, validate, notify'
      });
    }

    // Validate Machine Executable Layer
    if (!ucl.machine_executable.functions || ucl.machine_executable.functions.length === 0) {
      warnings.push({
        layer: 'machine_executable',
        field: 'functions',
        message: 'No executable functions defined',
        suggestion: 'Add functions that can be executed programmatically'
      });
    }

    if (!ucl.machine_executable.state_machine) {
      warnings.push({
        layer: 'machine_executable',
        field: 'state_machine',
        message: 'State machine not defined',
        suggestion: 'Define states and transitions for contract lifecycle'
      });
    }

    // Validate Blockchain Compilable Layer
    if (!ucl.blockchain_compilable.solidity_version) {
      warnings.push({
        layer: 'blockchain_compilable',
        field: 'solidity_version',
        message: 'Solidity version not specified',
        suggestion: 'Specify target Solidity version (e.g., ^0.8.0)'
      });
    }

    if (!ucl.blockchain_compilable.contract_code) {
      warnings.push({
        layer: 'blockchain_compilable',
        field: 'contract_code',
        message: 'No Solidity contract code generated',
        suggestion: 'Generate Solidity code for blockchain deployment'
      });
    }

    const completeness_score = this.calculateCompletenessScore(ucl, errors, warnings);

    return {
      is_valid: errors.filter(e => e.severity === 'critical').length === 0,
      errors,
      warnings,
      completeness_score
    };
  }

  /**
   * Generate Human Readable Layer
   */
  private generateHumanReadableLayer(config: Smart402Config): HumanReadableLayer {
    const terms = this.extractTerms(config);
    const conditions = this.extractConditions(config);

    return {
      title: config.title,
      description: config.description,
      parties: config.parties || [],
      terms,
      conditions
    };
  }

  /**
   * Generate LLM Structured Layer
   */
  private generateLLMStructuredLayer(config: Smart402Config): LLMStructuredLayer {
    const intent: Intent = {
      primary_goal: this.inferPrimaryGoal(config),
      success_criteria: this.inferSuccessCriteria(config),
      failure_conditions: this.inferFailureConditions(config)
    };

    const entities: Entity[] = this.extractEntities(config);
    const actions: Action[] = this.generateActions(config);
    const constraints = this.generateConstraints(config);

    return {
      contract_type: config.type,
      intent,
      entities,
      actions,
      constraints
    };
  }

  /**
   * Generate Machine Executable Layer
   */
  private generateMachineExecutableLayer(config: Smart402Config): MachineExecutableLayer {
    const functions = this.generateExecutableFunctions(config);
    const state_machine = this.generateStateMachine(config);
    const data_schema = this.generateDataSchema(config);

    return {
      functions,
      state_machine,
      data_schema
    };
  }

  /**
   * Generate Blockchain Compilable Layer
   */
  private generateBlockchainCompilableLayer(config: Smart402Config): BlockchainCompilableLayer {
    const solidity_code = this.generateSolidityCode(config);
    const abi = this.generateABI(config);

    return {
      solidity_version: '^0.8.20',
      contract_code: solidity_code,
      abi
    };
  }

  /**
   * Extract terms from configuration
   */
  private extractTerms(config: Smart402Config): string[] {
    const terms: string[] = [];

    if (config.terms) {
      if (Array.isArray(config.terms)) {
        terms.push(...config.terms);
      } else if (typeof config.terms === 'object') {
        Object.entries(config.terms).forEach(([key, value]) => {
          terms.push(`${key}: ${value}`);
        });
      }
    }

    return terms;
  }

  /**
   * Extract conditions from configuration
   */
  private extractConditions(config: Smart402Config): string[] {
    const conditions: string[] = [];

    if (config.metadata?.conditions) {
      conditions.push(...config.metadata.conditions);
    }

    // Infer conditions from contract type
    if (config.type.includes('payment')) {
      conditions.push('Payment must be received before service delivery');
    }
    if (config.type.includes('service')) {
      conditions.push('Service must meet quality standards');
    }

    return conditions;
  }

  /**
   * Infer primary goal from configuration
   */
  private inferPrimaryGoal(config: Smart402Config): string {
    const type = config.type.toLowerCase();

    if (type.includes('payment')) return 'Execute payment transaction';
    if (type.includes('service')) return 'Deliver service as specified';
    if (type.includes('rental')) return 'Facilitate rental agreement';
    if (type.includes('subscription')) return 'Manage subscription lifecycle';

    return `Execute ${config.type} contract`;
  }

  /**
   * Infer success criteria
   */
  private inferSuccessCriteria(config: Smart402Config): string[] {
    return [
      'All parties fulfill their obligations',
      'Payment is successfully processed',
      'Terms and conditions are met',
      'Contract completes without disputes'
    ];
  }

  /**
   * Infer failure conditions
   */
  private inferFailureConditions(config: Smart402Config): string[] {
    return [
      'Payment fails or is insufficient',
      'Party fails to meet obligations',
      'Deadline is exceeded',
      'Terms are violated'
    ];
  }

  /**
   * Extract entities from configuration
   */
  private extractEntities(config: Smart402Config): Entity[] {
    const entities: Entity[] = [];

    // Add parties as entities
    config.parties?.forEach(party => {
      entities.push({
        name: party.role,
        type: 'Party',
        properties: {
          id: party.id,
          address: party.address,
          ...party.metadata
        }
      });
    });

    // Add payment as entity if applicable
    if (config.type.includes('payment') || config.terms?.amount) {
      entities.push({
        name: 'Payment',
        type: 'FinancialTransaction',
        properties: {
          amount: config.terms?.amount,
          currency: config.terms?.currency || 'USDC'
        }
      });
    }

    return entities;
  }

  /**
   * Generate actions from configuration
   */
  private generateActions(config: Smart402Config): Action[] {
    const actions: Action[] = [];

    // Add payment action if applicable
    if (config.type.includes('payment')) {
      actions.push({
        id: 'payment_transfer',
        name: 'Transfer Payment',
        type: 'transfer',
        parameters: [
          { name: 'amount', type: 'uint256', required: true },
          { name: 'recipient', type: 'address', required: true },
          { name: 'token', type: 'address', required: true }
        ],
        preconditions: ['Payer has sufficient balance', 'Contract is active'],
        postconditions: ['Payment transferred successfully', 'Receipt generated']
      });
    }

    // Add validation action
    actions.push({
      id: 'validate_terms',
      name: 'Validate Contract Terms',
      type: 'validate',
      parameters: [
        { name: 'terms', type: 'bytes', required: true }
      ],
      preconditions: ['Contract is initialized'],
      postconditions: ['Terms validated', 'Contract ready for execution']
    });

    return actions;
  }

  /**
   * Generate constraints
   */
  private generateConstraints(config: Smart402Config) {
    return [
      {
        type: 'time' as const,
        expression: 'block.timestamp < deadline',
        severity: 'error' as const
      },
      {
        type: 'value' as const,
        expression: 'amount > 0',
        severity: 'error' as const
      }
    ];
  }

  /**
   * Generate executable functions
   */
  private generateExecutableFunctions(config: Smart402Config): ExecutableFunction[] {
    return [
      {
        name: 'execute',
        signature: 'execute() returns (bool)',
        logic: 'validateTerms() && processPayment() && emitCompletion()',
        gas_estimate: 150000
      },
      {
        name: 'cancel',
        signature: 'cancel() returns (bool)',
        logic: 'require(msg.sender == initiator); refundPayment(); emitCancellation()',
        gas_estimate: 50000
      }
    ];
  }

  /**
   * Generate state machine
   */
  private generateStateMachine(config: Smart402Config): StateMachine {
    return {
      initial_state: 'initialized',
      states: [
        { name: 'initialized', type: 'initial' },
        { name: 'active', type: 'active' },
        { name: 'completed', type: 'final' },
        { name: 'cancelled', type: 'final' },
        { name: 'failed', type: 'error' }
      ],
      transitions: [
        { from: 'initialized', to: 'active', trigger: 'activate', condition: 'termsValidated' },
        { from: 'active', to: 'completed', trigger: 'complete', condition: 'paymentConfirmed' },
        { from: 'active', to: 'cancelled', trigger: 'cancel' },
        { from: 'active', to: 'failed', trigger: 'fail', condition: 'deadlineExceeded' }
      ]
    };
  }

  /**
   * Generate data schema
   */
  private generateDataSchema(config: Smart402Config): Record<string, any> {
    return {
      contract_id: 'string',
      status: 'string',
      parties: 'array<Party>',
      terms: 'object',
      created_at: 'timestamp',
      updated_at: 'timestamp',
      metadata: 'object'
    };
  }

  /**
   * Generate Solidity contract code
   */
  private generateSolidityCode(config: Smart402Config): string {
    const contractName = this.sanitizeContractName(config.type);

    return `// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * ${config.title}
 * ${config.description}
 * Generated by Smart402 LLMO Engine v${this.version}
 */
contract ${contractName} {
    // State variables
    address public initiator;
    address public beneficiary;
    uint256 public amount;
    uint256 public deadline;
    bool public completed;

    // Events
    event ContractInitialized(address indexed initiator, uint256 amount);
    event PaymentExecuted(address indexed from, address indexed to, uint256 amount);
    event ContractCompleted(uint256 timestamp);
    event ContractCancelled(uint256 timestamp);

    // Modifiers
    modifier onlyInitiator() {
        require(msg.sender == initiator, "Only initiator can call this");
        _;
    }

    modifier notCompleted() {
        require(!completed, "Contract already completed");
        _;
    }

    modifier beforeDeadline() {
        require(block.timestamp < deadline, "Deadline exceeded");
        _;
    }

    constructor(
        address _beneficiary,
        uint256 _amount,
        uint256 _deadline
    ) {
        initiator = msg.sender;
        beneficiary = _beneficiary;
        amount = _amount;
        deadline = _deadline;

        emit ContractInitialized(msg.sender, _amount);
    }

    function execute() external payable onlyInitiator notCompleted beforeDeadline {
        require(msg.value >= amount, "Insufficient payment");

        (bool success, ) = beneficiary.call{value: amount}("");
        require(success, "Payment transfer failed");

        completed = true;

        emit PaymentExecuted(msg.sender, beneficiary, amount);
        emit ContractCompleted(block.timestamp);
    }

    function cancel() external onlyInitiator notCompleted {
        completed = true;
        emit ContractCancelled(block.timestamp);
    }

    receive() external payable {}
}`;
  }

  /**
   * Generate ABI
   */
  private generateABI(config: Smart402Config): any[] {
    return [
      {
        type: 'constructor',
        inputs: [
          { name: '_beneficiary', type: 'address' },
          { name: '_amount', type: 'uint256' },
          { name: '_deadline', type: 'uint256' }
        ]
      },
      {
        type: 'function',
        name: 'execute',
        inputs: [],
        outputs: [],
        stateMutability: 'payable'
      },
      {
        type: 'function',
        name: 'cancel',
        inputs: [],
        outputs: [],
        stateMutability: 'nonpayable'
      },
      {
        type: 'event',
        name: 'ContractInitialized',
        inputs: [
          { name: 'initiator', type: 'address', indexed: true },
          { name: 'amount', type: 'uint256', indexed: false }
        ]
      }
    ];
  }

  /**
   * Sanitize contract name for Solidity
   */
  private sanitizeContractName(type: string): string {
    return type
      .split(/[^a-zA-Z0-9]/)
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join('') + 'Contract';
  }

  /**
   * Calculate optimization score
   */
  private calculateOptimizationScore(ucl: UCLLayer, config: Smart402Config): number {
    let score = 0;

    // Layer completeness (0.4)
    if (ucl.human_readable) score += 0.1;
    if (ucl.llm_structured) score += 0.1;
    if (ucl.machine_executable) score += 0.1;
    if (ucl.blockchain_compilable) score += 0.1;

    // LLM-friendly structure (0.3)
    if (ucl.llm_structured.intent) score += 0.1;
    if (ucl.llm_structured.actions.length > 0) score += 0.1;
    if (ucl.llm_structured.entities.length > 0) score += 0.1;

    // Executable code quality (0.3)
    if (ucl.machine_executable.functions.length > 0) score += 0.1;
    if (ucl.machine_executable.state_machine) score += 0.1;
    if (ucl.blockchain_compilable.contract_code) score += 0.1;

    return Math.min(score, 1.0);
  }

  /**
   * Calculate token efficiency (characters per semantic unit)
   */
  private calculateTokenEfficiency(ucl: UCLLayer): number {
    const totalChars = JSON.stringify(ucl).length;
    const semanticUnits =
      (ucl.llm_structured.actions?.length || 0) +
      (ucl.llm_structured.entities?.length || 0) +
      (ucl.machine_executable.functions?.length || 0);

    return semanticUnits > 0 ? totalChars / semanticUnits : 0;
  }

  /**
   * Calculate completeness score
   */
  private calculateCompletenessScore(
    ucl: UCLLayer,
    errors: ValidationError[],
    warnings: ValidationWarning[]
  ): number {
    const criticalErrors = errors.filter(e => e.severity === 'critical').length;
    const regularErrors = errors.filter(e => e.severity === 'error').length;
    const warningCount = warnings.length;

    const penalty = (criticalErrors * 0.3) + (regularErrors * 0.1) + (warningCount * 0.05);

    return Math.max(0, 1.0 - penalty);
  }

  /**
   * Create passing validation result
   */
  private createPassingValidation(): ValidationResult {
    return {
      is_valid: true,
      errors: [],
      warnings: [],
      completeness_score: 1.0
    };
  }
}

export default LLMOEngine;
