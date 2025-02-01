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