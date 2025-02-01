import logging
import platform
import time
from pathlib import Path
import io
import os
from PIL import Image, ImageDraw
from flask import Flask, render_template, send_file, jsonify, request
from flask_cors import CORS
from werkzeug.serving import is_running_from_reloader

# Configure logging with more detail
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__, 
    template_folder='templates',  # Explicitly set template folder
    static_folder='static'       # Explicitly set static folder
)
CORS(app)  # Enable CORS for all routes

# Disable Flask debug mode
app.debug = False

# Ensure the images directory exists
UPLOAD_FOLDER = Path("static/images")
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

# Global camera instance
camera = None

# Camera settings
CAMERA_SETTINGS = {
    'brightness': 50,
    'contrast': 50,
    'rotation': 0,
    'resolution': (640, 480)
}

class MockCamera:
    """Mock camera for development environment"""
    def __init__(self):
        self.width = 640
        self.height = 480
        self.settings = CAMERA_SETTINGS.copy()
        self.is_running = False
        logger.info("Mock camera initialized with settings: %s", self.settings)

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

            # Add text and timestamp
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            draw.text((self.width//2 - 100, self.height//2), 
                     'Development Mode', fill='white')
            draw.text((10, self.height - 30), 
                     timestamp, fill='white')

            # Apply rotation if needed
            if self.settings['rotation'] != 0:
                logger.info(f"Rotating image by {self.settings['rotation']} degrees")
                img = img.rotate(self.settings['rotation'])

            img.save(filename)
            logger.info(f"Mock camera: captured image saved to {filename}")
            return True
        except Exception as e:
            logger.error(f"Mock camera: error capturing image: {e}")
            return False

    def get_status(self):
        return {
            'running': self.is_running,
            'settings': self.settings
        }

    def update_settings(self, new_settings):
        try:
            for key, value in new_settings.items():
                if key in self.settings:
                    self.settings[key] = value
                    if key == 'rotation':
                        # Normalize rotation to 0, 90, 180, or 270
                        self.settings['rotation'] = (value % 360)
                        logger.info(f"Updated rotation to {self.settings['rotation']} degrees")
            return self.settings
        except Exception as e:
            logger.error(f"Error updating settings: {e}")
            raise

def initialize_camera():
    """Initialize and configure the camera based on environment"""
    global camera

    try:
        machine = platform.machine()
        logger.info(f"Detected platform machine: {machine}")

        # Check for Raspberry Pi hardware
        is_raspberry_pi = machine.startswith('arm') or machine.startswith('aarch64')
        logger.info(f"Is Raspberry Pi? {is_raspberry_pi}")

        if is_raspberry_pi:
            logger.info("Detected ARM architecture (Raspberry Pi hardware)")
            try:
                from picamera2 import Picamera2
                logger.info("Successfully imported picamera2")

                # Create Picamera2 instance
                camera = Picamera2()
                logger.info("Created Picamera2 instance")

                # Create camera configuration
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

                # Test capture
                camera.capture_file("test.jpg")
                logger.info("Successfully performed test capture")
                os.remove("test.jpg")  # Clean up test file

                return camera
            except Exception as e:
                logger.error(f"Error initializing Raspberry Pi camera: {e}")
                logger.info("Falling back to mock camera")
                return MockCamera()
        else:
            logger.info("Using mock camera for development")
            return MockCamera()
    except Exception as e:
        logger.error(f"Unexpected error in camera initialization: {e}")
        return MockCamera()

# Initialize camera
camera = initialize_camera()

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route('/capture')
def capture_image():
    """Capture an image and return it."""
    if not camera:
        return jsonify({'status': 'error', 'message': 'Camera not initialized'}), 500

    try:
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = f"latest_{timestamp}.jpg"
        filepath = UPLOAD_FOLDER / filename

        camera.capture_file(str(filepath))
        logger.info(f"Image captured successfully: {filepath}")

        return send_file(str(filepath), mimetype='image/jpeg')
    except Exception as e:
        logger.error(f"Error capturing image: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/status')
def get_status():
    """Get camera status."""
    if not camera:
        return jsonify({'status': 'error', 'message': 'Camera not initialized'}), 500

    try:
        status_data = camera.get_status()
        return jsonify({'status': 'ok', 'data': status_data})
    except Exception as e:
        logger.error(f"Error getting status: {e}")
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
            logger.error(f"Error updating settings: {e}")
            return jsonify({'status': 'error', 'message': str(e)}), 500
    else:
        try:
            settings = camera.get_status()['settings']
            return jsonify({'status': 'ok', 'data': settings})
        except Exception as e:
            logger.error(f"Error getting settings: {e}")
            return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/rotate', methods=['POST'])
def rotate_camera():
    """Rotate the camera view 90 degrees clockwise."""
    if not camera:
        return jsonify({'status': 'error', 'message': 'Camera not initialized'}), 500

    try:
        current_rotation = camera.get_status()['settings'].get('rotation', 0)
        new_rotation = (current_rotation + 90) % 360
        logger.info(f"Rotating camera from {current_rotation} to {new_rotation} degrees")

        camera.update_settings({'rotation': new_rotation})

        return jsonify({
            'status': 'ok',
            'data': {'rotation': new_rotation}
        })
    except Exception as e:
        logger.error(f"Error rotating camera: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/live')
def live_feed():
    """Render the live feed page."""
    return render_template('live.html')

if __name__ == '__main__':
    logger.info("Starting Flask server on 0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)