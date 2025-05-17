import concurrent.futures
import csv
import os
import requests
import time 
import random

class ProxyManager:
    def __init__(self, session, test_proxy : bool = False, max_workers : int =10):
        self.session = session
        self.proxys_unchecked = self.read_proxy_file()
        random.shuffle(self.proxys_unchecked)
        self.max_workers = max_workers
        self.init_proxy_csv(self.proxys_unchecked)
        
        if test_proxy:
            self.test_proxys()
        
    def read_proxy_file(self) -> list:
        with open('static/proxy.txt', 'r') as file:
            lines = file.readlines()
        return [line.strip() for line in lines]
    
    def fetch_with_proxy(self, p: str, url: str = "https://www.reddit.com/", timeout: int = 5, params: dict = None):
        address, port = p.split(':')
        # Définition des proxys pour HTTP et SOCKS5
        http_proxy = f"http://{address}:{port}"
        proxies_http = {"http": http_proxy, "https": address+":"+port}
        try:
            # Tentative avec proxy HTTP
            response = self.session.get(url, proxies=proxies_http, timeout=timeout, params=params)
            response.raise_for_status()
            self.update_proxy_count(p)
            time.sleep(5)
            return response
        except requests.RequestException as e:
            print(e)
            return
            
            
    def test_proxys(self) -> list[str]:
        print("Started Proxys Test")
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            executor.map(self.fetch_with_proxy, self.proxys_unchecked)
        print("Finished Proxys Test")
        
    def init_proxy_csv(self, proxies, filename: str = "proxy_success.csv"):
        existing_proxies = set()
        
        # Read existing proxies if file exists
        if os.path.exists(filename):
            with open(filename, mode='r', newline='') as file:
                reader = csv.reader(file)
                next(reader, None)  # Skip header
                existing_proxies = {rows[0] for rows in reader}
        
        # Append only new proxies
        with open(filename, mode='a', newline='') as file:
            writer = csv.writer(file)
            for proxy in proxies:
                if proxy not in existing_proxies:
                    writer.writerow([proxy, 0])
                    
        print("Initialized CSV with proxies.")
    
    def update_proxy_count(self, proxy: str, filename: str = "static/proxy_success.csv"):
        data = {}
        
        # Read existing data if file exists
        if os.path.exists(filename):
            with open(filename, mode='r', newline='') as file:
                reader = csv.reader(file)
                next(reader, None)  # Skip header
                data = {rows[0]: int(rows[1]) for rows in reader}
        
        # Update or add new proxy count
        data[proxy] = data.get(proxy, 0) + 1
        
        # Write back to CSV
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["PROXY", "SUCCESS_REQUEST_COUNT"])
            for key, value in sorted(data.items(), key=lambda item: item[1], reverse=True):
                writer.writerow([key, value])

    def get_sorted_proxies(self, filename: str = "static/proxy_success.csv"):
        if not os.path.exists(filename):
            return []
        
        with open(filename, mode='r', newline='') as file:
            reader = csv.reader(file)
            next(reader, None)  # Skip header
            proxies = sorted(reader, key=lambda row: int(row[1]), reverse=True)
            
        return [p[0] for p in proxies]