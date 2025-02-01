import asyncio
import websockets
import logging
import json
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Store connected devices
connected_devices = {}

async def handle_device_connection(websocket, path):
    """Handle incoming device connections"""
    device_id = None
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                message_type = data.get('type')
                
                if message_type == 'device_info':
                    device_id = data.get('device_id')
                    connected_devices[device_id] = {
                        'websocket': websocket,
                        'connection_type': data.get('connection_type'),
                        'last_seen': datetime.now(),
                        'status': 'connected'
                    }
                    logger.info(f"Device {device_id} connected via {data.get('connection_type')}")
                
                elif message_type == 'heartbeat':
                    if device_id in connected_devices:
                        connected_devices[device_id]['last_seen'] = datetime.now()
                        connected_devices[device_id]['connection_type'] = data.get('connection_type')
                
                elif message_type == 'status_response':
                    if device_id in connected_devices:
                        connected_devices[device_id].update({
                            'last_seen': datetime.now(),
                            'connection_type': data.get('connection_type')
                        })
                
            except json.JSONDecodeError:
                logger.error("Invalid JSON message received")
                continue
            
    except websockets.exceptions.ConnectionClosed:
        logger.info(f"Device {device_id} disconnected")
    finally:
        if device_id and device_id in connected_devices:
            del connected_devices[device_id]

async def check_devices():
    """Periodically check device status and clean up stale connections"""
    while True:
        current_time = datetime.now()
        for device_id, info in list(connected_devices.items()):
            time_diff = (current_time - info['last_seen']).total_seconds()
            if time_diff > 30:  # Device considered stale after 30 seconds
                logger.warning(f"Device {device_id} connection stale, removing")
                del connected_devices[device_id]
        await asyncio.sleep(10)

def get_connected_devices():
    """Return list of connected devices"""
    return {
        device_id: {
            'connection_type': info['connection_type'],
            'last_seen': info['last_seen'].isoformat(),
            'status': info['status']
        }
        for device_id, info in connected_devices.items()
    }

async def start_server(host='0.0.0.0', port=6789):
    """Start WebSocket server"""
    server = await websockets.serve(handle_device_connection, host, port)
    logger.info(f"WebSocket server started on ws://{host}:{port}")
    
    # Start device checker
    asyncio.create_task(check_devices())
    
    await server.wait_closed()

if __name__ == '__main__':
    asyncio.run(start_server())
