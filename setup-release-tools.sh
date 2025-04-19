#!/bin/bash
# Setup script for DevKit release tools

set -e  # Exit on error

echo "=== Setting up DevKit Release Tools ==="

# Check if running with sudo
if [ "$EUID" -ne 0 ]; then
  echo "⚠️ This script should be run with sudo for system-wide installations"
  echo "Please run: sudo ./setup-release-tools.sh"
  exit 1
fi

echo "Installing system dependencies..."
apt-get update
apt-get install -y \
  curl \
  wget \
  jq \
  apt-transport-https \
  ca-certificates \
  gnupg-agent \
  software-properties-common

# Install Docker if not installed
if ! command -v docker &> /dev/null; then
  echo "Installing Docker..."
  # Add Docker's official GPG key
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -
  
  # Add Docker repository
  add-apt-repository \
     "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
     $(lsb_release -cs) \
     stable"
     
  apt-get update
  apt-get install -y docker-ce docker-ce-cli containerd.io
  
  # Add current user to docker group
  if [ -n "$SUDO_USER" ]; then
    usermod -aG docker "$SUDO_USER"
    echo "✅ Added $SUDO_USER to the docker group. You may need to log out and back in."
  else
    echo "⚠️ Could not determine the sudo user. Please manually add your user to the docker group:"
    echo "sudo usermod -aG docker YOUR_USERNAME"
  fi
  
  echo "✅ Docker installed"
else
  echo "✅ Docker already installed"
fi

# Install Syft for SBOM generation
if ! command -v syft &> /dev/null; then
  echo "Installing Syft for SBOM generation..."
  curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh -s -- -b /usr/local/bin
  echo "✅ Syft installed"
else
  echo "✅ Syft already installed"
fi

# Install Trivy for vulnerability scanning
if ! command -v trivy &> /dev/null; then
  echo "Installing Trivy for vulnerability scanning..."
  wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | apt-key add -
  echo deb https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main | tee -a /etc/apt/sources.list.d/trivy.list
  apt-get update
  apt-get install -y trivy
  echo "✅ Trivy installed"
else
  echo "✅ Trivy already installed"
fi

# Install Cosign for container signing
if ! command -v cosign &> /dev/null; then
  echo "Installing Cosign for container signing..."
  COSIGN_VERSION=$(curl -s https://api.github.com/repos/sigstore/cosign/releases/latest | jq -r '.tag_name')
  curl -L "https://github.com/sigstore/cosign/releases/download/${COSIGN_VERSION}/cosign-linux-amd64" -o /usr/local/bin/cosign
  chmod +x /usr/local/bin/cosign
  echo "✅ Cosign installed"
else
  echo "✅ Cosign already installed"
fi

# Install Kyverno CLI for policy validation (optional)
if ! command -v kyverno &> /dev/null; then
  echo "Installing Kyverno CLI for policy validation..."
  KYVERNO_VERSION=$(curl -s https://api.github.com/repos/kyverno/kyverno/releases/latest | jq -r '.tag_name')
  curl -L "https://github.com/kyverno/kyverno/releases/download/${KYVERNO_VERSION}/kyverno-cli_${KYVERNO_VERSION}_linux_x86_64.tar.gz" -o kyverno.tar.gz
  tar -xvf kyverno.tar.gz
  mv kyverno /usr/local/bin/
  rm kyverno.tar.gz
  echo "✅ Kyverno CLI installed"
else
  echo "✅ Kyverno CLI already installed"
fi

# Install GitHub CLI (optional)
if ! command -v gh &> /dev/null; then
  echo "Installing GitHub CLI..."
  curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
  chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg
  echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | tee /etc/apt/sources.list.d/github-cli.list > /dev/null
  apt-get update
  apt-get install -y gh
  echo "✅ GitHub CLI installed"
else
  echo "✅ GitHub CLI already installed"
fi

echo
echo "=== Release Tools Setup Complete ==="
echo "The following tools are now installed:"
echo "- Docker"
echo "- Syft (SBOM generation)"
echo "- Trivy (vulnerability scanning)"
echo "- Cosign (container signing)"
echo "- Kyverno CLI (policy validation)"
echo "- GitHub CLI (for GitHub releases)"
echo
echo "You can now use ./release.sh to automate the release process"
echo "For local testing, you can start a local registry with:"
echo "  docker run -d -p 5000:5000 --name registry registry:2"

exit 0 