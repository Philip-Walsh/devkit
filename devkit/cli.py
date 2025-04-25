#!/usr/bin/env python3

import json
import subprocess
import sys
from pathlib import Path
from typing import List, Optional, Tuple

import click

# Import versioning and docker modules
from devkit.versioning import (
    VersionBump,
    bump_version,
    commit_version_change,
    create_git_tag,
    get_current_version,
    get_latest_git_tag,
    push_git_tag,
    update_version_in_files,
)

try:
    from devkit.docker import (
        DockerError,
        build_docker_image,
        check_docker_installed,
        check_kyverno_policy,
        check_tool_installed,
        generate_docker_tags,
        generate_sbom,
        push_docker_image,
        scan_docker_image,
        secure_pipeline,
        sign_image,
        tag_docker_image,
        test_docker_image,
        verify_image_signature,
    )
    DOCKER_AVAILABLE = True
except ImportError:
    DOCKER_AVAILABLE = False


def run_command(
    command: List[str], capture_output: bool = True, check: bool = True
) -> Tuple[bool, Optional[str]]:
    """Run a shell command and return success status and output."""
    try:
        if capture_output:
            result = subprocess.run(
                command, check=check, capture_output=True, text=True
            )
            return True, result.stdout
        else:
            subprocess.run(command, check=check)
            return True, None
    except subprocess.CalledProcessError as e:
        if capture_output:
            click.echo(f"Error: {e.stderr}", err=True)
        return False, None


class GitManager:
    def __init__(self):
        self.current_branch = self._get_current_branch()
        self.root_dir = Path(__file__).parent.parent

    def _run_command(self, command: List[str], check: bool = True) -> bool:
        try:
            subprocess.run(command, check=check,
                           capture_output=True, text=True)
            return True
        except subprocess.CalledProcessError as e:
            click.echo(f"Error: {e.stderr}", err=True)
            return False

    def _get_current_branch(self) -> str:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            check=False,
        )
        return result.stdout.strip()

    def fetch_all(self) -> bool:
        click.echo("🔄 Fetching all changes...")
        return self._run_command(["git", "fetch", "--all"])

    def pull_rebase(self, branch: Optional[str] = None) -> bool:
        branch = branch or self.current_branch
        click.echo(f"🔄 Pulling changes with rebase for {branch}...")
        return self._run_command(["git", "pull", "--rebase", "origin", branch])

    def push(self, branch: Optional[str] = None, force: bool = False) -> bool:
        branch = branch or self.current_branch
        click.echo(f"🚀 Pushing to {branch}...")
        cmd = ["git", "push"]
        if force:
            cmd.append("--force")
        cmd.extend(["origin", branch])
        return self._run_command(cmd)

    def run_tests(self) -> bool:
        click.echo("🧪 Running tests...")
        return self._run_command(["npm", "run", "test"])

    def run_lint(self) -> bool:
        click.echo("🔍 Running linting...")
        return self._run_command(["npm", "run", "lint"])

    def check_branch_protection(self, target_branch: str) -> bool:
        if target_branch == "main":
            click.echo(
                "❌ Direct pushes to main branch are not allowed.", err=True)
            click.echo(
                "Please create a pull request from your feature branch to main.")
            return False
        elif target_branch != "dev":
            click.echo(
                f"⚠️  Warning: Pushing to {target_branch} instead of dev branch.")
            click.echo("Consider pushing to dev branch instead.")
        return True


@click.group()
def cli():
    """DevKit CLI - Development workflow automation tool"""
    pass


@cli.command()
@click.argument("branch_type")
@click.argument("branch_name")
def create(branch_type, branch_name):
    """Create a new branch with proper naming convention"""
    valid_types = ["feature", "bugfix", "release", "hotfix"]
    if branch_type not in valid_types:
        click.echo(f"Error: Branch type must be one of {valid_types}")
        sys.exit(1)

    branch = f"{branch_type}/{branch_name}"
    success, _ = run_command(["git", "checkout", "-b", branch])
    if not success:
        sys.exit(1)
    click.echo(f"Created and switched to branch: {branch}")


