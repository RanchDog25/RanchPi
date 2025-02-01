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
import numpy as np
from datetime import datetime
import threading
import schedule

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

# Configure CORS for external access
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Disable Flask debug mode
app.debug = False

# Global variables section
UPLOAD_FOLDER = Path("static/images")
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

# Add scheduled capture settings
CAPTURE_SETTINGS = {
    'interval': 0,  # 0 means disabled, otherwise minutes between captures
    'is_scheduled': False
}

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
        self.is_running = True
        self.capture_thread = None
        logger.info("Mock camera initialized with settings: %s", self.settings)

    def start_scheduled_capture(self, interval_minutes):
        """Start scheduled capture"""
        if interval_minutes <= 0:
            logger.info("Scheduled capture disabled")
            CAPTURE_SETTINGS['is_scheduled'] = False
            CAPTURE_SETTINGS['interval'] = 0
            return

        CAPTURE_SETTINGS['interval'] = interval_minutes
        CAPTURE_SETTINGS['is_scheduled'] = True
        logger.info(f"Starting scheduled capture every {interval_minutes} minutes")

        def scheduled_capture():
            while CAPTURE_SETTINGS['is_scheduled']:
                self.capture_scheduled_image()
                time.sleep(interval_minutes * 60)

        if self.capture_thread is None or not self.capture_thread.is_alive():
            self.capture_thread = threading.Thread(target=scheduled_capture)
            self.capture_thread.daemon = True
            self.capture_thread.start()

    def stop_scheduled_capture(self):
        """Stop scheduled capture"""
        CAPTURE_SETTINGS['is_scheduled'] = False
        CAPTURE_SETTINGS['interval'] = 0
        logger.info("Stopped scheduled capture")

    def capture_scheduled_image(self):
        """Capture image on schedule"""
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        filename = f"scheduled_{timestamp}.jpg"
        filepath = UPLOAD_FOLDER / filename
        self.capture_file(str(filepath))
        logger.info(f"Scheduled capture saved to {filepath}")

    def start(self):
        self.is_running = True
        logger.info("Mock camera started")

    def stop(self):
        self.is_running = False
        logger.info("Mock camera stopped")

    def get_status(self):
        return {
            'running': self.is_running,
            'settings': self.settings
        }

    def capture_file(self, filename):
        try:
            # Create a test pattern image
            img = Image.new('RGB', (self.width, self.height), color='white')
            draw = ImageDraw.Draw(img)

            # Add colored stripes
            stripe_height = self.height // 3
            colors = ['red', 'green', 'blue']
            for i, color in enumerate(colors):
                draw.rectangle(
                    [0, i * stripe_height, self.width, (i + 1) * stripe_height],
                    fill=color
                )

            # Add development mode indicator
            font_size = 36
            text = "Development Mode"
            draw.text(
                (self.width//2 - 100, self.height//2 - font_size//2),
                text,
                fill='white',
                stroke_width=2,
                stroke_fill='black'
            )

            # Add timestamp
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            draw.text(
                (10, self.height - 30),
                timestamp,
                fill='white',
                stroke_width=1,
                stroke_fill='black'
            )

            # Apply brightness and contrast
            brightness = self.settings['brightness'] / 50.0  # Convert to float 0-2
            contrast = self.settings['contrast'] / 50.0  # Convert to float 0-2

            # Apply image enhancements
            if brightness != 1.0:
                img = Image.eval(img, lambda x: min(255, max(0, int(x * brightness))))
            if contrast != 1.0:
                img = Image.eval(img, lambda x: min(255, max(0, int(128 + (x-128) * contrast))))

            # Apply rotation if needed
            if self.settings['rotation'] != 0:
                logger.info(f"Rotating image by {self.settings['rotation']} degrees")
                img = img.rotate(self.settings['rotation'], expand=True)

            img.save(filename, quality=95)
            logger.info(f"Mock camera: captured test pattern saved to {filename}")
            return True
        except Exception as e:
            logger.error(f"Mock camera: error capturing image: {e}")
            return False

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

class PiCamera2Wrapper:
    """Wrapper for PiCamera2 to handle rotation consistently"""
    def __init__(self, picam):
        self.camera = picam
        self.settings = CAMERA_SETTINGS.copy()
        self.is_running = True
        logger.info("PiCamera2Wrapper initialized with settings: %s", self.settings)

    def capture_file(self, filename):
        try:
            # Always capture to memory first for consistent rotation handling
            stream = io.BytesIO()
            self.camera.capture_file(stream, format='jpeg')
            stream.seek(0)

            # Open with PIL for rotation
            with Image.open(stream) as img:
                # Apply rotation if needed
                if self.settings['rotation'] != 0:
                    logger.info(f"Rotating image by {self.settings['rotation']} degrees")
                    img = img.rotate(self.settings['rotation'])

                # Save the final image
                img.save(filename, 'JPEG', quality=85)
                logger.info(f"Captured and saved image to {filename}")

        except Exception as e:
            logger.error(f"Error in PiCamera capture: {e}")
            # Fallback to direct capture if rotation fails
            self.camera.capture_file(filename)
            logger.info("Fallback: Direct capture successful")

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
                        self.settings['rotation'] = value % 360
                        logger.info(f"Updated PiCamera rotation to {self.settings['rotation']} degrees")
            return self.settings
        except Exception as e:
            logger.error(f"Error updating PiCamera settings: {e}")
            raise

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
                from picamera2 import Picamera2
                logger.info("Successfully imported picamera2")

                # Create Picamera2 instance
                picam = Picamera2()
                logger.info("Created Picamera2 instance")

                # Get available cameras
                cameras = picam.global_camera_info()
                logger.info(f"Available cameras: {cameras}")

                # Create camera configuration
                camera_config = picam.create_still_configuration(
                    main={"size": (640, 480)},
                    lores={"size": (320, 240)},
                    display="lores"
                )
                logger.info(f"Created camera configuration: {camera_config}")

                picam.configure(camera_config)
                logger.info("Applied camera configuration")

                picam.start()
                logger.info("Started camera")

                # Test capture
                picam.capture_file("test.jpg")
                logger.info("Successfully performed test capture")
                os.remove("test.jpg")  # Clean up test file

                # Return wrapped PiCamera2
                return PiCamera2Wrapper(picam)

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

# Add new endpoint for scheduled capture settings
@app.route('/schedule', methods=['POST'])
def set_schedule():
    """Set or update scheduled capture interval"""
    if not camera:
        return jsonify({'status': 'error', 'message': 'Camera not initialized'}), 500

    try:
        data = request.get_json()
        interval = int(data.get('interval', 0))

        if interval > 0:
            camera.start_scheduled_capture(interval)
            message = f"Scheduled capture enabled every {interval} minutes"
        else:
            camera.stop_scheduled_capture()
            message = "Scheduled capture disabled"

        return jsonify({
            'status': 'ok',
            'message': message,
            'settings': {
                'interval': CAPTURE_SETTINGS['interval'],
                'is_scheduled': CAPTURE_SETTINGS['is_scheduled']
            }
        })
    except Exception as e:
        logger.error(f"Error setting schedule: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/schedule/status')
def get_schedule_status():
    """Get current schedule settings"""
    return jsonify({
        'status': 'ok',
        'settings': {
            'interval': CAPTURE_SETTINGS['interval'],
            'is_scheduled': CAPTURE_SETTINGS['is_scheduled']
        }
    })


if __name__ == '__main__':
    logger.info("Starting Flask server on 0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)