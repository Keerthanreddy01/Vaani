"""
ADB Connection Manager
Handles device detection, connection, and port forwarding
"""

import subprocess
import logging
import time
from typing import Optional, List

logger = logging.getLogger(__name__)


class ADBConnection:
    """Manage ADB connection to Android device"""

    def __init__(self):
        self.device_id: Optional[str] = None
        self.connected = False
        self.server_port = 8765
        self.adb_path = 'adb'

    def check_adb_installed(self) -> bool:
        """Check if ADB is installed and accessible"""
        # Common ADB locations
        adb_paths = [
            'adb',
            r'C:\Users\keert\AppData\Local\Android\Sdk\platform-tools\adb.exe',
            r'C:\platform-tools\adb.exe',
            r'C:\Android\platform-tools\adb.exe',
        ]

        for adb_path in adb_paths:
            try:
                result = subprocess.run(
                    [adb_path, 'version'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    self.adb_path = adb_path
                    logger.info(f"✅ ADB found at: {adb_path}")
                    return True
            except (FileNotFoundError, Exception):
                continue

        logger.error("❌ ADB not found in common locations")
        return False
    
    def restart_adb_server(self) -> bool:
        """Restart ADB server"""
        try:
            logger.info("Restarting ADB server...")
            subprocess.run([self.adb_path, 'kill-server'], timeout=5)
            time.sleep(1)
            subprocess.run([self.adb_path, 'start-server'], timeout=5)
            time.sleep(2)
            logger.info("✅ ADB server restarted")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to restart ADB: {e}")
            return False

    def detect_devices(self) -> List[str]:
        """Detect connected Android devices"""
        try:
            result = subprocess.run(
                [self.adb_path, 'devices'],
                capture_output=True,
                text=True,
                timeout=5
            )

            # Parse output
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            devices = []

            for line in lines:
                if '\tdevice' in line or '\tunauthorized' in line:
                    device_id = line.split('\t')[0]
                    status = line.split('\t')[1] if '\t' in line else 'unknown'
                    devices.append(device_id)
                    if 'unauthorized' in status:
                        logger.warning(f"⚠️ Device {device_id} is unauthorized - please accept USB debugging prompt on phone")

            return devices

        except Exception as e:
            logger.error(f"❌ Device detection failed: {e}")
            return []
    
    def connect(self, device_id: Optional[str] = None) -> bool:
        """
        Connect to Android device.
        
        Args:
            device_id: Specific device ID, or None for auto-detect
            
        Returns:
            True if connected successfully
        """
        # Check ADB
        if not self.check_adb_installed():
            return False
        
        # Detect devices
        devices = self.detect_devices()
        
        if not devices:
            logger.error("❌ No Android devices found!")
            logger.error("Please:")
            logger.error("  1. Connect phone via USB")
            logger.error("  2. Enable USB debugging in Developer Options")
            logger.error("  3. Accept USB debugging prompt on phone")
            return False
        
        # Select device
        if device_id:
            if device_id not in devices:
                logger.error(f"❌ Device {device_id} not found")
                return False
            self.device_id = device_id
        else:
            self.device_id = devices[0]
            if len(devices) > 1:
                logger.warning(f"Multiple devices found. Using: {self.device_id}")
        
        logger.info(f"✅ Connected to device: {self.device_id}")
        
        # Get device info
        self._print_device_info()
        
        # Setup port forwarding
        self._setup_port_forwarding()
        
        self.connected = True
        return True
    
    def _print_device_info(self):
        """Print device information"""
        try:
            # Get device model
            model = self._shell_command('getprop ro.product.model')
            manufacturer = self._shell_command('getprop ro.product.manufacturer')
            android_version = self._shell_command('getprop ro.build.version.release')
            
            logger.info(f"📱 Device: {manufacturer} {model}")
            logger.info(f"🤖 Android: {android_version}")
            
        except Exception as e:
            logger.warning(f"Could not get device info: {e}")
    
    def _setup_port_forwarding(self):
        """Setup port forwarding for communication"""
        try:
            # Forward port for WebSocket server
            subprocess.run(
                [self.adb_path, '-s', self.device_id, 'forward',
                 f'tcp:{self.server_port}', f'tcp:{self.server_port}'],
                timeout=5
            )
            logger.info(f"✅ Port forwarding: localhost:{self.server_port}")
        except Exception as e:
            logger.warning(f"Port forwarding failed: {e}")

    def _shell_command(self, command: str) -> str:
        """Execute ADB shell command"""
        try:
            result = subprocess.run(
                [self.adb_path, '-s', self.device_id, 'shell', command],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.stdout.strip()
        except Exception as e:
            logger.error(f"Shell command failed: {e}")
            return ""
    
    def disconnect(self):
        """Disconnect from device"""
        if self.connected:
            try:
                # Remove port forwarding
                subprocess.run(
                    ['adb', '-s', self.device_id, 'forward', '--remove-all'],
                    timeout=5
                )
            except:
                pass
            
            self.connected = False
            self.device_id = None
            logger.info("Disconnected from device")
    
    def is_connected(self) -> bool:
        """Check if device is still connected"""
        if not self.connected or not self.device_id:
            return False
        
        devices = self.detect_devices()
        return self.device_id in devices

