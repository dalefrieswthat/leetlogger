import os
import subprocess
import logging
from datetime import datetime

class NotificationManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.setup_logging()
        
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
        
        self.icon_path = None
        for path in icon_paths:
            if os.path.exists(path):
                self.icon_path = path
                self.logger.info(f"Found icon at: {path}")
                break
        
        if not self.icon_path:
            self.logger.warning("Could not find application icon")
            # Create a default icon if none exists
            try:
                self.create_default_icon()
                self.icon_path = os.path.join(os.getcwd(), "icon.png")
            except Exception as e:
                self.logger.error(f"Failed to create default icon: {e}")

    def create_default_icon(self):
        """Create a simple default icon if none exists"""
        from PIL import Image, ImageDraw
        img = Image.new('RGBA', (1024, 1024), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        # Draw a green circle
        draw.ellipse((100, 100, 924, 924), fill=(76, 175, 80, 255))
        # Draw a white 'L'
        draw.rectangle((400, 300, 500, 800), fill=(255, 255, 255, 255))
        draw.rectangle((500, 600, 700, 700), fill=(255, 255, 255, 255))
        img.save("icon.png")

    def setup_logging(self):
        """Set up logging configuration"""
        log_dir = os.path.join(os.path.expanduser("~"), "Library", "Logs", "LeetLogger")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, f"notifications_{datetime.now().strftime('%Y%m%d')}.log")
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )

    def send_daily_problem_notification(self, title, url):
        """Send a notification for the daily problem"""
        try:
            notification_args = {
                "title": "LeetLogger - Daily Problem",
                "subtitle": title,
                "message": f"Click to open: {url}",
                "sound": "default"
            }
            
            if self.icon_path and os.path.exists(self.icon_path):
                notification_args["appIcon"] = self.icon_path
            
            subprocess.run([
                "osascript",
                "-e",
                f'display notification "{notification_args["message"]}" with title "{notification_args["title"]}" subtitle "{notification_args["subtitle"]}" sound name "{notification_args["sound"]}"'
            ])
            self.logger.info(f"Sent daily problem notification: {title}")
        except Exception as e:
            self.logger.error(f"Failed to send daily problem notification: {e}")

    def send_reminder_notification(self):
        """Send a reminder notification"""
        try:
            notification_args = {
                "title": "LeetLogger - Reminder",
                "message": "Don't forget to solve today's problem!",
                "sound": "default"
            }
            
            if self.icon_path and os.path.exists(self.icon_path):
                notification_args["appIcon"] = self.icon_path
            
            subprocess.run([
                "osascript",
                "-e",
                f'display notification "{notification_args["message"]}" with title "{notification_args["title"]}" sound name "{notification_args["sound"]}"'
            ])
            self.logger.info("Sent reminder notification")
        except Exception as e:
            self.logger.error(f"Failed to send reminder notification: {e}")

    def send_completion_notification(self, problem_title):
        """Send a notification for problem completion"""
        try:
            notification_args = {
                "title": "LeetLogger - Problem Completed",
                "message": f"Great job completing: {problem_title}",
                "sound": "default"
            }
            
            if self.icon_path and os.path.exists(self.icon_path):
                notification_args["appIcon"] = self.icon_path
            
            subprocess.run([
                "osascript",
                "-e",
                f'display notification "{notification_args["message"]}" with title "{notification_args["title"]}" sound name "{notification_args["sound"]}"'
            ])
            self.logger.info(f"Sent completion notification for: {problem_title}")
        except Exception as e:
            self.logger.error(f"Failed to send completion notification: {e}") 