@cli.command()
@click.argument("target_branch", default="dev")
def push(target_branch):
    """Push changes with pre-push checks"""
    # Check branch protection
    if target_branch == "main":
        click.echo("❌ Direct pushes to main branch are not allowed.", err=True)
        click.echo(
            "Please create a pull request from your feature branch to main.")
        sys.exit(1)

    # Run formatting
    click.echo("Running code formatting...")
    success, _ = run_command(["npm", "run", "format:all"])
    if not success:
        click.echo("❌ Code formatting failed")
        sys.exit(1)

    # Run Python formatting
    click.echo("Running Python formatting...")
    commands = [["black", "."], ["isort", "."],
                ["ruff", "check", ".", "--fix"]]
    for cmd in commands:
        success, _ = run_command(cmd)
        if not success:
            click.echo(f"❌ Python formatting failed: {' '.join(cmd)}")
            sys.exit(1)

    # Verify build works
    click.echo("Verifying build...")
    success, _ = run_command(
        ["npm", "run", "build", "--", "--no-lint"], capture_output=False
    )
    if not success:
        click.echo("❌ Build verification failed")
        sys.exit(1)

    # Run tests
    click.echo("Running tests...")
    success, output = run_command(
        ["npm", "test", "--", "--passWithNoTests", "--coverage=false"],
        capture_output=False,
    )
    if not success:
        click.echo("❌ Tests failed")
        sys.exit(1)

    # Push changes
    click.echo(f"Pushing to {target_branch}...")
    success, _ = run_command(
        ["git", "push", "origin", f"HEAD:{target_branch}"])
    if not success:
        click.echo("❌ Push failed")
        sys.exit(1)

    click.echo("✅ All checks passed and changes pushed successfully!")


@cli.command()
def format():
    """Format all code files"""
    commands = [
        # Python formatting
        ["black", "."],
        ["isort", "."],
        ["ruff", "check", ".", "--fix"],
        # JS/TS formatting if npm exists
        ["npm", "run", "format:all"]
    ]

    for cmd in commands:
        click.echo(f"Running: {' '.join(cmd)}")
        success, _ = run_command(cmd, capture_output=False)
        if not success:
            click.echo(f"❌ Formatting failed: {' '.join(cmd)}")
            sys.exit(1)

    click.echo("✅ All code formatting completed!")


@cli.command()
def setup():
    """Setup development environment"""
    # Create virtual environment
    click.echo("Creating Python virtual environment...")
    success, _ = run_command(["python", "-m", "venv", ".venv"])
    if not success:
        click.echo("❌ Failed to create virtual environment")
        sys.exit(1)

    # Install Python dependencies
    click.echo("Installing Python dependencies...")
    pip_cmd = [".venv/bin/pip", "install", "-e", ".", "-r", "requirements.txt"]
    success, _ = run_command(pip_cmd)
    if not success:
        click.echo("❌ Failed to install Python dependencies")
        sys.exit(1)

    # Try to install npm dependencies if package.json exists
    if Path("package.json").exists():
        click.echo("Installing npm dependencies...")
        success, _ = run_command(["npm", "install"])
        if not success:
            click.echo("❌ Failed to install npm dependencies")
            sys.exit(1)

    click.echo("✅ Development environment setup complete!")
    click.echo("Activate the virtual environment with 'source .venv/bin/activate'")


@cli.command()
def status():
    """Check development environment status"""
    # Check Git status
    click.echo("📊 Git Status:")
    run_command(["git", "status"], capture_output=False)

    # Check Python version
    click.echo("\n📊 Python Version:")
    run_command(["python", "--version"], capture_output=False)

    # Check if virtual environment exists
    venv_path = Path(".venv")
    if venv_path.exists():
        click.echo("✅ Virtual environment found")
    else:
        click.echo("❌ Virtual environment not found")

    # Check if npm is installed
    try:
        click.echo("\n📊 Node.js Status:")
        run_command(["npm", "--version"], capture_output=False)
        if Path("package.json").exists():
            click.echo("✅ package.json found")
        else:
            click.echo("❌ package.json not found")
    except:
        click.echo("❌ npm not installed")


