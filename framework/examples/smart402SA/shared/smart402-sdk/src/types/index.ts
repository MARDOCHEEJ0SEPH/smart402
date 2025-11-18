/**
 * Smart402 SDK TypeScript Type Definitions
 * Comprehensive types for AEO, LLMO, and X402 Protocol
 */

// ============================================================================
// Universal Contract Language (UCL) Types
// ============================================================================

export interface UCLLayer {
  human_readable: HumanReadableLayer;
  llm_structured: LLMStructuredLayer;
  machine_executable: MachineExecutableLayer;
  blockchain_compilable: BlockchainCompilableLayer;
}

export interface HumanReadableLayer {
  title: string;
  description: string;
  parties: Party[];
  terms: string[];
  conditions: string[];
}

export interface LLMStructuredLayer {
  contract_type: string;
  intent: Intent;
  entities: Entity[];
  actions: Action[];
  constraints: Constraint[];
}

export interface MachineExecutableLayer {
  functions: ExecutableFunction[];
  state_machine: StateMachine;
  data_schema: Record<string, any>;
}

export interface BlockchainCompilableLayer {
  solidity_version: string;
  contract_code: string;
  abi: any[];
  bytecode?: string;
}

export interface Party {
  id: string;
  role: string;
  address?: string;
  metadata?: Record<string, any>;
}

export interface Intent {
  primary_goal: string;
  success_criteria: string[];
  failure_conditions: string[];
}

export interface Entity {
  name: string;
  type: string;
  properties: Record<string, any>;
}

export interface Action {
  id: string;
  name: string;
  type: 'transfer' | 'validate' | 'notify' | 'compute' | 'custom';
  parameters: Parameter[];
  preconditions: string[];
  postconditions: string[];
}

export interface Parameter {
  name: string;
  type: string;
  required: boolean;
  default?: any;
}

export interface Constraint {
  type: 'time' | 'value' | 'state' | 'logic';
  expression: string;
  severity: 'error' | 'warning' | 'info';
}

export interface ExecutableFunction {
  name: string;
  signature: string;
  logic: string;
  gas_estimate?: number;
}

export interface StateMachine {
  initial_state: string;
  states: State[];
  transitions: Transition[];
}

export interface State {
  name: string;
  type: 'initial' | 'active' | 'final' | 'error';
  data?: Record<string, any>;
}

export interface Transition {
  from: string;
  to: string;
  trigger: string;
  condition?: string;
}

// ============================================================================
// AEO (Answer Engine Optimization) Types
// ============================================================================

export interface AEOConfig {
  target_score?: number;
  optimize_for?: ('clarity' | 'completeness' | 'discoverability')[];
  schema_org?: boolean;
  keywords?: string[];
}

export interface AEOResult {
  score: number;
  recommendations: Recommendation[];
  metadata: AEOMetadata;
  schema_org?: any;
}

export interface Recommendation {
  category: string;
  priority: 'high' | 'medium' | 'low';
  message: string;
  fix?: string;
}

export interface AEOMetadata {
  timestamp: Date;
  version: string;
  analysis_time_ms: number;
  factors: Record<string, number>;
}

// ============================================================================
// LLMO (Large Language Model Optimization) Types
// ============================================================================

export interface LLMOConfig {
  optimization_level?: 'basic' | 'standard' | 'high' | 'maximum';
  target_models?: string[];
  include_examples?: boolean;
  validate_ucl?: boolean;
}

export interface LLMOResult {
  ucl: UCLLayer;
  validation: ValidationResult;
  optimization_score: number;
  token_efficiency: number;
}

export interface ValidationResult {
  is_valid: boolean;
  errors: ValidationError[];
  warnings: ValidationWarning[];
  completeness_score: number;
}

export interface ValidationError {
  layer: keyof UCLLayer;
  field: string;
  message: string;
  severity: 'critical' | 'error';
}

export interface ValidationWarning {
  layer: keyof UCLLayer;
  field: string;
  message: string;
  suggestion?: string;
}

// ============================================================================
// X402 Payment Protocol Types
// ============================================================================

export interface X402Config {
  provider_url: string;
  private_key?: string;
  chain_id?: number;
  payment_token?: string;
  gas_limit?: number;
  gas_price_multiplier?: number;
}

export interface X402PaymentRequest {
  amount: string;
  currency: string;
  recipient: string;
  contract_id: string;
  metadata?: Record<string, any>;
  deadline?: number;
}

export interface X402PaymentResult {
  transaction_hash: string;
  status: 'pending' | 'confirmed' | 'failed';
  amount: string;
  fee: string;
  timestamp: Date;
  block_number?: number;
  confirmations?: number;
}

export interface X402Header {
  version: string;
  contract_id: string;
  payment_address: string;
  payment_token: string;
  amount: string;
  deadline?: number;
  signature?: string;
}

// ============================================================================
// Smart402 Contract Types
// ============================================================================

export interface Smart402Config {
  type: string;
  title: string;
  description: string;
  parties: Party[];
  terms: any;
  aeo_config?: AEOConfig;
  llmo_config?: LLMOConfig;
  x402_config?: X402Config;
  metadata?: Record<string, any>;
}

export interface Smart402Contract {
  contract_id: string;
  ucl: UCLLayer;
  aeo_score: number;
  aeo_result: AEOResult;
  llmo_result: LLMOResult;
  x402_header?: X402Header;
  created_at: Date;
  updated_at: Date;
  status: ContractStatus;
  metadata: Record<string, any>;
}

export type ContractStatus =
  | 'draft'
  | 'validated'
  | 'deployed'
  | 'active'
  | 'completed'
  | 'cancelled'
  | 'error';

// ============================================================================
// Database & Storage Types
// ============================================================================

export interface DatabaseConfig {
  postgres?: {
    url: string;
    pool_size?: number;
  };
  mongodb?: {
    url: string;
    database: string;
  };
  redis?: {
    url: string;
    ttl?: number;
  };
  elasticsearch?: {
    url: string;
    index_prefix?: string;
  };
}

// ============================================================================
// Events & WebSocket Types
// ============================================================================

export interface Smart402Event {
  event_id: string;
  event_type: Smart402EventType;
  contract_id: string;
  data: any;
  timestamp: Date;
}

export type Smart402EventType =
  | 'contract.created'
  | 'contract.validated'
  | 'contract.deployed'
  | 'contract.executed'
  | 'payment.initiated'
  | 'payment.confirmed'
  | 'payment.failed'
  | 'aeo.score_updated'
  | 'llmo.validation_complete';

// ============================================================================
// API Response Types
// ============================================================================

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: ApiError;
  metadata?: {
    timestamp: Date;
    request_id: string;
    version: string;
  };
}

export interface ApiError {
  code: string;
  message: string;
  details?: any;
  stack?: string;
}

// ============================================================================
// Monitoring & Telemetry Types
// ============================================================================

export interface TelemetryData {
  metric_name: string;
  value: number;
  unit: string;
  tags: Record<string, string>;
  timestamp: Date;
}

export interface PerformanceMetrics {
  request_duration_ms: number;
  memory_usage_mb: number;
  cpu_usage_percent: number;
  active_connections: number;
}
