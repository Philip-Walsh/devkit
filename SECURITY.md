# Security Practices

This document outlines the security practices implemented in our DevOps pipeline and container deployments for the DevKit project.

## Secure Container Image Practices

### 1. Base Image Security
- Using Chainguard's minimal Python images (`cgr.dev/chainguard/python`) 
- Regular scanning for vulnerabilities using Trivy
- Images are rebuilt daily to incorporate the latest security patches

### 2. Least Privilege Principle
- Running as non-root user (`USER nonroot:nonroot`)
- Dropping all Linux capabilities not required
- Setting read-only filesystem where possible
- Configuring seccomp profiles to restrict system calls

### 3. Build Provenance & Artifact Integrity
- OCI-compliant metadata labels including version, build date, and VCS reference
- Software Bill of Materials (SBOM) generation
- Image signing with Cosign for supply chain integrity

### 4. Image Building Best Practices
- Multi-stage builds to minimize final image size and attack surface
- No credentials or secrets in the image
- Regular security scanning with policy enforcement
- Proper versioning (avoiding `latest` tag in production)

## CI/CD Security Practices

Our CI/CD pipeline incorporates the following security controls:

### 1. Automated Security Checks
- Vulnerability scanning with Trivy
- SBOM generation and validation
- Automated policy checks (Kyverno) for K8s manifests
- Enforcement of secure defaults

### 2. Build Pipeline Security
- Separate build and production environments
- Limited access to production deployment credentials
- Signing of container images and attestations
- Validation of dependencies through SBOM

### 3. Deployment Security
- Kubernetes security policies (via Kyverno)
- Resource limits to prevent DoS
- Health checks to ensure container integrity
- Proper securityContext settings

## Verification

### Verifying Image Signatures

```bash
# Install cosign if not already installed
# Verify a signed image
cosign verify ghcr.io/philip-walsh/devkit:1.0.3
```

### Viewing SBOM

```bash
# Using Syft
syft ghcr.io/philip-walsh/devkit:1.0.3

# Or if the SBOM is attached as attestation
cosign download attestation ghcr.io/philip-walsh/devkit:1.0.3 | jq -r '.payload' | base64 -d | jq
```

## Security Standards Compliance

Our practices align with:
- NIST Secure Software Development Framework (SSDF)
- Supply chain Levels for Software Artifacts (SLSA) Level 3
- CIS Docker Benchmarks
- OWASP Top 10 for Docker and Kubernetes

## Reporting a Security Issue

If you discover a security vulnerability, please report it by sending an email to security@example.com. Please do not report security vulnerabilities through public GitHub issues.

## References

- [OWASP Top 10 CI/CD Security Risks](https://owasp.org/www-project-top-10-ci-cd-security-risks/)
- [SLSA Framework](https://slsa.dev/)
- [Sigstore/Cosign](https://github.com/sigstore/cosign)
- [Chainguard Images](https://www.chainguard.dev/chainguard-images) 