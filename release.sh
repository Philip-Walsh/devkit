#!/bin/bash
# DevKit Comprehensive Release Script
# This script automates the entire release process for DevKit

set -e  # Exit on error

# Parse arguments
VERSION_TYPE=${1:-"patch"}  # Default to patch release
REGISTRY=${2:-"localhost:5000"}
PUSH_TO_REGISTRY=${3:-"true"}
CREATE_GITHUB_RELEASE=${4:-"false"}
RUN_REGRESSION=${5:-"true"}
REGRESSION_ENV=${6:-"production"}

# Validate version type
if [[ ! "$VERSION_TYPE" =~ ^(patch|minor|major)$ ]]; then
    echo "❌ Invalid version type: $VERSION_TYPE"
    echo "Usage: $0 [patch|minor|major] [registry] [push_to_registry] [create_github_release] [run_regression] [regression_env]"
    exit 1
fi

echo "=== Starting DevKit Release Process ==="
echo "Version Type: $VERSION_TYPE"
echo "Registry: $REGISTRY"
echo "Push to Registry: $PUSH_TO_REGISTRY"
echo "Create GitHub Release: $CREATE_GITHUB_RELEASE"
echo "Run Regression Tests: $RUN_REGRESSION"
echo "Regression Test Environment: $REGRESSION_ENV"
echo

# Step 1: Bump the version
echo "Step 1: Bumping version ($VERSION_TYPE)..."
python -m devkit.cli version bump "$VERSION_TYPE"
NEW_VERSION=$(python -m devkit.cli version current | awk '{print $3}')
echo "✅ Version bumped to $NEW_VERSION"
echo

# Step 2: Update CHANGELOG.md
echo "Step 2: Updating CHANGELOG.md..."
if [ -f CHANGELOG.md ]; then
    # Create a temporary file for the new changelog content
    TEMP_CHANGELOG=$(mktemp)
    
    # Extract the header (everything before ## [Unreleased])
    sed -n '1,/## \[Unreleased\]/p' CHANGELOG.md > "$TEMP_CHANGELOG"
    
    # Add the new version entry
    cat >> "$TEMP_CHANGELOG" << EOF

## [$NEW_VERSION] - $(date +%Y-%m-%d)

### Fixed
- Add fixed items here

### Added
- Add new features here

### Changed
- Add changes here

EOF

    # Add the rest of the original changelog (excluding the header)
    sed -n '/## \[Unreleased\]/,$p' CHANGELOG.md | tail -n +2 >> "$TEMP_CHANGELOG"
    
    # Update the comparison links at the bottom
    PREVIOUS_VERSION=$(grep -oP '\[\d+\.\d+\.\d+\]' CHANGELOG.md | head -1 | tr -d '[]')
    if [ -n "$PREVIOUS_VERSION" ]; then
        # Update the Unreleased comparison link
        sed -i "s|\[Unreleased\]: .*/compare/v$PREVIOUS_VERSION...HEAD|\[Unreleased\]: https://github.com/Philip-Walsh/devkit/compare/v$NEW_VERSION...HEAD\n\[$NEW_VERSION\]: https://github.com/Philip-Walsh/devkit/compare/v$PREVIOUS_VERSION...v$NEW_VERSION|g" "$TEMP_CHANGELOG"
    fi
    
    # Replace the original changelog
    mv "$TEMP_CHANGELOG" CHANGELOG.md
    echo "✅ CHANGELOG.md updated with new version $NEW_VERSION"
    echo "⚠️ NOTE: Please manually edit CHANGELOG.md to add the actual changes!"
else
    echo "⚠️ CHANGELOG.md not found. Skipping update."
fi

# Step 3: Build and test Docker image
echo "Step 3: Building and testing Docker image..."
python -m devkit.cli docker release --registry "$REGISTRY" --test
echo "✅ Docker image built and tested successfully"
echo

# Step 4: Push to registry if requested
if [ "$PUSH_TO_REGISTRY" = "true" ]; then
    echo "Step 4: Pushing Docker image to registry..."
    python -m devkit.cli docker release --registry "$REGISTRY" --push
    echo "✅ Docker image pushed to registry"
else
    echo "Step 4: Skipping pushing to registry as requested"
fi
echo

# Step 5: Create Git tag
echo "Step 5: Creating Git tag..."
git tag -a "v$NEW_VERSION" -m "Release v$NEW_VERSION"
echo "✅ Git tag v$NEW_VERSION created"
echo

# Step 6: Create/Update RELEASES.md
echo "Step 6: Updating RELEASES.md..."
if [ ! -f RELEASES.md ]; then
    echo "# DevKit Release History" > RELEASES.md
fi

