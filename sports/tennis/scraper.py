"""
Tennis predictions scraper — Z Code System Scores Predictor
Fetches the page with Selenium, extracts all Tennis predictions (60%+ confidence),
and saves results to this folder as predictions.json / predictions.csv.

Tennis differences vs Football:
  - League → Tournament (ATP / WTA / Davis Cup / Challenger / ITF)
  - No draw — only Player 1 Win / Player 2 Win
  - Score prediction = sets (e.g. 2:1), not goals
  - Player names sometimes include seeding [1], [Q], etc.
"""

import re
import json
import time
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

SPORT_NAME = "Tennis"
OUTPUT_DIR = "sports/tennis"
SOURCE_URL = "https://zcodesystem.com/scorespredictor/?hop=sportsmart"

TENNIS_KEYWORDS = [
    'tennis', 'atp', 'wta', 'open', 'wimbledon', 'roland garros',
    'us open', 'australian open', 'french open', 'davis cup', 'fed cup',
    'billie jean king', 'challenger', 'itf', 'grand slam', 'masters',
    'atp 250', 'atp 500', 'atp 1000', 'wta 125', 'wta 250', 'wta 500',
    'wta 1000', 'nextgen', 'laver cup',
]

SEEDING_PATTERN = re.compile(r'\s*\[\w+\]\s*')


def fetch_page() -> str | None:
    """Fetch the Z Code predictions page and click the TENNIS tab."""
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

        # Wait for initial page load
        try:
            WebDriverWait(driver, 15).until(
                lambda d: d.execute_script('return document.readyState') == 'complete'
            )
        except Exception:
            pass
        time.sleep(2)

        # Click the TENNIS sport tab so the page loads tennis predictions
        print("[*] Clicking TENNIS tab…")
        try:
            tennis_tab = WebDriverWait(driver, 10).until(
                lambda d: d.find_element(By.CSS_SELECTOR, 'span[data-sport="TENNIS"]')
            )
            driver.execute_script("arguments[0].click();", tennis_tab)
            print("[+] TENNIS tab clicked — waiting for data…")
            time.sleep(4)  # let AJAX load tennis rows
        except Exception as e:
            print(f"[!] Could not click TENNIS tab: {e}")
            print("[!] Proceeding with whatever is on screen (may be football data)")

        html = driver.page_source
        print("[+] Page captured.")
        return html

    except Exception as e:
        print(f"[-] Selenium failed: {e}")
        # No useful fallback — page_source.html only has football data
        print("[-] No usable fallback for tennis (cached page is football-only).")
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


def _is_tennis(league: str) -> bool:
    ll = league.lower()
    return any(kw in ll for kw in TENNIS_KEYWORDS)


def _split_tournament_date(raw: str) -> tuple[str, str]:
    """Split 'ATP Roland Garros15th May 2025,08:00 ET' into (tournament, date_time)."""
    m = re.search(r'\d{1,2}(?:st|nd|rd|th)\s+\w+\s+\d{4}', raw)
    if m and m.start() > 0:
        return raw[:m.start()].strip(), raw[m.start():]
    return 'Unknown', raw


def _parse_player(name: str) -> tuple[str, str]:
    """Strip seeding/odds and return (clean_name, odds_str)."""
    name = SEEDING_PATTERN.sub(' ', name).strip()
    m = re.search(r'\s*(\d+\.\d+)\s*$', name)
    if m:
        return name[:m.start()].strip(), m.group(1)
    return name.strip(), ''


def _extract_round(tournament: str) -> tuple[str, str]:
    """Try to separate round info from tournament name, e.g. 'ATP Wimbledon - QF'."""
    m = re.search(r'\s*[-–]\s*(R\d+|QF|SF|F|Round\s+\d+|Quarter|Semi|Final)', tournament, re.I)
    if m:
        round_name = m.group(1).strip()
        tourney    = tournament[:m.start()].strip()
        return tourney, round_name
    return tournament, ''


