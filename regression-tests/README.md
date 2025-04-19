# DevKit Regression Testing Framework

This directory contains tools for comprehensive regression testing of DevKit releases. These tools are designed to be run in a private repository to verify core functionalities before public releases.

## Overview

The regression testing framework allows you to:

1. Test core APIs and functionality
2. Verify backward compatibility
3. Run performance benchmarks
4. Perform integration tests
5. Check security and compliance

## Components

- **regression-test.sh**: Main script for running all regression tests
- **config.yaml**: Configuration file for test environments and suites
- **setup-private-repo.sh**: Script to set up a private testing repository

## Usage

### Setting Up Private Testing Repository

```bash
# Create a private repository for regression testing
./regression-tests/setup-private-repo.sh [public_repo_url] [private_repo_url] [branch_name]

# Example
./regression-tests/setup-private-repo.sh \
  https://github.com/Philip-Walsh/devkit.git \
  git@github.com:yourusername/devkit-private-testing.git \
  regression-testing
```

### Running Regression Tests

```bash
# Run regression tests with default settings
./regression-tests/regression-test.sh

# Run tests against a specific version in a specific registry
./regression-tests/regression-test.sh localhost:5000 1.0.7 production

# Arguments:
# $1 - Registry (default: localhost:5000)
# $2 - Version (default: current version)
# $3 - Test environment (default: production)
```

### Adding Regression Testing to Release Process

You can modify the `release.sh` script to include regression testing:

```bash
# Add to release.sh arguments
RUN_REGRESSION=${7:-"true"}
TEST_ENV=${8:-"production"}

# Add a step for regression testing
if [ "$RUN_REGRESSION" = "true" ]; then
  echo "Step X: Running regression tests..."
  ./regression-tests/regression-test.sh "$REGISTRY" "$NEW_VERSION" "$TEST_ENV"
  echo "✅ Regression tests passed"
fi
```

## Test Configuration

Edit `config.yaml` to customize:

- Registry settings
- Test environments
- Test suites
- Notification settings

## Continuous Integration

For automated testing, set up GitHub Actions in your private repository:

```yaml
# .github/workflows/regression.yml
name: Regression Tests
on:
  push:
    branches: [regression-testing]
  workflow_dispatch:
jobs:
  regression:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run regression tests
        run: ./regression-tests/regression-test.sh localhost:5000 latest development
```

## Best Practices

1. Always run regression tests before public releases
2. Keep the private repository updated with the latest public code
3. Add new tests as new features are developed
4. Verify fixes for reported bugs with dedicated test cases
