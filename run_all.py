"""
Run all sport scrapers in sequence, then report a summary.
Usage: python run_all.py
"""
import sys
import os

# Ensure project root is on the path so sport scrapers can import shared libs
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

SCRAPERS = [
    ('Football', 'sports.football.scraper'),
    ('Tennis',   'sports.tennis.scraper'),
]


def run_scraper(label: str, module_path: str) -> bool:
    print(f"\n{'#'*60}")
    print(f"  Running: {label}")
    print(f"{'#'*60}")
    try:
        import importlib
        mod = importlib.import_module(module_path)
        mod.main()
        return True
    except Exception as e:
        print(f"[ERROR] {label} scraper failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    results = {}
    for label, mod in SCRAPERS:
        results[label] = run_scraper(label, mod)

    print(f"\n{'='*60}")
    print("  SUMMARY")
    print(f"{'='*60}")
    for label, ok in results.items():
        status = 'OK' if ok else 'FAILED'
        print(f"  {label:<15} {status}")
    print()
    print("Open dashboard:  python serve.py")