@cli.group()
def version():
    """Version management commands"""
    pass


@version.command()
def current():
    """Show current version"""
    version = get_current_version()
    click.echo(f"Current version: {version}")


@version.command()
@click.argument("version_type", type=click.Choice(["major", "minor", "patch"]))
@click.option("--no-commit", is_flag=True, help="Don't create a commit")
@click.option("--no-tag", is_flag=True, help="Don't create a git tag")
@click.option("--tag-message", help="Custom tag message")
@click.option("--push", is_flag=True, help="Push tag to remote repository")
def bump(version_type, no_commit, no_tag, tag_message, push):
    """Bump version (major, minor, patch)"""
    # Convert version_type to enum
    bump_type = VersionBump[version_type.upper()]

    # Get current version
    current_version = get_current_version()
    click.echo(f"Current version: {current_version}")

    # Bump version
    new_version = bump_version(current_version, bump_type)
    click.echo(f"New version: {new_version}")

    # Update version in files
    update_version_in_files(new_version)
    click.echo("✅ Updated version in files")

    # Create commit
    if not no_commit:
        commit_message = f"chore: bump version to {new_version}"
        if not commit_version_change(commit_message, bump_type):
            click.echo("❌ Failed to create version commit")
            sys.exit(1)
        click.echo(f"✅ Created version commit")

    # Create tag
    if not no_tag:
        tag_name = f"v{new_version}"
        if not tag_message:
            tag_message = f"Version {new_version}"

        if not create_git_tag(tag_name, tag_message):
            click.echo("❌ Failed to create git tag")
            sys.exit(1)
        click.echo(f"✅ Created git tag {tag_name}")

        # Push tag if requested
        if push:
            if not push_git_tag(tag_name):
                click.echo("❌ Failed to push git tag")
                sys.exit(1)
            click.echo(f"✅ Pushed tag {tag_name}")

    click.echo(f"✅ Version bumped to {new_version}")


@version.command()
@click.argument("version")
@click.option("--tag-message", help="Custom tag message")
@click.option("--push", is_flag=True, help="Push tag to remote repository")
def set(version, tag_message, push):
    """Set specific version"""
    # Validate version format
    if not version.replace(".", "").isdigit():
        click.echo(
            "❌ Invalid version format. Use semantic versioning (e.g., 1.2.3)")
        sys.exit(1)

    # Get current version
    current_version = get_current_version()
    click.echo(f"Current version: {current_version}")

    # Update version in files
    update_version_in_files(version)
    click.echo("✅ Updated version in files")

    # Create commit
    commit_message = f"chore: set version to {version}"
    if not commit_version_change(commit_message):
        click.echo("❌ Failed to create version commit")
        sys.exit(1)
    click.echo(f"✅ Created version commit")

    # Create tag
    tag_name = f"v{version}"
    if not tag_message:
        tag_message = f"Version {version}"

    if not create_git_tag(tag_name, tag_message):
        click.echo("❌ Failed to create git tag")
        sys.exit(1)
    click.echo(f"✅ Created git tag {tag_name}")

    # Push tag if requested
    if push:
        if not push_git_tag(version):
            click.echo("❌ Failed to push git tag")
            sys.exit(1)
        click.echo(f"✅ Pushed tag v{version}")

    click.echo(f"✅ Version set to {version}")


@cli.group()
def docker():
    """Docker image management"""
    if not DOCKER_AVAILABLE:
        click.echo("❌ Docker functionality not available.")
        click.echo("Make sure the docker module is installed.")
        sys.exit(1)

    if not check_docker_installed():
        click.echo("❌ Docker is not installed or not in PATH.")
        sys.exit(1)


