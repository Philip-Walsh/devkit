#!/usr/bin/env python3

import os
import subprocess
import time
from typing import List, Optional, Dict, Tuple

from devkit.versioning import get_current_version


class DockerError(Exception):
    """Exception raised for Docker-related errors"""
    pass


def check_docker_installed() -> bool:
    """
    Check if Docker is installed and available

    Returns:
        bool: True if Docker is installed, False otherwise
    """
    try:
        subprocess.run(
            ["docker", "--version"],
            capture_output=True,
            check=True
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def build_docker_image(
    dockerfile_path: str = "Dockerfile",
    context_path: str = ".",
    image_name: Optional[str] = None,
    build_args: Optional[dict] = None,
    cache: bool = True,
    platform: Optional[str] = None,
) -> str:
    """
    Build a Docker image

    Args:
        dockerfile_path: Path to the Dockerfile
        context_path: Path to the build context
        image_name: Name for the image (optional)
        build_args: Dictionary of build arguments (optional)
        cache: Whether to use Docker build cache
        platform: Target platform (e.g., linux/amd64, linux/arm64)

    Returns:
        str: The built image name with tag

    Raises:
        DockerError: If Docker build fails
    """
    if not check_docker_installed():
        raise DockerError("Docker is not installed or not in PATH")

    if not os.path.exists(dockerfile_path):
        raise DockerError(f"Dockerfile not found at {dockerfile_path}")

    # Generate image name if not provided
    if not image_name:
        # Get the project name (current directory name)
        project_name = os.path.basename(os.path.abspath("."))
        version = get_current_version()
        image_name = f"{project_name}:{version}"

    # Prepare the build command
    cmd = ["docker", "build"]

    # Add build args
    if build_args:
        for key, value in build_args.items():
            cmd.extend(["--build-arg", f"{key}={value}"])

    # Add platform if specified
    if platform:
        cmd.extend(["--platform", platform])

    # Add image name (tag)
    cmd.extend(["-t", image_name])

    # Add Dockerfile path
    cmd.extend(["-f", dockerfile_path])

    # Disable cache if needed
    if not cache:
        cmd.append("--no-cache")

    # Add context path
    cmd.append(context_path)

    try:
        subprocess.run(cmd, check=True)
        return image_name
    except subprocess.CalledProcessError as e:
        raise DockerError(f"Docker build failed: {e}")


def tag_docker_image(
    source_image: str,
    target_tags: List[str]
) -> List[str]:
    """
    Tag a Docker image with multiple tags

    Args:
        source_image: Source image name with tag
        target_tags: List of target tags

    Returns:
        List[str]: List of successfully tagged images

    Raises:
        DockerError: If Docker tag operation fails
    """
    if not check_docker_installed():
        raise DockerError("Docker is not installed or not in PATH")

    successful_tags = []

    for tag in target_tags:
        try:
            subprocess.run(
                ["docker", "tag", source_image, tag],
                check=True
            )
            successful_tags.append(tag)
        except subprocess.CalledProcessError as e:
            print(f"Error tagging {source_image} as {tag}: {e}")

    return successful_tags


def push_docker_image(tags: List[str]) -> List[str]:
    """
    Push Docker images to a registry

    Args:
        tags: List of image tags to push

    Returns:
        List[str]: List of successfully pushed images

    Raises:
        DockerError: If Docker push operation fails
    """
    if not check_docker_installed():
        raise DockerError("Docker is not installed or not in PATH")

    successful_pushes = []

    for tag in tags:
        try:
            subprocess.run(
                ["docker", "push", tag],
                check=True
            )
            successful_pushes.append(tag)
        except subprocess.CalledProcessError as e:
            print(f"Error pushing {tag}: {e}")

    return successful_pushes


def generate_docker_tags(
    base_name: str,
    version: str,
    include_latest: bool = True,
    chainguard_tags: bool = False,
) -> List[str]:
    """
    Generate Docker tags following best practices

    Args:
        base_name: Base name for the Docker image
        version: Semantic version (e.g., "1.2.3")
        include_latest: Whether to include 'latest' tag
        chainguard_tags: Whether to include Chainguard-specific tags

    Returns:
        List[str]: List of tags
    """
    # Split version into components
    version_parts = version.split('.')

    # Generate tags
    tags = [
        f"{base_name}:{version}",  # Full version: org/name:1.2.3
        # Minor version: org/name:1.2
        f"{base_name}:{version_parts[0]}.{version_parts[1]}"
    ]

    # Add major version tag
    tags.append(f"{base_name}:{version_parts[0]}")  # Major version: org/name:1

    # Add latest tag if requested
    if include_latest:
        tags.append(f"{base_name}:latest")

    # Add Chainguard-specific tags if requested
    if chainguard_tags:
        # Chainguard uses versioning scheme that includes additional formats
        tags.extend([
            # Static version tag format
            f"{base_name}:v{version}",
            # Date-based versioning used by Chainguard
            f"{base_name}:{version_parts[0]}.{version_parts[1]}-chainguard",
            # Static tag for latest "secure" version
            f"{base_name}:secure",
        ])

    return tags


def test_docker_image(image_name: str, test_cmd: Optional[List[str]] = None) -> Tuple[bool, str]:
    """
    Test that a Docker image works properly by running it with a test command

    Args:
        image_name: The Docker image name with tag
        test_cmd: Command to run in the container (default: --help)

    Returns:
        Tuple[bool, str]: Success status and output
    """
    if not check_docker_installed():
        raise DockerError("Docker is not installed or not in PATH")

    # Default test command if none provided
    if test_cmd is None:
        test_cmd = ["--help"]

    container_name = f"test-{int(time.time())}"

    try:
        # Run the container with the test command
        result = subprocess.run(
            ["docker", "run", "--rm", "--name",
                container_name, image_name] + test_cmd,
            capture_output=True,
            text=True,
            check=True
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        # Try to stop and remove container in case it's still running
        try:
            subprocess.run(["docker", "rm", "-f", container_name],
                           check=False, capture_output=True)
        except:
            pass
        return False, f"Error testing Docker image: {e.stderr}"


def scan_docker_image(image_name: str) -> Tuple[bool, Dict]:
    """
    Scan Docker image for vulnerabilities using Trivy

    Args:
        image_name: The Docker image name with tag

    Returns:
        Tuple[bool, Dict]: Success status and scan results
    """
    if not check_docker_installed():
        raise DockerError("Docker is not installed or not in PATH")

    try:
        # Check if Trivy is installed
        subprocess.run(["trivy", "--version"],
                       capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        raise DockerError("Trivy is not installed or not in PATH")

    try:
        # Run Trivy scan and output as JSON
        result = subprocess.run(
            ["trivy", "image", "--format", "json", image_name],
            capture_output=True,
            text=True,
            check=True
        )

        # Simple parsing to determine if there are critical vulnerabilities
        has_critical = "CRITICAL" in result.stdout
        has_high = "HIGH" in result.stdout

        scan_result = {
            "has_critical": has_critical,
            "has_high": has_high,
            "output": result.stdout
        }

        # Consider the scan successful if no critical vulnerabilities
        return not has_critical, scan_result
    except subprocess.CalledProcessError as e:
        return False, {"error": f"Error scanning Docker image: {e.stderr}"}