def parse_row(cols: list, min_confidence: float) -> dict | None:
    """Parse one HTML table row into a tennis prediction dict."""
    try:
        raw_date = cols[0].get_text(strip=True)
        tournament, date_time = _split_tournament_date(raw_date)

        if not _is_tennis(tournament):
            return None

        tournament, round_name = _extract_round(tournament)

        player1, odds1 = _parse_player(cols[1].get_text(strip=True))
        player2, odds2 = _parse_player(cols[2].get_text(strip=True))
        if not (player1 and player2):
            return None

        # In tennis the "score" columns typically hold predicted sets (e.g. 2:1)
        set_prediction = cols[3].get_text(strip=True) if len(cols) > 3 else ''
        # col[4] may hold full-match sets or be empty for tennis
        match_score    = cols[4].get_text(strip=True) if len(cols) > 4 else ''
        conf_str       = cols[5].get_text(strip=True) if len(cols) > 5 else '0%'

        # Tennis has no draw — col[6] = player1 win, col[7] might be draw (skip), col[8] = player2 win
        prob_p1  = cols[6].get_text(strip=True) if len(cols) > 6 else ''
        # Detect if col[7] is draw (small value) or player2 win; for tennis skip draw column
        col7_val = _pct(cols[7].get_text(strip=True)) if len(cols) > 7 else 0
        col8_val = _pct(cols[8].get_text(strip=True)) if len(cols) > 8 else 0

        # If three probability columns exist and they sum ~100, col[7] is draw → skip it
        # If col[7] looks like a second player win probability (high), treat it as player2
        col7_txt = cols[7].get_text(strip=True) if len(cols) > 7 else ''
        col8_txt = cols[8].get_text(strip=True) if len(cols) > 8 else ''

        if col8_val > 0:
            prob_p2 = col8_txt   # standard 3-col layout: p1 | draw | p2
        else:
            prob_p2 = col7_txt   # 2-col layout: p1 | p2

        conf_val = _pct(conf_str)
        if conf_val < min_confidence:
            return None

        return {
            'sport': SPORT_NAME,
            'tournament': tournament,
            'round': round_name,
            'date_time': date_time,
            'player1': player1,
            'player2': player2,
            'odds_player1': odds1,
            'odds_player2': odds2,
            'set_prediction': set_prediction,
            'match_score': match_score,
            'confidence': conf_str,
            'confidence_value': conf_val,
            'prob_player1_win': prob_p1,
            'prob_player2_win': prob_p2,
        }
    except Exception:
        return None


