# Kyverno Security Policies

This directory contains Kyverno policies that enforce security best practices for Kubernetes deployments of the DevKit application.

## What is Kyverno?

[Kyverno](https://kyverno.io/) is a policy engine designed for Kubernetes. It can validate, mutate, and generate configurations using policies as Kubernetes resources.

## Available Policies

- **secure-container-policy.yaml**: Enforces security best practices for containers, including:
  - Prohibiting privileged containers
  - Requiring non-root users
  - Preventing hostPath volumes
  - Requiring resource limits
  - Disallowing the use of the 'latest' tag

## How to Apply These Policies

### Prerequisites

1. A Kubernetes cluster
2. Kyverno installed in your cluster

### Installing Kyverno

```bash
# Using Helm
helm repo add kyverno https://kyverno.github.io/kyverno/
helm repo update
helm install kyverno kyverno/kyverno --namespace kyverno --create-namespace
```

### Applying the Policies

```bash
kubectl apply -f kyverno-policies/secure-container-policy.yaml
```

## Testing the Policies

After applying the policies, you can test them by creating a Pod that violates one of the rules:

```bash
# Create a test Pod that runs as root (should be blocked)
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: test-pod
spec:
  containers:
  - name: nginx
    image: nginx:latest
EOF
```

You should receive an error message explaining why the Pod was rejected.

## Integration with CI/CD

These policies can be checked in your CI/CD pipeline using tools like `kyverno test` or `conftest`. For example:

```bash
# Test a Kubernetes manifest against your policies
kyverno test my-deployment.yaml --policy kyverno-policies/secure-container-policy.yaml
```

## Additional Documentation

- [Kyverno Documentation](https://kyverno.io/docs/)
- [Kyverno Policy Examples](https://kyverno.io/policies/) 