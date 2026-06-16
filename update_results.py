"""
update_results.py — Fetch actual match results and mark predictions as success/failed.

HOW IT WORKS
------------
1. Reads predictions from sports/football/predictions.json
2. For each past prediction that has no result yet, looks up the actual score
3. Compares: predicted winner  vs  actual winner
4. Marks the prediction as "success" or "failed"
5. Saves back to the JSON file (dashboard picks it up automatically)

FREE API SETUP (Football)
--------------------------
Source: https://api-football.com  — free tier: 100 requests/day, no credit card needed
Steps:
  1. Go to https://dashboard.api-football.com/register
  2. Create a free account
  3. Copy your API key
  4. Set it below as FOOTBALL_API_KEY = "your_key_here"
  OR pass it as an environment variable:  set FOOTBALL_API_KEY=your_key

TENNIS RESULTS
--------------
Tennis live score APIs that offer free tiers:
  • api-tennis.com  — free tier available
  • sofascore.com   — unofficial API, no key needed (may break)
  • For now this script handles tennis as PENDING until a tennis API is wired up.

RUNNING
-------
  python update_results.py              # updates all sports
  python update_results.py --sport football
  python update_results.py --dry-run   # preview without saving
"""

import os
import re
import sys
import json
import time
import argparse
import requests
from datetime import datetime, timedelta
from pathlib import Path

# ── API Config ─────────────────────────────────────────────────────────────
FOOTBALL_API_KEY = os.getenv('FOOTBALL_API_KEY', '')   # or hardcode your key here
FOOTBALL_API_URL = 'https://v3.football.api-sports.io'

# TheSportsDB (no key needed for free tier — good backup)
SPORTSDB_URL = 'https://www.thesportsdb.com/api/v1/json/3'

SPORT_FILES = {
    'Football': Path('sports/football/predictions.json'),
    'Tennis':   Path('sports/tennis/predictions.json'),
}


# ── Date parsing ────────────────────────────────────────────────────────────
def parse_pred_date(date_str: str) -> datetime | None:
    """Parse '30th Nov 2025,10:00 ET' → datetime object."""
    if not date_str:
        return None
    m = re.search(r'(\d{1,2})(?:st|nd|rd|th)\s+(\w+)\s+(\d{4})', date_str, re.I)
    if not m:
        return None
    try:
        return datetime.strptime(f"{m.group(2)} {m.group(1)} {m.group(3)}", "%b %d %Y")
    except ValueError:
        return None


def date_to_api_format(dt: datetime) -> str:
    return dt.strftime('%Y-%m-%d')


# ── Predicted winner ────────────────────────────────────────────────────────
def predicted_winner(pred: dict) -> str:
    """Return 'team1' | 'team2' | 'draw' based on highest probability."""
    def pct(s):
        try:
            return float(str(s).replace('%', '').strip())
        except Exception:
            return 0.0

    t1 = pct(pred.get('prob_team1_win', pred.get('prob_player1_win', 0)))
    dr = pct(pred.get('prob_draw', 0))
    t2 = pct(pred.get('prob_team2_win', pred.get('prob_player2_win', 0)))

    best = max(t1, dr, t2)
    if best == t1: return 'team1'
    if best == t2: return 'team2'
    return 'draw'


# ── Football API ─────────────────────────────────────────────────────────────
def _api_football_headers():
    return {'x-apisports-key': FOOTBALL_API_KEY}


def fetch_football_results_api(date_str: str) -> list[dict]:
    """Fetch all football fixtures for a date from api-football.com."""
    if not FOOTBALL_API_KEY:
        return []
    try:
        r = requests.get(
            f'{FOOTBALL_API_URL}/fixtures',
            params={'date': date_str, 'status': 'FT'},
            headers=_api_football_headers(),
            timeout=15,
        )
        data = r.json()
        return data.get('response', [])
    except Exception as e:
        print(f"  [api-football] Error: {e}")
        return []


def fetch_football_results_sportsdb(date_str: str) -> list[dict]:
    """Fallback: TheSportsDB free endpoint (no key needed)."""
    try:
        r = requests.get(
            f'{SPORTSDB_URL}/eventsday.php',
            params={'d': date_str, 's': 'Soccer'},
            timeout=15,
        )
        events = r.json().get('events') or []
        # Normalize to a common shape
        results = []
        for e in events:
            home  = e.get('strHomeTeam', '')
            away  = e.get('strAwayTeam', '')
            score = e.get('strResult', '') or ''
            parts = score.replace(' ', '').split('-')
            if len(parts) == 2:
                try:
                    gh, ga = int(parts[0]), int(parts[1])
                except ValueError:
                    continue
                winner = 'home' if gh > ga else ('away' if ga > gh else 'draw')
                results.append({'home': home, 'away': away, 'score': score,
                                 'home_goals': gh, 'away_goals': ga, 'winner': winner})
        return results
    except Exception as e:
        print(f"  [thesportsdb] Error: {e}")
        return []


def find_football_match(fixtures: list[dict], team1: str, team2: str) -> dict | None:
    """Fuzzy-match team names in fixture list."""
    def norm(s):
        return re.sub(r'[^a-z0-9]', '', s.lower())

    n1, n2 = norm(team1), norm(team2)
    for fix in fixtures:
        # api-football format
        if 'teams' in fix:
            h = norm(fix['teams']['home']['name'])
            a = norm(fix['teams']['away']['name'])
        # sportsdb format
        elif 'home' in fix:
            h = norm(fix['home'])
            a = norm(fix['away'])
        else:
            continue

        if (n1 in h or h in n1) and (n2 in a or a in n2):
            return fix
        if (n2 in h or h in n2) and (n1 in a or a in n1):
            return {'_swapped': True, **fix}
    return None


