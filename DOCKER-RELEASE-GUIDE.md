# Docker Release Guide for DevKit

This guide explains how to use the fixed Docker release functionality in DevKit to build, test, and publish Docker images.

## Prerequisites

- Docker installed and running
- Access to a Docker registry (Docker Hub, GitHub Container Registry, or a local registry)
- Authentication to the Docker registry (if using a remote registry)

## Local Registry Setup

If you're testing the release process or don't have access to a remote registry, you can use a local registry:

```bash
# Start a local registry
docker run -d -p 5000:5000 --name registry registry:2

# Verify it's running
curl -X GET http://localhost:5000/v2/_catalog
```

## Release Process

### Step 1: Bump the Version

First, increment the version according to semantic versioning:

```bash
# For a patch release
python -m devkit.cli version bump patch

# For a minor release
python -m devkit.cli version bump minor

# For a major release
python -m devkit.cli version bump major
```

### Step 2: Build and Test the Docker Image

Build and test the Docker image without pushing it:

```bash
# For a local registry
python -m devkit.cli docker release --registry localhost:5000/devkit --test

# For Docker Hub
python -m devkit.cli docker release --registry yourname/devkit --test

# For GitHub Container Registry
python -m devkit.cli docker release --registry ghcr.io/Philip-Walsh/devkit --test
```

### Step 3: Push the Docker Image

If the tests pass, push the image to the registry:

```bash
# For a local registry
python -m devkit.cli docker release --registry localhost:5000/devkit --push

# For Docker Hub (requires docker login first)
docker login
python -m devkit.cli docker release --registry yourname/devkit --push

# For GitHub Container Registry (requires authentication)
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin
python -m devkit.cli docker release --registry ghcr.io/Philip-Walsh/devkit --push
```

### Step 4: Create a Git Tag

Create a Git tag for the release:

```bash
# Get the current version
VERSION=$(python -m devkit.cli version current | awk '{print $3}')

# Create and push the tag
git tag -a v$VERSION -m "Release v$VERSION"
git push origin v$VERSION
```

### Step 5: Update Documentation

Update the release documentation:

1. Update CHANGELOG.md with the changes in the new release
2. Update RELEASES.md with details about the release
3. Commit and push these changes

## Using GitHub Actions for Releases

You can also use the GitHub Actions workflow to automate releases:

1. Go to the Actions tab in your GitHub repository
2. Select the "DevKit Release Process" workflow
3. Click "Run workflow"
4. Choose the release type (patch, minor, major) and click "Run workflow"

The workflow will:
- Run tests
- Bump the version
- Create a Git tag
- Build and test the Docker image
- Push the Docker image to the registry
- Create a GitHub release

## Troubleshooting

If you encounter issues:

1. **Authentication errors**: Make sure you're authenticated to the Docker registry
2. **Push failures**: Check if the registry URL is correct
3. **Test failures**: Verify that the Docker image builds correctly and passes tests
4. **Version conflicts**: Ensure your local repository is up to date with the remote 