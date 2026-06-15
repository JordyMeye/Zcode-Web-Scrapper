#!/usr/bin/env python3
"""Direct scraper that processes the cached page_source.html"""

import sys
import os

# Add path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Read HTML file
html_file = 'page_source.html'
print(f"[*] Reading {html_file}...")

if not os.path.exists(html_file):
    print(f"[-] File not found!")
    sys.exit(1)

with open(html_file, 'r', encoding='utf-8') as f:
    html = f.read()

print(f"[+] Loaded {len(html)} bytes")

# Parse with BeautifulSoup
from bs4 import BeautifulSoup

soup = BeautifulSoup(html, 'html.parser')
table = soup.find('table')

if not table:
    print("[-] No table found!")
    sys.exit(1)

print("[+] Found table")

# Extract predictions
predictions = []
rows = table.find_all('tr')
print(f"[*] Processing {len(rows)} rows...")

for row in rows:
    # Skip header rows
    if row.find('td') is None:
        continue
    
    cols = row.find_all('td')
    if len(cols) < 9:
        continue
    
    # Extract data
    try:
        date_td = cols[0]
        team1_td = cols[1]
        team2_td = cols[2]
        score1_td = cols[3]
        score2_td = cols[4]
        conf_td = cols[5]
        p1_td = cols[6]
        draw_td = cols[7]
        p2_td = cols[8]
        
        # Get text
        date_text = date_td.get_text(strip=True)
        team1_text = team1_td.get_text(strip=True)
        team2_text = team2_td.get_text(strip=True)
        score1_text = score1_td.get_text(strip=True)
        score2_text = score2_td.get_text(strip=True)
        conf_text = conf_td.get_text(strip=True)
        p1_text = p1_td.get_text(strip=True)
        draw_text = draw_td.get_text(strip=True)
        p2_text = p2_td.get_text(strip=True)
        
        # Extract confidence percentage
        import re
        conf_match = re.search(r'(\d+(?:\.\d+)?)', conf_text)
        if not conf_match:
            continue
        conf_val = float(conf_match.group(1))
        
        # Filter by confidence >= 60%
        if conf_val < 60:
            continue
        
        pred = {
            'date_time': date_text,
            'team1': team1_text,
            'team2': team2_text,
            'score_first_half': score1_text,
            'score_final': score2_text,
            'confidence': conf_text,
            'confidence_value': conf_val,
            'prob_team1_win': p1_text,
            'prob_draw': draw_text,
            'prob_team2_win': p2_text,
        }
        predictions.append(pred)
        print(f"[+] {team1_text} vs {team2_text}: {conf_text}")
    except:
        continue

print(f"\n[+] Found {len(predictions)} predictions with 60%+ confidence\n")

# Display
if predictions:
    print("="*100)
    for idx, p in enumerate(predictions[:10], 1):
        print(f"{idx}. {p['team1']} vs {p['team2']}")
        print(f"   Confidence: {p['confidence']}")
        print(f"   Predictions: {p['prob_team1_win']} / {p['prob_draw']} / {p['prob_team2_win']}")
    print("="*100)
    
    # Save to JSON
    import json
    from datetime import datetime
    
    output = {
        "status": "success",
        "scrape_time": datetime.now().isoformat(),
        "source": "offline (page_source.html)",
        "total_predictions": len(predictions),
        "predictions": predictions
    }
    
    with open('high_confidence_predictions_processed.json', 'w') as f:
        json.dump(output, f, indent=2)
    print("\n[+] Saved to high_confidence_predictions_processed.json")
    
    # Save to CSV
    import pandas as pd
    df = pd.DataFrame(predictions)
    df.to_csv('high_confidence_predictions_processed.csv', index=False)
    print("[+] Saved to high_confidence_predictions_processed.csv")
else:
    print("[-] No predictions found")

print("\n[+] Done!")
