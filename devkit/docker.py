#!/usr/bin/env python3

import os
import subprocess
from typing import List, Optional

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
) -> str:
    """
    Build a Docker image

    Args:
        dockerfile_path: Path to the Dockerfile
        context_path: Path to the build context
        image_name: Name for the image (optional)
        build_args: Dictionary of build arguments (optional)
        cache: Whether to use Docker build cache

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
    include_latest: bool = True
) -> List[str]:
    """
    Generate Docker tags following best practices

    Args:
        base_name: Base name for the Docker image
        version: Semantic version (e.g., "1.2.3")
        include_latest: Whether to include 'latest' tag

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

    return tags