@docker.command()
@click.option("--dockerfile", default="Dockerfile", help="Path to Dockerfile")
@click.option("--context", default=".", help="Path to build context")
@click.option("--name", help="Name for the image (default: project name)")
@click.option("--no-cache", is_flag=True, help="Disable Docker build cache")
@click.option("--platform", help="Target platform (e.g., linux/amd64)")
def build(dockerfile, context, name, no_cache, platform):
    """Build Docker image"""
    try:
        # Use project name if name not provided
        if not name:
            project_name = Path.cwd().name
            version = get_current_version()
            name = f"{project_name}:{version}"

        click.echo(f"🔨 Building Docker image {name}...")

        image_name = build_docker_image(
            dockerfile_path=dockerfile,
            context_path=context,
            image_name=name,
            cache=not no_cache,
            platform=platform
        )

        click.echo(f"✅ Built Docker image: {image_name}")
        return image_name
    except DockerError as e:
        click.echo(f"❌ {e}")
        sys.exit(1)


@docker.command()
@click.argument("source_image")
@click.argument("registry_path")
@click.option("--push", is_flag=True, help="Push images to registry")
@click.option("--no-latest", is_flag=True, help="Don't include latest tag")
@click.option("--chainguard", is_flag=True, help="Include Chainguard-specific tags")
def tag(source_image, registry_path, push, no_latest, chainguard):
    """Tag Docker image with semantic versions"""
    try:
        # Get version from the current package
        version = get_current_version()

        # Generate tags
        tags = generate_docker_tags(
            registry_path,
            version,
            include_latest=not no_latest,
            chainguard_tags=chainguard
        )

        click.echo(f"🔖 Tagging Docker image {source_image} with:")
        for tag in tags:
            click.echo(f"  - {tag}")

        # Tag the images
        tagged_images = tag_docker_image(source_image, tags)

        if not tagged_images:
            click.echo("❌ Failed to tag any images")
            sys.exit(1)

        click.echo(f"✅ Tagged {len(tagged_images)} Docker images")

        # Push images if requested
        if push:
            click.echo("🚀 Pushing images to registry...")
            pushed_images = push_docker_image(tags)

            if not pushed_images:
                click.echo("❌ Failed to push any images")
                sys.exit(1)

            click.echo(f"✅ Pushed {len(pushed_images)} Docker images")

    except DockerError as e:
        click.echo(f"❌ {e}")
        sys.exit(1)


@docker.command()
@click.option("--dockerfile", default="Dockerfile", help="Path to Dockerfile")
@click.option("--context", default=".", help="Path to build context")
@click.option("--registry", help="Docker registry path (e.g., username/repo)")
@click.option("--no-cache", is_flag=True, help="Disable Docker build cache")
@click.option("--no-latest", is_flag=True, help="Don't include latest tag")
@click.option("--push", is_flag=True, help="Push images to registry")
@click.option("--chainguard", is_flag=True, help="Include Chainguard-specific tags")
@click.option("--platform", help="Target platform (e.g., linux/amd64)")
@click.option("--test", is_flag=True, help="Test the image after building")
def release(dockerfile, context, registry, no_cache, no_latest, push, chainguard, platform, test):
    """Build, tag and optionally push Docker image"""
    try:
        # Get version
        version = get_current_version()

        # Use project name if registry not provided
        if not registry:
            registry = Path.cwd().name

        # First build the image
        image_name = f"{registry}:{version}"
        click.echo(f"🔨 Building Docker image {image_name}...")

        built_image = build_docker_image(
            dockerfile_path=dockerfile,
            context_path=context,
            image_name=image_name,
            cache=not no_cache,
            platform=platform
        )

        click.echo(f"✅ Built Docker image: {built_image}")

        # Test the image if requested
        if test:
            click.echo(f"🧪 Testing Docker image {built_image}...")
            success, output = test_docker_image(built_image)
            if not success:
                click.echo(f"❌ Docker image test failed: {output}")
                sys.exit(1)
            click.echo(f"✅ Docker image test passed")
            click.echo(output)

        # Generate tags
        tags = generate_docker_tags(
            registry,
            version,
            include_latest=not no_latest,
            chainguard_tags=chainguard
        )

        # Filter out the main tag which is already built
        tags = [tag for tag in tags if tag != built_image]

        if tags:
            click.echo(f"🔖 Tagging Docker image with additional tags:")
            for tag in tags:
                click.echo(f"  - {tag}")

            # Tag the images
            tagged_images = tag_docker_image(built_image, tags)

            if not tagged_images:
                click.echo("❌ Failed to tag any images")
                sys.exit(1)

            click.echo(
                f"✅ Tagged {len(tagged_images)} additional Docker images")

        # Push images if requested
        if push:
            # Include the built image in the push
            all_tags = [built_image] + tags

            click.echo("🚀 Pushing images to registry...")
            pushed_images = push_docker_image(all_tags)

            if not pushed_images:
                click.echo("❌ Failed to push any images")
                sys.exit(1)

            click.echo(f"✅ Pushed {len(pushed_images)} Docker images")

    except DockerError as e:
        click.echo(f"❌ {e}")
        sys.exit(1)


