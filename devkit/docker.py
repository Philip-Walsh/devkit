#!/usr/bin/env python3

import os
import subprocess
import time
import json
import tempfile
from typing import List, Optional, Dict, Tuple, Union

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


def check_tool_installed(tool_name: str) -> bool:
    """
    Check if a tool is installed and available

    Args:
        tool_name: Name of the tool to check

    Returns:
        bool: True if the tool is installed, False otherwise
    """
    try:
        subprocess.run(
            [tool_name, "--version"],
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
        date_str = time.strftime("%Y%m%d")
        # Date-based tag: org/name:20230501
        tags.append(f"{base_name}:{date_str}")
        # Commit hash tag if git is available
        try:
            git_hash = subprocess.check_output(
                ["git", "rev-parse", "--short", "HEAD"],
                text=True
            ).strip()
            # Git hash tag: org/name:a1b2c3d
            tags.append(f"{base_name}:{git_hash}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

    return tags


def test_docker_image(image_name: str, test_cmd: Optional[List[str]] = None) -> Tuple[bool, str]:
    """
    Test a Docker image by running it with a command

    Args:
        image_name: The Docker image name with tag
        test_cmd: The command to run (optional)

    Returns:
        Tuple[bool, str]: Success status and output/error
    """
    if not check_docker_installed():
        raise DockerError("Docker is not installed or not in PATH")

    # Generate a unique container name
    container_name = f"test-{int(time.time())}"

    # Default command if none provided
    if not test_cmd:
        test_cmd = ["echo", "Container test successful"]

    # Run the container with the test command
    cmd = ["docker", "run", "--name", container_name, "--rm", image_name]
    if isinstance(test_cmd, str):
        cmd.append(test_cmd)
    else:
        cmd.extend(test_cmd)

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        return True, result.stdout.strip()
    except subprocess.CalledProcessError as e:
        # Try to stop and remove container in case it's still running
        try:
            subprocess.run(["docker", "rm", "-f", container_name],
                           check=False, capture_output=True)
        except:
            pass
        return False, f"Error testing Docker image: {e.stderr}"


def scan_docker_image(image_name: str, output_format: str = "text") -> Tuple[bool, Union[Dict, str]]:
    """
    Scan Docker image for vulnerabilities using Trivy

    Args:
        image_name: The Docker image name with tag
        output_format: Output format ("text" or "json")

    Returns:
        Tuple[bool, Union[Dict, str]]: Success status and scan results
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
        # Run Trivy scan
        fmt = "json" if output_format == "json" else "table"
        result = subprocess.run(
            ["trivy", "image", "--format", fmt, image_name],
            capture_output=True,
            text=True,
            check=True
        )

        # Parse results based on format
        if output_format == "json":
            # Parse JSON output
            scan_data = json.loads(result.stdout)

            # Extract vulnerability counts
            vuln_counts = {"CRITICAL": 0, "HIGH": 0,
                           "MEDIUM": 0, "LOW": 0, "UNKNOWN": 0}

            for results in scan_data.get("Results", []):
                for vuln in results.get("Vulnerabilities", []):
                    severity = vuln.get("Severity", "UNKNOWN")
                    if severity in vuln_counts:
                        vuln_counts[severity] += 1

            # Determine success (no critical vulnerabilities)
            return vuln_counts["CRITICAL"] == 0, {
                "vulnerability_counts": vuln_counts,
                "raw_data": scan_data
            }
        else:
            # Simple parsing for text output
            has_critical = "CRITICAL" in result.stdout
            return not has_critical, result.stdout
    except subprocess.CalledProcessError as e:
        error_msg = f"Error scanning Docker image: {e.stderr}"
        return False, error_msg if output_format == "text" else {"error": error_msg}


def generate_sbom(image_name: str, output_file: Optional[str] = None, format: str = "spdx-json") -> Tuple[bool, str]:
    """
    Generate Software Bill of Materials (SBOM) for a Docker image

    Args:
        image_name: The Docker image name with tag
        output_file: Path to save the SBOM (optional)
        format: SBOM format (e.g., spdx-json, cyclonedx-json)

    Returns:
        Tuple[bool, str]: Success status and output file path or error message
    """
    # Try syft first (preferred)
    if check_tool_installed("syft"):
        try:
            cmd = ["syft", image_name, "-o", format]

            if output_file:
                cmd.extend(["-f", output_file])
                result = subprocess.run(cmd, check=True)
                return True, output_file
            else:
                # Create a temporary file if no output file is specified
                with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
                    temp_path = tmp.name

                cmd.extend(["-f", temp_path])
                result = subprocess.run(cmd, check=True)
                return True, temp_path
        except subprocess.CalledProcessError as e:
            return False, f"Error generating SBOM with syft: {e}"

    # Fallback to Docker Scout if available
    elif check_tool_installed("docker-scout"):
        try:
            cmd = ["docker", "scout", "sbom", image_name]

            if output_file:
                cmd.extend(["--output", output_file])
                result = subprocess.run(cmd, check=True)
                return True, output_file
            else:
                result = subprocess.run(
                    cmd, capture_output=True, text=True, check=True)

                # Create a temporary file to store the SBOM
                with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
                    tmp.write(result.stdout)
                    temp_path = tmp.name

                return True, temp_path
        except subprocess.CalledProcessError as e:
            return False, f"Error generating SBOM with Docker Scout: {e}"

    # If no SBOM tools are available
    else:
        return False, "No SBOM generation tools found. Please install syft or Docker Scout."


def sign_image(image_name: str, key_path: Optional[str] = None) -> Tuple[bool, str]:
    """
    Sign a Docker image using Cosign

    Args:
        image_name: The Docker image name with tag
        key_path: Path to the Cosign private key (optional, for keyless signing)

    Returns:
        Tuple[bool, str]: Success status and output or error message
    """
    if not check_tool_installed("cosign"):
        return False, "Cosign is not installed or not in PATH"

    try:
        # Keyless signing if no key is provided
        if not key_path:
            # Check if running in CI
            if "GITHUB_ACTIONS" in os.environ:
                cmd = ["cosign", "sign", image_name]
            else:
                return False, "Keyless signing requires CI environment or explicit key path"
        else:
            # Sign with key if provided
            cmd = ["cosign", "sign", "--key", key_path, image_name]

        result = subprocess.run(
            cmd, capture_output=True, text=True, check=True)
        return True, "Image signed successfully"
    except subprocess.CalledProcessError as e:
        return False, f"Error signing image: {e.stderr}"


def verify_image_signature(image_name: str, key_path: Optional[str] = None) -> Tuple[bool, str]:
    """
    Verify a Docker image signature

    Args:
        image_name: The Docker image name with tag
        key_path: Path to the Cosign public key (optional, for key-based verification)

    Returns:
        Tuple[bool, str]: Success status and output or error message
    """
    if not check_tool_installed("cosign"):
        return False, "Cosign is not installed or not in PATH"

    try:
        if key_path:
            cmd = ["cosign", "verify", "--key", key_path, image_name]
        else:
            cmd = ["cosign", "verify", image_name]

        result = subprocess.run(
            cmd, capture_output=True, text=True, check=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, f"Error verifying image signature: {e.stderr}"


def check_kyverno_policy(k8s_manifest: str, policy_file: str) -> Tuple[bool, Dict]:
    """
    Check Kubernetes manifest against Kyverno policy

    Args:
        k8s_manifest: Path to the Kubernetes manifest file
        policy_file: Path to the Kyverno policy file

    Returns:
        Tuple[bool, Dict]: Success status and policy check results
    """
    if not check_tool_installed("kyverno"):
        return False, {"error": "Kyverno CLI is not installed or not in PATH"}

    try:
        cmd = ["kyverno", "test", k8s_manifest,
               "--policy", policy_file, "--output", "json"]
        result = subprocess.run(
            cmd, capture_output=True, text=True, check=True)

        try:
            policy_results = json.loads(result.stdout)
            # Check if any policy rules failed
            success = True
            for policy in policy_results:
                if policy.get("pass") is False:
                    success = False
                    break

            return success, policy_results
        except json.JSONDecodeError:
            # Fallback to non-JSON output handling
            success = "PASS" in result.stdout and "FAIL" not in result.stdout
            return success, {"output": result.stdout}
    except subprocess.CalledProcessError as e:
        return False, {"error": f"Error checking policy compliance: {e.stderr}"}


def secure_pipeline(
    dockerfile_path: str = "Dockerfile",
    context_path: str = ".",
    image_name: Optional[str] = None,
    registry: Optional[str] = None,
    build_args: Optional[dict] = None,
    policy_files: Optional[List[str]] = None,
    k8s_manifest: Optional[str] = None,
    signing_key: Optional[str] = None,
    push: bool = False
) -> Dict:
    """
    Run a complete secure CI/CD pipeline for Docker images

    Args:
        dockerfile_path: Path to the Dockerfile
        context_path: Path to the build context
        image_name: Name for the image
        registry: Container registry path
        build_args: Dictionary of build arguments
        policy_files: List of Kyverno policy files
        k8s_manifest: Path to Kubernetes manifest to check
        signing_key: Path to Cosign signing key
        push: Whether to push to registry

    Returns:
        Dict: Results of the pipeline
    """
    results = {
        "build": {"success": False, "output": None},
        "scan": {"success": False, "output": None},
        "sbom": {"success": False, "output": None},
        "policy": {"success": False, "output": None},
        "sign": {"success": False, "output": None},
        "push": {"success": False, "output": None}
    }

    # 1. Build the image
    try:
        print("🔨 Building Docker image...")
        built_image = build_docker_image(
            dockerfile_path=dockerfile_path,
            context_path=context_path,
            image_name=image_name,
            build_args=build_args
        )
        results["build"] = {"success": True, "output": built_image}
        print(f"✅ Image built: {built_image}")
    except Exception as e:
        results["build"] = {"success": False, "output": str(e)}
        print(f"❌ Build failed: {str(e)}")
        return results  # Stop if build fails

    # 2. Test the image
    test_cmd = [
        "--version"] if not image_name or "devkit" in image_name.lower() else None
    try:
        print("🧪 Testing the image...")
        test_success, test_output = test_docker_image(built_image, test_cmd)
        if not test_success:
            results["test"] = {"success": False, "output": test_output}
            print(f"❌ Test failed: {test_output}")
            return results  # Stop if test fails
        results["test"] = {"success": True, "output": test_output}
        print(f"✅ Test passed: {test_output}")
    except Exception as e:
        results["test"] = {"success": False, "output": str(e)}
        print(f"❌ Test failed: {str(e)}")
        return results

    # 3. Scan for vulnerabilities
    try:
        print("🔍 Scanning for vulnerabilities...")
        scan_success, scan_output = scan_docker_image(
            built_image, output_format="json")
        results["scan"] = {"success": scan_success, "output": scan_output}
        if not scan_success:
            print("⚠️ Vulnerability scan found critical issues:")
            if isinstance(scan_output, dict) and "vulnerability_counts" in scan_output:
                for severity, count in scan_output["vulnerability_counts"].items():
                    if count > 0:
                        print(f"  - {severity}: {count}")
            return results  # Stop if critical vulnerabilities found
        print("✅ Vulnerability scan passed")
    except Exception as e:
        results["scan"] = {"success": False, "output": str(e)}
        print(f"❌ Scan failed: {str(e)}")

    # 4. Generate SBOM
    try:
        print("📄 Generating SBOM...")
        sbom_dir = "sboms"
        os.makedirs(sbom_dir, exist_ok=True)
        output_file = os.path.join(
            sbom_dir, f"{os.path.basename(built_image).replace(':', '-')}.sbom.json")
        sbom_success, sbom_output = generate_sbom(built_image, output_file)
        results["sbom"] = {"success": sbom_success, "output": sbom_output}
        if sbom_success:
            print(f"✅ SBOM generated: {sbom_output}")
        else:
            print(f"⚠️ SBOM generation warning: {sbom_output}")
    except Exception as e:
        results["sbom"] = {"success": False, "output": str(e)}
        print(f"❌ SBOM generation failed: {str(e)}")

    # 5. Check Kubernetes manifest against policies
    if policy_files and k8s_manifest:
        try:
            print("🔒 Checking policy compliance...")
            policy_results = []
            overall_policy_success = True

            for policy_file in policy_files:
                policy_success, policy_output = check_kyverno_policy(
                    k8s_manifest, policy_file)
                policy_results.append({
                    "policy": policy_file,
                    "success": policy_success,
                    "output": policy_output
                })
                if not policy_success:
                    overall_policy_success = False

            results["policy"] = {
                "success": overall_policy_success, "output": policy_results}
            if overall_policy_success:
                print("✅ Policy compliance checks passed")
            else:
                print("⚠️ Policy compliance checks failed")
        except Exception as e:
            results["policy"] = {"success": False, "output": str(e)}
            print(f"❌ Policy check failed: {str(e)}")

    # 6. Tag the image for registry if needed
    if registry:
        version = get_current_version()
        target_tags = generate_docker_tags(registry, version)
        try:
            print("🏷️ Tagging images...")
            tagged_images = tag_docker_image(built_image, target_tags)
            results["tag"] = {"success": len(
                tagged_images) > 0, "output": tagged_images}
            print(f"✅ Tagged {len(tagged_images)} images")
        except Exception as e:
            results["tag"] = {"success": False, "output": str(e)}
            print(f"❌ Tagging failed: {str(e)}")
            return results

        # 7. Sign the image
        try:
            print("🔏 Signing image...")
            if registry:
                # Sign the full version tag
                sign_success, sign_output = sign_image(
                    target_tags[0], signing_key)
                results["sign"] = {
                    "success": sign_success, "output": sign_output}
                if sign_success:
                    print("✅ Image signed successfully")
                else:
                    print(f"⚠️ Image signing warning: {sign_output}")
        except Exception as e:
            results["sign"] = {"success": False, "output": str(e)}
            print(f"❌ Image signing failed: {str(e)}")

        # 8. Push to registry if requested
        if push:
            try:
                print("🚀 Pushing to registry...")
                pushed_images = push_docker_image(target_tags)
                results["push"] = {"success": len(
                    pushed_images) > 0, "output": pushed_images}
                print(f"✅ Pushed {len(pushed_images)} images to registry")
            except Exception as e:
                results["push"] = {"success": False, "output": str(e)}
                print(f"❌ Push failed: {str(e)}")

    print("✅ Secure pipeline completed!")
    return results
