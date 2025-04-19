# DevKit GitHub Workflows

This directory contains the GitHub Actions workflows for DevKit, organized by their primary purpose.

## Active Workflows

### ci-pr.yml
**Purpose**: Basic verification of pull requests
- Runs tests
- Lints code
- Validates Dockerfile
- Fast and focused on quick feedback

### cd-release.yml
**Purpose**: Release pipeline for version tags
- Builds and publishes Docker images to GitHub Container Registry
- Creates GitHub releases with release notes
- Triggered by pushing version tags (v*)

### ci-main.yml
**Purpose**: Main branch integration
- Runs when code is pushed to main
- Builds and publishes a development image
- Focuses on validating the integrated code

## Disabled Workflows (Enable When Ready)

### security-scan.yml
**Purpose**: Security scanning
- Scans dependencies for vulnerabilities
- Creates SBOM
- Scans Docker images
- Currently only triggered manually via workflow_dispatch

### scheduled-maintenance.yml
**Purpose**: Maintenance tasks
- Rebuilds images with latest dependencies
- Checks for outdated dependencies
- Disabled by default (requires enabling the cron schedule)

## Workflow Usage

### Development Flow
1. Create a branch and make changes
2. Submit a PR → `ci-pr.yml` runs
3. Merge to main → `ci-main.yml` runs
4. Create a version tag → `cd-release.yml` runs

### Running Security Scans
Manually trigger the `security-scan.yml` workflow from the Actions tab. 
Specify the image to scan and severity levels.

## Best Practices
- Keep the CI workflows fast
- Use specific dependency versions
- Test before releasing
- Validate security scans periodically

## Future Improvements
- Add unit testing
- Implement matrix testing for multiple Python versions
- Add code coverage reporting 