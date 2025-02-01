# Raspberry Pi Python Development Environment

This repository contains a Python development environment setup for Raspberry Pi with GitHub integration.

## Setup Instructions

### 1. Initial Setup on Development Machine

1. Clone this repository:
   ```bash
   git clone <your-repository-url>
   cd raspberry-pi-dev
   ```

2. Set up GitHub integration:
   ```bash
   python3 setup_github.py
   ```
   This will:
   - Configure your Git username and email
   - Generate SSH keys if needed
   - Guide you through adding SSH keys to GitHub

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

2. Clone the repository using SSH:
   ```bash
   git clone git@github.com:your-username/your-repo-name.git
   ```

3. Pull latest changes when needed:
   ```bash
   python3 git_utils.py pull
   ```

## Development Workflow

1. Develop and test code on your development machine
2. Push changes to GitHub using `git_utils.py`
3. Pull changes on your Raspberry Pi using `git_utils.py`
4. Run and test your code on the Raspberry Pi

## Requirements

- Python 3.x
- Git
- SSH access to GitHub
- Raspberry Pi OS Lite (64-bit)