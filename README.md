# Raspberry Pi Python Development Environment

This repository contains a Python development environment setup for Raspberry Pi with GitHub integration.

## Latest Update (February 1, 2025)
- Configured development environment with Replit integration
- Set up secure HTTPS connection for Replit→GitHub workflow
- Established SSH-based workflow for Raspberry Pi
- Added external access configuration

## Trail Camera Architecture (Future Implementation)

For deploying this system as a trail camera, the following architecture is recommended:

### Hardware Requirements
- Raspberry Pi with Camera
- 4G/LTE USB Modem
- Solar Panel + Battery Pack
- Weatherproof Enclosure
- IR LED Array for Night Vision
- Temperature/Humidity Sensors

### Network Architecture
1. **Image Capture Layer** (On Pi):
   - Motion detection using PiCamera2
   - Local image storage buffer
   - Power management system
   - Cellular connection management

2. **Cloud Layer**:
   - S3 Bucket for image storage
   - Lambda functions for image processing
   - API Gateway for secure access
   - Web interface hosted on cloud

3. **Access Layer**:
   - Web interface for viewing images
   - Mobile app support
   - Admin dashboard for camera management

### Data Flow
1. Motion triggers camera
2. Image captured and stored locally
3. Uploaded to cloud when connection available
4. Processed and stored in S3
5. Available via web interface

## External Access Setup

To access your RanchPi camera from outside your local network:

1. **Configure Port Forwarding**:
   - Access your router's admin panel (typically http://192.168.1.1)
   - Navigate to Port Forwarding settings
   - Add a new rule:
     * Internal IP: 192.168.1.135 (your Raspberry Pi's IP)
     * Internal Port: 5000
     * External Port: 80 (or your preferred port)
     * Protocol: TCP

2. **Set Up Dynamic DNS (Optional but recommended)**:
   - Sign up for a free Dynamic DNS service (e.g., No-IP, DuckDNS)
   - Install the DDNS client on your Raspberry Pi:
     ```bash
     sudo apt install ddclient
     ```
   - Configure the client with your DDNS provider details

3. **Access Your Camera**:
   - Local network: http://192.168.1.135:5000
   - External network: http://your-ddns-domain.com:80 (or your configured port)

**Important Security Notes**:
- Always use strong passwords and keep your Raspberry Pi updated
- Consider setting up HTTPS for secure external access
- Regularly check for and install security updates

## Setup Instructions

### 1. Initial Setup on Development Machine (Replit)

1. Clone this repository:
   ```bash
   git clone https://github.com/RanchDog25/RanchPi.git
   cd RanchPi
   ```

2. Configure Git:
   ```bash
   ./configure_git.sh
   ```
   This script configures Git with your credentials. Authentication with GitHub is handled securely through environment variables.

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

## Authentication Methods

This project uses two different authentication methods:

1. **Replit → GitHub**: HTTPS with secure token authentication
   - Uses environment variables for secure GitHub authentication
   - No tokens are exposed in the code or configuration

2. **Raspberry Pi → GitHub**: SSH-based authentication
   - Uses SSH key pairs for secure authentication
   - Required for secure communication from your Pi

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

## Project Purpose
Raspberry Pi dev for Ranch Cams
Travis and Jackson 2/1/25, making Ranching Intelligence history

## Camera Application Setup

### 1. Development Environment (Replit)
The camera application runs in development mode on Replit, simulating camera captures with test images. To test:

```bash
python camera_app.py
```

### 2. Raspberry Pi Setup

1. Ensure your camera module is properly connected to the Pi

2. Install required packages:
   ```bash
   sudo apt update
   sudo apt install -y python3-picamera2 python3-libcamera
   pip3 install flask pillow
   ```

3. Clone the repository (if not already done):
   ```bash
   git clone git@github.com:RanchDog25/RanchPi.git
   cd RanchPi
   ```

4. Run the camera application:
   ```bash
   python3 camera_app.py
   ```

### 3. Automatic Image Capture and Sync

To automatically capture images and sync them to GitHub:

1. On your Raspberry Pi, run:
   ```bash
   python3 pi_camera_sync.py
   ```

This will:
- Capture an image using the Pi camera
- Save it with a timestamp
- Automatically push it to the GitHub repository

Images are stored in the `captured_images` directory and automatically synced to GitHub.