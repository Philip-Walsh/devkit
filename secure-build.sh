#!/bin/bash
set -e

# Get the version from setup.py
VERSION=$(grep version setup.py | cut -d'"' -f2)
echo "Building version: $VERSION"

# Check if prerequisites are installed
command -v docker >/dev/null 2>&1 || { echo "Docker is required but not installed. Aborting."; exit 1; }
command -v cosign >/dev/null 2>&1 || { echo "Warning: Cosign not found. Image signing will be skipped."; }
command -v syft >/dev/null 2>&1 || { echo "Warning: Syft not found. SBOM generation will use alternative method."; }

# Build the image with proper arguments
echo "🔨 Building Docker image..."
BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ')
VCS_REF=$(git rev-parse --short HEAD 2>/dev/null || echo "dev")

devkit docker build \
  --name devkit \
  --dockerfile Dockerfile \
  --no-cache \
  --platform linux/amd64 \
  --build-arg VERSION=$VERSION \
  --build-arg BUILD_DATE=$BUILD_DATE \
  --build-arg VCS_REF=$VCS_REF

# Test the image
echo "🧪 Testing the image..."
devkit docker test devkit:$VERSION --command "version current"
devkit docker test devkit:$VERSION --command "--help"

# Scan for vulnerabilities
echo "🔍 Scanning for vulnerabilities..."
devkit docker scan devkit:$VERSION --output text
echo "If critical vulnerabilities are found, consider addressing them before proceeding."
read -p "Continue with tagging and signing? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    exit 1
fi

# Tag the image for registry
echo "🏷️ Tagging the image..."
devkit docker tag devkit:$VERSION ghcr.io/philip-walsh/devkit

# Generate SBOM if Syft is available
if command -v syft >/dev/null 2>&1; then
  echo "📄 Generating SBOM..."
  mkdir -p sboms
  syft devkit:$VERSION -o spdx-json > sboms/devkit-$VERSION.sbom.json
  echo "SBOM saved to sboms/devkit-$VERSION.sbom.json"
fi

# Sign the image if Cosign is available
if command -v cosign >/dev/null 2>&1; then
  echo "🔏 Signing the image..."
  # Use keyless signing if possible
  if [[ -n "$GITHUB_ACTIONS" ]]; then
    cosign sign ghcr.io/philip-walsh/devkit:$VERSION
  else
    echo "For local signing, you'll need a Cosign key pair."
    read -p "Do you have a Cosign key pair? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
      read -p "Enter the path to your Cosign private key: " COSIGN_KEY
      cosign sign --key $COSIGN_KEY ghcr.io/philip-walsh/devkit:$VERSION
    else
      echo "Skipping signing. You can generate a key pair with 'cosign generate-key-pair'"
    fi
  fi
fi

# Push to registry if requested
read -p "Push to registry? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo "🚀 Pushing to registry..."
    docker push ghcr.io/philip-walsh/devkit:$VERSION
    docker push ghcr.io/philip-walsh/devkit:latest
    echo "Image pushed to registry!"
fi

# Apply Kyverno policies if in a Kubernetes environment
if command -v kubectl >/dev/null 2>&1 && command -v kyverno >/dev/null 2>&1; then
  echo "🔒 Would you like to apply Kyverno security policies to your cluster?"
  read -p "Apply Kyverno policies? (y/n) " -n 1 -r
  echo
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Applying Kyverno policies..."
    kubectl apply -f kyverno-policies/secure-container-policy.yaml
    echo "Policies applied!"
    
    echo "Testing deployment against policies..."
    kyverno test kubernetes/deployment.yaml --policy kyverno-policies/secure-container-policy.yaml
  fi
fi

echo "✅ Process completed!"
echo "Your image has been built, tested, scanned, signed, and made ready for deployment." 