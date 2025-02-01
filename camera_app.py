from flask import Flask, render_template, send_file, jsonify, request
import time
from pathlib import Path
import io
import os
import platform
from PIL import Image, ImageDraw
import json

app = Flask(__name__)

# Ensure the images directory exists
UPLOAD_FOLDER = Path("static/images")
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

class MockCamera:
    """Mock camera for development environment"""
    def __init__(self):
        self.width = 640
        self.height = 480
        self.settings = {
            'brightness': 50,
            'contrast': 50,
            'resolution': f"{self.width}x{self.height}"
        }

    def start(self):
        self.is_running = True

    def stop(self):
        self.is_running = False

    def capture_file(self, filename):
        # Create a test image
        img = Image.new('RGB', (self.width, self.height), color='gray')
        draw = ImageDraw.Draw(img)

        # Add some text and timestamp
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        draw.text((self.width//2 - 100, self.height//2), 
                 'Development Mode', fill='white')
        draw.text((10, self.height - 30), 
                 timestamp, fill='white')

        # Save the image
        img.save(filename)

    def get_status(self):
        return {
            'running': getattr(self, 'is_running', False),
            'settings': self.settings
        }

    def update_settings(self, new_settings):
        self.settings.update(new_settings)
        return self.settings

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

@app.route('/status')
def get_status():
    """Get camera operational status."""
    if not camera:
        return jsonify({'status': 'error', 'message': 'Camera not initialized'}), 500

    try:
        status = camera.get_status()
        return jsonify({'status': 'ok', 'data': status})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/settings', methods=['GET', 'POST'])
def camera_settings():
    """Get or update camera settings."""
    if not camera:
        return jsonify({'status': 'error', 'message': 'Camera not initialized'}), 500

    if request.method == 'POST':
        try:
            new_settings = request.get_json()
            updated_settings = camera.update_settings(new_settings)
            return jsonify({'status': 'ok', 'data': updated_settings})
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500
    else:
        try:
            status = camera.get_status()
            return jsonify({'status': 'ok', 'data': status['settings']})
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/live')
def live_feed():
    """Render the live feed page."""
    return render_template('live.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)