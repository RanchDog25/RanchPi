#!/usr/bin/env python3

import subprocess
import sys
import os

class GitOperations:
    def __init__(self):
        self.verify_git_installed()

    def verify_git_installed(self):
        """Verify that git is installed and accessible."""
        try:
            subprocess.run(['git', '--version'], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            print("Error: Git is not installed or not accessible")
            sys.exit(1)

    def git_pull(self):
        """Pull latest changes from remote repository."""
        try:
            result = subprocess.run(['git', 'pull'], 
                                 check=True, 
                                 capture_output=True,
                                 text=True)
            print("Pull successful:")
            print(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"Error pulling changes: {e.stderr}")
            sys.exit(1)

    def git_push(self, commit_message):
        """
        Stage all changes, commit, and push to remote repository.
        
        Args:
            commit_message (str): Commit message for the changes
        """
        try:
            # Stage changes
            subprocess.run(['git', 'add', '.'], check=True)
            
            # Commit changes
            subprocess.run(['git', 'commit', '-m', commit_message], check=True)
            
            # Push changes
            result = subprocess.run(['git', 'push'], 
                                 check=True,
                                 capture_output=True,
                                 text=True)
            print("Push successful:")
            print(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"Error during git operations: {e.stderr}")
            sys.exit(1)

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Pull changes: python3 git_utils.py pull")
        print("  Push changes: python3 git_utils.py push \"Commit message\"")
        sys.exit(1)

    git_ops = GitOperations()
    command = sys.argv[1].lower()

    if command == "pull":
        git_ops.git_pull()
    elif command == "push":
        if len(sys.argv) < 3:
            print("Error: Commit message required for push operation")
            sys.exit(1)
        git_ops.git_push(sys.argv[2])
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
