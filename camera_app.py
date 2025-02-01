import logging
import platform
import time
from pathlib import Path
import io
import os
from PIL import Image, ImageDraw
from flask import Flask, render_template, send_file, jsonify, request
from flask_cors import CORS

# Configure logging with more detail
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Ensure the images directory exists
UPLOAD_FOLDER = Path("static/images")
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

def initialize_camera():
    """Initialize and configure the camera based on environment"""
    try:
        machine = platform.machine()
        logger.info(f"Detected platform machine: {machine}")

        # Check for Raspberry Pi hardware
        is_raspberry_pi = machine.startswith('arm') or machine.startswith('aarch64')
        logger.info(f"Is Raspberry Pi? {is_raspberry_pi}")

        if is_raspberry_pi:
            logger.info("Detected ARM architecture (Raspberry Pi hardware)")
            try:
                # Try importing picamera2
                from picamera2 import Picamera2
                logger.info("Successfully imported picamera2")

                # Initialize camera
                camera = Picamera2()
                logger.info("Created Picamera2 instance")

                # Configure camera
                camera_config = camera.create_still_configuration(
                    main={"size": (640, 480)},
                    lores={"size": (320, 240)},
                    display="lores"
                )
                logger.info(f"Created camera configuration: {camera_config}")

                camera.configure(camera_config)
                logger.info("Applied camera configuration")

                camera.start()
                logger.info("Started camera")

                time.sleep(2)  # Give camera time to initialize

                # Test capture to verify camera is working
                try:
                    camera.capture_file("test.jpg")
                    logger.info("Successfully performed test capture")
                    os.remove("test.jpg")  # Clean up test file
                except Exception as capture_error:
                    logger.error(f"Test capture failed: {capture_error}")
                    raise

                return camera

            except ImportError as e:
                logger.error(f"Failed to import picamera2: {e}")
                logger.info("Falling back to mock camera")
                return MockCamera()
            except Exception as e:
                logger.error(f"Error initializing Raspberry Pi camera: {e}")
                logger.info("Falling back to mock camera")
                return MockCamera()
        else:
            logger.info(f"Not on Raspberry Pi (machine: {machine}), using mock camera")
            camera = MockCamera()
            camera.start()
            return camera
    except Exception as e:
        logger.error(f"Unexpected error in camera initialization: {e}")
        return None

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
        self.is_running = False
        logger.info("Mock camera initialized")

    def start(self):
        self.is_running = True
        logger.info("Mock camera started")

    def stop(self):
        self.is_running = False
        logger.info("Mock camera stopped")

    def capture_file(self, filename):
        try:
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
            logger.info(f"Mock camera: captured image saved to {filename}")
            return True
        except Exception as e:
            logger.error(f"Mock camera: error capturing image: {e}")
            return False

    def get_status(self):
        """Get the current status of the mock camera"""
        return {
            'running': self.is_running,
            'settings': self.settings
        }

    def update_settings(self, new_settings):
        """Update mock camera settings"""
        try:
            for key, value in new_settings.items():
                if key in self.settings:
                    self.settings[key] = value
            logger.info(f"Mock camera: settings updated to {self.settings}")
            return self.settings
        except Exception as e:
            logger.error(f"Mock camera: error updating settings: {e}")
            raise

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
        return jsonify({'status': 'error', 'message': 'Camera not initialized'}), 500

    try:
        logger.info("Attempting to capture image")
        output = io.BytesIO()

        if isinstance(camera, MockCamera):
            success = camera.capture_file("latest.jpg")
            if not success:
                raise Exception("Failed to capture mock image")
        else:
            # For Picamera2
            try:
                # Capture using the current configuration
                camera.capture_file("latest.jpg")
                logger.info("Successfully captured image with Picamera2")
            except Exception as e:
                logger.error(f"Error capturing with Picamera2: {e}")
                raise

        # Read the captured image and send it
        with open("latest.jpg", "rb") as f:
            output.write(f.read())
        output.seek(0)
        logger.info("Image captured and prepared for sending")
        return send_file(output, mimetype='image/jpeg')
    except Exception as e:
        logger.error(f"Error in capture_image: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/status')
def get_status():
    """Get camera operational status."""
    if not camera:
        logger.error("Camera not initialized")
        return jsonify({'status': 'error', 'message': 'Camera not initialized'}), 500

    try:
        status_data = camera.get_status()
        logger.info(f"Status retrieved successfully: {status_data}")
        return jsonify({'status': 'ok', 'data': status_data})
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
            logger.info(f"Attempting to update settings: {new_settings}")
            updated_settings = camera.update_settings(new_settings)
            logger.info(f"Settings updated successfully: {updated_settings}")
            return jsonify({'status': 'ok', 'data': updated_settings})
        except Exception as e:
            logger.error(f"Error updating settings: {e}")
            return jsonify({'status': 'error', 'message': str(e)}), 500
    else:
        try:
            settings = camera.get_status()['settings']
            return jsonify({'status': 'ok', 'data': settings})
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