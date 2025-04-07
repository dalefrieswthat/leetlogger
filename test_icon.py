import os
import subprocess
import logging
from datetime import datetime

def setup_logging():
    """Set up logging configuration"""
    log_dir = os.path.join(os.path.expanduser("~"), "Library", "Logs", "LeetLogger")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"icon_test_{datetime.now().strftime('%Y%m%d')}.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def find_icon():
    """Try to find the icon in various locations"""
    logger = setup_logging()
    
    # Try multiple possible icon locations
    icon_paths = [
        os.path.join(os.getcwd(), "icon.png"),
        os.path.join(os.getcwd(), "resources", "icon.png"),
        os.path.abspath("icon.png"),
        os.path.abspath(os.path.join("resources", "icon.png")),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.png"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "icon.png"),
        "/Applications/LeetLogger.app/Contents/Resources/icon.png"
    ]
    
    logger.info("Testing icon paths:")
    for path in icon_paths:
        exists = os.path.exists(path)
        logger.info(f"Path: {path}")
        logger.info(f"Exists: {exists}")
        if exists:
            logger.info(f"File size: {os.path.getsize(path)} bytes")
            return path
    
    logger.warning("No icon found in any location")
    return None

def send_test_notification(icon_path):
    """Send a test notification with the icon"""
    logger = setup_logging()
    
    try:
        notification_args = {
            "title": "LeetLogger - Icon Test",
            "message": "This is a test notification to check the icon",
            "sound": "default"
        }
        
        if icon_path and os.path.exists(icon_path):
            notification_args["appIcon"] = icon_path
            logger.info(f"Using icon at: {icon_path}")
        else:
            logger.warning("No valid icon path provided")
        
        subprocess.run([
            "osascript",
            "-e",
            f'display notification "{notification_args["message"]}" with title "{notification_args["title"]}" sound name "{notification_args["sound"]}"'
        ])
        logger.info("Test notification sent successfully")
    except Exception as e:
        logger.error(f"Failed to send test notification: {e}")

if __name__ == "__main__":
    logger = setup_logging()
    logger.info("Starting icon test...")
    
    icon_path = find_icon()
    if icon_path:
        logger.info(f"Found icon at: {icon_path}")
        send_test_notification(icon_path)
    else:
        logger.error("No icon found, cannot send test notification") 