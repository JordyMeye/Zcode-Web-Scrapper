#!/usr/bin/env python3
"""Simplified scraper without Selenium - test if the page even works"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

print("[*] Testing direct HTTP request to Z Code System...")

url = "https://zcodesystem.com/scorespredictor/?hop=sportsmart"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

try:
    print(f"[*] Fetching: {url}")
    response = requests.get(url, headers=headers, timeout=15)
    print(f"[+] Status code: {response.status_code}")
    
    if response.status_code == 200:
        print("[+] Page loaded successfully!")
        
        # Save page source for inspection
        with open('page_source_test.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print("[+] Saved page source to page_source_test.html")
        
        # Try to parse
        soup = BeautifulSoup(response.text, 'html.parser')
        tables = soup.find_all('table')
        print(f"[+] Found {len(tables)} tables")
        
        # Extract text
        text = soup.get_text()
        text_preview = text[:500]
        print(f"[+] Page text preview:\n{text_preview}")
        
    else:
        print(f"[-] Unexpected status code: {response.status_code}")
        
except requests.exceptions.Timeout:
    print("[-] Request timed out")
except requests.exceptions.ConnectionError as e:
    print(f"[-] Connection error: {e}")
except Exception as e:
    print(f"[-] Error: {e}")

print("[*] Test complete!")