def parse_text(text: str, min_confidence: float) -> list[dict]:
    """Fallback text-based extraction for tennis matches."""
    pattern = (
        r'(\d{1,2}(?:st|nd|rd|th)\s+\w+\s+\d{4},?\s+\d{1,2}:\d{2}\s+ET)'
        r'\s*\|\s*([^\d|]+?)\s+(\d+\.?\d+)\s*\|\s*([^\d]+?)\s+(\d+\.?\d+)'
    )
    results = []
    for m in re.finditer(pattern, text):
        try:
            raw_dt = m.group(1)
            prefix_m = re.search(r'\d{1,2}(?:st|nd|rd|th)', raw_dt)
            if prefix_m and prefix_m.start() > 0:
                tournament = raw_dt[:prefix_m.start()].strip()
                date_time  = raw_dt[prefix_m.start():]
            else:
                tournament, date_time = 'Unknown', raw_dt

            if tournament == 'Unknown':
                ctx_before = text[max(0, m.start()-300):m.start()]
                for line in reversed(ctx_before.split('\n')[-5:]):
                    line = line.strip()
                    if line and len(line) > 3 and not line[0].isdigit() and _is_tennis(line):
                        tournament = line
                        break

            if not _is_tennis(tournament):
                continue

            tournament, round_name = _extract_round(tournament)

            player1, odds1 = _parse_player(m.group(2).strip())
            player2, odds2 = _parse_player(m.group(4).strip())

            ctx = text[m.start():min(len(text), m.end() + 1500)]

            cm = re.search(r'CONFIDENCE\s+(\d+(?:\.\d+)?)\s*%', ctx)
            conf_val = float(cm.group(1)) if cm else 0.0
            if conf_val < min_confidence:
                continue

            def _prob(pat):
                pm = re.search(pat, ctx, re.I)
                if pm:
                    return f"{pm.group(1) or pm.group(2)}%"
                return 'N/A'

            sm  = re.search(r'FINAL\s+SCORE\s+(\d+:\d+)', ctx)
            hm  = re.search(r'FIRST\s+(?:SET|HALF)\s+(\d+:\d+)', ctx)

            results.append({
                'sport': SPORT_NAME,
                'tournament': tournament,
                'round': round_name,
                'date_time': date_time,
                'player1': player1,
                'player2': player2,
                'odds_player1': odds1,
                'odds_player2': odds2,
                'set_prediction': hm.group(1) if hm else '',
                'match_score': sm.group(1) if sm else '',
                'confidence': f'{conf_val}%',
                'confidence_value': conf_val,
                'prob_player1_win': _prob(r'TEAM.*?1.*?WIN\s+(\d+\.?\d*)\s*%|(\d+\.?\d*)\s*%\s+TEAM.*?1.*?WIN'),
                'prob_player2_win': _prob(r'TEAM.*?2.*?WIN\s+(\d+\.?\d*)\s*%|(\d+\.?\d*)\s*%\s+TEAM.*?2.*?WIN'),
            })
        except Exception:
            continue
    return results


def extract(html: str, min_confidence: float = 60) -> list[dict]:
    """Parse HTML and return filtered tennis predictions."""
    soup = BeautifulSoup(html, 'html.parser')
    preds = []

    for table in soup.find_all('table'):
        for row in table.find_all('tr'):
            cols = row.find_all(['td', 'th'])
            if len(cols) >= 7:
                p = parse_row(cols, min_confidence)
                if p:
                    preds.append(p)

    if not preds:
        print("[*] Table parse found nothing — trying text extraction…")
        preds = parse_text(soup.get_text(), min_confidence)

    # Deduplicate
    seen, unique = set(), []
    for p in preds:
        k = f"{p['player1']}|{p['player2']}|{p['date_time']}"
        if k not in seen:
            seen.add(k)
            unique.append(p)

    return unique


def save(predictions: list[dict], min_confidence: float) -> None:
    """Save predictions to this sport's folder."""
    if not predictions:
        print("[-] No tennis predictions to save.")
        return

    predictions.sort(key=lambda p: p['confidence_value'], reverse=True)

    by_tournament: dict[str, list] = {}
    for p in predictions:
        by_tournament.setdefault(p['tournament'], []).append(p)

    # High-value = strong favourite (player win prob > 60%)
    high_value = [
        p for p in predictions
        if _pct_val(p['prob_player1_win']) > 60 or _pct_val(p['prob_player2_win']) > 60
    ]

    output = {
        'status': 'success',
        'sport': SPORT_NAME,
        'scrape_time': datetime.now().isoformat(),
        'source': SOURCE_URL,
        'filter': {'min_confidence': f'{min_confidence}%'},
        'summary': {
            'total_predictions': len(predictions),
            'tournaments_covered': len(by_tournament),
            'breakdown': {t: len(v) for t, v in by_tournament.items()},
            'strong_favourite_count': len(high_value),
        },
        'high_value_predictions': high_value,
        'predictions_by_tournament': by_tournament,
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
    print(f"  TENNIS SCRAPER  |  min confidence: {min_confidence}%")
    print(f"{'='*60}\n")

    html = fetch_page()
    if not html:
        print("[-] Could not fetch page. Aborting.")
        return

    print("[*] Extracting tennis predictions…")
    preds = extract(html, min_confidence)
    print(f"[+] Found {len(preds)} tennis predictions.")

    save(preds, min_confidence)
    print("\n[+] Done.\n")


if __name__ == '__main__':
    main()
