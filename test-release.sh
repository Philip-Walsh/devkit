#!/bin/bash
# Script to test a DevKit release

# Set variables
REGISTRY=${1:-"localhost:5000"}
VERSION=${2:-$(python -m devkit.cli version current | awk '{print $3}')}
IMAGE_NAME="${REGISTRY}/devkit:${VERSION}"

echo "=== Testing DevKit Release ==="
echo "Version: $VERSION"
echo "Image: $IMAGE_NAME"
echo

# Pull the image
echo "1. Pulling the image..."
docker pull "$IMAGE_NAME"
if [ $? -ne 0 ]; then
    echo "❌ Failed to pull image: $IMAGE_NAME"
    exit 1
fi
echo "✅ Image pulled successfully"
echo

# Test version command
echo "2. Testing version command..."
VERSION_OUTPUT=$(docker run --rm "$IMAGE_NAME" version current)
if [[ "$VERSION_OUTPUT" != *"$VERSION"* ]]; then
    echo "❌ Version mismatch. Expected: $VERSION, Got: $VERSION_OUTPUT"
    exit 1
fi
echo "✅ Version command works correctly: $VERSION_OUTPUT"
echo

# Test health check
echo "3. Testing health check..."
HEALTH_OUTPUT=$(docker run --rm "$IMAGE_NAME" health live)
if [[ "$HEALTH_OUTPUT" != "OK" ]]; then
    echo "❌ Health check failed. Expected: OK, Got: $HEALTH_OUTPUT"
    exit 1
fi
echo "✅ Health check works correctly: $HEALTH_OUTPUT"
echo

# Test notification system
echo "4. Testing notification system..."
NOTIFY_OUTPUT=$(docker run --rm "$IMAGE_NAME" notify send --channel test --message "Test message")
if [[ "$NOTIFY_OUTPUT" != *"Notification sent to test"* ]]; then
    echo "❌ Notification system failed. Expected message about notification sent, Got: $NOTIFY_OUTPUT"
    exit 1
fi
echo "✅ Notification system works correctly"
echo

echo "=== All tests passed! ==="
echo "DevKit release $VERSION is working correctly." 