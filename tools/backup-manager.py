"""备份管理器 - 增量备份, 压缩, 保留策略"""
import shutil
from datetime import datetime, timedelta
from pathlib import Path

class BackupManager:
    def __init__(self, source: str, backup_dir: str, retention_days: int = 7):
        self.source = Path(source)
        self.backup_dir = Path(backup_dir)
        self.retention_days = retention_days
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def create_backup(self, compress=True) -> str:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = self.backup_dir / f"backup_{ts}"
        if compress:
            shutil.make_archive(str(path), "gztar", self.source)
            return str(path) + ".tar.gz"
        shutil.copytree(self.source, path)
        return str(path)
    
    def cleanup(self):
        cutoff = datetime.now() - timedelta(days=self.retention_days)
        for f in self.backup_dir.glob("backup_*"):
            if f.stat().st_mtime < cutoff.timestamp():
                f.unlink()

if __name__ == "__main__":
    m = BackupManager("/tmp/src", "/tmp/bak")
    print(m.create_backup())
