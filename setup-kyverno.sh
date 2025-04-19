#!/bin/bash
set -e

# Check if Kubernetes is available
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl command not found. Please install Kubernetes CLI first."
    exit 1
fi

# Check if Helm is available
if ! command -v helm &> /dev/null; then
    echo "❌ Helm command not found. Please install Helm first."
    echo "Visit https://helm.sh/docs/intro/install/ for installation instructions."
    exit 1
fi

echo "🔄 Setting up Kyverno in your Kubernetes cluster..."

# Add Kyverno Helm repository
helm repo add kyverno https://kyverno.github.io/kyverno/
helm repo update

# Check if Kyverno namespace exists
if ! kubectl get namespace kyverno &> /dev/null; then
    echo "Creating kyverno namespace..."
    kubectl create namespace kyverno
fi

# Install Kyverno using Helm
echo "Installing Kyverno..."
helm upgrade --install kyverno kyverno/kyverno --namespace kyverno --wait

# Apply our security policies
echo "🔒 Applying DevKit security policies..."
kubectl apply -f kyverno-policies/secure-container-policy.yaml

echo "✅ Kyverno setup complete!"
echo "Policies applied: secure-container-policy.yaml"

# Test a deployment against the policies
echo "Would you like to test the DevKit deployment against the policies?"
read -p "Test deployment? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Check if kyverno CLI is installed
    if ! command -v kyverno &> /dev/null; then
        echo "⚠️ Kyverno CLI not found. Installing..."
        # Platform detection
        PLATFORM=$(uname -s | tr '[:upper:]' '[:lower:]')
        ARCH=$(uname -m)
        if [[ "$ARCH" == "x86_64" ]]; then
            ARCH="amd64"
        elif [[ "$ARCH" == "aarch64" ]]; then
            ARCH="arm64"
        fi
        
        # Download the latest release
        curl -LO "https://github.com/kyverno/kyverno/releases/latest/download/kyverno-cli_${PLATFORM}_${ARCH}.tar.gz"
        tar -xvf kyverno-cli_${PLATFORM}_${ARCH}.tar.gz
        chmod +x kyverno
        sudo mv kyverno /usr/local/bin/
        rm kyverno-cli_${PLATFORM}_${ARCH}.tar.gz
    fi
    
    echo "Testing deployment.yaml against policies..."
    kyverno test kubernetes/deployment.yaml --policy kyverno-policies/secure-container-policy.yaml
    
    echo "Would you like to deploy the DevKit application to your cluster?"
    read -p "Deploy application? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        kubectl apply -f kubernetes/deployment.yaml
        echo "✅ Deployment applied!"
    fi
fi

echo ""
echo "📖 To learn more about Kyverno, visit: https://kyverno.io/docs/"
echo "For more information about our security policies, see: ./kyverno-policies/README.md" 