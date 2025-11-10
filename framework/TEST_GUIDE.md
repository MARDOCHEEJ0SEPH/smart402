# Smart402 Testing Guide

Comprehensive testing documentation for all Smart402 SDKs.

## Overview

Smart402 includes comprehensive test suites for all three SDKs:
- **JavaScript**: Jest-based testing framework
- **Python**: pytest-based testing framework
- **Rust**: Built-in Rust testing framework

All test suites cover the same functionality to ensure consistency across languages.

## Test Coverage

Each SDK test suite covers:

### Core Functionality
- ✅ Contract creation
- ✅ Template usage
- ✅ Unique ID generation
- ✅ Field validation

### AEO (Answer Engine Optimization)
- ✅ Score calculation (5 dimensions)
- ✅ JSON-LD generation
- ✅ Metadata optimization
- ✅ SEO integration

### LLMO (Large Language Model Optimization)
- ✅ Contract validation
- ✅ Plain-English explanations
- ✅ Multi-target compilation (Solidity, JavaScript, Rust)
- ✅ Error detection

### X402 Protocol
- ✅ Header generation
- ✅ Nonce uniqueness
- ✅ Signature creation
- ✅ Payment flow

### Deployment
- ✅ Testnet deployment
- ✅ Mainnet deployment
- ✅ Receipt generation
- ✅ Gas estimation

### Monitoring
- ✅ Condition checking
- ✅ Payment execution
- ✅ Auto-monitoring

### Export/Import
- ✅ YAML export/import
- ✅ JSON export/import
- ✅ Data integrity

### Error Handling
- ✅ Invalid inputs
- ✅ Missing fields
- ✅ Boundary conditions

## Running Tests

### JavaScript SDK

```bash
cd framework/sdk/javascript

# Install dependencies
npm install

# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Watch mode
npm run test:watch

# Run specific test file
npm test -- smart402.test.js
```

**Expected Output:**
```
PASS  tests/smart402.test.js
  Smart402 SDK
    Contract Creation
      ✓ should create a basic SaaS subscription contract (45ms)
      ✓ should create contract from template (32ms)
      ✓ should validate required fields (12ms)
      ✓ should generate unique contract IDs (28ms)
    AEO
      ✓ should calculate AEO score (18ms)
      ✓ should generate JSON-LD markup (15ms)
      ...

Test Suites: 1 passed, 1 total
Tests:       45 passed, 45 total
Coverage:    92.5%
```

### Python SDK

```bash
cd framework/sdk/python

# Install dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run with coverage
pytest --cov=smart402 --cov-report=html

# Run specific test class
pytest tests/test_smart402.py::TestAEO

# Run specific test
pytest tests/test_smart402.py::TestAEO::test_calculate_aeo_score

# Verbose output
pytest -v

# Show print statements
pytest -s
```

**Expected Output:**
```
============================= test session starts ==============================
collected 45 items

tests/test_smart402.py::TestContractCreation::test_create_basic_contract PASSED [2%]
tests/test_smart402.py::TestContractCreation::test_create_from_template PASSED [4%]
tests/test_smart402.py::TestContractCreation::test_validate_required_fields PASSED [6%]
...

============================== 45 passed in 3.42s ===============================

----------- coverage: platform linux, python 3.10.0 -----------
Name                            Stmts   Miss  Cover
---------------------------------------------------
smart402/__init__.py               12      0   100%
smart402/core/smart402.py         145      8    94%
smart402/core/contract.py         178     12    93%
smart402/aeo/engine.py             89      4    95%
smart402/llmo/engine.py           102      6    94%
smart402/x402/client.py            76      3    96%
---------------------------------------------------
TOTAL                             602     33    95%
```

### Rust SDK

```bash
cd framework/sdk/rust

# Run all tests
cargo test

# Run with output
cargo test -- --nocapture

# Run specific test
cargo test test_create_basic_contract

# Run integration tests only
cargo test --test integration_tests

# Run with coverage (requires tarpaulin)
cargo tarpaulin --out Html

# Release mode
cargo test --release
```

**Expected Output:**
```
running 30 tests
test test_create_basic_contract ... ok
test test_create_from_template ... ok
test test_unique_contract_ids ... ok
test test_calculate_aeo_score ... ok
test test_generate_jsonld ... ok
test test_validate_contract ... ok
test test_generate_explanation ... ok
test test_compile_to_solidity ... ok
test test_compile_to_javascript ... ok
test test_compile_to_rust ... ok
test test_generate_x402_headers ... ok
test test_deploy_to_testnet ... ok
test test_check_conditions ... ok
test test_execute_payment ... ok
test test_export_yaml ... ok
test test_export_json ... ok
test test_list_templates ... ok
test test_invalid_payment_amount ... ok
test test_contract_summary ... ok
test test_aeo_score_improvement_with_metadata ... ok
test test_validation_errors ... ok
test test_x402_unique_nonce ... ok
...

test result: ok. 30 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out

Coverage: 94.2%
```

