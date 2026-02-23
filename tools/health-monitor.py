"""健康监控器 - HTTP/TCP健康检查"""
import requests, socket

class HealthMonitor:
    def check_http(self, url: str, timeout: int = 5) -> bool:
        try: return requests.get(url, timeout=timeout).status_code == 200
        except: return False
    
    def check_tcp(self, host: str, port: int, timeout: int = 5) -> bool:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(timeout)
            r = s.connect_ex((host, port))
            s.close()
            return r == 0
        except: return False

if __name__ == "__main__":
    m = HealthMonitor()
    print(f"HTTP: {m.check_http('https://github.com')}")
    print(f"TCP: {m.check_tcp('github.com', 443)}")
