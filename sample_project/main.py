#!/usr/bin/env python3

"""
Sample Raspberry Pi Python project to test GitHub workflow.
This script demonstrates basic Raspberry Pi GPIO interaction.
"""

def print_system_info():
    """Print basic system information."""
    try:
        with open('/proc/cpuinfo', 'r') as f:
            cpu_info = f.read()
        
        print("Raspberry Pi System Information")
        print("=" * 30)
        
        # Extract model name
        for line in cpu_info.split('\n'):
            if 'Model' in line:
                print(line)
            if 'Hardware' in line:
                print(line)
        
        # Print Python version
        import sys
        print(f"\nPython Version: {sys.version.split()[0]}")
        
    except Exception as e:
        print(f"Error reading system information: {e}")

def main():
    print_system_info()
    print("\nGitHub workflow test successful!")

if __name__ == "__main__":
    main()
