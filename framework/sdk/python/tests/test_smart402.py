"""
Smart402 Python SDK Tests

Comprehensive test suite for Smart402 Python SDK functionality
"""

import pytest
import asyncio
import json
import yaml
from smart402.core.smart402 import Smart402
from smart402.core.contract import Contract


class TestContractCreation:
    """Test contract creation functionality"""

    @pytest.mark.asyncio
    async def test_create_basic_contract(self):
        """Test creating a basic SaaS subscription contract"""
        contract = await Smart402.create({
            'type': 'saas-subscription',
            'parties': ['vendor@example.com', 'customer@example.com'],
            'payment': {
                'amount': 99,
                'token': 'USDC',
                'blockchain': 'polygon',
                'frequency': 'monthly'
            }
        })

        assert isinstance(contract, Contract)
        assert 'smart402:' in contract.ucl['contract_id']
        assert contract.ucl['payment']['amount'] == 99
        assert contract.ucl['payment']['token'] == 'USDC'
        assert len(contract.ucl['metadata']['parties']) == 2

    @pytest.mark.asyncio
    async def test_create_from_template(self):
        """Test creating contract from template"""
        contract = await Smart402.from_template('saas-subscription', {
            'vendor_email': 'vendor@test.com',
            'customer_email': 'customer@test.com',
            'amount': 49
        })

        assert isinstance(contract, Contract)
        assert contract.ucl['payment']['amount'] == 49

    @pytest.mark.asyncio
    async def test_validate_required_fields(self):
        """Test validation of required fields"""
        with pytest.raises(Exception):
            await Smart402.create({
                'type': 'invalid',
                'parties': []
            })

    @pytest.mark.asyncio
    async def test_unique_contract_ids(self):
        """Test that contract IDs are unique"""
        contract1 = await Smart402.create({
            'type': 'test',
            'parties': ['a@test.com', 'b@test.com'],
            'payment': {
                'amount': 10,
                'token': 'USDC',
                'blockchain': 'polygon',
                'frequency': 'monthly'
            }
        })

        contract2 = await Smart402.create({
            'type': 'test',
            'parties': ['a@test.com', 'b@test.com'],
            'payment': {
                'amount': 10,
                'token': 'USDC',
                'blockchain': 'polygon',
                'frequency': 'monthly'
            }
        })

        assert contract1.ucl['contract_id'] != contract2.ucl['contract_id']


class TestAEO:
    """Test AEO (Answer Engine Optimization) functionality"""

    @pytest.fixture
    async def contract(self):
        """Create a test contract"""
        return await Smart402.create({
            'type': 'saas-subscription',
            'parties': ['vendor@example.com', 'customer@example.com'],
            'payment': {
                'amount': 99,
                'token': 'USDC',
                'blockchain': 'polygon',
                'frequency': 'monthly'
            },
            'metadata': {
                'title': 'Monthly SaaS Subscription',
                'description': 'Automated monthly payment for software service',
                'category': 'saas'
            }
        })

    @pytest.mark.asyncio
    async def test_calculate_aeo_score(self, contract):
        """Test AEO score calculation"""
        score = contract.get_aeo_score()

        assert 'total' in score
        assert 'semantic_richness' in score
        assert 'citation_friendliness' in score
        assert 'findability' in score
        assert 'authority_signals' in score
        assert 'citation_presence' in score

        assert 0 <= score['total'] <= 1

    @pytest.mark.asyncio
    async def test_generate_jsonld(self, contract):
        """Test JSON-LD generation"""
        jsonld = contract.generate_jsonld()

        assert '@context' in jsonld
        assert 'https://schema.org/' in jsonld
        assert 'SmartContract' in jsonld
        assert contract.ucl['contract_id'] in jsonld

    @pytest.mark.asyncio
    async def test_score_improvement_with_metadata(self):
        """Test that better metadata improves AEO score"""
        basic_contract = await Smart402.create({
            'type': 'test',
            'parties': ['a@test.com', 'b@test.com'],
            'payment': {
                'amount': 10,
                'token': 'USDC',
                'blockchain': 'polygon',
                'frequency': 'monthly'
            }
        })

        rich_contract = await Smart402.create({
            'type': 'test',
            'parties': ['a@test.com', 'b@test.com'],
            'payment': {
                'amount': 10,
                'token': 'USDC',
                'blockchain': 'polygon',
                'frequency': 'monthly'
            },
            'metadata': {
                'title': 'Comprehensive Test Contract',
                'description': 'Detailed description with rich metadata',
                'category': 'testing',
                'tags': ['test', 'example', 'smart402']
            }
        })

        basic_score = basic_contract.get_aeo_score()
        rich_score = rich_contract.get_aeo_score()

        assert rich_score['total'] >= basic_score['total']