def actual_winner_from_fixture(fix: dict, swapped: bool = False) -> tuple[str, str]:
    """Return (winner: 'team1'|'team2'|'draw', score: '2:1')."""
    if 'goals' in fix:  # api-football
        gh = fix['goals']['home'] or 0
        ga = fix['goals']['away'] or 0
    elif 'home_goals' in fix:  # sportsdb
        gh, ga = fix['home_goals'], fix['away_goals']
    else:
        return 'unknown', '?'

    score  = f"{gh}:{ga}"
    winner = 'draw' if gh == ga else ('home' if gh > ga else 'away')

    if swapped:
        score  = f"{ga}:{gh}"
        winner = 'draw' if gh == ga else ('away' if gh > ga else 'home')
        # Now home = team2, away = team1
        winner = 'draw' if winner == 'draw' else ('team2' if winner == 'home' else 'team1')
    else:
        winner = 'draw' if winner == 'draw' else ('team1' if winner == 'home' else 'team2')

    return winner, score


# ── Main update logic ────────────────────────────────────────────────────────
def update_sport(sport: str, dry_run: bool = False) -> int:
    path = SPORT_FILES.get(sport)
    if not path or not path.exists():
        print(f"[{sport}] No predictions file found at {path}. Run the scraper first.")
        return 0

    with open(path, encoding='utf-8') as f:
        data = json.load(f)

    updated = 0
    today   = datetime.now().date()

    # Collect all predictions across all sections
    def iter_preds():
        for section_key in ('predictions_by_sport', 'predictions_by_league',
                            'predictions_by_tournament', 'high_value_predictions'):
            section = data.get(section_key)
            if isinstance(section, dict):
                for lst in section.values():
                    yield from lst
            elif isinstance(section, list):
                yield from section

    # Cache fixtures per date to avoid repeated API calls
    fixture_cache: dict[str, list] = {}

    for pred in iter_preds():
        if pred.get('result'):
            continue  # already has result — skip

        date_obj = parse_pred_date(pred.get('date_time', ''))
        if not date_obj:
            continue

        if date_obj.date() >= today:
            continue  # match hasn't happened yet

        date_str = date_to_api_format(date_obj)

        if sport == 'Football':
            if date_str not in fixture_cache:
                print(f"  [Football] Fetching results for {date_str}…")
                # Try api-football first, fall back to sportsdb
                fixtures = fetch_football_results_api(date_str)
                if not fixtures:
                    print(f"  [Football] Trying TheSportsDB fallback…")
                    fixtures = fetch_football_results_sportsdb(date_str)
                fixture_cache[date_str] = fixtures
                time.sleep(0.5)  # rate limit

            fixtures = fixture_cache[date_str]
            t1 = pred.get('team1', '')
            t2 = pred.get('team2', '')
            fix = find_football_match(fixtures, t1, t2)

            if fix is None:
                print(f"  [?] Match not found: {t1} vs {t2} on {date_str}")
                continue

            swapped = fix.pop('_swapped', False)
            actual_w, actual_score = actual_winner_from_fixture(fix, swapped)
            pred_w   = predicted_winner(pred)

            result = 'success' if actual_w == pred_w else 'failed'
            print(f"  {'✓' if result=='success' else '✗'} {t1} vs {t2} [{date_str}]  "
                  f"pred={pred_w}  actual={actual_w} ({actual_score})  → {result.upper()}")

            if not dry_run:
                pred['result']        = result
                pred['actual_score']  = actual_score
                pred['actual_winner'] = actual_w
            updated += 1

        elif sport == 'Tennis':
            # Tennis result fetching is not yet wired up
            # To add: use api-tennis.com or sofascore
            print(f"  [Tennis] Skipping {pred.get('player1')} vs {pred.get('player2')} — no tennis API configured yet")

    if not dry_run and updated > 0:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"\n[{sport}] Updated {updated} prediction(s) → saved to {path}")
    elif dry_run:
        print(f"\n[{sport}] DRY RUN — {updated} prediction(s) would be updated (nothing saved)")
    else:
        print(f"\n[{sport}] Nothing to update.")

    return updated


# ── CLI ─────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description='Update prediction results from live scores')
    parser.add_argument('--sport', choices=['Football', 'Tennis', 'all'], default='all')
    parser.add_argument('--dry-run', action='store_true', help='Preview without saving')
    args = parser.parse_args()

    if not FOOTBALL_API_KEY:
        print("⚠️  FOOTBALL_API_KEY is not set.")
        print("   Get a free key at: https://dashboard.api-football.com/register")
        print("   Then run:  set FOOTBALL_API_KEY=your_key  (Windows)")
        print("   Or:        export FOOTBALL_API_KEY=your_key  (Mac/Linux)")
        print("   Trying TheSportsDB fallback (no key needed)…\n")

    sports = ['Football', 'Tennis'] if args.sport == 'all' else [args.sport]

    total = 0
    for sport in sports:
        print(f"\n{'='*55}")
        print(f"  {sport} Results Update{'  [DRY RUN]' if args.dry_run else ''}")
        print(f"{'='*55}")
        total += update_sport(sport, dry_run=args.dry_run)

    print(f"\n{'='*55}")
    print(f"  Total updated: {total}")
    print(f"  Refresh the dashboard to see results.")
    print(f"{'='*55}\n")


if __name__ == '__main__':
    main()
