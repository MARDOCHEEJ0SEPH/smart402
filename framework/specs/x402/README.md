# X402 Protocol Specification
## HTTP Extension for Machine-to-Machine Automated Payments

**Version:** 1.0.0
**Status:** Draft Specification
**Last Updated:** 2024-01-01

---

## Abstract

X402 is an HTTP protocol extension that enables automatic, machine-to-machine commercial transactions. It extends HTTP with headers and semantics for expressing commercial terms, triggering payments, and settling transactions on blockchain networks.

**Think of X402 as:** `HTTP + Payment Terms + Automatic Execution`

---

## 1. Overview

### 1.1 Problem Statement

Current HTTP enables:
- ✅ Data exchange
- ✅ Authentication
- ✅ Resource access

But NOT:
- ❌ Automatic payments
- ❌ Commercial terms negotiation
- ❌ Machine-readable pricing
- ❌ Blockchain settlement

### 1.2 X402 Solution

X402 adds:
```http
X402-Contract-ID: smart402:abc123
X402-Payment-Amount: 99.00
X402-Payment-Token: USDC
X402-Conditions-Met: true
```

Result:
```
HTTP Request → X402 Headers → Automatic Payment → Blockchain Settlement
```

---

## 2. Protocol Headers

### 2.1 Core Headers

#### X402-Contract-ID
**Required:** Yes
**Format:** `smart402:{type}:{id}`

```http
X402-Contract-ID: smart402:saas:abc123
```

Uniquely identifies the Smart402 contract governing this transaction.

---

#### X402-Payment-Amount
**Required:** Yes
**Format:** Decimal number

```http
X402-Payment-Amount: 99.00
```

Amount to be paid in the specified currency/token.

---

#### X402-Payment-Token
**Required:** Yes
**Format:** Token symbol

```http
X402-Payment-Token: USDC
```

Supported tokens:
- `USDC` - USD Coin
- `USDT` - Tether
- `DAI` - Dai Stablecoin
- `ETH` - Ethereum
- `MATIC` - Polygon
- Custom ERC-20 tokens

---

#### X402-Settlement-Network
**Required:** Yes
**Format:** Blockchain network name

```http
X402-Settlement-Network: Polygon
```

Supported networks:
- `Ethereum` - Ethereum Mainnet
- `Polygon` - Polygon PoS
- `Arbitrum` - Arbitrum One
- `Optimism` - Optimism Mainnet
- `Base` - Base Network

---

#### X402-Settlement-Address
**Required:** Yes
**Format:** Blockchain address

```http
X402-Settlement-Address: 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb
```

Destination address for payment settlement.

---

#### X402-Conditions-Met
**Required:** Yes
**Format:** `true` | `false`

```http
X402-Conditions-Met: true
```

Indicates whether all contract conditions have been satisfied.

---

#### X402-Oracle-Confirmations
**Required:** If conditions exist
**Format:** Comma-separated oracle IDs

```http
X402-Oracle-Confirmations: chainlink:0x123,custom:uptime-api
```

List of oracles that confirmed conditions are met.

---

#### X402-Dispute-Resolution
**Required:** No
**Format:** Resolution method

```http
X402-Dispute-Resolution: multisig-2-of-3
```

Dispute resolution mechanism:
- `multisig-2-of-3` - 2-of-3 multisignature
- `multisig-3-of-5` - 3-of-5 multisignature
- `arbitrator` - Third-party arbitrator
- `dao-vote` - DAO governance vote

---

#### X402-Webhook-URL
**Required:** No
**Format:** HTTPS URL

```http
X402-Webhook-URL: https://api.example.com/webhooks/payment
```

Callback URL for payment notifications.

---

#### X402-Signature
**Required:** Yes (for payment execution)
**Format:** Hex-encoded signature

```http
X402-Signature: 0xabcdef...
```

Cryptographic signature authorizing the payment.

---

### 2.2 Optional Headers

#### X402-Payment-Frequency
```http
X402-Payment-Frequency: monthly
```

Values: `one-time`, `daily`, `weekly`, `monthly`, `yearly`

