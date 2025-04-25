#!/bin/bash
# Setup script for private DevKit regression testing repository

set -e  # Exit on error

echo "=== Setting up Private DevKit Regression Testing Repository ==="

# Configuration
PUBLIC_REPO=${1:-"https://github.com/Philip-Walsh/devkit.git"}
PRIVATE_REPO=${2:-"git@github.com:yourusername/private-repository.git"}
BRANCH_NAME=${3:-"regression-testing"}

echo "Public Repository: $PUBLIC_REPO"
echo "Private Repository: $PRIVATE_REPO"
echo "Branch Name: $BRANCH_NAME"

# Check if Git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install Git and try again."
    exit 1
fi

# Create temporary directory
TEMP_DIR=$(mktemp -d)
echo "Working in temporary directory: $TEMP_DIR"

# Clone the public repository
echo "Cloning public repository..."
git clone "$PUBLIC_REPO" "$TEMP_DIR/devkit"
cd "$TEMP_DIR/devkit"

# Create regression testing branch
echo "Creating regression testing branch: $BRANCH_NAME"
git checkout -b "$BRANCH_NAME"

# Copy regression testing scripts
echo "Setting up regression testing infrastructure..."
mkdir -p regression-tests
cp -r /home/robo/code/devkit1.0.2/regression-tests/* regression-tests/

# Add regression test integration to release.sh
echo "Integrating regression tests with release process..."
# This would typically modify release.sh to add regression testing steps
# For demonstration, we'll just create a simple integration script
cat > integrate-regression.sh << 'EOF'
#!/bin/bash
# Run regression tests as part of release process
set -e

VERSION=$1
REGISTRY=$2
ENVIRONMENT=$3

echo "Running regression tests for version $VERSION..."
./regression-tests/regression-test.sh "$REGISTRY" "$VERSION" "$ENVIRONMENT"
EOF
chmod +x integrate-regression.sh

# Add files to Git
echo "Adding files to Git..."
git add regression-tests/
git add integrate-regression.sh

# Commit changes
echo "Committing changes..."
git commit -m "Add regression testing infrastructure"

# Change remote to private repository
echo "Setting up private repository..."
git remote remove origin
git remote add origin "$PRIVATE_REPO"

# Instructions for final steps
echo
echo "=== Setup Complete ==="
echo
echo "To finalize the private repository setup:"
echo "1. Push to your private repository:"
echo "   cd $TEMP_DIR/devkit"
echo "   git push -u origin $BRANCH_NAME"
echo
echo "2. Set up GitHub Actions for automated testing (optional)"
echo "   Create a file at .github/workflows/regression.yml"
echo
echo "3. Run regression tests manually:"
echo "   ./regression-tests/regression-test.sh localhost:5000 latest"
echo
echo "4. For enhanced security, make sure to protect this branch in your GitHub repository settings"

exit 0 