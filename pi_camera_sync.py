#!/usr/bin/env python3

import os
import time
from datetime import datetime
from pathlib import Path
from git_utils import GitOperations

class PiCameraSync:
    def __init__(self):
        self.git_ops = GitOperations()
        self.image_dir = Path("captured_images")
        self.image_dir.mkdir(exist_ok=True)
        
    def capture_and_sync(self):
        try:
            # Import picamera2 only on Raspberry Pi
            from picamera2 import Picamera2
            
            # Initialize camera
            camera = Picamera2()
            camera.start()
            time.sleep(2)  # Warm-up time
            
            # Generate timestamp for filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_path = self.image_dir / f"capture_{timestamp}.jpg"
            
            # Capture image
            camera.capture_file(str(image_path))
            print(f"Image captured: {image_path}")
            
            # Git operations
            commit_message = f"Add camera capture from {timestamp}"
            self.git_ops.git_pull()  # Ensure we're up to date
            self.git_ops.git_push(commit_message)
            print("Successfully pushed to GitHub")
            
            return str(image_path)
            
        except ImportError:
            print("This script should only be run on a Raspberry Pi")
            return None
        except Exception as e:
            print(f"Error during capture and sync: {e}")
            return None

if __name__ == "__main__":
    sync = PiCameraSync()
    sync.capture_and_sync()
