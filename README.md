# DevKit

A Python package providing development workflow automation and Git utility functions.

## Features

- Commit message validation
- Git hook management
- Repository utilities
- CI/CD integration
- Command-line interface
- Development workflow automation

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
```

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