class TestLLMO:
    """Test LLMO (Large Language Model Optimization) functionality"""

    @pytest.fixture
    async def contract(self):
        """Create a test contract"""
        return await Smart402.create({
            'type': 'saas-subscription',
            'parties': ['vendor@example.com', 'customer@example.com'],
            'payment': {
                'amount': 99,
                'token': 'USDC',
                'blockchain': 'polygon',
                'frequency': 'monthly'
            }
        })

    @pytest.mark.asyncio
    async def test_validate_contract(self, contract):
        """Test contract validation"""
        validation = contract.validate()

        assert 'valid' in validation
        assert 'errors' in validation
        assert 'warnings' in validation
        assert validation['valid'] is True
        assert len(validation['errors']) == 0

    @pytest.mark.asyncio
    async def test_generate_explanation(self, contract):
        """Test human-readable explanation generation"""
        explanation = contract.explain()

        assert isinstance(explanation, str)
        assert 'contract' in explanation.lower()
        assert 'payment' in explanation.lower()
        assert len(explanation) > 0

    @pytest.mark.asyncio
    async def test_compile_to_solidity(self, contract):
        """Test compilation to Solidity"""
        solidity = await contract.compile('solidity')

        assert 'pragma solidity' in solidity
        assert 'contract' in solidity
        assert 'function' in solidity

    @pytest.mark.asyncio
    async def test_compile_to_javascript(self, contract):
        """Test compilation to JavaScript"""
        javascript = await contract.compile('javascript')

        assert 'class' in javascript
        assert 'async' in javascript
        assert 'executePayment' in javascript

    @pytest.mark.asyncio
    async def test_compile_to_rust(self, contract):
        """Test compilation to Rust"""
        rust = await contract.compile('rust')

        assert 'pub struct' in rust
        assert 'impl' in rust
        assert 'execute_payment' in rust

    @pytest.mark.asyncio
    async def test_detect_validation_errors(self):
        """Test detection of validation errors"""
        invalid_contract = await Smart402.create({
            'type': 'test',
            'parties': [],  # Invalid: no parties
            'payment': {
                'amount': -10,  # Invalid: negative amount
                'token': 'USDC',
                'blockchain': 'polygon',
                'frequency': 'monthly'
            }
        })

        validation = invalid_contract.validate()

        assert validation['valid'] is False
        assert len(validation['errors']) > 0


class TestX402:
    """Test X402 Protocol functionality"""

    @pytest.fixture
    async def contract(self):
        """Create a test contract"""
        return await Smart402.create({
            'type': 'api-payment',
            'parties': ['provider@api.com', 'consumer@client.com'],
            'payment': {
                'amount': 0.10,
                'token': 'USDC',
                'blockchain': 'polygon',
                'frequency': 'per-request'
            }
        })

    @pytest.mark.asyncio
    async def test_generate_x402_headers(self, contract):
        """Test X402 header generation"""
        headers = contract.generate_x402_headers(conditions_met=True)

        assert 'X402-Contract-ID' in headers
        assert 'X402-Payment-Amount' in headers
        assert 'X402-Payment-Token' in headers
        assert 'X402-Settlement-Network' in headers
        assert 'X402-Conditions-Met' in headers
        assert 'X402-Signature' in headers
        assert 'X402-Nonce' in headers

        assert headers['X402-Contract-ID'] == contract.ucl['contract_id']
        assert headers['X402-Payment-Amount'] == '0.10'
        assert headers['X402-Payment-Token'] == 'USDC'

    @pytest.mark.asyncio
    async def test_unique_nonce(self, contract):
        """Test that nonces are unique"""
        headers1 = contract.generate_x402_headers(conditions_met=True)
        headers2 = contract.generate_x402_headers(conditions_met=True)

        assert headers1['X402-Nonce'] != headers2['X402-Nonce']

    @pytest.mark.asyncio
    async def test_signature_generation(self, contract):
        """Test signature generation"""
        headers = contract.generate_x402_headers(conditions_met=True)

        assert headers['X402-Signature'] is not None
        assert len(headers['X402-Signature']) > 0


