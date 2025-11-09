# Smart402 Web Interface

Interactive web interface for the Smart402 AI-Native Smart Contract Framework.

## Features

- **Interactive Landing Page** - Overview of Smart402 and its four pillars
- **Real-time Dashboard** - Monitor contract processing and system metrics
- **Live Demo** - Process contracts through the complete pipeline
- **Comprehensive Documentation** - Getting started guides, API reference, and algorithms
- **REST API** - Full API for integration with external systems

## Quick Start

### Option 1: Static Files (No Server Required)

Simply open the HTML files in your browser:

```bash
# Open landing page
open web/index.html

# Or open dashboard
open web/dashboard.html
```

### Option 2: With API Server

For full functionality including live contract processing:

1. **Install API dependencies:**

```bash
cd web/api
pip install -r requirements.txt
```

2. **Start the API server:**

```bash
python server.py
```

The API will be available at `http://localhost:5000`

3. **Open the web interface:**

```bash
# Open in browser
open http://localhost:5000/../index.html

# Or serve with a simple HTTP server
cd web
python -m http.server 8000

# Then visit http://localhost:8000
```

## Directory Structure

```
web/
├── index.html              # Landing page
├── dashboard.html          # Real-time dashboard
├── static/
│   ├── css/
│   │   ├── main.css       # Main styles
│   │   └── dashboard.css  # Dashboard styles
│   └── js/
│       ├── main.js        # Main JavaScript
│       ├── demo.js        # Demo functionality
│       └── dashboard.js   # Dashboard logic
├── docs/
│   ├── getting-started.md # Getting started guide
│   ├── api-reference.md   # Complete API reference
│   └── algorithms.md      # Mathematical formulations
├── api/
│   ├── server.py          # Flask API server
│   └── requirements.txt   # API dependencies
└── README.md              # This file
```

## Pages

### Landing Page (`index.html`)

The main landing page features:

- **Hero Section** - Animated particle visualization
- **Features Section** - Detailed overview of AEO, LLMO, SCC, and X402
- **Interactive Demo** - Process contracts in real-time
- **Documentation Links** - Quick access to all docs
- **Responsive Design** - Works on mobile, tablet, and desktop

### Dashboard (`dashboard.html`)

Real-time analytics dashboard with:

- **Key Metrics** - Total contracts, success rate, processing time, fitness score
- **Pipeline Visualization** - Contract flow through all stages
- **Performance Charts** - Success rate and efficiency over time
- **Component Efficiency** - Radar chart of AEO, LLMO, SCC, X402
- **State Transitions** - Distribution of contracts across states
- **Network Analytics** - Network effect visualization
- **Contract Registry** - Searchable table of all contracts

## API Integration

The web interface integrates with the Smart402 Python API:

### Health Check

```javascript
fetch('http://localhost:5000/api/health')
  .then(response => response.json())
  .then(data => console.log(data.status));
```

### Process Contract

```javascript
fetch('http://localhost:5000/api/contract/process', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    type: 'payment',
    amount: 10000,
    parties: ['Alice', 'Bob'],
    terms: 'Payment for services'
  })
})
  .then(response => response.json())
  .then(result => console.log(result));
```

### Get Statistics

```javascript
fetch('http://localhost:5000/api/stats')
  .then(response => response.json())
  .then(stats => {
    console.log(`Total contracts: ${stats.totalContracts}`);
    console.log(`Success rate: ${stats.stateMachine.success_rate}`);
  });
```

## Customization

### Styling

Customize colors and theme in `static/css/main.css`:

```css
:root {
    --primary: #667eea;
    --secondary: #764ba2;
    --success: #43e97b;
    /* ... more variables ... */
}
```

### Configuration

Update API endpoint in JavaScript files:

```javascript
// static/js/demo.js
const API_BASE_URL = 'http://localhost:5000/api';
```

## Features in Detail

### Interactive Demo

The demo allows users to:

