# Changelog

All notable changes to DevKit will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.7] - 2024-04-30

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

## [1.0.6] - 2023-09-20

### Changed
- Reorganized GitHub Actions workflows for better maintainability
- Split monolithic workflow into focused, smaller workflows
- Optimized CI/CD pipeline for GitHub Free tier

### Added
- Dedicated PR verification workflow
- Simplified release workflow
- Main branch integration workflow
- Disabled but configurable security scanning workflow
- Disabled but configurable scheduled maintenance workflow

## [1.0.5] - 2023-09-15

### Added
- Optimized GitHub Actions workflow for free tier
- Combined security check and build jobs for efficiency
- Enhanced error handling in CI pipeline

### Changed
- Reduced artifact storage requirements
- Improved Docker image scanning process
- Streamlined release process

## [1.0.4] - 2023-09-01

### Added
- Improved repository structure with GitHub templates
- SECURITY.md with security policy
- CHANGELOG.md to track changes
- Standardized issue and PR templates
- CODEOWNERS file

### Changed
- Simplified workflow documentation
- Restructured documentation directories

### Fixed
- Removed placeholder team references in CODEOWNERS
- Added .gitkeep files to preserve empty directory structure

## [1.0.3] - 2023-07-25

### Added
- Support for custom security policies
- Extended CLI documentation

### Fixed
- DevKit version management commands

## [1.0.2] - 2023-06-15

### Added
- Docker publishing workflow with security scanning
- Kyverno policies for Kubernetes
- Support for arm64 architecture

### Changed
- Updated CI pipeline
- Better Python dependency management

### Fixed
- Security issues in Docker builds

## [1.0.1] - 2023-03-10

### Added
- Basic container scanning
- Dockerfile linting

### Changed
- Improved documentation

## [1.0.0] - 2023-01-20

### Added
- Initial release
- Docker build capabilities
- Python package functionality
- Security scanning

[Unreleased]: https://github.com/philip-walsh/devkit/compare/v1.0.7...HEAD
[1.0.7]: https://github.com/philip-walsh/devkit/compare/v1.0.6...v1.0.7
[1.0.6]: https://github.com/philip-walsh/devkit/compare/v1.0.5...v1.0.6
[1.0.5]: https://github.com/philip-walsh/devkit/compare/v1.0.4...v1.0.5
[1.0.4]: https://github.com/philip-walsh/devkit/compare/v1.0.3...v1.0.4
[1.0.3]: https://github.com/philip-walsh/devkit/compare/v1.0.2...v1.0.3
[1.0.2]: https://github.com/philip-walsh/devkit/compare/v1.0.1...v1.0.2
[1.0.1]: https://github.com/philip-walsh/devkit/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/philip-walsh/devkit/releases/tag/v1.0.0
