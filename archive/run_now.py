#!/usr/bin/env python3
"""Direct execution - no Selenium, pure HTML parsing"""

import os
import re
import json
from datetime import datetime

os.chdir(os.path.dirname(os.path.abspath(__file__)) or ".")

print("[*] Starting web scraper (offline mode)...\n")

# Load HTML
html_file = "page_source.html"
if not os.path.exists(html_file):
    print(f"[-] {html_file} not found!")
    exit(1)

with open(html_file, "r", encoding="utf-8") as f:
    html = f.read()

print(f"[+] Loaded {len(html)} bytes from {html_file}")

# Extract predictions
predictions = []

# Find all table rows
rows = re.findall(r'<tr class="game"[^>]*>(.*?)</tr>', html, re.DOTALL)
print(f"[*] Found {len(rows)} game rows\n")

for row in rows:
    try:
        # Extract confidence
        conf_match = re.search(r'confidence_text">(\d+(?:\.\d+)?)', row)
        if not conf_match:
            continue
        
        conf_val = float(conf_match.group(1))
        
        # Skip if below threshold
        if conf_val < 60:
            continue
        
        # Extract teams
        teams = re.findall(r'<div class="team">([^<\n]+)(?:<br>)?', row)
        if len(teams) < 2:
            continue
        
        team1 = teams[0].strip()
        team2 = teams[1].strip()
        
        # Extract scores
        scores = re.findall(r'class="predict score[^"]*">(\d+:\d+)<', row)
        score_first_half = scores[0] if len(scores) > 0 else ""
        score_final = scores[1] if len(scores) > 1 else ""
        
        # Extract probabilities
        probs = re.findall(r'(\d+(?:\.\d+)?%)', row)
        p1_win = probs[1] if len(probs) > 1 else "N/A"
        draw = probs[2] if len(probs) > 2 else "N/A"
        p2_win = probs[3] if len(probs) > 3 else "N/A"
        
        # Extract league
        league_match = re.search(r'data-league="([^"]+)"', row)
        league = league_match.group(1) if league_match else "Unknown"
        
        # Extract date
        date_match = re.search(r'<p>(\d+[a-z]{2}\s+\w+\s+\d+,?)\s*</p>\s*<p>(\d+:\d+)\s+ET', row)
        date_time = f"{date_match.group(1)}, {date_match.group(2)} ET" if date_match else "N/A"
        
        pred = {
            "team1": team1,
            "team2": team2,
            "date_time": date_time,
            "league": league,
            "score_first_half": score_first_half,
            "score_final": score_final,
            "confidence": f"{conf_val}%",
            "confidence_value": conf_val,
            "prob_team1_win": p1_win,
            "prob_draw": draw,
            "prob_team2_win": p2_win,
        }
        
        predictions.append(pred)
        print(f"[+] {team1:30} vs {team2:30} - {conf_val:5.1f}%")
        
    except Exception as e:
        continue

print(f"\n[+] EXTRACTED {len(predictions)} PREDICTIONS WITH 60%+ CONFIDENCE!\n")

if predictions:
    # Sort by confidence
    predictions.sort(key=lambda x: x["confidence_value"], reverse=True)
    
    print("="*100)
    print("TOP PREDICTIONS")
    print("="*100)
    for idx, p in enumerate(predictions[:10], 1):
        print(f"\n{idx}. {p['team1']} vs {p['team2']}")
        print(f"   League: {p['league']}")
        print(f"   Date: {p['date_time']}")
        print(f"   Confidence: {p['confidence']}")
        print(f"   Predictions: {p['prob_team1_win']} / {p['prob_draw']} / {p['prob_team2_win']}")
    
    if len(predictions) > 10:
        print(f"\n... and {len(predictions) - 10} more predictions")
    
    print("\n" + "="*100)
    
    # Save JSON
    output = {
        "status": "success",
        "scrape_time": datetime.now().isoformat(),
        "source": "page_source.html (offline extraction)",
        "min_confidence": "60%",
        "total_predictions": len(predictions),
        "predictions": predictions
    }
    
    with open("high_confidence_predictions_FINAL.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print("\n[+] Saved to high_confidence_predictions_FINAL.json")
    
    # Save CSV
    csv_lines = ["team1,team2,league,date_time,score_1h,score_final,confidence,p_team1,p_draw,p_team2"]
    for p in predictions:
        csv_lines.append(f'"{p["team1"]}","{p["team2"]}","{p["league"]}","{p["date_time"]}","{p["score_first_half"]}","{p["score_final"]}","{p["confidence"]}","{p["prob_team1_win"]}","{p["prob_draw"]}","{p["prob_team2_win"]}"')
    
    with open("high_confidence_predictions_FINAL.csv", "w", encoding="utf-8") as f:
        f.write("\n".join(csv_lines))
    
    print("[+] Saved to high_confidence_predictions_FINAL.csv")
    print("\n[+] SUCCESS - Program completed!")
else:
    print("[-] No predictions found")
