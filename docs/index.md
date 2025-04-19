# DevKit Documentation

Welcome to the DevKit documentation. DevKit simplifies secure container development by turning complex, multi-step security processes into simple commands.

## Guides

- [Dogfooding Guide](guides/dogfooding.md) - How to use DevKit to manage DevKit itself
- [Git Hooks Guide](guides/git-hooks.md) - Using DevKit's Git hooks functionality
- [Release Automation Guide](guides/release-automation.md) - How to automate releases with DevKit
- [Project Compatibility Guide](guides/project-compatibility.md) - Using DevKit with different project structures

## Example Files

- Release scripts in [examples/release-scripts/](../examples/release-scripts/)
- Git hooks in [examples/hooks/](../examples/hooks/)
- CI/CD workflows in [examples/workflows/](../examples/workflows/)
- Configuration examples in [examples/configs/](../examples/configs/)

## Core Documentation

- [README.md](../README.md) - Project overview and quick start
- [ABOUT.md](../ABOUT.md) - Project philosophy and principles
- [SECURITY.md](../SECURITY.md) - Security features and best practices
- [ROADMAP.md](../ROADMAP.md) - Future development plans
- [CHANGELOG.md](../CHANGELOG.md) - Version history

## Getting Started

```bash
# Install DevKit
pip install git+https://github.com/Philip-Walsh/devkit.git

# Initialize DevKit in your project
cd your-project
devkit init

# Build and scan a secure container in one step
devkit docker secure --dockerfile=Dockerfile
``` 