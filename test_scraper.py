#!/usr/bin/env python3
"""Test script to debug the scraper"""

import sys
import traceback

print("[DEBUG] Starting test script...", flush=True)

# Test 1: Check imports
print("[TEST 1] Checking imports...", flush=True)
try:
    import requests
    print("  ✓ requests", flush=True)
except Exception as e:
    print(f"  ✗ requests: {e}", flush=True)

try:
    from bs4 import BeautifulSoup
    print("  ✓ BeautifulSoup", flush=True)
except Exception as e:
    print(f"  ✗ BeautifulSoup: {e}", flush=True)

try:
    from selenium import webdriver
    print("  ✓ Selenium", flush=True)
except Exception as e:
    print(f"  ✗ Selenium: {e}", flush=True)

try:
    from webdriver_manager.chrome import ChromeDriverManager
    print("  ✓ webdriver_manager", flush=True)
except Exception as e:
    print(f"  ✗ webdriver_manager: {e}", flush=True)

# Test 2: Test basic HTTP request
print("\n[TEST 2] Testing basic HTTP request...", flush=True)
try:
    import requests
    response = requests.get("https://httpbin.org/get", timeout=10)
    print(f"  ✓ HTTP request successful: {response.status_code}", flush=True)
except Exception as e:
    print(f"  ✗ HTTP request failed: {e}", flush=True)

# Test 3: Test ChromeDriver
print("\n[TEST 3] Testing ChromeDriver...", flush=True)
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.chrome.service import Service
    
    print("  Starting Chrome driver...", flush=True)
    
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    print("  Chrome driver started successfully!", flush=True)
    print("  Testing page load...", flush=True)
    
    # Test with a simple page
    driver.get("https://httpbin.org/html")
    print(f"  Page loaded! Title: {driver.title}", flush=True)
    
    driver.quit()
    print("  ✓ ChromeDriver test successful", flush=True)
    
except Exception as e:
    print(f"  ✗ ChromeDriver test failed: {e}", flush=True)
    traceback.print_exc()

print("\n[DEBUG] Test completed!", flush=True)