# Add new release entry at the top
TEMP_RELEASES=$(mktemp)
cat > "$TEMP_RELEASES" << EOF
# DevKit Release History

## v$NEW_VERSION (Released on $(date +%Y-%m-%d))

### Summary
This release includes updates to the DevKit CLI.

### Changes
- Add your changes here

### Docker Images
The following Docker images are available in the registry:
- \`$REGISTRY/devkit:$NEW_VERSION\` - Full version tag
- \`$REGISTRY/devkit:${NEW_VERSION%.*}\` - Minor version tag
- \`$REGISTRY/devkit:${NEW_VERSION%%.*}\` - Major version tag
- \`$REGISTRY/devkit:latest\` - Latest tag

### Release Notes
Add detailed release notes here.

### Next Steps
For future releases:
- Add future plans here

### Release Process Used
\`\`\`bash
# Generated with release.sh
./release.sh $VERSION_TYPE $REGISTRY $PUSH_TO_REGISTRY $CREATE_GITHUB_RELEASE $RUN_REGRESSION $REGRESSION_ENV
\`\`\`
EOF

# Append the existing content (excluding the title)
grep -v "# DevKit Release History" RELEASES.md >> "$TEMP_RELEASES"
mv "$TEMP_RELEASES" RELEASES.md
echo "✅ RELEASES.md updated with new version $NEW_VERSION"
echo "⚠️ NOTE: Please manually edit RELEASES.md to add the actual changes!"
echo

# Step 7: Commit changes
echo "Step 7: Committing changes..."
git add setup.py devkit/__init__.py CHANGELOG.md RELEASES.md
git commit -m "chore: release version $NEW_VERSION"
echo "✅ Changes committed"
echo

# Step 8: Push changes and tag
echo "Step 8: Pushing changes and tag to repository..."
git push origin main
git push origin "v$NEW_VERSION"
echo "✅ Changes and tag pushed to repository"
echo

# Step 9: Run verification tests
echo "Step 9: Running verification tests..."
./test-release.sh "$REGISTRY" "$NEW_VERSION"
echo "✅ Release verification tests passed"
echo

# Step 8.5: Run regression tests if requested
if [ "$RUN_REGRESSION" = "true" ] && [ -f "regression-tests/regression-test.sh" ]; then
    echo "Step 8.5: Running regression tests..."
    chmod +x regression-tests/regression-test.sh
    ./regression-tests/regression-test.sh "$REGISTRY" "$NEW_VERSION" "$REGRESSION_ENV"
    echo "✅ Regression tests passed"
elif [ "$RUN_REGRESSION" = "true" ]; then
    echo "Step 8.5: Skipping regression tests - regression-tests/regression-test.sh not found"
    echo "⚠️ To enable regression testing, set up the regression testing framework"
else
    echo "Step 8.5: Skipping regression tests as requested"
fi
echo

# Step 10: Create GitHub release if requested
if [ "$CREATE_GITHUB_RELEASE" = "true" ]; then
    echo "Step 10: Creating GitHub release..."
    if command -v gh &> /dev/null; then
        echo "Using GitHub CLI to create release..."
        # Extract RELEASES.md content for this version only
        RELEASE_NOTES=$(sed -n "/## v$NEW_VERSION/,/## v/p" RELEASES.md | sed '$d')
        echo "$RELEASE_NOTES" > release-notes-temp.md
        gh release create "v$NEW_VERSION" --title "DevKit v$NEW_VERSION" --notes-file release-notes-temp.md
        rm release-notes-temp.md
        echo "✅ GitHub release created"
    else
        echo "⚠️ GitHub CLI not found. Please create the release manually following the instructions in GITHUB-RELEASE-INSTRUCTIONS.md"
    fi
else
    echo "Step 10: Skipping GitHub release creation as requested"
    echo "ℹ️  To create a GitHub release, follow the instructions in GITHUB-RELEASE-INSTRUCTIONS.md"
fi
echo

echo "=== DevKit Release $NEW_VERSION Completed Successfully ==="
echo "Version: $NEW_VERSION"
echo "Docker Image: $REGISTRY/devkit:$NEW_VERSION"
echo "Git Tag: v$NEW_VERSION"
echo
echo "Next steps:"
echo "1. Update CHANGELOG.md with the actual changes"
echo "2. Update RELEASES.md with detailed information"
echo "3. If not done automatically, create a GitHub release following GITHUB-RELEASE-INSTRUCTIONS.md"
if [ "$RUN_REGRESSION" != "true" ] || [ ! -f "regression-tests/regression-test.sh" ]; then
    echo "4. Consider running regression tests separately with:"
    echo "   ./regression-tests/regression-test.sh $REGISTRY $NEW_VERSION production"
fi
echo

exit 0 