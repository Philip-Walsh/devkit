# DevKit

A Python package providing development workflow automation and Git utility functions.

## Features

- Commit message validation
- Git hook management
- Repository utilities
- CI/CD integration
- Command-line interface
- Development workflow automation
- Automated versioning and releases
- Docker image building and tagging
- Chainguard secure images integration
- Docker image testing and security scanning

## Documentation

- [ABOUT.md](ABOUT.md) - CI/CD principles and best practices
- [ROADMAP.md](ROADMAP.md) - Future development plans
- [CHANGELOG.md](CHANGELOG.md) - Version history and changes

## Installation

### Install from PyPI (Coming soon)

```bash
pip install devkit
```

### Install directly from GitHub

```bash
pip install git+https://github.com/Philip-Walsh/devkit.git
```

### Development installation

```bash
git clone https://github.com/Philip-Walsh/devkit.git
cd devkit
pip install -e .
```

## Usage

### Command Line Interface

```bash
# Create a new branch with proper naming convention
devkit create feature new-awesome-feature

# Push changes with pre-push checks
devkit push dev

# Format all code files
devkit format

# Setup development environment
devkit setup

# Check development environment status
devkit status

# Version Management
devkit version current                   # Show current version
devkit version bump patch                # Bump patch version
devkit version bump minor                # Bump minor version
devkit version bump major                # Bump major version
devkit version set 1.2.3                 # Set specific version

# Docker Image Management
devkit docker build                      # Build Docker image with current version
devkit docker build --platform linux/amd64  # Build for specific platform
devkit docker tag image-name registry/repo  # Tag Docker image with semantic versions
devkit docker tag image-name registry/repo --chainguard  # Include Chainguard tags
devkit docker test image-name            # Test that a Docker image works
devkit docker scan image-name            # Scan for vulnerabilities
devkit docker release --push --test --chainguard  # Build, test, tag, and push Docker image
```

### Docker Integration

DevKit provides comprehensive Docker support with Chainguard integration:

1. **Secure Base Images**: Uses Chainguard's minimal, secure Python images
2. **Automated Testing**: Tests Docker images before pushing to registries
3. **Security Scanning**: Scans images for vulnerabilities using Trivy
4. **Semantic Versioning**: Creates Docker tags following best practices
5. **Chainguard Tags**: Supports Chainguard's tagging conventions

Example Chainguard tags:
- `v1.0.2` - Explicit version with "v" prefix
- `1.0-chainguard` - Minor version with Chainguard suffix
- `secure` - Latest secure version

### Automated Release Workflow

This project includes a GitHub Actions workflow for automating releases:

1. Automatically bumps version (patch, minor, or major)
2. Creates Git tags with proper naming
3. Tests Docker images for functionality
4. Scans Docker images for security vulnerabilities
5. Builds Docker images with semantic versioning tags
6. Pushes Docker images to container registries
7. Creates GitHub releases with release notes

To create a release:
1. Go to the Actions tab in your GitHub repository
2. Select the "Release" workflow
3. Click "Run workflow"
4. Choose the version bump type, enable Chainguard support, and optionally add release notes
5. Click "Run workflow" to start the release process

### Python API

```python
from git_utils import CommitManager, HookManager, GitUtils

# Initialize managers
commit_mgr = CommitManager()
hook_mgr = HookManager()
git_utils = GitUtils()

# Validate commit message
commit_mgr.validate_message("feat: add new feature")

# Create commit
commit_mgr.create_commit("feat: add new feature", ["file1.txt"])

# Install hook
hook_mgr.install_hook("pre-commit", "#!/bin/sh\necho 'Hook executed'")

# Get repository status
print(git_utils.get_current_branch())
print(git_utils.is_clean_working_directory())
```

## Development

1. Clone the repository
2. Create a virtual environment
3. Install dependencies
4. Run tests

```bash
git clone https://github.com/yourusername/git-utils.git
cd git-utils
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .
pytest
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Write tests
5. Update documentation
6. Submit a pull request

## License

MIT License

## Support

- GitHub Issues
- Documentation
- Community forum
- Professional support options
