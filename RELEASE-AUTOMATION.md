# DevKit Release Automation

This document explains the release automation tools created to streamline the DevKit release process.

## Overview

The release process for DevKit has been automated with scripts that handle everything from version bumping to creating GitHub releases. These scripts ensure consistency across releases and reduce manual steps.

## Scripts

### 1. `release.sh`

This comprehensive script automates the entire release process in one go.

**Usage:**
```bash
./release.sh [version_type] [registry] [push_to_registry] [create_github_release] [run_regression] [regression_env]
```

**Arguments:**
- `version_type`: The type of release (patch, minor, major). Defaults to "patch".
- `registry`: The Docker registry to use. Defaults to "localhost:5000".
- `push_to_registry`: Whether to push to the registry (true/false). Defaults to "true".
- `create_github_release`: Whether to create a GitHub release (true/false). Defaults to "false".
- `run_regression`: Whether to run regression tests (true/false). Defaults to "true".
- `regression_env`: Environment for regression tests (development/staging/production). Defaults to "production".

**Example:**
```bash
# Create a minor release, push to registry, and run regression tests
./release.sh minor localhost:5000 true false true production

# Create a patch release without regression tests
./release.sh patch ghcr.io/philip-walsh/devkit true true false
```

**Steps Performed:**
1. Bumps the version according to semantic versioning
2. Updates CHANGELOG.md with a template for the new version
3. Builds and tests the Docker image
4. Pushes the Docker image to the registry (if requested)
5. Creates a Git tag for the release
6. Updates RELEASES.md with details about the release
7. Commits all changes
8. Pushes changes and tag to the repository
9. Runs verification tests using test-release.sh
10. Runs comprehensive regression tests (if requested)
11. Creates a GitHub release (if requested and GitHub CLI is installed)

### 2. `test-release.sh`

This script verifies that a released Docker image works correctly.

**Usage:**
```bash
./test-release.sh [registry] [version]
```

**Arguments:**
- `registry`: The Docker registry to use. Defaults to "localhost:5000".
- `version`: The version to test. Defaults to the current version from DevKit.

**Example:**
```bash
# Test the local registry image for version 1.0.7
./test-release.sh localhost:5000 1.0.7

# Test a GitHub Container Registry image
./test-release.sh ghcr.io/philip-walsh/devkit 1.0.7
```

**Tests Performed:**
1. Pulls the specified Docker image
2. Verifies the version command works and returns the correct version
3. Checks that the health endpoint responds with "OK"
4. Ensures the notification system works properly

### 3. `setup-release-tools.sh`

This script sets up all the necessary tools for the release process.

**Usage:**
```bash
sudo ./setup-release-tools.sh
```

**Tools Installed:**
- Docker (for container operations)
- Syft (for SBOM generation)
- Trivy (for vulnerability scanning)
- Cosign (for container signing)
- Kyverno CLI (for policy validation)
- GitHub CLI (for GitHub releases)

### 4. Regression Testing Framework

The regression testing framework allows for comprehensive validation of releases in various environments.

**Components:**
- `regression-tests/regression-test.sh`: Main regression test script
- `regression-tests/config.yaml`: Configuration for test environments and test suites
- `regression-tests/setup-private-repo.sh`: Script to set up a private repository for testing

**Usage:**
```bash
# Run regression tests with defaults
./regression-tests/regression-test.sh

# Run regression tests with specific parameters
./regression-tests/regression-test.sh [registry] [version] [environment]
```

**Example:**
```bash
# Test version 1.0.7 in production environment
./regression-tests/regression-test.sh localhost:5000 1.0.7 production
```

## Workflow for Future Releases

1. **Setup (first time only):**
   ```bash
   # Install release tools
   sudo ./setup-release-tools.sh
   
   # Optional: Set up private regression testing repository
   ./regression-tests/setup-private-repo.sh
   ```

2. **Release Process:**
   ```bash
   # For testing locally
   docker run -d -p 5000:5000 --name registry registry:2
   
   # Create a release with regression testing
   ./release.sh patch localhost:5000 true false true production
   ```

3. **GitHub Release:**
   Either set `create_github_release` to `true` in the release.sh command, or manually create a GitHub release following the instructions in GITHUB-RELEASE-INSTRUCTIONS.md.

## Benefits

- **Consistency**: Ensures all releases follow the same process
- **Time-saving**: Automates repetitive tasks
- **Error reduction**: Minimizes manual errors
- **Documentation**: Automatically updates version information in documentation
- **Verification**: Tests releases automatically to ensure they work properly
- **Regression Testing**: Validates functionality across multiple environments

## Troubleshooting

If you encounter issues with the release process:

1. Check the Docker registry is running and accessible
2. Verify that Git credentials are configured correctly
3. Ensure all required tools are installed (run setup-release-tools.sh)
4. Check for errors in the CHANGELOG.md or RELEASES.md formatting
5. Verify that the Docker image builds and tests correctly in isolation
6. For regression test failures, check the test logs in regression-tests/results/
7. Ensure the test environment configuration in config.yaml is correct 