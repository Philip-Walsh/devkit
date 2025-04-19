# DevKit Release Automation Guide

This guide demonstrates how to use DevKit to automate your release processes, including version management, container builds, and publishing artifacts.

## Basic Release Commands

```bash
# Create a new release with auto-incremented version
devkit release create

# Create a specific release type
devkit release create --type minor   # Options: major, minor, patch

# Create a release with a specific version
devkit release create --version 1.2.3

# View release history
devkit release list
```

## Release Configuration

DevKit's release automation is configured in `.devkit.yaml`:

```yaml
release:
  versioning:
    strategy: semver
    source: git-tag  # Options: git-tag, file
    file: version.txt  # If source is 'file'
  
  artifacts:
    - type: container
      name: ${PROJECT_NAME}
      registry: ghcr.io/${GITHUB_OWNER}
      platforms: [linux/amd64, linux/arm64]
      context: .
      push: true

    - type: package
      format: python  # Options: python, npm, maven, etc.
      directory: .
      publish: true
  
  notifications:
    - type: slack
      channel: releases
    - type: email
      recipients: [team@example.com]
```

## Container Release Workflow

```bash
# Build and tag a container image for the current version
devkit container build

# Build for a specific platform
devkit container build --platform linux/arm64

# Push the container to configured registries
devkit container push

# Build and push in one command
devkit container release

# Scan a container before releasing
devkit container scan && devkit container release
```

## Package Release Workflow

```bash
# Build a distributable package
devkit package build

# Publish a package
devkit package publish

# Build and publish in one command
devkit package release
```

## Git Integration

```bash
# Create a release with automatic changelog generation
devkit release create --generate-changelog

# Create a release with release notes
devkit release create --notes "Fixed critical bugs"

# Create a release with a GitHub release
devkit release create --github-release
```

## CI/CD Integration

For GitHub Actions:

```yaml
name: Release

on:
  workflow_dispatch:
    inputs:
      version_type:
        description: 'Release type (major/minor/patch)'
        default: 'patch'
        required: true

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0
      
      - name: Install DevKit
        run: pip install devkit-cli
      
      - name: Create Release
        run: devkit release create --type ${{ github.event.inputs.version_type }}
      
      - name: Build and Push Container
        run: devkit container release
      
      - name: Publish Package
        run: devkit package release
```

## Advanced Release Features

### Automatic Changelog Generation

```bash
# Generate changelog from commit history
devkit changelog generate

# Create a release with an auto-generated changelog
devkit release create --generate-changelog

# Specify changelog format
devkit changelog generate --format markdown --since v1.0.0
```

### Release Testing

```bash
# Test a release before publishing
devkit release test

# Validate release configuration
devkit release validate

# Perform a dry run
devkit release create --dry-run
```

### Multi-artifact Releases

```bash
# Release multiple artifacts
devkit release create --artifacts container,package,docs

# Release specific artifacts
devkit release create --artifacts container
```

### Rollback Capability

```bash
# List available rollback targets
devkit release rollback --list

# Rollback to previous release
devkit release rollback

# Rollback to a specific version
devkit release rollback --version 1.1.0
```

## DevKit "Dogfooding" Example

Using DevKit to manage its own releases:

```bash
# From the DevKit repository
devkit release create --type minor
devkit container release --name devkit-cli
devkit package release --repository pypi
devkit docs publish
```

This demonstrates how we "eat our own dog food" by using DevKit to manage DevKit itself.

## Release Automation Script Example

Here's an example script that automates a full release process:

```bash
#!/bin/bash
# DevKit Release Automation Example

VERSION=$1

# Validate version format using DevKit
devkit version validate --version "$VERSION" || {
    echo "❌ Invalid version format. Must be in format X.Y.Z"
    exit 1
}

echo "🚀 Starting release process for version $VERSION..."

# Run automated checks
devkit security audit --fix
devkit lint python --path .
devkit test run --all

# Create a new release branch
devkit git branch --create "release-$VERSION"

# Update version in files
devkit version bump --version "$VERSION" --files "setup.py,pyproject.toml,VERSION"

# Build and scan container
devkit container build --tag "devkit:$VERSION"
devkit security scan-image --image "devkit:$VERSION" --severity high,critical

# Validate against policies
devkit k8s validate --policy kyverno-policies/secure-container-policy.yaml

# Generate changelog
devkit changelog generate --from-latest-tag --output CHANGELOG.md

# Create GitHub release
devkit ci create-release --version "$VERSION" --changelog CHANGELOG.md --draft

# Publish container to registry
devkit container publish --image "devkit:$VERSION" --registry "ghcr.io/myorg/devkit" --tag "$VERSION"

echo "✅ Release $VERSION prepared successfully!"
```

## Best Practices

1. **Use semantic versioning**: Follow semver principles for version increments
2. **Automate changelogs**: Generate from structured commit messages
3. **Test before releasing**: Always validate releases before publishing
4. **Sign your artifacts**: Use DevKit's signing capabilities
5. **Document releases**: Create proper release notes for each version
6. **Coordinate artifacts**: Ensure all artifacts use the same version

## Troubleshooting

```bash
# Debug release issues
devkit release create --debug

# Validate release configuration
devkit release validate

# Check release status
devkit release status

# View release logs
devkit release logs
```

Using DevKit for release management streamlines the process, reduces errors, and ensures consistency across all your artifacts and environments. 