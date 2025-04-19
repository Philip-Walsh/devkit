# GitHub Release Instructions for DevKit v1.0.7

Follow these steps to create a GitHub release for DevKit v1.0.7:

## 1. Go to GitHub Releases Page

Navigate to the GitHub repository's Releases page:
`https://github.com/Philip-Walsh/devkit/releases`

## 2. Click "Draft a new release"

Look for the "Draft a new release" button on the Releases page.

## 3. Fill in Release Information

Complete the release form with the following information:

### Choose a tag
Select the existing tag: `v1.0.7`

### Release title
Enter: `DevKit v1.0.7`

### Description
Copy and paste the following release notes:

```markdown
## DevKit v1.0.7

This release includes bug fixes for the DevKit CLI, specifically focusing on the version management and Docker testing functionality.

### Fixed
- Error in `versioning.py` with `commit_version_change()` function
- Docker testing functionality to use a valid default test command
- Fixed the GitHub Actions release workflow

### Added
- `notify` command to support release notifications
- Documentation for the release process with RELEASES.md

### Changed
- Streamlined Docker release process with better error handling
- Improved local Docker registry support

### Docker Images
The following Docker images have been published to the local registry:
- `localhost:5000/devkit:1.0.7` (Full version)
- `localhost:5000/devkit:1.0` (Minor version)
- `localhost:5000/devkit:1` (Major version)
- `localhost:5000/devkit:latest` (Latest version)

For production use, you would need to authenticate to a production registry.
```

## 4. Assets (Optional)

If you want to attach any assets to the release (like the SBOM), click "Attach binaries by dropping them here or selecting them" and upload them.

## 5. Publish Release

Click "Publish release" to make the release public.

## 6. Verify the Release

After publishing, make sure to verify that the release appears correctly on the releases page.

## Using GitHub CLI (Alternative Method)

If you have GitHub CLI installed, you can create a release with the following command:

```bash
gh release create v1.0.7 \
  --title "DevKit v1.0.7" \
  --notes-file RELEASES.md
```

For more advanced options with GitHub CLI, refer to:
```bash
gh release create --help
``` 