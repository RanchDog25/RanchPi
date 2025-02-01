#!/bin/bash

# Configure Git credentials
git config --global user.name "RanchDog25"
git config --global user.email "administration@evergold.tech"

# Initialize Git repository if needed
git init

# Add the remote repository using HTTPS
# Note: Authentication will be handled by GITHUB_TOKEN environment variable
git remote add origin https://github.com/RanchDog25/RanchPi.git

echo "Git configuration completed!"