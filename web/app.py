"""
Smart402 Web Application
Flask backend API for the Smart402 Dashboard
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import asyncio
import threading
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src import Smart402Orchestrator

app = Flask(__name__)
CORS(app)

# Global orchestrator instance
orchestrator = None
orchestrator_task = None
orchestrator_thread = None
is_running = False
is_complete = False


def run_orchestrator(duration):
    """Run the orchestrator in a separate thread"""
    global is_running, is_complete

    async def run_async():
        global orchestrator, is_running, is_complete
        is_running = True
        is_complete = False
        try:
            await orchestrator.run(duration=duration)
            is_complete = True
        except Exception as e:
            print(f"Error in orchestrator: {e}")
        finally:
            is_running = False

    # Create new event loop for this thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_async())
    loop.close()


@app.route('/')
def index():
    """Serve the main dashboard page"""
    return render_template('index.html')


@app.route('/api/start', methods=['POST'])
def start_orchestration():
    """Start the Smart402 orchestration"""
    global orchestrator, orchestrator_thread, is_running, is_complete

    if is_running:
        return jsonify({
            'success': False,
            'error': 'Orchestration is already running'
        }), 400

    try:
        data = request.get_json()
        duration = data.get('duration', 10)

        # Create new orchestrator instance
        orchestrator = Smart402Orchestrator()
        is_complete = False

        # Start orchestrator in a separate thread
        orchestrator_thread = threading.Thread(
            target=run_orchestrator,
            args=(duration,),
            daemon=True
        )
        orchestrator_thread.start()

        return jsonify({
            'success': True,
            'message': f'Orchestration started for {duration} seconds'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/stop', methods=['POST'])
def stop_orchestration():
    """Stop the Smart402 orchestration"""
    global is_running, is_complete

    try:
        is_running = False
        is_complete = True

        return jsonify({
            'success': True,
            'message': 'Orchestration stopped'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/reset', methods=['POST'])
def reset_system():
    """Reset the Smart402 system"""
    global orchestrator, is_running, is_complete

    try:
        is_running = False
        is_complete = False
        orchestrator = None

        return jsonify({
            'success': True,
            'message': 'System reset successfully'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/stats', methods=['GET'])
def get_statistics():
    """Get current statistics from the orchestrator"""
    global orchestrator, is_running, is_complete

    try:
        if orchestrator is None:
            # Return default stats
            return jsonify({
                'success': True,
                'stats': {
                    'state_machine': {
                        'current_state': '-',
                        'total_transitions': 0,
                        'success_rate': 0.0
                    },
                    'total_contracts': 0,
                    'registry_size': 0,
                    'best_fitness': 0.0,
                    'is_complete': False
                }
            })

        # Get statistics from orchestrator
        stats = orchestrator.get_statistics()
        stats['is_complete'] = is_complete

        return jsonify({
            'success': True,
            'stats': stats
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'success': True,
        'status': 'healthy',
        'is_running': is_running
    })


if __name__ == '__main__':
    print("=" * 60)
    print("Smart402 Web Dashboard")
    print("=" * 60)
    print("\nStarting Flask server...")
    print("Dashboard will be available at: http://localhost:5000")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 60)

    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        use_reloader=False  # Disable reloader to avoid issues with threads
    )
