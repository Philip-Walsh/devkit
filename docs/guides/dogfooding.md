# Eating Your Own Dog Food: Using DevKit to Manage DevKit

This guide demonstrates how the DevKit team uses DevKit to manage itself - a software development best practice known as "eating your own dog food" or "dogfooding."

## Why Use DevKit to Manage DevKit?

1. **Real-world validation**: We encounter the same issues our users might face
2. **User experience improvements**: Directly experiencing pain points leads to better solutions 
3. **Feature discovery**: Using our own tool reveals missing functionality
4. **Quality assurance**: If we can't effectively use DevKit to manage itself, our users likely can't either
5. **Dogfooding as documentation**: Our self-usage patterns become living documentation

## Setting Up DevKit for Self-Management

```bash
# Clone the DevKit repository
git clone https://github.com/yourusername/devkit.git
cd devkit

# Install DevKit in development mode
pip install -e .

# Initialize DevKit within its own repository
devkit init --project-type python
```

## Version Management

```bash
# Check current version
devkit version current
# Output: Current version: 1.1.0

# Bump to next patch version
devkit version bump patch --tag-message "Bug fix release" --push
# Output: ✅ Version bumped to 1.1.1
#         ✅ Pushed tag v1.1.1

# Or create a minor version
devkit version bump minor --tag-message "New features release" --push
# Output: ✅ Version bumped to 1.2.0
#         ✅ Pushed tag v1.2.0
```

## Building & Publishing Docker Images

```bash
# Build a secure Docker image of DevKit
devkit docker secure --dockerfile Dockerfile --push

# Or step by step:
devkit docker build
devkit docker scan devkit:1.1.0
devkit docker sbom devkit:1.1.0 --output-file sbom.json
devkit docker tag devkit:1.1.0 ghcr.io/philip-walsh/devkit:1.1.0 --push
```

## Setting Up Git Hooks

DevKit uses its own Git hooks functionality to maintain code quality:

```bash
# Initialize Git hooks
devkit hooks install

# Enable specific hooks
devkit hooks enable pre-commit
devkit hooks enable pre-push
devkit hooks enable commit-msg

# Configure hooks for Python projects
devkit hooks config --language python

# Add custom pre-commit actions
devkit hooks add pre-commit "black ."
devkit hooks add pre-commit "pytest tests/unit"
devkit hooks add pre-commit "devkit security scan-deps"
```

This creates a `.devkitrc` file similar to:

```json
{
  "hooks": {
    "pre-commit": [
      "devkit format",
      "pytest"
    ],
    "pre-push": [
      "devkit docker scan $(devkit version current)"
    ],
    "post-tag": [
      "devkit docker secure --push"
    ]
  }
}
```

## Security Self-Testing

DevKit uses its own security features to validate itself:

```bash
# Scan DevKit's own dependencies
devkit security scan-deps

# Analyze DevKit's code for security issues
devkit security analyze-code

# Validate DevKit against security standards
devkit security validate --standard OWASP-TOP10

# Apply Kyverno policies to DevKit's own container
devkit k8s validate --policy kyverno-policies/secure-container-policy.yaml --resource Dockerfile

# Apply policies to DevKit's Kubernetes deployments
devkit k8s apply-policies --dir kyverno-policies/ --namespace devkit
```

## Automated Release Process

DevKit has automated its own release process with a script that uses DevKit commands:

```bash
#!/bin/bash
set -e

# Automated release script using DevKit CLI
echo "Starting DevKit release process..."

# 1. Bump version
VERSION_TYPE=${1:-"patch"} # Default to patch, can override with argument
echo "Bumping $VERSION_TYPE version..."
NEW_VERSION=$(devkit version bump $VERSION_TYPE --tag-message "Release $VERSION_TYPE version" --push)
echo "New version: $NEW_VERSION"

# 2. Build and publish Docker image
echo "Building secure Docker image..."
devkit docker secure \
  --tag $NEW_VERSION \
  --tag latest \
  --scan \
  --sign \
  --push

# 3. Validate Kubernetes manifests 
echo "Validating Kubernetes manifests..."
devkit k8s validate --policy kyverno-policies/secure-container-policy.yaml

# 4. Update changelog
echo "Updating changelog..."
devkit changelog update --version $NEW_VERSION

# 5. Create GitHub release
echo "Creating GitHub release..."
devkit github release create \
  --tag v$NEW_VERSION \
  --name "DevKit $NEW_VERSION" \
  --body "$(devkit changelog get --version $NEW_VERSION)" \
  --draft false

echo "Release $NEW_VERSION completed successfully!" 
```

## Using DevKit in CI/CD

DevKit integrates with its own CI/CD pipelines:

```yaml
# Excerpt from .github/workflows/ci-cd.yml
jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install DevKit
        run: pip install .
      - name: Run security checks
        run: devkit security full-scan
  
  build-container:
    runs-on: ubuntu-latest
    needs: security-scan
    steps:
      - uses: actions/checkout@v3
      - name: Build secure container
        run: devkit container build-secure --tag ${{ github.sha }}
```

## Project Structure Compatibility

DevKit has been designed to support various project structures, including its own:

### Monorepo Structure
```
devkit/
├── components/
│   ├── cli/           # Command-line interface
│   ├── container/     # Container management
│   ├── k8s/           # Kubernetes integration
│   └── security/      # Security scanning
├── .github/workflows/ # CI/CD pipelines
└── scripts/           # Utility scripts
```

### Single Package Structure
```
devkit/
├── devkit/           # Main package code
│   ├── __init__.py
│   ├── cli.py
│   ├── security.py
│   └── container.py
├── tests/            # Test suite
└── setup.py          # Package definition
```

## Real-World Examples from the DevKit Team

### Example 1: Container build optimization

We used DevKit to analyze our own container build process:

```bash
devkit container analyze-build
```

This identified several optimizations that reduced our container size by 32%.

### Example 2: Dependency management

We use DevKit to analyze and update our own dependencies:

```bash
devkit deps analyze
devkit deps update --security-only
```

### Example 3: Custom Git Hooks

We've set up specialized Git hooks for our own development workflow:

```bash
# Our pre-commit hook content
#!/bin/bash
set -e

echo "Running DevKit pre-commit hooks..."

# Run security checks
devkit security lint --path .

# Run SAST analysis
devkit security sast --path . --severity high

# Lint code
devkit lint python --path .

# Run tests
devkit test run --unittest

echo "All pre-commit checks passed!"
```

## Benefits We've Experienced

By using DevKit on itself, we've experienced:

1. **Consistent Development Environment**: All team members use the same checks and workflows
2. **Faster Releases**: Automation reduced our release time from days to hours
3. **Better Security**: Continuous scanning catches issues before they reach production
4. **Documentation Through Code**: Examples in our codebase serve as living documentation
5. **Improved Quality**: Pre-commit hooks ensure code quality from the start

## Lessons Learned from Dogfooding

1. **Command UX matters**: If a command feels awkward for us, it's awkward for users
2. **Error messages are critical**: Clear errors save development time
3. **Default values matter**: Good defaults reduce friction
4. **Documentation is never enough**: Tools should be intuitive beyond docs
5. **Cross-platform testing is essential**: We use DevKit on the same platforms as our users

## Implementing Your Own Dogfooding Strategy

1. Start using DevKit to manage your project as early as possible
2. Track pain points during usage
3. Prioritize fixing issues you encounter during dogfooding
4. Rotate responsibilities among team members
5. Use dogfooding sessions to onboard new team members

By consistently using DevKit to manage its own development, we ensure the tool remains practical, user-friendly, and capable of handling real-world development challenges. 