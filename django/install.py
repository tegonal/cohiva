#!/usr/bin/env python3
"""
Dependency installation script for Cohiva Django project.
This script replaces the functionality of install_dependencies.sh with Python.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def get_python_version():
    """Get the current Python version as a string (e.g., '3.11')."""
    return f"{sys.version_info[0]}.{sys.version_info[1]}"


def check_virtual_env(environment, auto_yes=False):
    """Check if we are in a virtual environment or docker."""
    venv = os.environ.get("VIRTUAL_ENV")
    pip_root_user_mode = None
    pip_sync_ask = [] if auto_yes else ["--ask"]

    if venv:
        print(f"Checking/installing dependencies in virtual environment '{venv}'...")
    elif environment == "docker":
        print(
            "Checking/installing dependencies on native environment since we are in docker mode..."
        )
        pip_root_user_mode = "ignore"
        pip_sync_ask = []
    else:
        print("It seems that no Python virtual environment is active.")
        print("Please create and activate a virtual environment first. (see README.md)")
        sys.exit(1)

    return pip_root_user_mode, pip_sync_ask


def get_requirements_file():
    """Determine which requirements file to use based on Python version."""
    python_version = get_python_version()
    legacy_requirements = Path(f"requirements_legacy_python{python_version}.txt")

    if legacy_requirements.exists():
        print(f"Using legacy requirements file for Python {python_version}")
        return str(legacy_requirements)

    return "requirements.txt"


def ensure_pip_sync(pip_root_user_mode):
    """Ensure pip-sync is installed."""
    if pip_root_user_mode:
        os.environ["PIP_ROOT_USER_ACTION"] = pip_root_user_mode

    # Check if pip-sync is available
    result = subprocess.run(
        ["command", "-v", "pip-sync"],
        shell=False,
        capture_output=True,
        executable="/bin/sh",
    )

    if result.returncode != 0:
        print("Installing pip-tools...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pip-tools"], check=True)


def get_site_packages():
    """Get the site-packages directory path."""
    result = subprocess.run(
        [sys.executable, "-c", "import site; print(site.getsitepackages()[0])"],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def remove_old_sepa_packages():
    """Remove old patched versions of python-sepa."""
    site_packages = get_site_packages()
    if not site_packages:
        return

    site_packages_path = Path(site_packages)
    # Find and remove old sepa packages matching pattern sepa-0.5.[1-3]+mst[1-9]-*.egg
    for egg_dir in site_packages_path.glob("sepa-0.5.[1-3]+mst[1-9]-*.egg"):
        print(f"Removing {egg_dir}")
        if egg_dir.is_dir():
            import shutil

            shutil.rmtree(egg_dir)
        else:
            egg_dir.unlink()


def install_python_sepa(environment):
    """Install patched version of python-sepa from submodule."""
    sepa_path = Path("geno/python-sepa")

    if environment != "docker":
        if not (sepa_path / ".git").exists():
            print("Initializing git submodule python-sepa")
            subprocess.run(
                ["git", "submodule", "update", "--init", "geno/python-sepa"],
                check=True,
            )
        else:
            subprocess.run(
                ["git", "submodule", "update", "geno/python-sepa"],
                check=True,
            )

    print("Installing python-sepa from submodule")
    subprocess.run(
        [sys.executable, "setup.py", "build", "install"],
        cwd=sepa_path,
        check=True,
    )


def ensure_sepa_in_requirements(requirements_file):
    """Ensure sepa package is listed in requirements.txt."""
    with open(requirements_file) as f:
        content = f.read()

    if "sepa==" not in content.split("\n")[0] if content else True:
        # Check each line for sepa==
        has_sepa = any(line.startswith("sepa==") for line in content.split("\n"))
        if not has_sepa:
            print(f"Adding sepa to {requirements_file}")
            with open(requirements_file, "a") as f:
                f.write("\n# Packages added/managed by install.py:\n")
                f.write("sepa==0.5.4+mst1\n")


def run_pip_sync(requirements_file, pip_sync_ask):
    """Run pip-sync to synchronize virtual environment with requirements.txt."""
    print(f"Syncing virtual environment with {requirements_file}...")
    cmd = ["pip-sync"] + pip_sync_ask + [requirements_file]
    subprocess.run(cmd, check=True)


def get_package_location(package_name):
    """Get the installation location of a package."""
    result = subprocess.run(
        [sys.executable, "-m", "pip", "show", package_name],
        capture_output=True,
        text=True,
        check=True,
    )
    for line in result.stdout.split("\n"):
        if line.startswith("Location:"):
            return line.split(":", 1)[1].strip()
    return None


def apply_patches():
    """Apply patches to site packages in virtual environment."""
    install_path = get_package_location("djangosaml2idp")
    if not install_path:
        print("Warning: Could not find djangosaml2idp installation path")
        return

    install_path = Path(install_path)

    patches = [
        (
            install_path / "djangosaml2idp" / "models.py",
            "cohiva/saml2/djangosaml2idp_models.py.patch",
        ),
        (
            install_path / "djangosaml2idp" / "views.py",
            "cohiva/saml2/djangosaml2idp_views.py.patch",
        ),
    ]

    for target_file, patch_file in patches:
        if not Path(patch_file).exists():
            print(f"Warning: Patch file {patch_file} not found, skipping...")
            continue

        print(f"Applying patch {patch_file} to {target_file}...")
        result = subprocess.run(
            [
                "patch",
                "--backup",
                "--forward",
                "--reject-file",
                "-",
                str(target_file),
                patch_file,
            ],
            capture_output=True,
            text=True,
        )
        # Don't fail if patch is already applied (exit code 1)
        if result.returncode not in [0, 1]:
            print(f"Warning: Patch may have failed: {result.stderr}")


def main():
    """Main installation function."""
    parser = argparse.ArgumentParser(description="Install dependencies for Cohiva Django project")
    parser.add_argument(
        "-e",
        "--environment",
        default="local",
        help="Environment mode (local or docker)",
    )
    parser.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="Auto-confirm pip-sync (skip --ask prompt)",
    )
    args = parser.parse_args()

    print(f"$ENVIRONMENT is set to {args.environment}")

    # Check virtual environment
    pip_root_user_mode, pip_sync_ask = check_virtual_env(args.environment, auto_yes=args.yes)

    # Determine requirements file
    requirements_file = get_requirements_file()

    # Ensure pip-sync is available
    ensure_pip_sync(pip_root_user_mode)

    # Remove old sepa packages
    remove_old_sepa_packages()

    # Install python-sepa from submodule
    install_python_sepa(args.environment)

    # Ensure sepa is in requirements
    ensure_sepa_in_requirements(requirements_file)

    # Sync dependencies
    run_pip_sync(requirements_file, pip_sync_ask)

    # Apply patches
    apply_patches()

    print("\nDependency installation completed successfully!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInstallation cancelled by user.")
        sys.exit(130)  # Standard exit code for SIGINT
