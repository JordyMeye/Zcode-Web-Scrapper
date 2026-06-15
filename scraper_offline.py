#!/usr/bin/env python3
"""
Scraper that uses existing page_source.html file
This allows extraction without needing network access
"""

from bs4 import BeautifulSoup
import pandas as pd
import json
from datetime import datetime
import re
import os

class OfflineScraper:
    """Scraper that works with existing HTML files"""
    
    def __init__(self, html_file='page_source.html', min_confidence=60):
        self.html_file = html_file
        self.predictions = []
        self.min_confidence = min_confidence
    
    def load_page(self):
        """Load HTML from file"""
        if not os.path.exists(self.html_file):
            print(f"[-] File not found: {self.html_file}")
            return None
        
        try:
            with open(self.html_file, 'r', encoding='utf-8') as f:
                print(f"[+] Loaded {self.html_file}")
                return f.read()
        except Exception as e:
            print(f"[-] Error loading file: {e}")
            return None
    
    def extract_predictions(self, html_content):
        """Extract betting predictions from HTML"""
        if not html_content:
            print("[-] No HTML content to parse")
            return
            
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Save some info about the page
        print(f"[*] Page title: {soup.title.string if soup.title else 'N/A'}")
        
        # Extract full text content
        text = soup.get_text()
        
        # Try table extraction first
        tables = soup.find_all('table')
        print(f"[*] Found {len(tables)} tables in page")
        
        if tables:
            for table_idx, table in enumerate(tables):
                print(f"[*] Parsing table {table_idx + 1}...")
                rows = table.find_all('tr')
                print(f"    Table has {len(rows)} rows")
                
                for row_idx, row in enumerate(rows):
                    cols = row.find_all(['td', 'th'])
                    if len(cols) >= 4:
                        try:
                            prediction = self.parse_row(cols)
                            if prediction:
                                self.predictions.append(prediction)
                                print(f"    [+] Row {row_idx}: Extracted {prediction['team1']} vs {prediction['team2']} ({prediction['confidence']})")
                        except Exception as e:
                            pass
        
        # Extract from text as fallback
        print("[*] Attempting text-based extraction...")
        self.extract_from_text(text)
        
        print(f"\n[+] Total predictions extracted: {len(self.predictions)}")
    
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
        # Look for confidence percentages
        confidence_pattern = r'CONFIDENCE\s+(\d+(?:\.\d+)?)\s*%'
        matches = list(re.finditer(confidence_pattern, text))
        print(f"[*] Found {len(matches)} confidence mentions in text")
    
    def save_to_csv(self, filename='high_confidence_predictions_new.csv'):
        """Save predictions to CSV file"""
        if self.predictions:
            df = pd.DataFrame(self.predictions)
            df.to_csv(filename, index=False)
            print(f"[+] Saved {len(self.predictions)} predictions to {filename}")
            return filename
        print("[-] No predictions to save to CSV")
        return None
    
    def save_to_json(self, filename='high_confidence_predictions_new.json'):
        """Save predictions to JSON file"""
        if self.predictions:
            # Create output data
            output_data = {
                "status": "success",
                "scrape_time": datetime.now().isoformat(),
                "source": "page_source.html (offline)",
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
        print("[-] No predictions to save to JSON")
        return None
    
    def display_results(self):
        """Display results"""
        if not self.predictions:
            print("\n[-] No predictions to display")
            return
        
        print("\n" + "="*100)
        print(f"HIGH CONFIDENCE PREDICTIONS ({self.min_confidence}%+)")
        print("="*100)
        
        for idx, pred in enumerate(self.predictions, 1):
            print(f"\n{idx}. {pred['team1']} vs {pred['team2']}")
            print(f"   Date: {pred['date_time']}")
            print(f"   Confidence: {pred['confidence']}")
            print(f"   Team 1 Win: {pred['prob_team1_win']}")
            print(f"   Draw: {pred['prob_draw']}")
            print(f"   Team 2 Win: {pred['prob_team2_win']}")
            if pred['score_first_half']:
                print(f"   1st Half: {pred['score_first_half']}")
            if pred['score_final']:
                print(f"   Final: {pred['score_final']}")

def main():
    """Main function"""
    try:
        print("[*] Starting Offline Scraper (using cached HTML)...")
        print("[+] Filtering: Confidence >= 60%\n")
        
        scraper = OfflineScraper('page_source.html', min_confidence=60)
        
        print("[*] Loading HTML file...")
        html = scraper.load_page()
        
        if html:
            print("[*] Extracting predictions...\n")
            scraper.extract_predictions(html)
            
            scraper.display_results()
            
            if scraper.predictions:
                print("\n" + "="*100)
                print("[*] Saving results...")
                scraper.save_to_csv()
                scraper.save_to_json()
                print("[+] Done!")
            else:
                print("\n[-] No predictions matched the criteria")
        else:
            print("[-] Failed to load HTML file")
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
