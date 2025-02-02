# Raspberry Pi Python Development Environment
This repository contains a Python development environment setup for Raspberry Pi with GitHub integration.

## Latest Update (February 2, 2025)
- Added WebSocket streaming support
- Implemented development workflow between Pi and Replit
- Enhanced camera rotation handling
- Added network management capabilities

## Development Workflow

### Working on Raspberry Pi

1. Before making changes, pull the latest code:
```bash
git pull origin main
```

2. After making changes on your Pi:
```bash
# Stage your changes
git add .

# Commit with a descriptive message
git commit -m "Description of your changes"

# Push to GitHub
git push origin main
```

3. Your changes are now on GitHub. Replit needs to be synced separately.

### Working on Replit

1. After changes are pushed from Pi to GitHub:
```bash
# Use the provided utility to pull changes
python3 git_utils.py pull
```

2. If you make changes on Replit:
```bash
# Use the provided utility to push changes
python3 git_utils.py push "Description of your changes"
```

3. Then on your Pi:
```bash
git pull origin main
```

### Handling Merge Conflicts

If you encounter merge conflicts:

1. Create a backup of your changes:
```bash
# Create a backup branch
git checkout -b backup_branch

# Save your changes
git add .
git commit -m "Backup of local changes"

# Return to main branch
git checkout main
```

2. Get the latest changes:
```bash
# Clean untracked files if needed
git clean -f

# Pull latest changes
git pull origin main
```

3. Restore your changes if needed:
```bash
# Cherry-pick your changes
git cherry-pick backup_branch
```

### Best Practices

1. Always pull before making changes
2. Commit and push changes frequently
3. Keep Pi and Replit in sync through GitHub
4. Use descriptive commit messages
5. Check the workflow status after syncing
6. Create backup branches when resolving conflicts

### Current Features

- Live camera streaming via WebSocket
- Network resilience with automatic failover
- Scheduled image capture
- Image rotation and basic settings
- Image gallery with metadata
- Development/Production environment detection

### Required Packages

On your Raspberry Pi:
```bash
pip3 install websockets schedule flask-cors pillow
sudo apt install -y python3-picamera2 python3-libcamera
```

On Replit:
- All dependencies are automatically managed

### Running the Application

1. On Raspberry Pi:
```bash
python3 camera_app.py
```

2. On Replit:
- The application runs automatically in the "Camera Server" workflow

The system will:
- Auto-detect available networks
- Start WebSocket server for streaming
- Initialize camera interface
- Begin serving web interface