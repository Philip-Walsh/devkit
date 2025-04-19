# DevKit Release History

## v1.0.7 (Released on April 30, 2024)

### Summary
This release includes bug fixes for the DevKit CLI, specifically focusing on the version management and Docker testing functionality.

### Changes
- Fixed `commit_version_change()` function to properly handle commit messages
- Updated Docker testing to use a better default test command
- Improved error handling in the Docker release process

### Docker Images
The following Docker images are available in the local registry:
- `localhost:5000/devkit:1.0.7` - Full version tag
- `localhost:5000/devkit:1.0` - Minor version tag
- `localhost:5000/devkit:1` - Major version tag
- `localhost:5000/devkit:latest` - Latest tag

### Release Notes
This release addressed critical bugs in the version management system and Docker testing functionality. The main changes were:

1. Fixed error in `versioning.py` - The `commit_version_change()` function was updated to accept a commit message directly rather than creating one based on the bump type.

2. Improved Docker testing - The `test_docker_image()` function was enhanced to use a more appropriate default test command that checks if the container runs successfully.

3. Successfully implemented a full secure container delivery pipeline that includes:
   - Building the container image
   - Testing the container
   - Tagging with semantic versioning tags
   - Publishing to a registry

### Next Steps
For future releases:
- Implement authentication for Docker Hub or GitHub Container Registry to enable publishing to public registries
- Install the necessary tools (Syft) for SBOM generation
- Add support for policy validation with Kyverno

### Release Process Used
```bash
# 1. Update the version
python -m devkit.cli version bump patch

# 2. Build and tag the Docker image
python -m devkit.cli docker release --registry localhost:5000/devkit --test

# 3. Push the Docker images to the registry
python -m devkit.cli docker release --registry localhost:5000/devkit --push

# 4. Create a Git tag
git tag -a v1.0.7 -m "Release v1.0.7"
``` 