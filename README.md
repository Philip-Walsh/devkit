# DevKit

DevKit simplifies secure container development by turning complex, multi-step security processes into simple commands. It's like having a DevOps expert built into your CLI.

## What Problems Does DevKit Solve?

- **"Docker security is too complicated"** → One command to build, scan, and secure your containers
- **"We need to comply with security requirements"** → Built-in tools for security reports and compliance
- **"Setting up Kubernetes securely is hard"** → Pre-configured secure deployments with sensible defaults
- **"Our deployment process is inconsistent"** → Standardized workflows for all environments
- **"We waste time on repetitive DevOps tasks"** → Automated versioning, releases, and security updates

## Main Features

- **Make Docker Security Simple**
  - Find vulnerabilities in your containers with one command
  - Generate security documentation automatically
  - Keep containers updated with security patches
  - Deploy to Kubernetes with secure defaults

- **Streamline Development Workflows**
  - Automate Git operations and version management
  - Create consistent release processes
  - Build containers for multiple platforms easily
  - Integrate with CI/CD pipelines

## Quick Start

```bash
# Install DevKit
pip install git+https://github.com/Philip-Walsh/devkit.git

# Build and scan a secure container in one step
devkit docker secure --dockerfile=Dockerfile

# Check for vulnerabilities in an existing image
devkit docker scan my-image:latest
```

## Common Use Cases

### Secure a Docker Image

```bash
# Before: 6+ separate commands with different tools
# After: One command with DevKit
devkit docker secure --push
```

This will:
1. Build your Docker image with security best practices
2. Check for vulnerabilities and security issues
3. Generate a security report (SBOM) listing all components
4. Sign the image to verify its authenticity
5. Push the image to your registry if it passes security checks

### Update Container Security Daily

DevKit automatically rebuilds your containers with security updates every day using the included GitHub workflow. No manual patching needed!

### Deploy Securely to Kubernetes

```yaml
# DevKit creates Kubernetes deployments with security built-in
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
spec:
  template:
    spec:
      # Security is pre-configured properly
      containers:
      - name: my-container
        image: my-registry/my-image:1.0.3
        # Health checks already set up
        livenessProbe:
          httpGet:
            path: /health/live
            port: http
```

## Command Overview

```bash
# Everyday Git Commands
devkit create feature new-feature   # Create a branch with naming convention
devkit push dev                     # Run checks and push changes

# Container Security Made Simple
devkit docker build                 # Build a secure container
devkit docker scan image-name       # Check for vulnerabilities
devkit docker sbom image-name       # Create a security report
```

## How It Makes Security Easier

DevKit handles many security best practices automatically:

- **Non-root containers** - Prevents privilege escalation attacks
- **Security scanning** - Finds vulnerabilities before deployment
- **Component tracking** - Creates inventory of all software in your container
- **Automated updates** - Keeps containers patched against new threats
- **Restricted permissions** - Limits what containers can do in production

## What's Inside?

DevKit combines several powerful tools into a simple package:

- **Vulnerability Scanning** using Trivy
- **Software Inventory** (SBOM) creation with Syft
- **Container Signing** with Cosign
- **Security Policies** with Kyverno
- **Multi-stage Builds** with Dockerfile optimization

## Getting Started

```bash
# Install from GitHub
pip install git+https://github.com/Philip-Walsh/devkit.git

# Setup a project
cd your-project
devkit setup

# Build and secure a container
devkit docker secure
```

## Documentation

- [SECURITY.md](SECURITY.md) - Details about security features
- [ABOUT.md](ABOUT.md) - CI/CD principles
- [ROADMAP.md](ROADMAP.md) - Future plans

## Development

```bash
git clone https://github.com/Philip-Walsh/devkit.git
cd devkit
python -m venv venv
source venv/bin/activate
pip install -e .
pytest
```

## License

[License information here]

## Support

- GitHub Issues
- Documentation
- Community forum
- Professional support options
