"""
Football predictions scraper — Z Code System Scores Predictor
Fetches the page with Selenium, extracts all Football predictions (60%+ confidence),
and saves results to this folder as predictions.json / predictions.csv.
"""

import re
import json
import time
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

SPORT_NAME = "Football"
OUTPUT_DIR = "sports/football"
SOURCE_URL = "https://zcodesystem.com/scorespredictor/?hop=sportsmart"

FOOTBALL_KEYWORDS = [
    'premier', 'league', 'bundesliga', 'serie', 'ligue', 'eredivisie',
    'championship', 'division', 'liga', 'fc', 'united', 'city', 'mls',
    'champions', 'coupe', 'cup', 'football', 'proximus', 'super',
    'primera', 'segunda', 'corgon', 'j-league', 'thai premier',
    'super league', 'national league', 'nationals l.', 'rfef',
    'vysshaya', 'tipico', '3. liga', 'primera division', 'segunda division',
]


def fetch_page() -> str | None:
    """Fetch the Z Code predictions page using headless Chrome."""
    driver = None
    try:
        print("[*] Launching headless Chrome…")
        opts = Options()
        opts.add_argument('--headless')
        opts.add_argument('--disable-blink-features=AutomationControlled')
        opts.add_argument('--no-sandbox')
        opts.add_argument('--disable-dev-shm-usage')
        opts.add_experimental_option("excludeSwitches", ["enable-automation"])
        opts.add_experimental_option('useAutomationExtension', False)

        service = Service(ChromeDriverManager().install())
        driver  = webdriver.Chrome(service=service, options=opts)
        driver.set_page_load_timeout(30)
        print(f"[*] Loading {SOURCE_URL}…")
        driver.get(SOURCE_URL)

        try:
            WebDriverWait(driver, 12).until(
                lambda d: d.execute_script('return document.readyState') == 'complete'
            )
        except Exception:
            pass

        time.sleep(2)
        html = driver.page_source
        print("[+] Page loaded.")
        return html

    except Exception as e:
        print(f"[-] Selenium failed: {e}")
        # Fallback: try root-level cached page
        try:
            with open('page_source.html', encoding='utf-8') as f:
                print("[+] Using cached page_source.html")
                return f.read()
        except FileNotFoundError:
            print("[-] No cached page found.")
            return None
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass


def _pct(text: str) -> float:
    m = re.search(r'(\d+(?:\.\d+)?)\s*%', str(text))
    return float(m.group(1)) if m else 0.0


def _pct_val(s: str | float) -> float:
    try:
        return float(str(s).replace('%', '').strip())
    except Exception:
        return 0.0


def _is_football(league: str) -> bool:
    ll = league.lower()
    return any(kw in ll for kw in FOOTBALL_KEYWORDS)


def _split_league_date(raw: str) -> tuple[str, str]:
    """Split 'Greece Super League30th Nov 2025,10:00 ET' into (league, date_time)."""
    m = re.search(r'\d{1,2}(?:st|nd|rd|th)\s+\w+\s+\d{4}', raw)
    if m and m.start() > 0:
        return raw[:m.start()].strip(), raw[m.start():]
    return 'Unknown', raw


def _parse_team(name: str) -> tuple[str, str]:
    """Split 'Olympiakos Piraeus1.310' → ('Olympiakos Piraeus', '1.31')."""
    m = re.search(r'\s*(\d+\.\d+)\s*$', name)
    if m:
        return name[:m.start()].strip(), m.group(1)
    return name.strip(), ''


def parse_row(cols: list, min_confidence: float) -> dict | None:
    """Parse one HTML table row into a prediction dict."""
    try:
        raw_date = cols[0].get_text(strip=True)
        league, date_time = _split_league_date(raw_date)

        if not _is_football(league):
            return None

        team1, odds1 = _parse_team(cols[1].get_text(strip=True))
        team2, odds2 = _parse_team(cols[2].get_text(strip=True))
        if not (team1 and team2):
            return None

        score_first_half = cols[3].get_text(strip=True) if len(cols) > 3 else ''
        score_final      = cols[4].get_text(strip=True) if len(cols) > 4 else ''
        conf_str         = cols[5].get_text(strip=True) if len(cols) > 5 else '0%'
        prob_t1          = cols[6].get_text(strip=True) if len(cols) > 6 else ''
        prob_draw        = cols[7].get_text(strip=True) if len(cols) > 7 else ''
        prob_t2          = cols[8].get_text(strip=True) if len(cols) > 8 else ''

        conf_val = _pct(conf_str)
        if conf_val < min_confidence:
            return None

        return {
            'sport': SPORT_NAME,
            'league': league,
            'date_time': date_time,
            'team1': team1,
            'team2': team2,
            'odds_team1': odds1,
            'odds_team2': odds2,
            'score_first_half': score_first_half,
            'score_final': score_final,
            'confidence': conf_str,
            'confidence_value': conf_val,
            'prob_team1_win': prob_t1,
            'prob_draw': prob_draw,
            'prob_team2_win': prob_t2,
        }
    except Exception:
        return None