---

#### X402-Payment-Schedule
```http
X402-Payment-Schedule: 0 0 1 * *
```

Cron expression for recurring payments.

---

#### X402-Rate-Limit
```http
X402-Rate-Limit: 100/hour
```

Maximum payment requests per time period.

---

#### X402-Escrow-Address
```http
X402-Escrow-Address: 0xEscrow...
```

Escrow contract for holding funds.

---

## 3. Request/Response Flow

### 3.1 Complete Flow

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       │ 1. HTTP Request with X402 headers
       ├────────────────────────────────────►┌─────────────┐
       │                                      │   Server    │
       │ 2. Server validates conditions       └──────┬──────┘
       │                                             │
       │                                             │ 3. Check oracles
       │                                             ├───────────────►┌──────────┐
       │                                             │                │ Oracles  │
       │                                             │◄───────────────┤          │
       │                                             │ 4. Confirmations└──────────┘
       │                                             │
       │ 5. Response with payment authorization     │
       │◄────────────────────────────────────────────┤
       │                                             │
       │ 6. Execute blockchain payment              │
       ├────────────────────────────────────────────┤
       │                                             │
       │                                             │ 7. Record settlement
       │                                             ├───────────────►┌──────────┐
       │                                             │                │Blockchain│
       │                                             │◄───────────────┤          │
       │                                             │ 8. Confirmation└──────────┘
       │                                             │
       │ 9. Webhook notification                    │
       │◄────────────────────────────────────────────┤
       │                                             │
       └                                             └
```

### 3.2 Example HTTP Request

```http
POST /api/service/access HTTP/1.1
Host: vendor.example.com
Content-Type: application/json
X402-Contract-ID: smart402:saas:abc123
X402-Payment-Amount: 99.00
X402-Payment-Token: USDC
X402-Settlement-Network: Polygon
X402-Settlement-Address: 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb
X402-Conditions-Met: true
X402-Oracle-Confirmations: chainlink:uptime-feed
X402-Signature: 0xabcdef1234567890...

{
  "service_request": "monthly_access",
  "user_id": "customer@example.com"
}
```

### 3.3 Example HTTP Response

```http
HTTP/1.1 200 OK
Content-Type: application/json
X402-Payment-Authorized: true
X402-Transaction-Hash: 0x9876543210fedcba...
X402-Settlement-Timestamp: 2024-01-01T00:00:00Z
X402-Receipt-URL: https://polygonscan.com/tx/0x987654...

{
  "status": "payment_processed",
  "service_granted": true,
  "valid_until": "2024-02-01T00:00:00Z",
  "receipt": {
    "amount": 99.00,
    "token": "USDC",
    "transaction_hash": "0x9876543210fedcba...",
    "block_number": 12345678
  }
}
```

---

## 4. Payment Execution Workflow

### 4.1 Four-Stage Flow

```
Stage 1: Condition Detection
   ↓
Stage 2: X402 Negotiation
   ↓
Stage 3: Payment Execution
   ↓
Stage 4: Settlement Confirmation
```

### 4.2 Stage 1: Condition Detection

```python
def detect_conditions(contract):
    """
    Monitor oracles until conditions met
    """
    while True:
        conditions = {}

        for condition in contract.conditions:
            oracle_data = fetch_oracle(condition.source)
            conditions[condition.id] = evaluate(
                oracle_data,
                condition.operator,
                condition.threshold
            )

        if all(conditions.values()):
            return {
                'conditions_met': True,
                'confirmations': list(conditions.keys())
            }

        sleep(monitoring_interval)
```

### 4.2 Stage 2: X402 Negotiation

```python
def negotiate_payment(contract, conditions):
    """
    Prepare X402 headers for payment request
    """
    headers = {
        'X402-Contract-ID': contract.id,
        'X402-Payment-Amount': calculate_amount(contract, conditions),
        'X402-Payment-Token': contract.payment.token,
        'X402-Settlement-Network': contract.payment.blockchain,
        'X402-Settlement-Address': contract.parties.vendor.address,
        'X402-Conditions-Met': 'true',
        'X402-Oracle-Confirmations': ','.join(conditions['confirmations']),
        'X402-Signature': sign_payment(contract, conditions)
    }

    return requests.post(
        contract.service_endpoint,
        headers=headers,
        json={'action': 'execute_payment'}
    )
