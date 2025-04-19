#!/usr/bin/env python3

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
        generate_docker_tags,
        push_docker_image,
        tag_docker_image,
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
    click.echo("Formatting JavaScript/TypeScript files...")
    success, _ = run_command(["npm", "run", "format:all"])
    if not success:
        sys.exit(1)

    click.echo("Formatting Python files...")
    commands = [["black", "."], ["isort", "."],
                ["ruff", "check", ".", "--fix"]]
    for cmd in commands:
        success, _ = run_command(cmd)
        if not success:
            sys.exit(1)

    click.echo("✅ Formatting complete!")


@cli.command()
def setup():
    """Setup development environment"""
    click.echo("Installing npm dependencies...")
    success, _ = run_command(["npm", "install"])
    if not success:
        sys.exit(1)

    click.echo("Installing Python dependencies...")
    commands = [
        ["pip", "install", "-e", "."],
        ["pip", "install", "black", "isort", "ruff"],
    ]
    for cmd in commands:
        success, _ = run_command(cmd)
        if not success:
            sys.exit(1)

    click.echo("Setting up git hooks...")
    success, _ = run_command(["npx", "husky", "install"])
    if not success:
        sys.exit(1)

    click.echo("✅ Setup complete!")


@cli.command()
def status():
    """Check development environment status"""
    all_good = True

    click.echo("Checking npm dependencies...")
    success, _ = run_command(["npm", "list", "--depth=0"])
    if not success:
        all_good = False

    click.echo("\nChecking Python dependencies...")
    success, _ = run_command(["pip", "list"])
    if not success:
        all_good = False

    click.echo("\nChecking git hooks...")
    if Path(".husky").exists():
        click.echo("✅ Git hooks are installed")
    else:
        click.echo("❌ Git hooks are not installed")
        all_good = False

    if not all_good:
        sys.exit(1)


@cli.group()
def version():
    """Version management commands"""
    pass


@version.command()
def current():
    """Get current version"""
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
    # Get current version
    current_version = get_current_version()
    click.echo(f"Current version: {current_version}")

    # Map to enum
    bump_type = VersionBump(version_type)

    # Calculate new version
    new_version = bump_version(current_version, bump_type)
    click.echo(f"New version: {new_version}")

    # Update version in files
    if not update_version_in_files(new_version):
        click.echo("❌ Failed to update version in files")
        sys.exit(1)

    # Commit changes
    if not no_commit:
        if not commit_version_change(new_version, bump_type):
            click.echo("❌ Failed to commit version change")
            sys.exit(1)
        click.echo("✅ Version change committed")

    # Create git tag
    if not no_tag:
        if not create_git_tag(new_version, tag_message):
            click.echo("❌ Failed to create git tag")
            sys.exit(1)
        click.echo(f"✅ Created tag v{new_version}")

        # Push tag
        if push:
            if not push_git_tag(new_version):
                click.echo("❌ Failed to push git tag")
                sys.exit(1)
            click.echo(f"✅ Pushed tag v{new_version}")

    click.echo(f"✅ Version bumped to {new_version}")


@version.command()
@click.argument("version")
@click.option("--tag-message", help="Custom tag message")
@click.option("--push", is_flag=True, help="Push tag to remote repository")
def set(version, tag_message, push):
    """Set version to specific value"""
    # Get current version
    current_version = get_current_version()
    click.echo(f"Current version: {current_version}")

    # Update version in files
    if not update_version_in_files(version):
        click.echo("❌ Failed to update version in files")
        sys.exit(1)

    # Commit changes
    try:
        # Stage the files
        subprocess.run(
            ["git", "add", "devkit/__init__.py", "setup.py"], check=True)

        # Create commit with conventional message
        message = f"chore(release): set version to {version}"
        subprocess.run(["git", "commit", "-m", message], check=True)
        click.echo("✅ Version change committed")
    except subprocess.CalledProcessError:
        click.echo("❌ Failed to commit version change")

    # Create git tag
    if not create_git_tag(version, tag_message):
        click.echo("❌ Failed to create git tag")
        sys.exit(1)
    click.echo(f"✅ Created tag v{version}")

    # Push tag
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
def build(dockerfile, context, name, no_cache):
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
            cache=not no_cache
        )

        click.echo(f"✅ Built Docker image: {image_name}")
    except DockerError as e:
        click.echo(f"❌ {e}")
        sys.exit(1)


@docker.command()
@click.argument("source_image")
@click.argument("registry_path")
@click.option("--push", is_flag=True, help="Push images to registry")
@click.option("--no-latest", is_flag=True, help="Don't include latest tag")
def tag(source_image, registry_path, push, no_latest):
    """Tag Docker image with semantic versions"""
    try:
        # Get version from the current package
        version = get_current_version()

        # Generate tags
        tags = generate_docker_tags(
            registry_path,
            version,
            include_latest=not no_latest
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
def release(dockerfile, context, registry, no_cache, no_latest, push):
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
            cache=not no_cache
        )

        click.echo(f"✅ Built Docker image: {built_image}")

        # Generate tags
        tags = generate_docker_tags(
            registry,
            version,
            include_latest=not no_latest
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


if __name__ == "__main__":
    cli()