def parse_text(text: str, min_confidence: float) -> list[dict]:
    """Fallback text-based extraction when table parsing yields nothing."""
    pattern = (
        r'(\d{1,2}(?:st|nd|rd|th)\s+\w+\s+\d{4},?\s+\d{1,2}:\d{2}\s+ET)'
        r'\s*\|\s*([^\d|]+?)\s+(\d+\.?\d+)\s*\|\s*([^\d]+?)\s+(\d+\.?\d+)'
    )
    results = []
    for m in re.finditer(pattern, text):
        try:
            raw_dt = m.group(1)
            league_prefix = re.search(r'\d{1,2}(?:st|nd|rd|th)', raw_dt)
            if league_prefix and league_prefix.start() > 0:
                league   = raw_dt[:league_prefix.start()].strip()
                date_time = raw_dt[league_prefix.start():]
            else:
                league, date_time = 'Unknown', raw_dt

            if league == 'Unknown':
                ctx_before = text[max(0, m.start()-300):m.start()]
                for line in reversed(ctx_before.split('\n')[-5:]):
                    line = line.strip()
                    if line and len(line) > 3 and not line[0].isdigit() and _is_football(line):
                        league = line
                        break

            if not _is_football(league):
                continue

            team1 = _clean_team(m.group(2).strip())
            team2 = _clean_team(m.group(4).strip())

            ctx_end   = m.end()
            context   = text[m.start():min(len(text), ctx_end + 1500)]

            cm = re.search(r'CONFIDENCE\s+(\d+(?:\.\d+)?)\s*%', context)
            conf_val  = float(cm.group(1)) if cm else 0.0
            if conf_val < min_confidence:
                continue

            def _prob(pat):
                pm = re.search(pat, context, re.I)
                if pm:
                    return f"{pm.group(1) or pm.group(2)}%"
                return 'N/A'

            sm = re.search(r'FINAL\s+SCORE\s+(\d+:\d+)', context)
            hm = re.search(r'FIRST\s+HALF\s+(\d+:\d+)', context)

            results.append({
                'sport': SPORT_NAME,
                'league': league,
                'date_time': date_time,
                'team1': team1,
                'team2': team2,
                'score_first_half': hm.group(1) if hm else '',
                'score_final': sm.group(1) if sm else '',
                'confidence': f'{conf_val}%',
                'confidence_value': conf_val,
                'prob_team1_win': _prob(r'TEAM.*?1.*?WIN\s+(\d+\.?\d*)\s*%|(\d+\.?\d*)\s*%\s+TEAM.*?1.*?WIN'),
                'prob_draw':      _prob(r'DRAW\s+(\d+\.?\d*)\s*%|(\d+\.?\d*)\s*%\s+DRAW'),
                'prob_team2_win': _prob(r'TEAM.*?2.*?WIN\s+(\d+\.?\d*)\s*%|(\d+\.?\d*)\s*%\s+TEAM.*?2.*?WIN'),
            })
        except Exception:
            continue
    return results


def extract(html: str, min_confidence: float = 60) -> list[dict]:
    """Parse HTML and return filtered football predictions."""
    soup = BeautifulSoup(html, 'html.parser')
    preds = []

    for table in soup.find_all('table'):
        for row in table.find_all('tr'):
            cols = row.find_all(['td', 'th'])
            if len(cols) >= 9:
                p = parse_row(cols, min_confidence)
                if p:
                    preds.append(p)

    if not preds:
        print("[*] Table parse found nothing — trying text extraction…")
        preds = parse_text(soup.get_text(), min_confidence)

    # Deduplicate
    seen, unique = set(), []
    for p in preds:
        k = f"{p['team1']}|{p['team2']}|{p['date_time']}"
        if k not in seen:
            seen.add(k)
            unique.append(p)

    return unique


def save(predictions: list[dict], min_confidence: float) -> None:
    """Save predictions to this sport's folder."""
    if not predictions:
        print("[-] No football predictions to save.")
        return

    # Sort by confidence desc
    predictions.sort(key=lambda p: p['confidence_value'], reverse=True)

    # Organize by league
    by_league: dict[str, list] = {}
    high_value: list[dict] = []
    for p in predictions:
        by_league.setdefault(p['league'], []).append(p)
        t1 = _pct_val(p['prob_team1_win'])
        t2 = _pct_val(p['prob_team2_win'])
        if t1 > 40 or t2 > 40:
            high_value.append(p)

    output = {
        'status': 'success',
        'sport': SPORT_NAME,
        'scrape_time': datetime.now().isoformat(),
        'source': SOURCE_URL,
        'filter': {'min_confidence': f'{min_confidence}%'},
        'summary': {
            'total_predictions': len(predictions),
            'leagues_covered': len(by_league),
            'breakdown': {lg: len(v) for lg, v in by_league.items()},
            'high_value_count': len(high_value),
        },
        'high_value_predictions': high_value,
        'predictions_by_league': by_league,
    }

    json_path = f'{OUTPUT_DIR}/predictions.json'
    csv_path  = f'{OUTPUT_DIR}/predictions.csv'

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"[+] Saved JSON  → {json_path}")

    pd.DataFrame(predictions).to_csv(csv_path, index=False)
    print(f"[+] Saved CSV   → {csv_path}")


def main(min_confidence: float = 60) -> None:
    print(f"\n{'='*60}")
    print(f"  FOOTBALL SCRAPER  |  min confidence: {min_confidence}%")
    print(f"{'='*60}\n")

    html = fetch_page()
    if not html:
        print("[-] Could not fetch page. Aborting.")
        return

    print("[*] Extracting football predictions…")
    preds = extract(html, min_confidence)
    print(f"[+] Found {len(preds)} football predictions.")

    save(preds, min_confidence)
    print("\n[+] Done.\n")


if __name__ == '__main__':
    main()