class TestDeployment:
    """Test contract deployment functionality"""

    @pytest.fixture
    async def contract(self):
        """Create a test contract"""
        return await Smart402.create({
            'type': 'test',
            'parties': ['a@test.com', 'b@test.com'],
            'payment': {
                'amount': 10,
                'token': 'USDC',
                'blockchain': 'polygon-mumbai',
                'frequency': 'one-time'
            }
        })

    @pytest.mark.asyncio
    async def test_deploy_to_testnet(self, contract):
        """Test deployment to testnet"""
        result = await contract.deploy(network='polygon-mumbai')

        assert 'address' in result
        assert 'transaction_hash' in result
        assert 'network' in result
        assert result['network'] == 'polygon-mumbai'
        assert result['address'].startswith('0x')
        assert len(result['address']) == 42

    @pytest.mark.asyncio
    async def test_deploy_to_mainnet(self, contract):
        """Test deployment to mainnet"""
        result = await contract.deploy(network='polygon')

        assert result['network'] == 'polygon'
        assert result['address'].startswith('0x')

    @pytest.mark.asyncio
    async def test_deployment_receipt(self, contract):
        """Test deployment receipt"""
        result = await contract.deploy(network='polygon-mumbai')

        assert 'block_number' in result
        assert 'gas_used' in result


class TestMonitoring:
    """Test contract monitoring functionality"""

    @pytest.fixture
    async def contract(self):
        """Create a test contract"""
        return await Smart402.create({
            'type': 'saas-subscription',
            'parties': ['vendor@example.com', 'customer@example.com'],
            'payment': {
                'amount': 99,
                'token': 'USDC',
                'blockchain': 'polygon',
                'frequency': 'monthly'
            },
            'conditions': [
                {
                    'id': 'uptime_check',
                    'type': 'api',
                    'description': 'Service uptime > 99%',
                    'threshold': 0.99
                }
            ]
        })

    @pytest.mark.asyncio
    async def test_start_monitoring(self, contract):
        """Test starting monitoring"""
        result = await contract.start_monitoring(frequency='hourly')

        assert 'monitoring_id' in result
        assert 'frequency' in result
        assert result['frequency'] == 'hourly'

    @pytest.mark.asyncio
    async def test_check_conditions(self, contract):
        """Test checking conditions"""
        result = await contract.check_conditions()

        assert 'all_met' in result
        assert 'conditions' in result
        assert 'timestamp' in result
        assert isinstance(result['conditions'], list)

    @pytest.mark.asyncio
    async def test_execute_payment(self, contract):
        """Test payment execution"""
        result = await contract.execute_payment()

        assert 'success' in result
        assert 'transaction_hash' in result
        assert 'amount' in result
        assert 'token' in result
        assert result['amount'] == 99
        assert result['token'] == 'USDC'


