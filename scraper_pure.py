#!/usr/bin/env python3
"""
Pure Python scraper - no external dependencies for core functionality
Parses HTML manually to extract predictions
"""

import os
import re
import json
from datetime import datetime

def extract_predictions_from_html(html_file, min_confidence=60):
    """Extract predictions using regex - no BeautifulSoup needed"""
    
    print(f"[*] Reading {html_file}...")
    with open(html_file, 'r', encoding='utf-8') as f:
        html = f.read()
    
    print(f"[+] Loaded {len(html)} characters")
    
    # Find all table rows with game data
    # Pattern: <tr class="game"...>...</tr>
    row_pattern = r'<tr class="game"[^>]*>(.*?)</tr>'
    rows = re.findall(row_pattern, html, re.DOTALL)
    print(f"[*] Found {len(rows)} game rows")
    
    predictions = []
    
    for idx, row in enumerate(rows):
        try:
            # Extract confidence percentage
            conf_pattern = r'confidence_text">(\d+(?:\.\d+)?)%?<'
            conf_match = re.search(conf_pattern, row)
            if not conf_match:
                continue
            
            conf_val = float(conf_match.group(1))
            
            # Only include if >= min_confidence
            if conf_val < min_confidence:
                continue
            
            # Extract team names - look for <div class="team">TeamName<
            team_pattern = r'<div class="team">([^<]+)'
            teams = re.findall(team_pattern, row)
            
            if len(teams) < 2:
                # Try alternate pattern
                team_alt_pattern = r'<div class="Text"><div class="team">([^<]+)'
                teams = re.findall(team_alt_pattern, row)
            
            if len(teams) < 2:
                continue
            
            team1 = teams[0].strip()
            team2 = teams[1].strip()
            
            # Extract scores
            score1_pattern = r'class="predict score[^"]*">(\d+:\d+)<'
            scores = re.findall(score1_pattern, row)
            
            score_first_half = scores[0] if len(scores) > 0 else ""
            score_final = scores[1] if len(scores) > 1 else ""
            
            # Extract probabilities
            prob_pattern = r'data-rollup ([a-z0-9]+)">([^<]*?(?:\d+(?:\.\d+)?%)?[^<]*)<'
            probs = {}
            
            # Try simpler pattern for percentages
            team1_win_pattern = r'class="team1win"[^>]*>([^<]*?\d+[^<]*)'
            team2_win_pattern = r'class="team2win"[^>]*>([^<]*?\d+[^<]*)'
            draw_pattern = r'class="draw"[^>]*>([^<]*?\d+[^<]*)'
            
            # Fallback: look for simple percentage patterns after confidence
            all_percentages = re.findall(r'(\d+(?:\.\d+)?%)', row)
            
            p1_win = all_percentages[1] if len(all_percentages) > 1 else "N/A"
            draw = all_percentages[2] if len(all_percentages) > 2 else "N/A"
            p2_win = all_percentages[3] if len(all_percentages) > 3 else "N/A"
            
            pred = {
                'team1': team1,
                'team2': team2,
                'score_first_half': score_first_half,
                'score_final': score_final,
                'confidence': f"{conf_val}%",
                'confidence_value': conf_val,
                'prob_team1_win': p1_win,
                'prob_draw': draw,
                'prob_team2_win': p2_win,
            }
            
            predictions.append(pred)
            print(f"[+] {team1} vs {team2}: {conf_val}%")
            
        except Exception as e:
            continue
    
    return predictions

def main():
    """Main function"""
    print("[*] Starting Pure Python Scraper")
    print("[*] (No external dependencies except json)\n")
    
    os.chdir(os.path.dirname(os.path.abspath(__file__)) or '.')
    
    html_file = 'page_source.html'
    
    if not os.path.exists(html_file):
        print(f"[-] {html_file} not found!")
        return False
    
    # Extract predictions
    predictions = extract_predictions_from_html(html_file, min_confidence=60)
    
    if not predictions:
        print("[-] No predictions found with 60%+ confidence")
        return False
    
    print(f"\n[+] SUCCESS! Found {len(predictions)} predictions\n")
    
    # Display results
    print("="*100)
    print(f"HIGH CONFIDENCE PREDICTIONS (60%+)")
    print("="*100)
    for idx, p in enumerate(predictions[:10], 1):
        print(f"\n{idx}. {p['team1']} vs {p['team2']}")
        print(f"   Confidence: {p['confidence']}")
        print(f"   Score (1st half): {p['score_first_half']}")
        print(f"   Score (final): {p['score_final']}")
        print(f"   Predictions: {p['prob_team1_win']} / {p['prob_draw']} / {p['prob_team2_win']}")
    
    if len(predictions) > 10:
        print(f"\n... and {len(predictions) - 10} more predictions")
    
    print("="*100)
    
    # Save to JSON
    output = {
        "status": "success",
        "scrape_time": datetime.now().isoformat(),
        "source": "page_source.html (pure Python extraction)",
        "min_confidence": "60%",
        "total_predictions": len(predictions),
        "predictions": predictions
    }
    
    json_file = 'predictions_pure_python.json'
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"\n[+] Saved to {json_file}")
    
    # Save to CSV (simple version without pandas)
    csv_file = 'predictions_pure_python.csv'
    with open(csv_file, 'w', encoding='utf-8') as f:
        # Write header
        f.write("team1,team2,score_first_half,score_final,confidence,prob_team1_win,prob_draw,prob_team2_win\n")
        # Write rows
        for p in predictions:
            f.write(f'"{p["team1"]}","{p["team2"]}","{p["score_first_half"]}","{p["score_final"]}","{p["confidence"]}","{p["prob_team1_win"]}","{p["prob_draw"]}","{p["prob_team2_win"]}"\n')
    print(f"[+] Saved to {csv_file}")
    
    print("\n[+] Program completed successfully!")
    return True

if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n[-] ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