## Test Structure

### JavaScript Tests (`tests/smart402.test.js`)
```javascript
describe('Smart402 SDK', () => {
  describe('Contract Creation', () => {
    test('should create a basic contract', async () => {
      // Test implementation
    });
  });

  describe('AEO', () => {
    test('should calculate AEO score', () => {
      // Test implementation
    });
  });
});
```

### Python Tests (`tests/test_smart402.py`)
```python
class TestContractCreation:
    @pytest.mark.asyncio
    async def test_create_basic_contract(self):
        # Test implementation

class TestAEO:
    @pytest.fixture
    async def contract(self):
        # Fixture setup

    @pytest.mark.asyncio
    async def test_calculate_aeo_score(self, contract):
        # Test implementation
```

### Rust Tests (`tests/integration_tests.rs`)
```rust
#[tokio::test]
async fn test_create_basic_contract() -> Result<()> {
    // Test implementation
    Ok(())
}

#[tokio::test]
async fn test_calculate_aeo_score() -> Result<()> {
    // Test implementation
    Ok(())
}
```

## Continuous Integration

### GitHub Actions Workflow

Create `.github/workflows/test.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test-javascript:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: cd framework/sdk/javascript && npm install
      - run: cd framework/sdk/javascript && npm test

  test-python:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - run: cd framework/sdk/python && pip install -e ".[dev]"
      - run: cd framework/sdk/python && pytest

  test-rust:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions-rs/toolchain@v1
        with:
          toolchain: stable
      - run: cd framework/sdk/rust && cargo test
```

## Test Data

All tests use consistent test data:

**Test Contract:**
```yaml
type: saas-subscription
parties:
  - vendor@example.com
  - customer@example.com
payment:
  amount: 99
  token: USDC
  blockchain: polygon
  frequency: monthly
```

**Test Networks:**
- Testnet: `polygon-mumbai`
- Mainnet: `polygon`

## Mocking

Tests use mocking for external dependencies:

- **Blockchain calls**: Simulated deployment and transactions
- **API calls**: Mocked condition checking
- **Time-based operations**: Controlled timestamps

## Coverage Goals

Target coverage for each SDK:
- **Overall**: > 90%
- **Core modules**: > 95%
- **Critical paths**: 100%

## Performance Benchmarks

Expected test execution times:
- **JavaScript**: < 5 seconds
- **Python**: < 8 seconds
- **Rust**: < 10 seconds (first run), < 3 seconds (cached)

## Troubleshooting

### JavaScript

**Issue**: Tests fail with module not found
```bash
npm install
npm run build
```

**Issue**: Async tests timeout
```javascript
// Increase timeout in jest.config.js
testTimeout: 10000
```

### Python

**Issue**: Import errors
```bash
pip install -e ".[dev]"
```

**Issue**: Async warnings
```python
# Add to pytest.ini
asyncio_mode = auto
```

### Rust

**Issue**: Compilation errors
```bash
cargo clean
cargo test
```

**Issue**: Test timeout
```rust
#[tokio::test(flavor = "multi_thread")]
async fn long_running_test() { }
```

## Writing New Tests

### Best Practices

1. **Descriptive names**: Use clear, descriptive test names
2. **Single responsibility**: One assertion per test when possible
3. **Setup/Teardown**: Use fixtures/beforeEach for common setup
4. **Assertions**: Test both success and failure cases
5. **Independence**: Tests should not depend on each other

### Example Test Template

**JavaScript:**
```javascript
test('should do something specific', async () => {
  // Arrange
  const input = createTestInput();

  // Act
  const result = await functionUnderTest(input);

  // Assert
  expect(result).toBe(expectedValue);
});
```

**Python:**
```python
@pytest.mark.asyncio
async def test_should_do_something_specific(self):
    # Arrange
    input = create_test_input()

    # Act
    result = await function_under_test(input)

    # Assert
    assert result == expected_value
```

**Rust:**
```rust
#[tokio::test]
async fn test_should_do_something_specific() -> Result<()> {
    // Arrange
    let input = create_test_input();

    // Act
    let result = function_under_test(input).await?;

    // Assert
    assert_eq!(result, expected_value);
    Ok(())
}
```

## Resources

- [Jest Documentation](https://jestjs.io/)
- [pytest Documentation](https://docs.pytest.org/)
- [Rust Testing Guide](https://doc.rust-lang.org/book/ch11-00-testing.html)
- [Smart402 Framework Docs](https://docs.smart402.io)

## Support

For testing issues:
- GitHub Issues: https://github.com/smart402/framework/issues
- Discord: https://discord.gg/smart402
- Documentation: https://docs.smart402.io

---

**Last Updated**: 2024
**Author**: Mardochée JOSEPH
