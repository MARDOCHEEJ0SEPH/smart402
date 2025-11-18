-- Smart402SA PostgreSQL Initialization Script
-- Creates database schema for contracts and transactions

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm"; -- For text search
CREATE EXTENSION IF NOT EXISTS "btree_gin"; -- For faster JSONB queries

-- Contracts table
CREATE TABLE IF NOT EXISTS contracts (
    id SERIAL PRIMARY KEY,
    contract_id VARCHAR(255) UNIQUE NOT NULL,
    ucl JSONB NOT NULL,
    aeo_score DECIMAL(3, 2) NOT NULL CHECK (aeo_score >= 0 AND aeo_score <= 1),
    status VARCHAR(50) NOT NULL DEFAULT 'draft',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb,
    CONSTRAINT valid_status CHECK (status IN ('draft', 'validated', 'deployed', 'active', 'completed', 'cancelled', 'error'))
);

-- Create indexes for contracts
CREATE INDEX IF NOT EXISTS idx_contracts_contract_id ON contracts(contract_id);
CREATE INDEX IF NOT EXISTS idx_contracts_status ON contracts(status);
CREATE INDEX IF NOT EXISTS idx_contracts_created_at ON contracts(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_contracts_aeo_score ON contracts(aeo_score DESC);
CREATE INDEX IF NOT EXISTS idx_contracts_metadata ON contracts USING GIN(metadata);
CREATE INDEX IF NOT EXISTS idx_contracts_ucl ON contracts USING GIN(ucl);

-- Transactions table for X402 payments
CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    transaction_hash VARCHAR(66) UNIQUE NOT NULL,
    contract_id VARCHAR(255) NOT NULL,
    amount VARCHAR(100) NOT NULL,
    currency VARCHAR(20) NOT NULL DEFAULT 'USDC',
    sender VARCHAR(42),
    recipient VARCHAR(42) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    block_number BIGINT,
    confirmations INTEGER DEFAULT 0,
    fee VARCHAR(100),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    confirmed_at TIMESTAMP,
    metadata JSONB DEFAULT '{}'::jsonb,
    FOREIGN KEY (contract_id) REFERENCES contracts(contract_id) ON DELETE CASCADE,
    CONSTRAINT valid_tx_status CHECK (status IN ('pending', 'confirmed', 'failed'))
);

-- Create indexes for transactions
CREATE INDEX IF NOT EXISTS idx_transactions_hash ON transactions(transaction_hash);
CREATE INDEX IF NOT EXISTS idx_transactions_contract_id ON transactions(contract_id);
CREATE INDEX IF NOT EXISTS idx_transactions_status ON transactions(status);
CREATE INDEX IF NOT EXISTS idx_transactions_created_at ON transactions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_transactions_sender ON transactions(sender);
CREATE INDEX IF NOT EXISTS idx_transactions_recipient ON transactions(recipient);

-- Parties table for contract participants
CREATE TABLE IF NOT EXISTS parties (
    id SERIAL PRIMARY KEY,
    contract_id VARCHAR(255) NOT NULL,
    party_id VARCHAR(255) NOT NULL,
    role VARCHAR(100) NOT NULL,
    address VARCHAR(42),
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    FOREIGN KEY (contract_id) REFERENCES contracts(contract_id) ON DELETE CASCADE,
    UNIQUE(contract_id, party_id)
);

CREATE INDEX IF NOT EXISTS idx_parties_contract_id ON parties(contract_id);
CREATE INDEX IF NOT EXISTS idx_parties_address ON parties(address);

-- AEO Scores History (for tracking optimization improvements)
CREATE TABLE IF NOT EXISTS aeo_scores_history (
    id SERIAL PRIMARY KEY,
    contract_id VARCHAR(255) NOT NULL,
    score DECIMAL(3, 2) NOT NULL,
    recommendations JSONB,
    factors JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    FOREIGN KEY (contract_id) REFERENCES contracts(contract_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_aeo_history_contract_id ON aeo_scores_history(contract_id);
CREATE INDEX IF NOT EXISTS idx_aeo_history_created_at ON aeo_scores_history(created_at DESC);

-- Events table for contract lifecycle events
CREATE TABLE IF NOT EXISTS events (
    id SERIAL PRIMARY KEY,
    event_id UUID DEFAULT uuid_generate_v4(),
    contract_id VARCHAR(255) NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    event_data JSONB NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    FOREIGN KEY (contract_id) REFERENCES contracts(contract_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_events_contract_id ON events(contract_id);
CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type);
CREATE INDEX IF NOT EXISTS idx_events_created_at ON events(created_at DESC);

-- Users table (for authentication)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    user_id UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    wallet_address VARCHAR(42),
    role VARCHAR(50) NOT NULL DEFAULT 'user',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    last_login TIMESTAMP,
    metadata JSONB DEFAULT '{}'::jsonb,
    CONSTRAINT valid_role CHECK (role IN ('user', 'admin', 'service'))
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_wallet_address ON users(wallet_address);

-- API Keys table
CREATE TABLE IF NOT EXISTS api_keys (
    id SERIAL PRIMARY KEY,
    key_id UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    user_id UUID NOT NULL,
    key_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    permissions JSONB DEFAULT '[]'::jsonb,
    rate_limit INTEGER DEFAULT 1000,
    expires_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    last_used_at TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_api_keys_key_id ON api_keys(key_id);
CREATE INDEX IF NOT EXISTS idx_api_keys_user_id ON api_keys(user_id);
CREATE INDEX IF NOT EXISTS idx_api_keys_active ON api_keys(is_active);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger for contracts updated_at
CREATE TRIGGER update_contracts_updated_at BEFORE UPDATE ON contracts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Trigger for users updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert demo data (optional for development)
-- INSERT INTO users (email, password_hash, role, wallet_address) VALUES
--     ('admin@smart402.io', '$2b$10$demohashdemohashdemohashdemohashdemohashdemohashdemo', 'admin', '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb'),
--     ('demo@smart402.io', '$2b$10$demohashdemohashdemohashdemohashdemohashdemohashdemo', 'user', '0x123456789abcdef123456789abcdef1234567890');

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO smart402;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO smart402;

COMMIT;
