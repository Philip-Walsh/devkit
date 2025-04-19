# DevKit v1.1.0

## Major Improvements

* Completely redesigned README with accessible, clear language
* Added daily security rebuilds with automated patching
* Enhanced Kyverno security policies for least privilege containers
* Implemented container health checks for Kubernetes deployments
* Improved security documentation and examples

## Security Enhancements

* Added seccomp profile configuration
* Implemented read-only root filesystem for containers
* Added capability dropping for enhanced container security
* Created health check endpoints for container monitoring
* Implemented comprehensive Kubernetes security policies

## Changes

* chore: bump version to 1.1.0
* docs: add ABOUT.md with CI/CD best practices documentation

## Docker Images

The following Docker images are available:

```bash
# Latest release
docker pull ghcr.io/philip-walsh/devkit:1.1.0
docker pull ghcr.io/philip-walsh/devkit:latest

# Security-hardened image (updated daily)
docker pull ghcr.io/philip-walsh/devkit:secure
```

## Verification

Verify the signed image with Cosign:

```bash
cosign verify ghcr.io/philip-walsh/devkit:1.1.0
```