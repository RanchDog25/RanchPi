#!/usr/bin/env python3

import subprocess
import sys
import os

def check_git_config():
    """Check if git global configuration exists."""
    try:
        name = subprocess.run(['git', 'config', '--global', 'user.name'],
                            capture_output=True,
                            text=True)
        email = subprocess.run(['git', 'config', '--global', 'user.email'],
                             capture_output=True,
                             text=True)
        return bool(name.stdout and email.stdout)
    except subprocess.CalledProcessError:
        return False

def setup_git_config():
    """Set up git global configuration."""
    print("Setting up Git configuration...")
    
    name = input("Enter your Git username: ").strip()
    email = input("Enter your Git email: ").strip()

    try:
        subprocess.run(['git', 'config', '--global', 'user.name', name], check=True)
        subprocess.run(['git', 'config', '--global', 'user.email', email], check=True)
        print("Git configuration completed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error setting up Git configuration: {e}")
        sys.exit(1)

def check_ssh_key():
    """Check if SSH key exists."""
    ssh_path = os.path.expanduser('~/.ssh/id_ed25519.pub')
    return os.path.exists(ssh_path)

def generate_ssh_key():
    """Generate new SSH key."""
    print("\nGenerating new SSH key...")
    email = input("Enter your email for SSH key: ").strip()
    
    try:
        subprocess.run([
            'ssh-keygen',
            '-t', 'ed25519',
            '-C', email,
            '-f', os.path.expanduser('~/.ssh/id_ed25519'),
            '-N', ''
        ], check=True)
        print("SSH key generated successfully!")
        
        # Display the public key
        with open(os.path.expanduser('~/.ssh/id_ed25519.pub'), 'r') as f:
            public_key = f.read().strip()
        
        print("\nYour public SSH key:")
        print("-" * 50)
        print(public_key)
        print("-" * 50)
        print("\nAdd this key to your GitHub account:")
        print("1. Go to GitHub Settings → SSH and GPG keys")
        print("2. Click 'New SSH key'")
        print("3. Paste the key above and save")
        
    except subprocess.CalledProcessError as e:
        print(f"Error generating SSH key: {e}")
        sys.exit(1)

def main():
    print("GitHub Setup Utility")
    print("=" * 50)

    # Check and setup git config
    if not check_git_config():
        setup_git_config()
    else:
        print("Git configuration already exists!")

    # Check and generate SSH key
    if not check_ssh_key():
        generate_ssh_key()
    else:
        print("\nSSH key already exists!")
        print("If you need to view it:")
        print(f"cat {os.path.expanduser('~/.ssh/id_ed25519.pub')}")

    print("\nSetup complete!")
    print("Test your GitHub connection with: ssh -T git@github.com")

if __name__ == "__main__":
    main()
