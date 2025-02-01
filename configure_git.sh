#!/bin/bash

# Configure Git credentials
git config --global user.name "RanchDog25"
git config --global user.email "administration@evergold.tech"

# Initialize Git repository if needed
git init

# Add the remote repository
git remote add origin git@github.com:RanchDog25/RanchPi.git

echo "Git configuration completed!"
