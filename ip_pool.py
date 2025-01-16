import asyncio
import time
import httpx
import requests
from httpx import Proxy
import threading
import random

class IpPool:
    def __init__(self):
        self.ip_list = {}
        # API接口，返回格式为json
        self.api_url = ""  # API接口
        self.username = ""
        self.password = ""
        threading.Thread(target=self.interval_add_ip, daemon=True).start()
        threading.Thread(target=self.interval_remove_ip, daemon=True).start()

    def interval_add_ip(self, interval=1):
        """定时添加IP"""
        while True:
            try:
                # 发送HTTP请求获取新的代理IP
                response = requests.get(self.api_url)
                if response.status_code == 200:
                    proxy_data = response.json()["data"]["proxy_list"]
                    for proxy in proxy_data:
                        data = proxy.split(",")
                        proxy_url = f"http://{self.username}:{self.password}@{data[0]}"
                        self.ip_list[proxy_url] = int(data[1]) + int(time.time())
                    print(f"Get IP : {len(self.ip_list)}")
                else:
                    print("Failed to fetch new proxy IP")
            except Exception as e:
                print(f"Error fetching new proxy IP: {e}")
            time.sleep(interval)

    def get_ip(self) -> str:
        """获取一个可用的代理IP"""
        if self.ip_list:
            proxy_url = random.choice(list(self.ip_list.keys()))  # 获取第一个可用的代理IP
            return proxy_url
        else:
            return None

    def interval_remove_ip(self, interval=60):
        """定时删除超时的IP"""
        while True:
            current_time = int(time.time())
            # 删除超时的IP
            self.ip_list = {ip: timestamp for ip, timestamp in self.ip_list.items() if current_time < timestamp}
            print(f"Removed expired proxies.")
            # 等待指定的时间间隔
            time.sleep(interval)

async def main():
    async def fetch(url):
        global a
        async with httpx.AsyncClient(proxy=a.get_ip(), timeout=10) as client:
            resp = await client.get(url)
            print(f"status_code: {resp.status_code}, content: {resp.content}")

    tasks = [fetch("https://4.ipw.cn/") for _ in range(5)]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    a = IpPool()
    time.sleep(2)
    print(a.get_ip())
    asyncio.run(main())
    