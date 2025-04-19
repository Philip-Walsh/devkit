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
devkit docker tag image-name registry/repo  # Tag Docker image with semantic versions
devkit docker release --push             # Build, tag, and push Docker image
```

### Automated Release Workflow

This project includes a GitHub Actions workflow for automating releases:

1. Automatically bumps version (patch, minor, or major)
2. Creates Git tags with proper naming
3. Builds Docker images with semantic versioning tags
4. Pushes Docker images to container registries
5. Creates GitHub releases with release notes

To create a release:
1. Go to the Actions tab in your GitHub repository
2. Select the "Release" workflow
3. Click "Run workflow"
4. Choose the version bump type and optionally add release notes
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
