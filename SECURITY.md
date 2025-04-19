# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting Security Issues

If you discover a security vulnerability in DevKit, please create a GitHub issue with the label "security" and mark it as confidential if the platform supports it. Alternatively, you can contact the repository maintainer through GitHub.

**Note:** We're a small team, so response times will vary based on the severity of the issue and our availability.

## Security Features in DevKit

DevKit includes several security-focused features:

- Vulnerability scanning for Docker images with Trivy
- Software Bill of Materials (SBOM) generation 
- Container signing capability
- Kyverno policies for Kubernetes security
- Security-focused CI/CD workflows

## Container Security Best Practices

DevKit encourages these container security practices:

- Using minimal base images
- Running containers as non-root
- Setting resource limits
- Avoiding the 'latest' tag
- Regular vulnerability scanning
- Proper image signing

## Kubernetes Security

Our Kyverno policies help enforce:

- Non-privileged containers
- Resource limits
- Disallowed capabilities
- No hostPath volumes
- Required security contexts

## Verifying Image Signatures

```bash
# Install cosign if not already installed
# Verify a signed image
cosign verify ghcr.io/philip-walsh/devkit:1.0.3
```

## Viewing SBOM

```bash
# Using Syft
syft ghcr.io/philip-walsh/devkit:1.0.3
```

## Security Standards

While we aim to follow good security practices, we don't claim formal compliance with any specific standard. 