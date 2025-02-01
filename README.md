# Raspberry Pi Python Development Environment

This repository contains a Python development environment setup for Raspberry Pi with GitHub integration.

## Setup Instructions

### 1. Initial Setup on Development Machine (Replit)

1. Clone this repository using HTTPS:
   ```bash
   git clone https://github.com/RanchDog25/RanchPi.git
   cd RanchPi
   ```

2. Configure Git:
   ```bash
   ./configure_git.sh
   ```
   This will set up your Git credentials for pushing changes from Replit.

### 2. Usage

#### Git Utilities

The `git_utils.py` script provides easy-to-use commands for Git operations:

1. Pull latest changes:
   ```bash
   python3 git_utils.py pull
   ```

2. Push your changes:
   ```bash
   python3 git_utils.py push "Your commit message"
   ```

#### Sample Project

A basic sample project is included in the `sample_project` directory to test the GitHub workflow:

1. The sample project demonstrates:
   - Basic Raspberry Pi system information display
   - Python environment verification
   - Git workflow testing

2. Run the sample project:
   ```bash
   python3 sample_project/main.py
   ```

### 3. Setup on Raspberry Pi

1. Install Git on your Raspberry Pi:
   ```bash
   sudo apt update
   sudo apt install git
   ```

2. Generate SSH key on Pi (if not already done):
   ```bash
   ssh-keygen -t ed25519 -C "administration@evergold.tech"
   ```

3. Add the SSH key to GitHub:
   - Display your public key: `cat ~/.ssh/id_ed25519.pub`
   - Add this key to GitHub (Settings → SSH and GPG keys)

4. Clone the repository using SSH on Pi:
   ```bash
   git clone git@github.com:RanchDog25/RanchPi.git
   ```

5. Pull latest changes when needed:
   ```bash
   python3 git_utils.py pull
   ```

## Development Workflow

1. Develop and test code on Replit (using HTTPS connection)
2. Push changes to GitHub using `git_utils.py`
3. Pull changes on your Raspberry Pi (using SSH connection)
4. Run and test your code on the Raspberry Pi

## Requirements

- Python 3.x
- Git
- SSH access to GitHub (for Pi only)
- Raspberry Pi OS Lite (64-bit)