@docker.command()
@click.argument("image_name")
@click.option("--command", "-c", help="Command to run in the container")
def test(image_name, command):
    """Test a Docker image by running it with a command"""
    try:
        click.echo(f"🧪 Testing Docker image {image_name}...")

        test_cmd = None
        if command:
            test_cmd = command.split()

        success, output = test_docker_image(image_name, test_cmd)
        if not success:
            click.echo(f"❌ Docker image test failed: {output}")
            sys.exit(1)

        click.echo(f"✅ Docker image test passed")
        click.echo(output)
    except DockerError as e:
        click.echo(f"❌ {e}")
        sys.exit(1)


@docker.command()
@click.argument("image_name")
@click.option("--output", "-o", type=click.Choice(["text", "json"]), default="text",
              help="Output format")
def scan(image_name, output):
    """Scan a Docker image for vulnerabilities"""
    try:
        click.echo(
            f"🔍 Scanning Docker image {image_name} for vulnerabilities...")

        success, scan_results = scan_docker_image(
            image_name, output_format=output)

        if output == "json":
            # For JSON output, print the formatted result
            click.echo(json.dumps(scan_results, indent=2))
        else:
            # For text output, just print the result directly
            click.echo(scan_results)

        # Exit with appropriate code
        if not success:
            click.echo("❌ Critical vulnerabilities found!")
            sys.exit(1)
        else:
            click.echo("✅ No critical vulnerabilities found")
    except DockerError as e:
        click.echo(f"❌ {e}")
        sys.exit(1)


@docker.command()
@click.argument("image_name")
@click.option("--output-file", "-o", help="Output file path for SBOM")
@click.option("--format", "-f", default="spdx-json",
              type=click.Choice(["spdx-json", "cyclonedx-json"]),
              help="SBOM format")
def sbom(image_name, output_file, format):
    """Generate SBOM for a Docker image"""
    try:
        click.echo(f"📄 Generating SBOM for {image_name}...")

        success, output = generate_sbom(image_name, output_file, format)

        if not success:
            click.echo(f"❌ SBOM generation failed: {output}")
            sys.exit(1)

        click.echo(f"✅ SBOM generated: {output}")
    except Exception as e:
        click.echo(f"❌ Error generating SBOM: {e}")
        sys.exit(1)


@docker.command()
@click.argument("image_name")
@click.option("--key", "-k", help="Path to Cosign private key")
def sign(image_name, key):
    """Sign a Docker image with Cosign"""
    try:
        click.echo(f"🔏 Signing image {image_name}...")

        success, output = sign_image(image_name, key)

        if not success:
            click.echo(f"❌ Image signing failed: {output}")
            sys.exit(1)

        click.echo(f"✅ Image signed successfully")
    except Exception as e:
        click.echo(f"❌ Error signing image: {e}")
        sys.exit(1)


@docker.command()
@click.argument("image_name")
@click.option("--key", "-k", help="Path to Cosign public key")
def verify(image_name, key):
    """Verify a Docker image signature"""
    try:
        click.echo(f"🔍 Verifying signature for {image_name}...")

        success, output = verify_image_signature(image_name, key)

        if not success:
            click.echo(f"❌ Signature verification failed: {output}")
            sys.exit(1)

        click.echo(f"✅ Signature verified successfully")
        click.echo(output)
    except Exception as e:
        click.echo(f"❌ Error verifying signature: {e}")
        sys.exit(1)


