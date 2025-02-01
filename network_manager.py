import logging
import socket
import netifaces
import subprocess
import time
import websockets
import asyncio
import json
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class NetworkManager:
    def __init__(self):
        self.connection_types = {
            'ethernet': {'priority': 1, 'interface': 'eth0'},
            'wifi': {'priority': 2, 'interface': 'wlan0'},
            'cellular': {'priority': 3, 'interface': 'ppp0'}
        }
        self.current_connection = None
        self.device_id = self._get_device_id()
        self.ws_connection = None
        
    def _get_device_id(self):
        """Generate or retrieve unique device ID"""
        id_file = Path("/etc/ranchpi_device_id")
        if id_file.exists():
            return id_file.read_text().strip()
        # Use MAC address as fallback device ID
        return self._get_mac_address()
        
    def _get_mac_address(self):
        """Get MAC address of the first available interface"""
        interfaces = netifaces.interfaces()
        for interface in interfaces:
            if interface != 'lo':  # Skip loopback
                addrs = netifaces.ifaddresses(interface)
                if netifaces.AF_LINK in addrs:
                    return addrs[netifaces.AF_LINK][0]['addr'].replace(':', '')
        return None

    def check_interface(self, interface):
        """Check if network interface is up and has an IP address"""
        try:
            addrs = netifaces.ifaddresses(interface)
            return netifaces.AF_INET in addrs
        except ValueError:
            return False

    def get_best_connection(self):
        """Check available connections in priority order"""
        available_connections = []
        
        for conn_type, details in self.connection_types.items():
            if self.check_interface(details['interface']):
                available_connections.append((details['priority'], conn_type))
                logger.info(f"Found available connection: {conn_type}")
        
        if available_connections:
            # Sort by priority (lowest number = highest priority)
            available_connections.sort()
            return available_connections[0][1]
        
        return None

    async def connect_to_server(self, server_url):
        """Connect to Replit server via WebSocket"""
        while True:
            try:
                # Check best available connection
                connection_type = self.get_best_connection()
                if not connection_type:
                    logger.error("No network connection available")
                    await asyncio.sleep(30)  # Wait before retry
                    continue

                if connection_type != self.current_connection:
                    logger.info(f"Switching to {connection_type} connection")
                    self.current_connection = connection_type

                # Connect to WebSocket server
                async with websockets.connect(server_url) as websocket:
                    self.ws_connection = websocket
                    logger.info(f"Connected to server via {connection_type}")
                    
                    # Send initial device info
                    await websocket.send(json.dumps({
                        'type': 'device_info',
                        'device_id': self.device_id,
                        'connection_type': connection_type
                    }))

                    # Handle WebSocket communication
                    while True:
                        try:
                            # Send heartbeat
                            await websocket.send(json.dumps({
                                'type': 'heartbeat',
                                'device_id': self.device_id,
                                'connection_type': connection_type
                            }))
                            
                            # Wait for commands
                            message = await websocket.recv()
                            await self.handle_message(message)
                            
                            await asyncio.sleep(5)  # Heartbeat interval
                            
                        except websockets.exceptions.ConnectionClosed:
                            logger.warning("WebSocket connection closed")
                            break

            except Exception as e:
                logger.error(f"Connection error: {e}")
                await asyncio.sleep(10)  # Wait before retry
                continue

    async def handle_message(self, message):
        """Handle incoming messages from server"""
        try:
            data = json.loads(message)
            if data.get('type') == 'capture_request':
                # Handle capture request
                logger.info("Received capture request")
                # TODO: Implement capture logic
                pass
            elif data.get('type') == 'status_request':
                # Send status update
                await self.ws_connection.send(json.dumps({
                    'type': 'status_response',
                    'device_id': self.device_id,
                    'connection_type': self.current_connection,
                    'timestamp': time.time()
                }))
        except Exception as e:
            logger.error(f"Error handling message: {e}")

async def main():
    manager = NetworkManager()
    server_url = "wss://your-replit-server/ws"  # Replace with actual server URL
    await manager.connect_to_server(server_url)

if __name__ == "__main__":
    asyncio.run(main())