```

### 4.3 Stage 3: Payment Execution

```python
def execute_payment(headers):
    """
    Execute blockchain transaction
    """
    # Verify signature
    assert verify_signature(headers['X402-Signature'])

    # Prepare transaction
    tx = {
        'from': get_payer_address(headers['X402-Contract-ID']),
        'to': headers['X402-Settlement-Address'],
        'amount': parse_amount(headers['X402-Payment-Amount']),
        'token': headers['X402-Payment-Token'],
        'network': headers['X402-Settlement-Network']
    }

    # Execute on blockchain
    tx_hash = blockchain.send_transaction(tx)

    return {
        'success': True,
        'transaction_hash': tx_hash
    }
```

### 4.4 Stage 4: Settlement Confirmation

```python
def confirm_settlement(tx_hash, network):
    """
    Wait for blockchain confirmation
    """
    while True:
        receipt = blockchain.get_receipt(tx_hash, network)

        if receipt.confirmations >= MIN_CONFIRMATIONS:
            # Send webhook notification
            send_webhook({
                'event': 'payment_confirmed',
                'transaction_hash': tx_hash,
                'confirmations': receipt.confirmations
            })

            return receipt

        sleep(BLOCK_TIME)
```

---

## 5. Security

### 5.1 Signature Requirements

All payment-triggering requests MUST include valid signature:

```javascript
function signPayment(contract, privateKey) {
  const message = {
    contractId: contract.id,
    amount: contract.payment.amount,
    timestamp: Date.now(),
    nonce: generateNonce()
  };

  const messageHash = keccak256(JSON.stringify(message));
  const signature = sign(messageHash, privateKey);

  return signature;
}
```

### 5.2 Replay Attack Prevention

```http
X402-Nonce: 1234567890
X402-Timestamp: 1704067200
```

Server MUST:
- Reject requests with used nonces
- Reject requests older than 5 minutes

### 5.3 Rate Limiting

```http
X402-Rate-Limit: 100/hour
X402-Rate-Remaining: 73
X402-Rate-Reset: 1704070800
```

### 5.4 HTTPS Only

X402 MUST use HTTPS. Plain HTTP is forbidden for payment operations.

---

## 6. Error Handling

### 6.1 Error Response Format

```http
HTTP/1.1 402 Payment Required
Content-Type: application/json
X402-Error-Code: conditions_not_met
X402-Error-Message: Service uptime below threshold

{
  "error": {
    "code": "conditions_not_met",
    "message": "Service uptime below threshold",
    "details": {
      "required_uptime": 0.99,
      "actual_uptime": 0.97
    },
    "retry_after": 3600
  }
}
```

### 6.2 Error Codes

| Code | Meaning |
|------|---------|
| `conditions_not_met` | Contract conditions not satisfied |
| `invalid_signature` | Signature verification failed |
| `insufficient_funds` | Payer lacks funds |
| `oracle_unreachable` | Cannot verify conditions |
| `network_congestion` | Blockchain network congested |
| `rate_limit_exceeded` | Too many requests |
| `contract_expired` | Contract term ended |
| `payment_disputed` | Active dispute exists |

---

## 7. Webhooks

### 7.1 Webhook Events

```http
POST https://api.example.com/webhooks/payment
Content-Type: application/json
X402-Event: payment.completed
X402-Signature: 0xwebhook_signature...

{
  "event": "payment.completed",
  "timestamp": "2024-01-01T00:00:00Z",
  "contract_id": "smart402:saas:abc123",
  "payment": {
    "amount": 99.00,
    "token": "USDC",
    "network": "Polygon",
    "transaction_hash": "0x987654...",
    "block_number": 12345678,
    "confirmations": 12
  }
}
```

### 7.2 Webhook Event Types

- `payment.authorized` - Payment approved, not yet executed
- `payment.executed` - Transaction sent to blockchain
- `payment.confirmed` - Transaction confirmed on-chain
- `payment.failed` - Payment failed
- `dispute.opened` - Dispute initiated
- `dispute.resolved` - Dispute settled

---

## 8. Implementation Guide

### 8.1 Client Implementation

```javascript
const Smart402 = require('@smart402/sdk');

