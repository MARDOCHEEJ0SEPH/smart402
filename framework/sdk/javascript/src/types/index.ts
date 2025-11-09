/**
 * TypeScript Type Definitions for Smart402 SDK
 */

// ============================================
// Core Types
// ============================================

export interface Smart402Options {
  network?: 'ethereum' | 'polygon' | 'arbitrum' | 'optimism' | 'base';
  apiKey?: string;
  rpcUrl?: string;
  privateKey?: string;
  debug?: boolean;
}

export interface NetworkConfig {
  name: string;
  chainId: number;
  rpcUrl: string;
  explorer: string;
}

export type ContractStatus = 'draft' | 'deploying' | 'deployed' | 'active' | 'paused' | 'completed' | 'failed';

// ============================================
// Contract Configuration
// ============================================

export interface ContractConfig {
  type: ContractType;
  parties: string[];
  payment: PaymentConfig;
  conditions?: ConditionConfig[];
  metadata?: ContractMetadata;
}

export type ContractType =
  | 'saas-subscription'
  | 'freelancer-milestone'
  | 'supply-chain'
  | 'affiliate-commission'
  | 'vendor-sla'
  | 'one-time-payment'
  | 'escrow'
  | 'custom';

export interface PaymentConfig {
  amount: number;
  currency?: string;
  token: string;
  blockchain?: string;
  frequency: 'one-time' | 'daily' | 'weekly' | 'monthly' | 'yearly';
  dayOfMonth?: number;
}

export interface ConditionConfig {
  id: string;
  description: string;
  source: string;
  operator: 'equals' | 'not_equals' | 'greater_than' | 'less_than' | 'gte' | 'lte';
  threshold: any;
}

export interface ContractMetadata {
  title?: string;
  description?: string;
  jurisdiction?: string;
  governingLaw?: string;
  duration?: string;
  tags?: string[];
}

// ============================================
// UCL (Universal Contract Language)
// ============================================

export interface UCLContract {
  contract_id: string;
  version: string;
  standard: string;
  summary: {
    title: string;
    plain_english: string;
    what_it_does: string;
    who_its_for: string;
    when_it_executes: string;
  };
  metadata: {
    type: string;
    category: string;
    parties: Array<{
      role: string;
      identifier: string;
      name?: string;
    }>;
    dates: {
      effective: string;
      duration: string;
      renewal: string;
    };
    jurisdiction?: string;
    governing_law?: string;
  };
  payment: {
    structure: string;
    amount: number;
    currency: string;
    token: string;
    blockchain: string;
    frequency: string;
    day_of_month?: number;
    timezone?: string;
  };
  conditions: {
    required: ConditionDefinition[];
    optional?: ConditionDefinition[];
  };
  rules: RuleDefinition[];
  oracles: OracleDefinition[];
  dispute?: DisputeResolution;
  termination?: TerminationTerms;
  llm_instructions: LLMInstructions;
  compliance?: ComplianceInfo;
}

export interface ConditionDefinition {
  id: string;
  description: string;
  source: string;
  metric?: string;
  operator: string;
  threshold?: any;
  expected?: any;
}

export interface RuleDefinition {
  rule_id: string;
  name: string;
  trigger: string;
  schedule?: string;
  conditions: {
    all_of?: string[];
    any_of?: string[];
  };
  actions: ActionDefinition[];
  on_success?: string[];
  on_failure?: string[];
}

export interface ActionDefinition {
  action: string;
  inputs?: Record<string, any>;
  output?: string;
  [key: string]: any;
}

export interface OracleDefinition {
  id: string;
  type: 'chainlink' | 'custom_api' | 'smart_contract' | 'iot_sensor';
  endpoint?: string;
  address?: string;
  blockchain?: string;
  method?: string;
  authentication?: string;
  refresh_rate: string;
  required: boolean;
}

export interface DisputeResolution {
  method: 'multisig' | 'arbitrator' | 'dao_vote';
  signers?: string[];
  required_signatures?: number;
  timeout?: string;
  escalation?: EscalationLevel[];
}

export interface EscalationLevel {
  level: number;
  method: string;
  timeout: string;
}

export interface TerminationTerms {
  notice_period: string;
  final_payment: string;
  data_retention: string;
  conditions: string[];
}

export interface LLMInstructions {
  how_to_read: string;
  how_to_verify: string;
  common_questions: Array<{ q: string; a: string }>;
}

export interface ComplianceInfo {
  standards: string[];
  certifications?: Array<{
    type: string;
    auditor: string;
    date: string;
    report: string;
  }>;
  legal?: {
    jurisdiction: string;
    governing_law: string;
    arbitration: string;
  };
}

// ============================================
// AEO Types
// ============================================

export interface AEOMetadata {
  score: number;
  dimensions: {
    semantic_relevance: number;
    citation_frequency: number;
    freshness: number;
    authority: number;
    cross_platform: number;
  };
  keywords: string[];
  json_ld: any;
  optimized_content: string;
  distribution_channels: string[];
}

// ============================================
// X402 Types
// ============================================

export interface X402Headers {
  'X402-Contract-ID': string;
  'X402-Payment-Amount': string;
  'X402-Payment-Token': string;
  'X402-Settlement-Network': string;
  'X402-Settlement-Address': string;
  'X402-Conditions-Met': string;
  'X402-Oracle-Confirmations'?: string;
  'X402-Dispute-Resolution'?: string;
  'X402-Webhook-URL'?: string;
  'X402-Signature'?: string;
}

export interface PaymentResult {
  success: boolean;
  transactionHash: string;
  amount: number;
  token: string;
  network: string;
  from: string;
  to: string;
  blockNumber?: number;
  timestamp: Date;
}

// ============================================
// Deployment Types
// ============================================

export interface DeployOptions {
  network?: string;
  gasLimit?: number;
  gasPrice?: string;
  confirmations?: number;
}

export interface DeployResult {
  success: boolean;
  address: string;
  transactionHash: string;
  network: string;
  blockNumber?: number;
  contractId: string;
}

// ============================================
// Monitoring Types
// ============================================

export interface MonitoringOptions {
  contractId: string;
  contractAddress: string;
  conditions: ConditionDefinition[];
  oracles: OracleDefinition[];
  frequency: 'realtime' | 'high' | 'medium' | 'low' | 'daily';
  webhook?: string;
}

export interface ConditionCheckResult {
  allMet: boolean;
  conditions: Record<string, boolean>;
  timestamp: Date;
  oracleData?: Record<string, any>;
}

// ============================================
// Template Types
// ============================================

export interface ContractTemplate {
  name: string;
  type: ContractType;
  description: string;
  variables: TemplateVariable[];
  instantiate: (vars: Record<string, any>) => ContractConfig;
  documentation: TemplateDocumentation;
}

export interface TemplateVariable {
  name: string;
  type: 'string' | 'number' | 'boolean' | 'address' | 'enum';
  description: string;
  required: boolean;
  default?: any;
  options?: any[];
}

export interface TemplateDocumentation {
  title: string;
  description: string;
  use_cases: string[];
  examples: Array<{
    title: string;
    variables: Record<string, any>;
  }>;
}

// ============================================
// Utility Types
// ============================================

export interface ValidationResult {
  valid: boolean;
  errors: string[];
  warnings?: string[];
}

export interface CompileOptions {
  target: 'solidity' | 'javascript' | 'rust';
  optimize?: boolean;
  version?: string;
}

export interface ExportFormat {
  format: 'yaml' | 'json' | 'ucl' | 'markdown';
  pretty?: boolean;
}