class TestExportImport:
    """Test export and import functionality"""

    @pytest.fixture
    async def contract(self):
        """Create a test contract"""
        return await Smart402.create({
            'type': 'test',
            'parties': ['a@test.com', 'b@test.com'],
            'payment': {
                'amount': 10,
                'token': 'USDC',
                'blockchain': 'polygon',
                'frequency': 'monthly'
            }
        })

    @pytest.mark.asyncio
    async def test_export_to_yaml(self, contract):
        """Test YAML export"""
        yaml_str = contract.export_yaml()

        assert 'contract_id:' in yaml_str
        assert 'payment:' in yaml_str
        assert 'amount: 10' in yaml_str

    @pytest.mark.asyncio
    async def test_export_to_json(self, contract):
        """Test JSON export"""
        json_str = contract.export_json()
        parsed = json.loads(json_str)

        assert 'contract_id' in parsed
        assert 'payment' in parsed
        assert parsed['payment']['amount'] == 10

    @pytest.mark.asyncio
    async def test_load_from_yaml(self, contract):
        """Test loading from YAML"""
        yaml_str = contract.export_yaml()
        loaded = Smart402.load_from_yaml(yaml_str)

        assert loaded['contract_id'] == contract.ucl['contract_id']
        assert loaded['payment']['amount'] == contract.ucl['payment']['amount']

    @pytest.mark.asyncio
    async def test_load_from_json(self, contract):
        """Test loading from JSON"""
        json_str = contract.export_json()
        loaded = Smart402.load_from_json(json_str)

        assert loaded['contract_id'] == contract.ucl['contract_id']
        assert loaded['payment']['amount'] == contract.ucl['payment']['amount']


class TestTemplates:
    """Test template functionality"""

    def test_list_templates(self):
        """Test listing available templates"""
        templates = Smart402.get_templates()

        assert isinstance(templates, list)
        assert len(templates) > 0

    @pytest.mark.asyncio
    async def test_saas_template(self):
        """Test SaaS subscription template"""
        contract = await Smart402.from_template('saas-subscription', {
            'vendor_email': 'vendor@test.com',
            'customer_email': 'customer@test.com',
            'amount': 99
        })

        assert contract.ucl['metadata']['contract_type'] == 'saas-subscription'
        assert contract.ucl['payment']['amount'] == 99

    @pytest.mark.asyncio
    async def test_freelancer_template(self):
        """Test freelancer payment template"""
        contract = await Smart402.from_template('freelancer-payment', {
            'freelancer_email': 'dev@freelance.com',
            'client_email': 'client@company.com',
            'amount': 5000
        })

        assert contract.ucl['metadata']['contract_type'] == 'freelancer-payment'
        assert contract.ucl['payment']['amount'] == 5000


class TestErrorHandling:
    """Test error handling"""

    @pytest.mark.asyncio
    async def test_invalid_contract_type(self):
        """Test error for invalid contract type"""
        with pytest.raises(Exception):
            await Smart402.create({
                'type': '',
                'parties': ['a@test.com'],
                'payment': {
                    'amount': 10,
                    'token': 'USDC',
                    'blockchain': 'polygon',
                    'frequency': 'monthly'
                }
            })

    @pytest.mark.asyncio
    async def test_invalid_payment_amount(self):
        """Test error for invalid payment amount"""
        with pytest.raises(Exception):
            await Smart402.create({
                'type': 'test',
                'parties': ['a@test.com', 'b@test.com'],
                'payment': {
                    'amount': -100,
                    'token': 'USDC',
                    'blockchain': 'polygon',
                    'frequency': 'monthly'
                }
            })

    @pytest.mark.asyncio
    async def test_missing_required_fields(self):
        """Test error for missing required fields"""
        with pytest.raises(Exception):
            await Smart402.create({
                'type': 'test'
                # Missing parties and payment
            })


class TestContractSummary:
    """Test contract summary functionality"""

    @pytest.mark.asyncio
    async def test_generate_summary(self):
        """Test summary generation"""
        contract = await Smart402.create({
            'type': 'saas-subscription',
            'parties': ['vendor@example.com', 'customer@example.com'],
            'payment': {
                'amount': 99,
                'token': 'USDC',
                'blockchain': 'polygon',
                'frequency': 'monthly'
            }
        })

        summary = contract.get_summary()

        assert '99' in summary
        assert 'USDC' in summary
        assert 'monthly' in summary


# Run tests
if __name__ == '__main__':
    pytest.main([__file__, '-v'])
