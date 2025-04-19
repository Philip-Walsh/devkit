# DevKit Workflows

## Available Workflows

### `secure-docker-publish.yml`

Builds and publishes Docker images with security checks.

**Triggers**:
- Push to `main`
- Version tags (`v*`)
- PRs to `main`
- Manual runs

**Features**:
- Multi-architecture builds
- Security scanning
- SBOM generation
- Container signing
- GitHub releases

### `ci.yml`

Quick validation for pull requests.

**Triggers**:
- Pull requests

**Features**:
- Code linting
- Test runs
- Basic security checks

## Usage

### Development
PRs automatically run the CI workflow.

### Releases
Three ways to build:
1. Merge to `main` → development image
2. Create version tag → release image
3. Manual trigger → custom build

### Manual Builds
1. Actions tab → Secure Docker Build & Publish → Run workflow
2. Set options
3. Run

## Improvements Needed
- Split into smaller workflows
- Add dependency updates
- Add multi-version testing 