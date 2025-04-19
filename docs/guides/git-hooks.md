# DevKit Git Hooks Guide

Git hooks allow you to run scripts before or after Git events like commit, push, or merge. DevKit simplifies hooks management through a dedicated CLI interface.

## Available Hooks

DevKit supports all standard Git hooks:

| Hook | Description |
|------|-------------|
| `pre-commit` | Run before commit is created |
| `prepare-commit-msg` | Customize default commit message |
| `commit-msg` | Validate commit messages |
| `post-commit` | Run after commit is created |
| `pre-push` | Run before push happens |
| `post-merge` | Run after merge completes |
| `pre-rebase` | Run before rebase begins |

## Basic Usage

```bash
# Install all default DevKit hooks
devkit hooks install

# Install only specific hooks
devkit hooks install pre-commit commit-msg

# Uninstall hooks
devkit hooks uninstall

# List active hooks
devkit hooks list
```

## Creating Custom Hooks

```bash
# Create a new hook (creates a template script)
devkit hooks create pre-commit

# Edit a hook with your editor
devkit hooks edit pre-commit

# Test a hook manually
devkit hooks test pre-commit
```

## Hook Configuration

DevKit hooks can be configured through the CLI or directly in `.devkit.yaml`:

```bash
# Set a hook to run linting and tests
devkit hooks configure pre-commit --command "devkit lint && devkit test"

# Configure the commit-msg hook to enforce a pattern
devkit hooks configure commit-msg --pattern "^(feat|fix|docs|style|refactor|test|chore)(\(.+\))?: .+"

# Skip hooks temporarily
git commit --no-verify
# OR
devkit hooks disable pre-commit
```

Example `.devkit.yaml` hooks configuration:

```yaml
hooks:
  pre-commit:
    commands:
      - devkit lint
      - devkit test
    on_failure: block
  commit-msg:
    pattern: "^(feat|fix|docs|style|refactor|test|chore)(\\(.+\\))?: .+"
    error_message: "Commit message must follow conventional commits format"
  pre-push:
    commands:
      - devkit security scan-deps
    on_failure: prompt
```

## Project-Specific Hook Configurations

### Python Projects

```bash
# Configure hooks for Python
devkit hooks config --language python

# Add custom pre-commit actions
devkit hooks add pre-commit "black ."
devkit hooks add pre-commit "pytest tests/unit"
```

This creates a configuration that:
- Runs Black formatter on all Python files
- Executes unit tests before allowing commit
- Checks for security issues in dependencies

### JavaScript/TypeScript Projects

```bash
# Configure hooks for JavaScript/TypeScript
devkit hooks config --language javascript

# Add ESLint and Prettier checks
devkit hooks add pre-commit "npm run lint"
devkit hooks add pre-commit "npm run format"
```

### Go Projects

```bash
# Configure hooks for Go
devkit hooks config --language go

# Add custom actions
devkit hooks add pre-commit "go fmt ./..."
devkit hooks add pre-commit "golangci-lint run"
```

## Practical Examples

### Example 1: Code Quality Hook

```bash
devkit hooks configure pre-commit --command "devkit lint && devkit format-check && devkit test-quick"
```

This pre-commit hook ensures code passes linting, is properly formatted, and passes critical tests.

### Example 2: Enforcing Commit Message Standards

```bash
devkit hooks configure commit-msg --pattern "^(feat|fix|docs|style|refactor|test|chore)(\(.+\))?: .+" --error-message "Please follow conventional commits format"
```

This commit-msg hook enforces conventional commits format.

### Example 3: Security Scanning Before Push

```bash
devkit hooks configure pre-push --command "devkit security scan-deps --severity high" --on-failure prompt
```

This pre-push hook scans for high-severity vulnerabilities and prompts the user if any are found.

### Example 4: Integration Testing on Merge

```bash
devkit hooks configure post-merge --command "devkit test-integration"
```

This post-merge hook runs integration tests automatically after merging changes.

## Integration with Different Project Structures

DevKit adapts to various project structures:

### Monorepo Support

```bash
# Configure DevKit for a monorepo
devkit init --monorepo
devkit hooks configure --monorepo-paths "service-a,service-b,libraries"
```

### Microservices Architecture

```bash
# Run checks only on changed services
devkit hooks configure --detect-changes
```

### Monorepos With Multiple Languages

For monorepos with multiple languages, DevKit provides path-specific hooks:

```bash
# Set up language-specific hooks in subdirectories
devkit hooks config --language python --path backend/
devkit hooks config --language javascript --path frontend/
devkit hooks config --language go --path services/

# Add global hooks for the entire repository
devkit hooks add pre-push "echo Running tests across all components..."
devkit hooks add pre-push "./scripts/run-all-tests.sh"
```

## Hook Templates

DevKit provides templates for common hook scenarios:

```bash
# List available hook templates
devkit hooks templates list

# Apply a template
devkit hooks template apply conventional-commits

# Available templates include:
# - conventional-commits: Enforce conventional commit messages
# - quality-checks: Lint, format, and test code
# - security-scan: Check for security issues
# - dependency-check: Ensure dependencies are updated
```

## Team Collaboration with Hooks

For team environments:

```bash
# Generate hook documentation
devkit hooks docs

# Share hooks with the team
devkit hooks export > team-hooks.json
devkit hooks import team-hooks.json

# Enable automatic hook updates
devkit hooks configure --auto-update
```

## Best Practices

1. **Keep hooks fast**: Long-running hooks disrupt workflow
2. **Make hooks meaningful**: Only block commits for important issues
3. **Test hooks thoroughly**: Broken hooks cause frustration
4. **Provide clear error messages**: Help developers fix issues
5. **Document custom hooks**: Make sure the team understands the purpose
6. **Use the `--on-failure` option**: Choose between block, prompt, or warn
7. **Consider CI integration**: Some checks belong in CI, not hooks

## Troubleshooting

```bash
# Debug hooks
devkit hooks test pre-commit --debug

# View hook logs
devkit hooks logs

# Reset hooks to default
devkit hooks reset
```

## Advanced Configuration

```yaml
# .devkit.yaml advanced hooks configuration
hooks:
  pre-commit:
    commands:
      - command: devkit lint
        paths: ["*.py", "*.js"]
        on_failure: block
      - command: devkit test-quick
        paths: ["tests/unit/**/*.py"]
        on_failure: prompt
    skip_if_empty: true
    timeout: 30  # seconds
    run_in_ci: false
```

By leveraging DevKit's Git hooks, you can automate quality checks, enforce standards, and improve overall code quality with minimal disruption to your development workflow. 