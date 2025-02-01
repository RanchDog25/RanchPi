import logging
import platform
import time
from pathlib import Path
import io
import os
from PIL import Image, ImageDraw
from flask import Flask, render_template, send_file, jsonify, request, url_for
from flask_cors import CORS
from werkzeug.serving import is_running_from_reloader
import libcamera

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

# Disable Flask development features
app.env = 'production'  # Force production mode
app.debug = False      # Ensure debug is off

# Ensure the images directory exists
UPLOAD_FOLDER = Path("static/images")
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

# Global camera instance
camera = None

def initialize_camera():
    """Initialize and configure the camera based on environment"""
    global camera
    if is_running_from_reloader():
        logger.info("Skipping camera initialization in reloader process")
        return MockCamera()

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
            except ImportError as e:
                logger.error(f"Failed to import picamera2: {e}")
                return MockCamera()

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

        else:
            logger.info(f"Not on Raspberry Pi (machine: {machine}), using mock camera")
            return MockCamera()
    except Exception as e:
        logger.error(f"Unexpected error in camera initialization: {e}")
        return MockCamera()

def cleanup():
    """Cleanup camera resources on shutdown"""
    global camera
    if camera:
        try:
            if hasattr(camera, 'stop'):
                camera.stop()
            if hasattr(camera, 'close'):
                camera.close()
            logger.info("Camera resources cleaned up")
        except Exception as e:
            logger.error(f"Error cleaning up camera: {e}")

class MockCamera:
    """Mock camera for development environment"""
    def __init__(self):
        self.width = 640
        self.height = 480
        self.settings = {
            'brightness': 50,
            'contrast': 50,
            'resolution': f"{self.width}x{self.height}",
            'rotation': 0  # Add rotation setting
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
                    if key == 'rotation':
                        # Normalize rotation to 0, 90, 180, or 270
                        self.settings['rotation'] = value % 360
            logger.info(f"Mock camera: settings updated to {self.settings}")
            return self.settings
        except Exception as e:
            logger.error(f"Mock camera: error updating settings: {e}")
            raise

# Initialize camera only in main process
if not is_running_from_reloader():
    camera = initialize_camera()
    import atexit
    atexit.register(cleanup)
else:
    camera = MockCamera()

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
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = f"latest_{timestamp}.jpg"
        filepath = UPLOAD_FOLDER / filename

        if isinstance(camera, MockCamera):
            success = camera.capture_file(str(filepath))
            if not success:
                raise Exception("Failed to capture mock image")
        else:
            # For Picamera2
            try:
                camera.capture_file(str(filepath))
                logger.info(f"Successfully captured image to {filepath}")
            except Exception as e:
                logger.error(f"Error capturing with Picamera2: {e}")
                raise

        logger.info("Image captured successfully")
        return send_file(str(filepath), mimetype='image/jpeg')
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
            
@app.route('/rotate', methods=['POST'])
def rotate_camera():
    """Rotate the camera view 90 degrees clockwise."""
    if not camera:
        logger.error("Camera not initialized")
        return jsonify({'status': 'error', 'message': 'Camera not initialized'}), 500

    try:
        current_rotation = camera.get_status()['settings'].get('rotation', 0)
        new_rotation = (current_rotation + 90) % 360  # Increment by 90 degrees

        if isinstance(camera, MockCamera):
            camera.update_settings({'rotation': new_rotation})
        else:
            # For real Picamera2, update the transform
            camera.configure(camera.create_still_configuration(
                main={"size": (640, 480)},
                lores={"size": (320, 240)},
                display="lores",
                transform=libcamera.Transform(rotation=new_rotation)
            ))
            logger.info(f"Updated camera rotation to {new_rotation} degrees")

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
    logger.info("Accessing live feed page")
    return render_template('live.html')

if __name__ == '__main__':
    # Disable debug mode and reloader to prevent camera initialization conflicts
    logger.info("Starting Flask server on 0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False, threaded=True)