1. Input contract details (type, amount, parties, terms)
2. Process through all four stages:
   - **AEO** - Optimize for AI discovery
   - **LLMO** - Ensure AI understanding
   - **SCC** - Compile to smart contract
   - **X402** - Execute payment
3. View detailed results for each stage
4. See real-time processing status

### Real-time Dashboard

Dashboard features:

- **Auto-refresh** - Updates every 10 seconds
- **Live Charts** - Powered by Chart.js
- **Responsive Grids** - Adapts to screen size
- **Sidebar Navigation** - Easy access to all sections
- **Metric Cards** - Key performance indicators
- **Progress Bars** - Component efficiency visualization

### Visualizations

Built-in chart types:

- **Funnel Chart** - Contract processing pipeline
- **Line Chart** - Performance metrics over time
- **Radar Chart** - Component efficiency
- **Doughnut Chart** - State distribution
- **Scatter Chart** - Network value growth
- **Area Chart** - Optimization landscape

## Documentation

Comprehensive markdown documentation:

- **[Getting Started](docs/getting-started.md)** - Installation and quick start
- **[API Reference](docs/api-reference.md)** - Complete API documentation
- **[Algorithms](docs/algorithms.md)** - Mathematical formulations

## Browser Support

The web interface supports:

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Opera (latest)

**Note:** Internet Explorer is not supported.

## Development

### Running Locally

```bash
# Install dependencies
cd web/api
pip install -r requirements.txt

# Start API server
python server.py

# In another terminal, serve static files
cd web
python -m http.server 8000
```

### Building for Production

For production deployment:

1. **Minify JavaScript and CSS:**

```bash
# Install terser and cssnano
npm install -g terser cssnano-cli

# Minify
terser static/js/main.js -o static/js/main.min.js
cssnano static/css/main.css static/css/main.min.css
```

2. **Update HTML to use minified files**

3. **Configure API endpoint:**

```javascript
const API_BASE_URL = 'https://api.smart402.io';
```

4. **Deploy to hosting:**

- Static files → Netlify, Vercel, GitHub Pages
- API server → Heroku, AWS, Google Cloud

## Performance

### Optimization Tips

- **Enable caching** - Set appropriate cache headers
- **Use CDN** - Serve static assets from CDN
- **Compress assets** - Enable gzip/brotli compression
- **Lazy load images** - Load images on demand
- **Code splitting** - Split JavaScript into chunks

### Lighthouse Scores

Target scores:

- Performance: 90+
- Accessibility: 95+
- Best Practices: 90+
- SEO: 95+

## Security

### Best Practices

- **HTTPS only** - Always use HTTPS in production
- **CORS configuration** - Restrict allowed origins
- **Rate limiting** - Implement on API endpoints
- **Input validation** - Validate all user inputs
- **CSP headers** - Add Content Security Policy
- **XSS prevention** - Sanitize user-generated content

### API Security

```python
# In production, add authentication
from flask_jwt_extended import jwt_required

@app.route('/api/contract/process', methods=['POST'])
@jwt_required()
def process_contract():
    # ... protected endpoint ...
```

## Troubleshooting

### Common Issues

**Charts not rendering:**
```javascript
// Make sure Chart.js is loaded
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
```

**API connection failed:**
```bash
# Check if server is running
curl http://localhost:5000/api/health

# Check CORS configuration
# Add to server.py: CORS(app, origins=['http://localhost:8000'])
```

**Icons not showing:**
```html
<!-- Verify Font Awesome is loaded -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
```

## Contributing

Contributions welcome! Areas for improvement:

- Additional visualizations
- Mobile app integration
- Advanced analytics
- Real-time collaboration
- Export/import functionality

## License

MIT License - see main repository for details.

## Support

- **Documentation**: https://docs.smart402.io
- **GitHub Issues**: https://github.com/smart402/smart402/issues
- **Discord**: https://discord.gg/smart402
- **Email**: team@smart402.io
