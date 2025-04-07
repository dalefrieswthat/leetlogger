import json
import os
import shutil
from datetime import datetime
from pathlib import Path

class BackupManager:
    def __init__(self, data_file="problems.json", backup_dir="backups"):
        self.data_file = data_file
        self.backup_dir = backup_dir
        self._ensure_backup_dir()
    
    def _ensure_backup_dir(self):
        """Ensure backup directory exists"""
        Path(self.backup_dir).mkdir(parents=True, exist_ok=True)
    
    def create_backup(self):
        """Create a backup of the current data file"""
        if not os.path.exists(self.data_file):
            return False
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(self.backup_dir, f"problems_{timestamp}.json")
        
        try:
            shutil.copy2(self.data_file, backup_file)
            return True
        except Exception as e:
            print(f"Backup failed: {e}")
            return False
    
    def restore_from_backup(self, backup_file):
        """Restore data from a backup file"""
        try:
            shutil.copy2(backup_file, self.data_file)
            return True
        except Exception as e:
            print(f"Restore failed: {e}")
            return False
    
    def get_available_backups(self):
        """Get list of available backups"""
        if not os.path.exists(self.backup_dir):
            return []
        
        backups = []
        for file in os.listdir(self.backup_dir):
            if file.startswith("problems_") and file.endswith(".json"):
                file_path = os.path.join(self.backup_dir, file)
                timestamp = file.replace("problems_", "").replace(".json", "")
                backups.append({
                    'file': file_path,
                    'timestamp': timestamp,
                    'date': datetime.strptime(timestamp, "%Y%m%d_%H%M%S").strftime("%Y-%m-%d %H:%M:%S")
                })
        
        return sorted(backups, key=lambda x: x['timestamp'], reverse=True)
    
    def cleanup_old_backups(self, keep_last_n=5):
        """Keep only the last N backups"""
        backups = self.get_available_backups()
        if len(backups) <= keep_last_n:
            return
        
        for backup in backups[keep_last_n:]:
            try:
                os.remove(backup['file'])
            except Exception as e:
                print(f"Failed to delete backup {backup['file']}: {e}") 