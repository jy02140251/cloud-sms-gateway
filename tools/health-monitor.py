"""
健康监控器
HTTP/TCP 健康检查工具
"""

import requests
import socket
from typing import Dict, List


class HealthMonitor:
    """健康监控器"""
    
    def check_http(self, url: str, timeout: int = 5) -> bool:
        """HTTP 健康检查"""
        try:
            resp = requests.get(url, timeout=timeout)
            return resp.status_code == 200
        except:
            return False
    
    def check_tcp(self, host: str, port: int, timeout: int = 5) -> bool:
        """TCP 健康检查"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except:
            return False


if __name__ == "__main__":
    monitor = HealthMonitor()
    http_result = monitor.check_http('https://github.com')
    tcp_result = monitor.check_tcp('github.com', 443)
    print(f"HTTP check: {http_result}")
    print(f"TCP check: {tcp_result}")
