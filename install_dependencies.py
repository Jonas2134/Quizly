#!/usr/bin/env python3
import os
import platform
import subprocess
import sys
from pathlib import Path

def check_nvidia_gpu():
    try:
        nvidia_smi = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
        return nvidia_smi.returncode == 0
    except FileNotFoundError:
        return False


def install_requirements(requirements_file):
    print(f"Installing dependencies from {requirements_file}...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', requirements_file], check=True)
        print("Dependencies installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        print("\nTroubleshooting tips:")
        print("- For MacOS: Try installing numpy, llvmlite, and numba manually without version constraints")
        print("- For Windows: Make sure you have Visual C++ build tools installed")
        print("- For Linux: Ensure development packages are installed (python3-dev, etc.)")
        sys.exit(1)


def main():
    # Get the directory where the script is located
    script_dir = Path(__file__).parent
    requirements_dir = script_dir / 'requirements'
    
    system = platform.system().lower()
    
    if system == 'linux':
        if check_nvidia_gpu():
            requirements_file = requirements_dir / 'requirements-linux.txt'
        else:
            # For Linux without NVIDIA GPU, use base ML requirements
            requirements_file = requirements_dir / 'requirements-base-ml.txt'
    elif system == 'darwin':
        requirements_file = requirements_dir / 'requirements-macos.txt'
    elif system == 'windows':
        requirements_file = requirements_dir / 'requirements-base-ml.txt'
    else:
        print(f"Unsupported operating system: {system}")
        sys.exit(1)

    if not Path(requirements_file).exists():
        print(f"Requirements file {requirements_file} not found!")
        sys.exit(1)

    install_requirements(requirements_file)


if __name__ == '__main__':
    main()
