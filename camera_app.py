from flask import Flask, render_template, send_file, jsonify, request
from flask_cors import CORS
import time
from pathlib import Path
import io
import os
import platform
from PIL import Image, ImageDraw
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

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
        logger.info("Camera started")

    def stop(self):
        self.is_running = False
        logger.info("Camera stopped")

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
        logger.info(f"Captured image saved to {filename}")

    def get_status(self):
        return {
            'running': getattr(self, 'is_running', False),
            'settings': self.settings
        }

    def update_settings(self, new_settings):
        self.settings.update(new_settings)
        logger.info(f"Camera settings updated: {new_settings}")
        return self.settings

def initialize_camera():
    """Initialize and configure the camera based on environment"""
    try:
        if platform.machine().startswith('arm'):  # Running on Raspberry Pi
            from picamera2 import Picamera2
            logger.info("Initializing Raspberry Pi camera")
            camera = Picamera2()
        else:  # Development environment
            logger.info("Initializing mock camera for development")
            camera = MockCamera()

        camera.start()
        time.sleep(1)  # Brief pause to ensure camera is ready
        return camera
    except Exception as e:
        logger.error(f"Error initializing camera: {e}")
        return None

# Initialize camera globally
camera = initialize_camera()

@app.route('/')
def index():
    """Render the main page."""
    logger.info("Accessing main page")
    return render_template('index.html')

@app.route('/capture')
def capture_image():
    """Capture an image and return it."""
    if not camera:
        logger.error("Camera not initialized")
        return "Camera not initialized", 500

    try:
        # Capture image to memory
        output = io.BytesIO()
        camera.capture_file("latest.jpg")
        with open("latest.jpg", "rb") as f:
            output.write(f.read())
        output.seek(0)
        logger.info("Image captured successfully")
        return send_file(output, mimetype='image/jpeg')
    except Exception as e:
        logger.error(f"Error capturing image: {e}")
        return str(e), 500

@app.route('/status')
def get_status():
    """Get camera operational status."""
    if not camera:
        logger.error("Camera not initialized")
        return jsonify({'status': 'error', 'message': 'Camera not initialized'}), 500

    try:
        status = camera.get_status()
        logger.info("Status retrieved successfully")
        return jsonify({'status': 'ok', 'data': status})
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/settings', methods=['GET', 'POST'])
def camera_settings():
    """Get or update camera settings."""
    if not camera:
        logger.error("Camera not initialized")
        return jsonify({'status': 'error', 'message': 'Camera not initialized'}), 500

    if request.method == 'POST':
        try:
            new_settings = request.get_json()
            updated_settings = camera.update_settings(new_settings)
            logger.info(f"Settings updated: {new_settings}")
            return jsonify({'status': 'ok', 'data': updated_settings})
        except Exception as e:
            logger.error(f"Error updating settings: {e}")
            return jsonify({'status': 'error', 'message': str(e)}), 500
    else:
        try:
            status = camera.get_status()
            return jsonify({'status': 'ok', 'data': status['settings']})
        except Exception as e:
            logger.error(f"Error getting settings: {e}")
            return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/live')
def live_feed():
    """Render the live feed page."""
    logger.info("Accessing live feed page")
    return render_template('live.html')

if __name__ == '__main__':
    # Enable all interfaces (0.0.0.0) and use port 5000
    logger.info("Starting Flask server on 0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)