# DevKit Project Compatibility Guide

DevKit is designed to work with various project structures and technology stacks. This guide explains how to use DevKit with different types of projects.

## Supported Project Types

DevKit provides built-in support for several project types:

| Project Type | Description | Key Features |
|--------------|-------------|--------------|
| Python | Python applications and packages | Virtual environment management, dependency analysis, testing tools |
| JavaScript/Node.js | JavaScript and Node.js applications | Package management, testing, security scanning |
| Container | Container-based applications | Image building, scanning, policy enforcement |
| Go | Go applications and services | Dependency management, testing, build optimization |
| Java | Java applications and services | Build tools, dependency management, testing |
| Multi-component | Microservices or multi-language projects | Cross-service management, integrated workflows |

## Initializing Different Project Types

```bash
# Python project
devkit init --project-type python

# JavaScript/Node.js project
devkit init --project-type javascript

# Container-based project
devkit init --project-type container

# Go project
devkit init --project-type go

# Java project
devkit init --project-type java

# Multi-component project
devkit init --project-type multi-component
```

## Project Structure Detection

DevKit automatically detects your project type based on files in your repository:

- **Python**: Presence of `requirements.txt`, `setup.py`, `pyproject.toml`
- **JavaScript**: Presence of `package.json`
- **Container**: Presence of `Dockerfile` or `docker-compose.yml`
- **Go**: Presence of `go.mod`
- **Java**: Presence of `pom.xml` or `build.gradle`

You can override the automatic detection:

```bash
devkit init --project-type python --force
```

## Customizing for Your Project Structure

### Configuration

Create a `.devkit.yaml` file to customize DevKit's behavior for your project:

```yaml
project:
  type: python
  name: my-project
  structure:
    # Define custom locations for project artifacts
    tests: custom/test/location
    docs: custom/docs/location
    source: src/custom/location

hooks:
  # Define custom hook behavior based on file types
  pre-commit:
    python: "black {file} && pylint {file}"
    javascript: "eslint {file}"

workflows:
  ci:
    template: custom-template.yml
```

### Project-Specific Commands

#### Python Projects

```bash
# Create a virtual environment
devkit python venv create

# Install dependencies
devkit python deps install

# Run tests
devkit python test run
```

#### JavaScript Projects

```bash
# Install dependencies
devkit js deps install

# Run linting
devkit js lint

# Run tests
devkit js test run
```

#### Container Projects

```bash
# Build container with optimizations
devkit container build --optimize

# Apply security policies
devkit container apply-policies

# Run container tests
devkit container test
```

## Supporting Legacy Project Structures

DevKit can be configured to work with legacy or non-standard project structures:

```bash
# Create a custom project adapter
devkit create adapter --name legacy-java-project

# Configure the adapter
devkit configure adapter --name legacy-java-project --source-path old/src --test-path legacy/tests
```

## Multi-Language Projects

For projects that use multiple languages or technologies:

```bash
# Initialize as a multi-component project
devkit init --project-type multi-component

# Add components
devkit component add --name api --type python --path ./api
devkit component add --name frontend --type javascript --path ./frontend
devkit component add --name database --type container --path ./database

# Run operations across all components
devkit run-all test
devkit run-all lint
devkit run-all build
```

## Sample Project Structures

DevKit works with various project structures, including:

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

### Microservices Structure
```
services/
├── devkit-api/        # DevKit API service
├── devkit-scanner/    # Vulnerability scanner service
├── devkit-builder/    # Container builder service
└── devkit-dashboard/  # Web UI service
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

## Custom Project Types

You can define entirely custom project types:

```bash
# Create a custom project type
devkit project-type create --name custom-framework

# Define project type behaviors
devkit project-type configure --name custom-framework --build-command "custom-tool build" --test-command "custom-tool test"

# Initialize with custom project type
devkit init --project-type custom-framework
```

## Compatibility Mode

For projects that can't be fully integrated with DevKit:

```bash
# Initialize in compatibility mode
devkit init --compatibility-mode

# Use shell pass-through for custom commands
devkit run "your-custom-build-tool --with-args"
```

## DevKit "Dogfooding" Configuration

Here's an example of how DevKit uses its own tools on itself (eating its own dog food):

```yaml
# .devkit.yaml example from DevKit's own repository
project:
  name: devkit
  description: A CLI tool for development workflow automation

git:
  hooks:
    pre-commit:
      - name: python-lint
        command: "black . && isort . && flake8"
      - name: security-check
        command: "bandit -r ."
    commit-msg:
      - name: conventional-commits
        command: ".devkit/scripts/validate-commit-msg.sh"

container:
  name: devkit-cli
  registry: ghcr.io/devkit-tools
  dockerfile: Dockerfile
  platforms: [linux/amd64, linux/arm64]
  
  validation:
    policies:
      - kyverno-policies/secure-container-policy.yaml
    scanners:
      - trivy
      - grype

quality:
  tools:
    - black
    - isort
    - flake8
    - mypy
    - bandit
  
release:
  versioning:
    strategy: semver
    source: git-tag
  
  artifacts:
    - type: container
      name: devkit-cli
    - type: package
      format: python
```

## Best Practices for Project Compatibility

1. **Start with a Standard Type**: Begin with the closest standard project type
2. **Customize Gradually**: Add customizations as needed rather than all at once
3. **Document Custom Settings**: Add comments to your `.devkit.yaml` file
4. **Use Component Approach**: Break down complex projects into manageable components
5. **Test Workflows**: Validate that DevKit operations work on all parts of your project 