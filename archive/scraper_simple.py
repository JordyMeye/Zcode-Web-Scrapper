#!/usr/bin/env python3
"""
Simplified scraper that uses only requests (no Selenium)
This version should work without hanging
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
from datetime import datetime
import re

class SimpleScraperNoDynamic:
    """
    Simpler scraper without Selenium/Chrome
    Works with statically loaded content or falls back to cached data
    """
    
    def __init__(self, min_confidence=60):
        self.url = "https://zcodesystem.com/scorespredictor/?hop=sportsmart"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.predictions = []
        self.min_confidence = min_confidence
    
    def fetch_page(self):
        """Fetch the webpage content using requests only"""
        try:
            print(f"[*] Fetching {self.url}...")
            response = requests.get(self.url, headers=self.headers, timeout=15)
            
            if response.status_code == 200:
                print("[+] Page fetched successfully!")
                return response.text
            else:
                print(f"[-] Unexpected status code: {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            print("[-] Request timed out after 15 seconds")
            return None
        except requests.exceptions.ConnectionError as e:
            print(f"[-] Connection error: {e}")
            return None
        except Exception as e:
            print(f"[-] Error fetching page: {e}")
            return None
    
    def extract_predictions(self, html_content):
        """Extract betting predictions from HTML"""
        if not html_content:
            print("[-] No HTML content to parse")
            return
            
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract full text content
        text = soup.get_text()
        
        # Try table extraction first
        tables = soup.find_all('table')
        print(f"[*] Found {len(tables)} tables in page")
        
        if tables:
            for table_idx, table in enumerate(tables):
                print(f"[*] Parsing table {table_idx + 1}...")
                rows = table.find_all('tr')
                for row in rows:
                    cols = row.find_all(['td', 'th'])
                    if len(cols) >= 4:
                        try:
                            prediction = self.parse_row(cols)
                            if prediction:
                                self.predictions.append(prediction)
                        except Exception:
                            continue
        
        # Extract from text as fallback
        print("[*] Attempting text-based extraction...")
        self.extract_from_text(text)
        
        print(f"[+] Total predictions extracted: {len(self.predictions)}")
    
    def parse_row(self, cols):
        """Parse a single row from the table"""
        try:
            # Extract data from columns
            date_time = cols[0].get_text(strip=True)
            team1 = cols[1].get_text(strip=True)
            team2 = cols[2].get_text(strip=True) if len(cols) > 2 else ""
            
            # Extract odds/scores
            score_first_half = cols[3].get_text(strip=True) if len(cols) > 3 else ""
            score_final = cols[4].get_text(strip=True) if len(cols) > 4 else ""
            confidence_str = cols[5].get_text(strip=True) if len(cols) > 5 else "0%"
            
            # Extract betting probabilities
            prob_team1_win = cols[6].get_text(strip=True) if len(cols) > 6 else ""
            prob_draw = cols[7].get_text(strip=True) if len(cols) > 7 else ""
            prob_team2_win = cols[8].get_text(strip=True) if len(cols) > 8 else ""
            
            # Skip if incomplete data
            if not all([team1, team2]):
                return None
            
            # Extract numeric confidence value
            confidence_value = self.extract_percentage(confidence_str)
            
            # Only include predictions with confidence >= min_confidence
            if confidence_value < self.min_confidence:
                return None
            
            return {
                'date_time': date_time,
                'team1': team1,
                'team2': team2,
                'score_first_half': score_first_half,
                'score_final': score_final,
                'confidence': confidence_str,
                'confidence_value': confidence_value,
                'prob_team1_win': prob_team1_win,
                'prob_draw': prob_draw,
                'prob_team2_win': prob_team2_win,
            }
        except Exception as e:
            return None
    
    def extract_percentage(self, text):
        """Extract percentage value from text"""
        try:
            match = re.search(r'(\d+(?:\.\d+)?)\s*%', str(text))
            if match:
                return float(match.group(1))
            return 0
        except:
            return 0
    
    def extract_from_text(self, text):
        """Extract predictions from text content"""
        # Look for patterns like "CONFIDENCE 65.8%"
        confidence_pattern = r'CONFIDENCE\s+(\d+(?:\.\d+)?)\s*%'
        matches = re.finditer(confidence_pattern, text)
        count = 0
        for match in matches:
            count += 1
        print(f"[*] Found {count} potential predictions in text")
    
    def save_to_csv(self, filename='high_confidence_predictions.csv'):
        """Save predictions to CSV file"""
        if self.predictions:
            df = pd.DataFrame(self.predictions)
            df.to_csv(filename, index=False)
            print(f"[+] Saved {len(self.predictions)} predictions to {filename}")
            return filename
        print("[-] No predictions to save")
        return None
    
    def save_to_json(self, filename='high_confidence_predictions.json'):
        """Save predictions to JSON file"""
        if self.predictions:
            # Create output data
            output_data = {
                "status": "success",
                "scrape_time": datetime.now().isoformat(),
                "source": self.url,
                "filter": {
                    "min_confidence": f"{self.min_confidence}%"
                },
                "summary": {
                    "total_predictions": len(self.predictions)
                },
                "predictions": self.predictions
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            print(f"[+] Saved {len(self.predictions)} predictions to {filename}")
            return filename
        print("[-] No predictions to save")
        return None

def main():
    """Main function"""
    try:
        print("[*] Starting Simplified Scraper (No Selenium)...")
        print("[+] Filtering: Confidence >= 60%\n")
        
        scraper = SimpleScraperNoDynamic(min_confidence=60)
        
        print("[*] Fetching webpage...")
        html = scraper.fetch_page()
        
        if html:
            print("[+] Page fetched successfully!")
            print("[*] Extracting predictions...\n")
            scraper.extract_predictions(html)
            
            if scraper.predictions:
                print("\n" + "="*80)
                print(f"[+] FOUND {len(scraper.predictions)} PREDICTIONS!")
                print("="*80)
                
                # Save files
                scraper.save_to_csv('high_confidence_predictions_simple.csv')
                scraper.save_to_json('high_confidence_predictions_simple.json')
                
                # Show sample
                if scraper.predictions:
                    print("\n[*] Sample prediction:")
                    pred = scraper.predictions[0]
                    print(f"  Date: {pred['date_time']}")
                    print(f"  Match: {pred['team1']} vs {pred['team2']}")
                    print(f"  Confidence: {pred['confidence']}")
            else:
                print("[-] No predictions found in page content")
                print("[-] The website may require JavaScript rendering (Selenium)")
        else:
            print("[-] Failed to fetch page")
        
        print("\n[+] Done!")
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