// Create client
const client = new Smart402.Client({
  privateKey: process.env.PRIVATE_KEY,
  network: 'Polygon'
});

// Make X402 request
const response = await client.request({
  url: 'https://vendor.example.com/api/service',
  contract: 'smart402:saas:abc123',
  method: 'POST',
  body: { action: 'access_service' }
});

// Payment executed automatically if conditions met
console.log('Payment status:', response.paymentStatus);
console.log('Transaction:', response.transactionHash);
```

### 8.2 Server Implementation

```javascript
const express = require('express');
const Smart402 = require('@smart402/sdk');

const app = express();
const x402 = new Smart402.Server({
  contracts: './contracts/',
  oracles: ['chainlink', 'custom'],
  network: 'Polygon'
});

// X402 middleware
app.use(x402.middleware());

// Protected endpoint
app.post('/api/service', x402.requirePayment(), async (req, res) => {
  // This only runs if payment successful
  const service = await provideService(req.user);

  res.json({
    status: 'success',
    service: service,
    payment: req.x402.payment
  });
});
```

---

## 9. Testing

### 9.1 Test Server

```bash
npm install -g @smart402/x402-test-server

x402-test-server --port 3000 --network testnet
```

### 9.2 Test Client

```javascript
const { testX402 } = require('@smart402/testing');

testX402()
  .makeRequest('http://localhost:3000/api/service')
  .withContract('smart402:saas:test123')
  .expectPaymentAuthorized()
  .expectTransactionHash()
  .run();
```

---

## 10. Examples

### 10.1 Monthly Subscription

```http
POST /api/monthly-access HTTP/1.1
Host: saas.example.com
X402-Contract-ID: smart402:saas:monthly-99
X402-Payment-Amount: 99.00
X402-Payment-Token: USDC
X402-Payment-Frequency: monthly
X402-Settlement-Network: Polygon
X402-Conditions-Met: true
```

### 10.2 One-Time Payment

```http
POST /api/purchase HTTP/1.1
Host: shop.example.com
X402-Contract-ID: smart402:purchase:product-abc
X402-Payment-Amount: 49.99
X402-Payment-Token: USDC
X402-Payment-Frequency: one-time
X402-Settlement-Network: Polygon
```

### 10.3 Escrow Payment

```http
POST /api/escrow/create HTTP/1.1
Host: freelance.example.com
X402-Contract-ID: smart402:freelance:project-123
X402-Payment-Amount: 5000.00
X402-Payment-Token: USDC
X402-Escrow-Address: 0xEscrow...
X402-Dispute-Resolution: multisig-2-of-3
```

---

## 11. Compliance Checklist

- [ ] All required headers present
- [ ] HTTPS only
- [ ] Valid signature on payment requests
- [ ] Nonce for replay protection
- [ ] Oracle confirmations attached
- [ ] Error handling implemented
- [ ] Webhook endpoints secured
- [ ] Rate limiting enforced
- [ ] Settlement confirmed on-chain

---

## 12. Future Extensions

### Version 1.1 (Planned)
- Multi-token payments
- Cross-chain atomic swaps
- Streaming payments
- Subscription management

### Version 2.0 (Research)
- Privacy-preserving payments (ZK proofs)
- AI agent negotiation
- Dynamic pricing
- Quantum-resistant signatures

---

## References

- [HTTP/1.1 RFC 7231](https://tools.ietf.org/html/rfc7231)
- [ERC-20 Token Standard](https://eips.ethereum.org/EIPS/eip-20)
- [JSON-RPC Ethereum API](https://ethereum.org/en/developers/docs/apis/json-rpc/)

---

**X402: The Payment Layer for HTTP**

*Making every HTTP request potentially a commercial transaction.*