@docker.command()
@click.option("--dockerfile", default="Dockerfile", help="Path to Dockerfile")
@click.option("--context", default=".", help="Path to build context")
@click.option("--name", help="Name for the image (default: project name)")
@click.option("--registry", help="Container registry path (e.g., username/repo)")
@click.option("--build-args", help="Build arguments (key=value,key2=value2)")
@click.option("--policy", "-p", multiple=True, help="Path(s) to Kyverno policy file(s)")
@click.option("--k8s-manifest", help="Path to Kubernetes manifest to check")
@click.option("--signing-key", help="Path to Cosign signing key")
@click.option("--push", is_flag=True, help="Push to registry")
@click.option("--json", "json_output", is_flag=True, help="Output results as JSON")
def secure(dockerfile, context, name, registry, build_args, policy, k8s_manifest, signing_key, push, json_output):
    """Run a complete secure delivery pipeline"""
    try:
        # Parse build args if provided
        build_args_dict = {}
        if build_args:
            for arg_pair in build_args.split(","):
                key, value = arg_pair.split("=", 1)
                build_args_dict[key] = value

        # Generate name if not provided
        if not name:
            project_name = Path.cwd().name
            version = get_current_version()
            name = f"{project_name}:{version}"

        # Convert policy list to None if empty
        policy_files = list(policy) if policy else None

        click.echo("🔒 Running secure delivery pipeline...")

        # Run the secure pipeline
        results = secure_pipeline(
            dockerfile_path=dockerfile,
            context_path=context,
            image_name=name,
            registry=registry,
            build_args=build_args_dict,
            policy_files=policy_files,
            k8s_manifest=k8s_manifest,
            signing_key=signing_key,
            push=push
        )

        # Output results
        if json_output:
            click.echo(json.dumps(results, indent=2))
        else:
            # Summary already printed by secure_pipeline function
            pass

        # Exit with error if any critical step failed
        if not results["build"]["success"]:
            sys.exit(1)
        if "scan" in results and not results["scan"]["success"]:
            sys.exit(1)
        if "policy" in results and not results["policy"]["success"]:
            sys.exit(1)

        click.echo("✅ Secure delivery pipeline completed successfully!")
    except Exception as e:
        click.echo(f"❌ Secure pipeline failed: {str(e)}")
        sys.exit(1)

# Health check endpoints for Kubernetes probes


@cli.group()
def health():
    """Health check commands for container health probes"""
    pass


@health.command()
def live():
    """Liveness probe endpoint"""
    try:
        # Check if the process is alive and responsive
        version = get_current_version()
        click.echo(json.dumps({
            "status": "ok",
            "version": version,
            "timestamp": subprocess.check_output(["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"]).decode().strip()
        }))
    except Exception as e:
        click.echo(json.dumps({
            "status": "error",
            "error": str(e)
        }), err=True)
        sys.exit(1)


@health.command()
def ready():
    """Readiness probe endpoint"""
    try:
        # Check if the application is ready to serve requests
        # This could include checking database connectivity, etc.
        dependencies_ok = True

        # Add any additional dependency checks here
        # Example: check database connection
        # db_connection = check_database_connection()
        # dependencies_ok = dependencies_ok and db_connection

        if dependencies_ok:
            click.echo(json.dumps({
                "status": "ready",
                "version": get_current_version(),
                "timestamp": subprocess.check_output(["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"]).decode().strip()
            }))
        else:
            click.echo(json.dumps({
                "status": "not_ready",
                "message": "Dependencies not ready"
            }), err=True)
            sys.exit(1)
    except Exception as e:
        click.echo(json.dumps({
            "status": "error",
            "error": str(e)
        }), err=True)
        sys.exit(1)


@health.command()
def started():
    """Startup probe endpoint"""
    try:
        # Check if the application has completed startup procedures
        click.echo(json.dumps({
            "status": "started",
            "version": get_current_version(),
            "timestamp": subprocess.check_output(["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"]).decode().strip()
        }))
    except Exception as e:
        click.echo(json.dumps({
            "status": "error",
            "error": str(e)
        }), err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
