# Smart402SA Quick Start Guide

Get the Smart402 Scalable Architecture up and running in minutes.

## Prerequisites

- **Docker** and **Docker Compose** (for infrastructure)
- **Node.js** 20+ (for local development)
- **Git**

## 1. Quick Start with Docker (Recommended)

The fastest way to see Smart402SA in action:

```bash
# 1. Clone and navigate to smart402SA
cd framework/examples/smart402SA

# 2. Copy environment file
cp .env.example .env

# 3. Start all services with Docker Compose
docker-compose up -d

# 4. Wait for services to be ready (30-60 seconds)
docker-compose ps

# 5. Access the services
```

### Service URLs

Once running, access these services in your browser:

| Service | URL | Description |
|---------|-----|-------------|
| **API Gateway** | http://localhost:4000 | RESTful API |
| **API Docs** | http://localhost:4000/docs | Swagger UI |
| **Frontend** | http://localhost:3000 | React App |
| **GraphQL** | http://localhost:4002/graphql | GraphQL Playground |
| **Grafana** | http://localhost:3100 | Metrics (admin/smart402_dev_password) |
| **Prometheus** | http://localhost:9090 | Metrics DB |
| **Kibana** | http://localhost:5601 | Log Viewer |
| **RabbitMQ** | http://localhost:15672 | Message Queue (smart402/smart402_dev_password) |
| **Jaeger** | http://localhost:16686 | Distributed Tracing |

## 2. Create Your First Smart402 Contract

Using the API:

```bash
curl -X POST http://localhost:4000/api/v1/contracts \
  -H "Content-Type: application/json" \
  -d '{
    "type": "service_payment",
    "title": "Web Development Service Contract",
    "description": "Contract for web development services with automatic payment upon completion",
    "parties": [
      {
        "id": "client_001",
        "role": "Client",
        "address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"
      },
      {
        "id": "developer_001",
        "role": "Developer",
        "address": "0x123456789abcdef123456789abcdef1234567890"
      }
    ],
    "terms": {
      "amount": "1000",
      "currency": "USDC",
      "deliverables": ["Website", "Mobile App"],
      "deadline": "2024-12-31"
    },
    "metadata": {
      "keywords": ["web development", "payment", "service", "contract"],
      "tags": ["technology", "freelance"]
    }
  }'
```

**Response:**

```json
{
  "success": true,
  "contract": {
    "contract_id": "smart402:service_payment:1732032000_a3f9k2",
    "aeo_score": 0.87,
    "status": "validated",
    "ucl": { ... },
    "x402_header": {
      "version": "1.0.0",
      "payment_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
      "amount": "1000",
      "payment_token": "USDC"
    }
  }
}
```

## 3. Check Contract Details

```bash
# Get contract by ID
curl http://localhost:4000/api/v1/contracts/smart402:service_payment:1732032000_a3f9k2

# List all contracts
curl http://localhost:4000/api/v1/contracts?page=1&limit=10
```

## 4. Execute Payment (Demo Mode)

```bash
curl -X POST http://localhost:4000/api/v1/contracts/smart402:service_payment:1732032000_a3f9k2/execute \
  -H "Content-Type: application/json" \
  -d '{
    "amount": "1000",
    "currency": "USDC",
    "recipient": "0x123456789abcdef123456789abcdef1234567890"
  }'
```

## 5. View Logs and Metrics

### Application Logs

```bash
# Gateway logs
docker-compose logs -f gateway

# All services
docker-compose logs -f
```

### Metrics Dashboard

1. Open Grafana: http://localhost:3100
2. Login: `admin` / `smart402_dev_password`
3. Navigate to Dashboards → Smart402

### Search Logs

1. Open Kibana: http://localhost:5601
2. Create index pattern: `smart402sa-*`
3. Discover logs with full-text search

## 6. Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
```

## Production Mode (Real Blockchain)

To enable real blockchain payments:

1. **Get a wallet private key**:
   ```bash
   # Using MetaMask or any Ethereum wallet
   # Export your private key (keep it secret!)
   ```

2. **Add to .env**:
   ```env
   PRIVATE_KEY=0x_your_private_key_here
   BLOCKCHAIN_RPC_URL=https://polygon-mainnet.g.alchemy.com/v2/YOUR_API_KEY
   CHAIN_ID=137  # Polygon Mainnet
   ```

3. **Fund your wallet**:
   - Ensure wallet has MATIC for gas fees
   - Ensure wallet has USDC for payments

4. **Restart services**:
   ```bash
   docker-compose restart gateway smart402-core
   ```

5. **Verify**:
   ```bash
   curl http://localhost:4000/health
   # Should show: "mode": "production"
   ```

## Development Mode (Local)

For active development without Docker:

```bash
# 1. Start infrastructure only
docker-compose up -d postgres mongodb redis elasticsearch

# 2. Install SDK dependencies
cd shared/smart402-sdk
npm install
npm run build

# 3. Install gateway dependencies
cd ../../backend/gateway
npm install

# 4. Start gateway in dev mode
npm run dev

# Gateway will run with hot-reload on http://localhost:4000
```

## Architecture Overview

```
┌─────────────┐
│   nginx     │  ← Reverse Proxy / Load Balancer
│  Port: 80   │
└──────┬──────┘
       │
   ┌───┴────┐
   │        │
┌──▼───┐ ┌─▼────────┐
│ React│ │  Gateway │  ← Fastify API + Smart402 SDK
│ :3000│ │  :4000   │
└──────┘ └─┬────────┘
           │
     ┌─────┼─────┐
     │     │     │
  ┌──▼──┐ │  ┌──▼─────┐
  │ PG  │ │  │ Redis  │
  │:5432│ │  │ :6379  │
  └─────┘ │  └────────┘
          │
       ┌──▼────┐
       │MongoDB│
       │:27017 │
       └───────┘
```

## Troubleshooting

### Services won't start

```bash
# Check docker logs
docker-compose logs

# Restart specific service
docker-compose restart gateway
```

### Port already in use

Edit `docker-compose.yml` and change conflicting ports:

```yaml
ports:
  - "4001:4000"  # Changed from 4000:4000
```

### Database connection failed

```bash
# Ensure databases are healthy
docker-compose ps

# Restart databases
docker-compose restart postgres mongodb redis
```

### Out of memory

```bash
# Reduce services or increase Docker memory limit
# In Docker Desktop: Settings → Resources → Memory
```

## Next Steps

- **Explore API**: http://localhost:4000/docs
- **Read Full Documentation**: See `README.md`
- **Frontend Development**: See `GETTING_STARTED.md`
- **Deploy to Production**: See `DEPLOYMENT.md` (coming soon)

## Support

- GitHub Issues: [smart402/issues](https://github.com/MARDOCHEEJ0SEPH/smart402/issues)
- Documentation: [docs.smart402.io](https://docs.smart402.io)
- Community: [community.smart402.io](https://community.smart402.io)

---

**Built with Smart402 Framework - Universal Contract Language for the AI Age**
