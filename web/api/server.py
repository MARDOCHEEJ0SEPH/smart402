"""
Smart402 API Server
Simple Flask-based API for web interface integration
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from src.core.orchestrator import Smart402Orchestrator
from src.aeo.engine import AEOEngine
from src.llmo.engine import LLMOEngine
from src.scc.engine import SCCEngine
from src.x402.engine import X402Engine

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for web interface

# Initialize orchestrator
orchestrator = Smart402Orchestrator()

# Initialize engines
aeo_engine = AEOEngine()
llmo_engine = LLMOEngine()
scc_engine = SCCEngine()
x402_engine = X402Engine()


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'version': '1.0.0',
        'components': {
            'aeo': 'operational',
            'llmo': 'operational',
            'scc': 'operational',
            'x402': 'operational'
        }
    })


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get system statistics"""
    stats = orchestrator.get_statistics()

    return jsonify({
        'totalContracts': stats['total_contracts'],
        'registrySize': stats['registry_size'],
        'bestFitness': stats['best_fitness'],
        'stateMachine': stats['state_machine'],
        'configuration': stats['current_configuration']
    })


@app.route('/api/contract/process', methods=['POST'])
def process_contract():
    """Process a contract through all stages"""
    try:
        data = request.json

        # Validate input
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Create contract object
        contract = {
            'id': data.get('id', f'contract_{int(asyncio.get_event_loop().time() * 1000)}'),
            'type': data.get('type', 'payment'),
            'amount': float(data.get('amount', 0)),
            'parties': data.get('parties', []),
            'terms': data.get('terms', ''),
            'conditions': data.get('conditions', []),
            'target_query': data.get('target_query', '')
        }

        # Process asynchronously
        result = asyncio.run(process_contract_async(contract))

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


async def process_contract_async(contract):
    """Process contract through pipeline"""
    results = {
        'contractId': contract['id'],
        'stages': []
    }

    try:
        # Stage 1: AEO
        aeo_result = await aeo_engine.optimize_discovery([contract])
        contract = aeo_result[0]
        results['stages'].append({
            'name': 'AEO',
            'status': 'success',
            'score': contract.get('aeo_score', 0),
            'details': {
                'contentLength': len(contract.get('optimized_content', '')),
                'cluster': contract.get('cluster')
            }
        })

        # Stage 2: LLMO
        llmo_result = await llmo_engine.optimize_understanding([contract])
        contract = llmo_result[0]
        results['stages'].append({
            'name': 'LLMO',
            'status': 'success',
            'score': contract.get('understanding_score', 0),
            'details': {
                'semanticComponents': contract.get('semantic_structure', {}).get('components', {})
            }
        })

        # Stage 3: SCC
        scc_result = await scc_engine.compile_and_verify([contract])
        contract = scc_result[0]
        results['stages'].append({
            'name': 'SCC',
            'status': contract.get('compilation_status', 'failed'),
            'details': {
                'gasEstimate': contract.get('gas_estimate', 0),
                'bytecode': contract.get('smart_contract_code', '')[:100] + '...',
                'verification': contract.get('verification_result', {})
            }
        })

        # Stage 4: X402
        x402_result = await x402_engine.optimize_execution([contract])
        contract = x402_result[0]
        results['stages'].append({
            'name': 'X402',
            'status': contract.get('execution_status', 'failed'),
            'details': {
                'txHash': contract.get('tx_hash', ''),
                'gasUsed': contract.get('gas_used', 0),
                'executionTime': contract.get('execution_time', 0)
            }
        })

        results['status'] = 'completed'
        results['finalContract'] = contract

    except Exception as e:
        results['status'] = 'failed'
        results['error'] = str(e)

    return results


@app.route('/api/contract/<contract_id>', methods=['GET'])
def get_contract(contract_id):
    """Get contract details"""
    if contract_id in orchestrator.contract_registry:
        contract = orchestrator.contract_registry[contract_id]
        return jsonify(contract)
    else:
        return jsonify({'error': 'Contract not found'}), 404


@app.route('/api/contracts', methods=['GET'])
def list_contracts():
    """List all contracts"""
    # Get pagination parameters
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))

    # Get all contracts
    contracts = list(orchestrator.contract_registry.values())

    # Sort by ID (newest first)
    contracts.sort(key=lambda x: x.get('id', ''), reverse=True)

    # Paginate
    start = (page - 1) * per_page
    end = start + per_page
    paginated = contracts[start:end]

    return jsonify({
        'contracts': paginated,
        'total': len(contracts),
        'page': page,
        'per_page': per_page,
        'pages': (len(contracts) + per_page - 1) // per_page
    })


@app.route('/api/aeo/score', methods=['POST'])
def calculate_aeo_score():
    """Calculate AEO score for contract"""
    try:
        contract = request.json

        from src.aeo.scoring import AEOScorer
        scorer = AEOScorer()
        score = scorer.calculate_aeo_score(contract)

        return jsonify({
            'aeoScore': score,
            'components': {
                'semanticRelevance': scorer.semantic_relevance(contract),
                'citationFrequency': scorer.citation_frequency(contract),
                'contentFreshness': scorer.content_freshness(contract),
                'authorityScore': scorer.authority_score(contract),
                'crossPlatformPresence': scorer.cross_platform_presence(contract)
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/llmo/score', methods=['POST'])
def calculate_llmo_score():
    """Calculate LLMO understanding score"""
    try:
        contract = request.json

        from src.llmo.understanding import UnderstandingScorer
        scorer = UnderstandingScorer()
        score = scorer.calculate_llmo_score(contract)

        return jsonify({
            'understandingScore': score,
            'ensembleScore': scorer.ensemble_understanding(contract)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/scc/compile', methods=['POST'])
def compile_contract():
    """Compile contract to smart contract"""
    try:
        contract = request.json

        from src.scc.compiler import SmartContractCompiler
        compiler = SmartContractCompiler(
            target_blockchain=request.args.get('blockchain', 'ethereum')
        )
        result = compiler.compile(contract)

        return jsonify({
            'success': result.success,
            'bytecode': result.bytecode,
            'gasEstimate': result.gas_estimate,
            'warnings': result.warnings,
            'errors': result.errors
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/x402/route', methods=['POST'])
def find_payment_route():
    """Find optimal payment route"""
    try:
        data = request.json
        source = data.get('source', 'ethereum')
        destination = data.get('destination', 'ethereum')
        amount = float(data.get('amount', 0))

        from src.x402.routing import PaymentRouter
        router = PaymentRouter()
        route = router.find_optimal_route(source, destination, amount)

        if route:
            return jsonify({
                'path': route.path,
                'cost': route.cost,
                'estimatedTime': route.estimated_time,
                'liquidityAvailable': route.liquidity_available
            })
        else:
            return jsonify({'error': 'No route found'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
