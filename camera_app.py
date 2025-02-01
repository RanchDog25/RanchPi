from flask import Flask, render_template, send_file
import time
from pathlib import Path
import io
import os
import platform
from PIL import Image, ImageDraw

app = Flask(__name__)

# Ensure the images directory exists
UPLOAD_FOLDER = Path("static/images")
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

class MockCamera:
    """Mock camera for development environment"""
    def __init__(self):
        self.width = 640
        self.height = 480

    def start(self):
        pass

    def capture_file(self, filename):
        # Create a test image
        img = Image.new('RGB', (self.width, self.height), color='gray')
        draw = ImageDraw.Draw(img)

        # Add some text
        draw.text((self.width//2 - 100, self.height//2), 
                 'Development Mode', fill='white')

        # Save the image
        img.save(filename)

def initialize_camera():
    """Initialize and configure the camera based on environment"""
    try:
        if platform.machine().startswith('arm'):  # Running on Raspberry Pi
            from picamera2 import Picamera2
            camera = Picamera2()
        else:  # Development environment
            camera = MockCamera()

        camera.start()
        time.sleep(1)  # Brief pause to ensure camera is ready
        return camera
    except Exception as e:
        print(f"Error initializing camera: {e}")
        return None

# Initialize camera globally
camera = initialize_camera()

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route('/capture')
def capture_image():
    """Capture an image and return it."""
    if not camera:
        return "Camera not initialized", 500

    try:
        # Capture image to memory
        output = io.BytesIO()
        camera.capture_file("latest.jpg")
        with open("latest.jpg", "rb") as f:
            output.write(f.read())
        output.seek(0)

        return send_file(output, mimetype='image/jpeg')
    except Exception as e:
        print(f"Error capturing image: {e}")
        return str(e), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)