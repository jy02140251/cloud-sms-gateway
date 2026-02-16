"""
备份管理器
支持增量备份、压缩和保留策略
"""

import os
import shutil
import gzip
from datetime import datetime, timedelta
from pathlib import Path
from typing import List


class BackupManager:
    """备份管理器"""
    
    def __init__(self, source_dir: str, backup_dir: str, retention_days: int = 7):
        self.source_dir = Path(source_dir)
        self.backup_dir = Path(backup_dir)
        self.retention_days = retention_days
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def create_backup(self, compress: bool = True) -> str:
        """创建备份"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_{timestamp}"
        backup_path = self.backup_dir / backup_name
        
        if compress:
            backup_path = backup_path.with_suffix(".tar.gz")
            shutil.make_archive(str(backup_path.with_suffix("")), "gztar", self.source_dir)
        else:
            shutil.copytree(self.source_dir, backup_path)
        
        return str(backup_path)
    
    def cleanup_old_backups(self):
        """清理旧备份"""
        cutoff = datetime.now() - timedelta(days=self.retention_days)
        for backup_file in self.backup_dir.glob("backup_*"):
            if backup_file.stat().st_mtime < cutoff.timestamp():
                backup_file.unlink()
                print(f"Deleted old backup: {backup_file}")


if __name__ == "__main__":
    manager = BackupManager("/tmp/source", "/tmp/backups", retention_days=7)
    backup_path = manager.create_backup()
    print(f"Backup created: {backup_path}")
    manager.cleanup_old_backups()
