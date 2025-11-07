# Smart402 Web Dashboard

A modern web interface for the Smart402 Algorithmic Framework, providing real-time monitoring and control of the AEO + LLMO + SCC + X402 Protocol integration.

## Features

- **Real-time Statistics Dashboard**: Monitor system performance with live updates
- **Component Status Tracking**: View the status of all four components (AEO, LLMO, SCC, X402)
- **State Machine Visualization**: Track state transitions through the contract lifecycle
- **Activity Logging**: Detailed logging of all system operations
- **Interactive Controls**: Start, stop, and reset orchestration with custom durations

## Installation

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

Or from the project root:

```bash
pip install -r requirements.txt
```

## Running the Web Dashboard

1. Navigate to the web directory:

```bash
cd web
```

2. Start the Flask server:

```bash
python app.py
```

3. Open your web browser and navigate to:

```
http://localhost:5000
```

## Usage

### Starting an Orchestration

1. Set the duration (in seconds) for the orchestration run
2. Click the "START ORCHESTRATION" button
3. Monitor real-time statistics and component status
4. View activity logs for detailed operation tracking

### Stopping an Orchestration

- Click the "STOP" button to halt the current orchestration

### Resetting the System

- Click the "RESET" button to clear all statistics and return to initial state

## Architecture

### Frontend (HTML/CSS/JavaScript)

- **index.html**: Main dashboard interface
- **style.css**: Modern, responsive styling with dark theme
- **app.js**: Client-side application logic and API communication

### Backend (Python/Flask)

- **app.py**: Flask API server providing REST endpoints for:
  - `/api/start` - Start orchestration
  - `/api/stop` - Stop orchestration
  - `/api/reset` - Reset system
  - `/api/stats` - Get real-time statistics
  - `/api/health` - Health check

## API Endpoints

### POST /api/start
Start the Smart402 orchestration.

**Request Body:**
```json
{
  "duration": 10
}
```

**Response:**
```json
{
  "success": true,
  "message": "Orchestration started for 10 seconds"
}
```

### POST /api/stop
Stop the currently running orchestration.

**Response:**
```json
{
  "success": true,
  "message": "Orchestration stopped"
}
```

### POST /api/reset
Reset the system to initial state.

**Response:**
```json
{
  "success": true,
  "message": "System reset successfully"
}
```

### GET /api/stats
Get current statistics from the orchestrator.

**Response:**
```json
{
  "success": true,
  "stats": {
    "state_machine": {
      "current_state": "s2",
      "total_transitions": 15,
      "success_rate": 0.95
    },
    "total_contracts": 10,
    "registry_size": 5,
    "best_fitness": 0.8765,
    "is_complete": false
  }
}
```

### GET /api/health
Health check endpoint.

**Response:**
```json
{
  "success": true,
  "status": "healthy",
  "is_running": false
}
```

## Components Overview

### 1. AEO (Answer Engine Optimization)
Handles contract discovery and semantic relevance scoring.

### 2. LLMO (Large Language Model Optimization)
Processes natural language understanding and contract interpretation.

### 3. SCC (Smart Contract Compilation)
Compiles and validates smart contracts.

### 4. X402 (Payment Protocol)
Manages payment execution and settlement.

## State Machine Flow

The dashboard visualizes the complete state transition flow:

```
S0 → S1 → S2 → S3 → S4 → S5 → S6
```

- **S0**: Contract Discovery (AEO)
- **S1**: Contract Understanding (LLMO)
- **S2**: Smart Contract Compilation (SCC)
- **S3**: Condition Verification (Oracle)
- **S4**: Payment Execution (X402)
- **S5**: Settlement Confirmation (Blockchain)
- **S6**: Contract Completion

## Customization

### Changing Update Frequency

Edit `app.js` and modify the update interval:

```javascript
this.updateInterval = setInterval(() => {
    this.fetchStatistics();
}, 1000); // Change 1000 to desired milliseconds
```

### Styling Customization

Edit `style.css` to customize colors, layouts, and themes. CSS variables are defined in `:root` for easy theming:

```css
:root {
    --primary-color: #2563eb;
    --secondary-color: #7c3aed;
    --success-color: #10b981;
    --danger-color: #ef4444;
    /* ... */
}
```

## Browser Compatibility

The dashboard is compatible with:
- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)

## Troubleshooting

### Port Already in Use

If port 5000 is already in use, modify `app.py`:

```python
app.run(host='0.0.0.0', port=5001, debug=True)
```

### CORS Issues

CORS is enabled by default. If you encounter issues, verify `flask-cors` is installed:

```bash
pip install flask-cors
```

## Development

To run in development mode with hot reload:

```bash
export FLASK_ENV=development
python app.py
```

## License

This web interface is part of the Smart402 project and follows the same license.
