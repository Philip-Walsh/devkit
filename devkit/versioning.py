#!/usr/bin/env python3

import re
import subprocess
from enum import Enum
from typing import Optional, Tuple


class VersionBump(Enum):
    """Version bump types following semantic versioning"""
    MAJOR = "major"
    MINOR = "minor"
    PATCH = "patch"


def get_current_version() -> str:
    """
    Get the current version from __init__.py

    Returns:
        str: The current version
    """
    try:
        from devkit import __version__
        return __version__
    except ImportError:
        return "0.0.0"


def parse_semantic_version(version: str) -> Tuple[int, int, int]:
    """
    Parse a semantic version string into its components

    Args:
        version: Semantic version string (e.g., "1.2.3")

    Returns:
        Tuple: (major, minor, patch) version numbers
    """
    match = re.match(r'^(\d+)\.(\d+)\.(\d+)$', version)
    if not match:
        raise ValueError(f"Invalid semantic version format: {version}")

    return int(match.group(1)), int(match.group(2)), int(match.group(3))


def bump_version(current_version: str, bump_type: VersionBump) -> str:
    """
    Bump the version according to semantic versioning rules

    Args:
        current_version: Current semantic version string
        bump_type: Type of version bump to perform

    Returns:
        str: New version string
    """
    major, minor, patch = parse_semantic_version(current_version)

    if bump_type == VersionBump.MAJOR:
        return f"{major + 1}.0.0"
    elif bump_type == VersionBump.MINOR:
        return f"{major}.{minor + 1}.0"
    elif bump_type == VersionBump.PATCH:
        return f"{major}.{minor}.{patch + 1}"

    raise ValueError(f"Invalid bump type: {bump_type}")


def update_version_in_files(new_version: str) -> bool:
    """
    Update version in all relevant files

    Args:
        new_version: New version to set

    Returns:
        bool: Success status
    """
    # Update in __init__.py
    try:
        with open("devkit/__init__.py", "r") as f:
            content = f.read()

        new_content = re.sub(
            r'__version__\s*=\s*"[^"]+"',
            f'__version__ = "{new_version}"',
            content
        )

        with open("devkit/__init__.py", "w") as f:
            f.write(new_content)

        # Update in setup.py
        with open("setup.py", "r") as f:
            content = f.read()

        new_content = re.sub(
            r'version="[^"]+"',
            f'version="{new_version}"',
            content
        )

        with open("setup.py", "w") as f:
            f.write(new_content)

        return True
    except Exception as e:
        print(f"Error updating version in files: {e}")
        return False


def create_git_tag(version: str, message: Optional[str] = None) -> bool:
    """
    Create a git tag for the current commit

    Args:
        version: Version to use for the tag (without 'v' prefix)
        message: Optional tag message

    Returns:
        bool: Success status
    """
    tag = f"v{version}"
    try:
        if message:
            subprocess.run(
                ["git", "tag", "-a", tag, "-m", message], check=True)
        else:
            default_message = f"Release {tag}"
            subprocess.run(["git", "tag", "-a", tag, "-m",
                           default_message], check=True)

        return True
    except subprocess.CalledProcessError as e:
        print(f"Error creating git tag: {e}")
        return False


def push_git_tag(version: str) -> bool:
    """
    Push a git tag to the remote repository

    Args:
        version: Version to push (without 'v' prefix)

    Returns:
        bool: Success status
    """
    tag = f"v{version}"
    try:
        subprocess.run(["git", "push", "origin", tag], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error pushing git tag: {e}")
        return False


def get_latest_git_tag() -> Optional[str]:
    """
    Get the latest git tag (semver only)

    Returns:
        str or None: Latest git tag without 'v' prefix, or None if no tags
    """
    try:
        result = subprocess.run(
            ["git", "tag", "--sort=-v:refname"],
            capture_output=True,
            text=True,
            check=True
        )

        tags = result.stdout.strip().split('\n')
        for tag in tags:
            # Match only semantic versioning tags
            if re.match(r'^v\d+\.\d+\.\d+$', tag):
                # Remove 'v' prefix
                return tag[1:]

        return None
    except subprocess.CalledProcessError:
        return None


def commit_version_change(version: str, bump_type: VersionBump) -> bool:
    """
    Commit version changes with proper conventional commit message

    Args:
        version: New version 
        bump_type: Type of version change

    Returns:
        bool: Success status
    """
    try:
        # Stage the files
        subprocess.run(
            ["git", "add", "devkit/__init__.py", "setup.py"], check=True)

        # Create commit with conventional message
        message = f"chore(release): bump version to {version}"
        if bump_type == VersionBump.MAJOR:
            message = f"chore(release): bump major version to {version}"
        elif bump_type == VersionBump.MINOR:
            message = f"chore(release): bump minor version to {version}"

        subprocess.run(["git", "commit", "-m", message], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error committing version change: {e}")
        return False
