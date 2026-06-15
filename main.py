import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
from datetime import datetime
import re
import time
import signal
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

class ScoresPredictorScraper:
    """
    Scraper for Z Code System Scores Predictor
    Extracts daily betting predictions with 60%+ confidence
    """
    
    def __init__(self, min_confidence=60):
        self.url = "https://zcodesystem.com/scorespredictor/?hop=sportsmart"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.predictions = []
        self.min_confidence = min_confidence
    
    def fetch_page(self):
        """Fetch the webpage content using Selenium for JavaScript rendering"""
        driver = None
        try:
            print("[*] Attempting Selenium/Chrome method...")
            print("[*] WARNING: If this hangs for >30 seconds, Ctrl+C to skip")
            
            # Setup Chrome options
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Initialize Chrome WebDriver with timeout
            print("[*] Installing ChromeDriver...")
            service = Service(ChromeDriverManager().install())
            print("[*] Starting Chrome (timeout: 30 seconds)...")
            
            # Use signal to timeout the Chrome initialization
            import signal
            def timeout_handler(signum, frame):
                raise TimeoutError("Chrome initialization timed out")
            
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(30)  # 30 second timeout
            
            try:
                driver = webdriver.Chrome(service=service, options=chrome_options)
                signal.alarm(0)  # Cancel alarm
                driver.set_page_load_timeout(15)
                
                # Load the page
                print(f"[*] Loading {self.url}...")
                driver.get(self.url)
                
                # Wait for page to load
                try:
                    WebDriverWait(driver, 10).until(
                        lambda driver: driver.execute_script('return document.readyState') == 'complete'
                    )
                except:
                    pass
                
                time.sleep(2)
                page_source = driver.page_source
                print("[+] Page fetched with Selenium!")
                return page_source
            except (TimeoutError, Exception) as e:
                signal.alarm(0)  # Cancel alarm
                raise e
            
        except (TimeoutError, Exception) as e:
            print(f"[-] Selenium failed ({type(e).__name__}: {str(e)[:50]})")
            print("[*] Falling back to cached page_source.html...")
            try:
                with open('page_source.html', 'r', encoding='utf-8') as f:
                    print("[+] Using cached page_source.html")
                    return f.read()
            except:
                print("[-] No cached file found")
                return None
        finally:
            try:
                if driver:
                    driver.quit()
            except:
                pass
    
    def extract_predictions(self, html_content):
        """Extract betting predictions from HTML"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract full text content
        text = soup.get_text()
        
        # Try table extraction first
        tables = soup.find_all('table')
        
        if tables:
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cols = row.find_all(['td', 'th'])
                    if len(cols) >= 8:
                        try:
                            prediction = self.parse_row(cols)
                            if prediction:
                                self.predictions.append(prediction)
                        except Exception:
                            continue
        
        # Extract from text as fallback
        self.extract_from_text(text)
    
    def parse_row(self, cols):
        """Parse a single row from the table"""
        try:
            # Column 0 contains league name concatenated with date, e.g. "Greece Super League30th Nov 2025,10:00 ET"
            date_col_text = cols[0].get_text(strip=True)
            date_only_match = re.search(r'\d{1,2}(?:st|nd|rd|th)\s+\w+\s+\d{4}', date_col_text)
            if date_only_match and date_only_match.start() > 0:
                league = date_col_text[:date_only_match.start()].strip()
                date_time = date_col_text[date_only_match.start():]
            elif date_only_match:
                league = 'Unknown'
                date_time = date_col_text
            else:
                league = 'Unknown'
                date_time = date_col_text

            sport = self.determine_sport(league)

            # Columns 1 and 2 may contain odds appended to team names, e.g. "Olympiakos Piraeus1.310"
            team1 = re.sub(r'\s*\d+\.\d+\s*$', '', cols[1].get_text(strip=True)).strip()
            team2 = re.sub(r'\s*\d+\.\d+\s*$', '', cols[2].get_text(strip=True)).strip()

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
                'league': league,
                'sport': sport,
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
    
    def determine_sport(self, league_name):
        """Determine sport type from league name"""
        league_lower = league_name.lower()
        
        # Football/Soccer - most comprehensive list
        football_keywords = ['premier', 'league', 'bundesliga', 'serie', 'ligue', 'eredivisie', 'championship', 'division', 'liga', 'fc', 'united', 'city', 'mls', 'champions', 'coupe', 'cup', 'football', 'proximus', 'super', 'primera', 'segunda', 'corgon', 'j-league', 'thai premier', 'super league', 'national league', 'nationals l.', 'rfef', 'vysshaya', 'tipico', 'tipico bundesliga', '3. liga']
        
        if any(word in league_lower for word in football_keywords):
            return 'Football'
        elif any(word in league_lower for word in ['tennis', 'atp', 'wta', 'open']):
            return 'Tennis'
        elif any(word in league_lower for word in ['basketball', 'nba', 'euroleague', 'bball']):
            return 'Basketball'
        elif any(word in league_lower for word in ['nfl', 'american football']):
            return 'American Football'
        elif any(word in league_lower for word in ['hockey', 'nhl', 'ice hockey']):
            return 'Hockey'
        elif any(word in league_lower for word in ['cricket', 'ipl', 't20', 'test']):
            return 'Cricket'
        elif any(word in league_lower for word in ['baseball', 'mlb', 'world series']):
            return 'Baseball'
        else:
            return 'Football'  # Default to Football if ambiguous
    
    def extract_from_text(self, text):
        """Extract predictions from text content using comprehensive regex patterns"""
        
        # Pattern to find complete game blocks
        # Match: Date | Team1 odds | Team2 odds | ... Confidence X% | Probabilities ...
        game_block_pattern = r'(\d{1,2}(?:st|nd|rd|th)\s+\w+\s+\d{4},?\s+\d{1,2}:\d{2}\s+ET)\s*\|\s*([^\d|]+?)\s+(\d+\.?\d+)\s*\|\s*([^\d]+?)\s+(\d+\.?\d+)'
        
        matches = re.finditer(game_block_pattern, text)
        
        for match in matches:
            try:
                date_time_raw = match.group(1)
                team1_raw = match.group(2).strip()
                odds1 = match.group(3)
                team2_raw = match.group(4).strip()
                odds2 = match.group(5)

                # The date_time may have league name prepended (e.g. "Greece Super League30th Nov 2025")
                # Split it: find where the numeric date starts
                date_prefix_match = re.search(r'\d{1,2}(?:st|nd|rd|th)\s+\w+\s+\d{4}', date_time_raw)
                if date_prefix_match and date_prefix_match.start() > 0:
                    league = date_time_raw[:date_prefix_match.start()].strip()
                    date_time = date_time_raw[date_prefix_match.start():]
                else:
                    league = "Unknown"
                    date_time = date_time_raw

                # Strip trailing odds from team names (e.g. "Olympiakos Piraeus1.310" → "Olympiakos Piraeus")
                team1 = re.sub(r'\s*\d+\.\d+\s*$', '', team1_raw).strip()
                team2 = re.sub(r'\s*\d+\.\d+\s*$', '', team2_raw).strip()

                # Get position for context extraction
                match_start = match.start()
                match_end = match.end()

                # Extract context - look back for league/sport and ahead for predictions
                context_before = text[max(0, match_start - 300):match_start]
                context_after = text[match_start:min(len(text), match_end + 1500)]
                context = context_before + context_after

                # If league still unknown, look in context lines before the match
                if league == "Unknown":
                    lines_before = context_before.split('\n')
                    for line in reversed(lines_before[-5:]):
                        line = line.strip()
                        if line and len(line) > 3 and not line[0].isdigit():
                            if any(keyword in line.lower() for keyword in ['league', 'division', 'championship', 'cup', 'coupe', 'liga', 'ligue', 'serie', 'bundesliga', 'premier', 'eredivisie', 'j-league', 'mls', 'primeira', 'super', 'national', 'proximus', 'tipico', 'rfef']):
                                league = line.strip()
                                break
                
                # Determine sport type from league name
                sport = self.determine_sport(league)
                
                # Extract confidence percentage
                conf_pattern = r'CONFIDENCE\s+(\d+(?:\.\d+)?)\s*%'
                conf_match = re.search(conf_pattern, context)
                confidence_value = 0
                if conf_match:
                    confidence_value = float(conf_match.group(1))
                
                # Only process if confidence meets minimum threshold
                if confidence_value < self.min_confidence:
                    continue
                
                # Extract probabilities
                prob_patterns = {
                    'prob_team1_win': r'TEAM.*?1.*?WIN\s+(\d+\.?\d*)\s*%|(\d+\.?\d*)\s*%\s+TEAM.*?1.*?WIN',
                    'prob_draw': r'DRAW\s+(\d+\.?\d*)\s*%|(\d+\.?\d*)\s*%\s+DRAW',
                    'prob_team2_win': r'TEAM.*?2.*?WIN\s+(\d+\.?\d*)\s*%|(\d+\.?\d*)\s*%\s+TEAM.*?2.*?WIN'
                }
                
                probabilities = {}
                for key, pattern in prob_patterns.items():
                    prob_match = re.search(pattern, context, re.IGNORECASE)
                    if prob_match:
                        # Get first non-None group
                        value = prob_match.group(1) if prob_match.group(1) else prob_match.group(2)
                        probabilities[key] = f"{value}%"
                    else:
                        probabilities[key] = "N/A"
                
                # Extract final score if available
                score_pattern = r'FINAL\s+SCORE\s+(\d+:\d+)'
                score_match = re.search(score_pattern, context)
                score_final = score_match.group(1) if score_match else ""
                
                # Extract first half score
                first_half_pattern = r'FIRST\s+HALF\s+(\d+:\d+)'
                first_half_match = re.search(first_half_pattern, context)
                score_first_half = first_half_match.group(1) if first_half_match else ""
                
                # Create prediction object
                prediction = {
                    'date_time': date_time,
                    'team1': team1,
                    'team2': team2,
                    'score_first_half': score_first_half,
                    'score_final': score_final,
                    'confidence': f"{confidence_value}%",
                    'confidence_value': confidence_value,
                    'prob_team1_win': probabilities['prob_team1_win'],
                    'prob_draw': probabilities['prob_draw'],
                    'prob_team2_win': probabilities['prob_team2_win'],
                }
                
                # Add sport and league information
                prediction['sport'] = sport
                prediction['league'] = league
                
                self.predictions.append(prediction)
                
            except Exception as e:
                continue
    

    
    def save_to_csv(self, filename='predictions.csv'):
        """Save predictions to CSV file"""
        if self.predictions:
            df = pd.DataFrame(self.predictions)
            df.to_csv(filename, index=False)
            print(f"[+] Saved {len(self.predictions)} predictions to {filename}")
            return filename
        print("[-] No predictions to save")
        return None
    
    def save_to_json(self, filename='predictions.json'):
        """Save predictions to JSON file with organized structure"""
        if self.predictions:
            # Organize predictions by sport
            predictions_by_sport = {}
            high_value_predictions = []
            
            for pred in self.predictions:
                sport = pred.get('sport', 'Other')
                if sport not in predictions_by_sport:
                    predictions_by_sport[sport] = []
                predictions_by_sport[sport].append(pred)
                
                # Check if either team has >40% win probability
                team1_win_pct = self.extract_percentage_value(pred['prob_team1_win'])
                team2_win_pct = self.extract_percentage_value(pred['prob_team2_win'])
                if team1_win_pct > 40 or team2_win_pct > 40:
                    high_value_predictions.append(pred)
            
            # Sort each sport by confidence (descending)
            for sport in predictions_by_sport:
                predictions_by_sport[sport].sort(
                    key=lambda x: x['confidence_value'],
                    reverse=True
                )
            
            # Sort high value by team win percentage (descending)
            high_value_predictions.sort(
                key=lambda x: max(
                    self.extract_percentage_value(x['prob_team1_win']),
                    self.extract_percentage_value(x['prob_team2_win'])
                ),
                reverse=True
            )
            
            # Create organized output
            output_data = {
                "status": "success",
                "scrape_time": datetime.now().isoformat(),
                "source": self.url,
                "filter": {
                    "min_confidence": f"{self.min_confidence}%"
                },
                "summary": {
                    "total_predictions": len(self.predictions),
                    "sports_covered": len(predictions_by_sport),
                    "breakdown": {sport: len(preds) for sport, preds in predictions_by_sport.items()},
                    "high_confidence_teams_count": len(high_value_predictions)
                },
                "high_value_predictions": high_value_predictions,
                "predictions_by_sport": predictions_by_sport
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            print(f"[+] Saved {len(self.predictions)} predictions to {filename}")
            return filename
        print("[-] No predictions to save")
        return None
    
    def extract_percentage_value(self, percent_str):
        """Extract numeric value from percentage string"""
        try:
            if isinstance(percent_str, str):
                return float(percent_str.replace('%', '').strip())
            return float(percent_str)
        except:
            return 0
    
    def display_json_results(self):
        """Display results as formatted JSON in terminal, organized by sport and confidence"""
        if not self.predictions:
            print(json.dumps({
                "status": "success",
                "total_predictions": 0,
                "min_confidence": f"{self.min_confidence}%",
                "predictions_by_sport": {},
                "message": "No predictions found with confidence >= " + str(self.min_confidence) + "%"
            }, indent=2))
            return
        
        # Organize predictions by sport
        predictions_by_sport = {}
        for pred in self.predictions:
            sport = pred.get('sport', 'Other')
            if sport not in predictions_by_sport:
                predictions_by_sport[sport] = []
            predictions_by_sport[sport].append(pred)
        
        # Prepare data for JSON output
        output_data = {
            "status": "success",
            "scrape_time": datetime.now().isoformat(),
            "source": self.url,
            "filter": {
                "min_confidence": f"{self.min_confidence}%"
            },
            "summary": {
                "total_predictions": len(self.predictions),
                "sports_covered": len(predictions_by_sport),
                "breakdown": {sport: len(preds) for sport, preds in predictions_by_sport.items()}
            },
            "high_value_predictions": [],
            "predictions_by_sport": {}
        }
        
        # Add predictions organized by sport
        for sport in sorted(predictions_by_sport.keys()):
            sport_predictions = []
            for pred in predictions_by_sport[sport]:
                # Extract team win percentages
                team1_win_pct = self.extract_percentage_value(pred['prob_team1_win'])
                team2_win_pct = self.extract_percentage_value(pred['prob_team2_win'])
                
                formatted_pred = {
                    "sport": pred.get('sport', 'Other'),
                    "league": pred.get('league', 'Unknown'),
                    "date_time": pred['date_time'],
                    "match": {
                        "team1": pred['team1'],
                        "team2": pred['team2']
                    },
                    "predictions": {
                        "first_half_score": pred['score_first_half'],
                        "final_score": pred['score_final']
                    },
                    "confidence": {
                        "overall_percentage": pred['confidence'],
                        "overall_numeric": pred['confidence_value']
                    },
                    "per_outcome_confidence": {
                        "team1_win": pred['prob_team1_win'],
                        "draw": pred['prob_draw'],
                        "team2_win": pred['prob_team2_win']
                    }
                }
                sport_predictions.append(formatted_pred)
                
                # Check if either team has >40% win probability
                if team1_win_pct > 40 or team2_win_pct > 40:
                    output_data["high_value_predictions"].append(formatted_pred)
            
            # Sort sport predictions by confidence (descending)
            sport_predictions.sort(key=lambda x: x['confidence']['overall_numeric'], reverse=True)
            output_data["predictions_by_sport"][sport] = sport_predictions
        
        # Sort high value predictions by team win percentage (descending)
        output_data["high_value_predictions"].sort(
            key=lambda x: max(
                self.extract_percentage_value(x['per_outcome_confidence']['team1_win']),
                self.extract_percentage_value(x['per_outcome_confidence']['team2_win'])
            ),
            reverse=True
        )
        
        # Print formatted JSON
        print(json.dumps(output_data, indent=2))
        return output_data


class GoodTeamConfidenceFilter:
    """
    Filters games with good team confidence based on criteria:
    - Team win % > 30%
    - Draw % > 30%
    - Both values must be greater than the opposite team
    """
    
    def __init__(self, predictions):
        self.predictions = predictions
        self.filtered_predictions = []
    
    def extract_percentage_value(self, percent_str):
        """Extract numeric value from percentage string"""
        try:
            if isinstance(percent_str, str):
                return float(percent_str.replace('%', '').strip())
            return float(percent_str)
        except:
            return 0
    
    def is_good_team_confidence(self, pred):
        """
        Check if prediction meets good team confidence criteria:
        - Team1 win % > 30 AND draw % > 30 AND both > team2 win %
        - OR Team2 win % > 30 AND draw % > 30 AND both > team1 win %
        """
        team1_win = self.extract_percentage_value(pred['prob_team1_win'])
        draw = self.extract_percentage_value(pred['prob_draw'])
        team2_win = self.extract_percentage_value(pred['prob_team2_win'])
        
        # Team 1 has good confidence: team1_win > 30 AND draw > 30 AND both > team2_win
        team1_good = team1_win > 30 and draw > 30 and team1_win > team2_win and draw > team2_win
        
        # Team 2 has good confidence: team2_win > 30 AND draw > 30 AND both > team1_win
        team2_good = team2_win > 30 and draw > 30 and team2_win > team1_win and draw > team1_win
        
        return team1_good or team2_good
    
    def filter_games(self):
        """Filter predictions and return games with good team confidence"""
        self.filtered_predictions = [
            pred for pred in self.predictions 
            if self.is_good_team_confidence(pred)
        ]
        return self.filtered_predictions
    
    def save_to_json(self, filename='good_team_confidence_predictions.json'):
        """Save filtered predictions to JSON file"""
        if not self.filtered_predictions:
            print(f"[-] No predictions found with good team confidence criteria")
            return None
        
        # Organize by sport
        predictions_by_sport = {}
        for pred in self.filtered_predictions:
            sport = pred.get('sport', 'Other')
            if sport not in predictions_by_sport:
                predictions_by_sport[sport] = []
            predictions_by_sport[sport].append(pred)
        
        # Sort each sport by confidence (descending)
        for sport in predictions_by_sport:
            predictions_by_sport[sport].sort(
                key=lambda x: x['confidence_value'],
                reverse=True
            )
        
        # Create output
        output_data = {
            "status": "success",
            "scrape_time": datetime.now().isoformat(),
            "source": "https://zcodesystem.com/scorespredictor/?hop=sportsmart",
            "filter": {
                "criteria": "Good Team Confidence",
                "team_win_percentage_minimum": ">30%",
                "draw_percentage_minimum": ">30%",
                "requirement": "Both team win % and draw % must be greater than opposite team"
            },
            "summary": {
                "total_predictions": len(self.filtered_predictions),
                "sports_covered": len(predictions_by_sport),
                "breakdown": {sport: len(preds) for sport, preds in predictions_by_sport.items()}
            },
            "predictions_by_sport": predictions_by_sport
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        print(f"[+] Saved {len(self.filtered_predictions)} good team confidence predictions to {filename}")
        return filename


def main():
    """Main function to run the scraper"""
    try:
        print("[*] Starting Z Code System Scores Predictor Scraper...")
        print("[+] Filtering: Confidence >= 60%")
        print("[+] Target URL: https://zcodesystem.com/scorespredictor/?hop=sportsmart\n")

        scraper = ScoresPredictorScraper(min_confidence=60)

        print("[*] Fetching webpage...")
        html = scraper.fetch_page()

        if html:
            print("[+] Page fetched successfully!")
            print("[*] Extracting predictions (60%+ confidence)...\n")
            scraper.extract_predictions(html)

            print("="*80)
            print("HIGH CONFIDENCE PREDICTIONS (60%+) - JSON FORMAT")
            print("="*80)
            scraper.display_json_results()

            print("\n" + "="*80)
            print("[*] Saving data...")
            scraper.save_to_csv('high_confidence_predictions.csv')
            scraper.save_to_json('high_confidence_predictions.json')

            print("\n" + "="*80)
            print("[*] Filtering for good team confidence predictions...")
            print("    Criteria: Team win % > 30%, Draw % > 30%")
            print("    AND both must be greater than opposite team")
            print("="*80)

            team_confidence_filter = GoodTeamConfidenceFilter(scraper.predictions)
            filtered_games = team_confidence_filter.filter_games()

            if filtered_games:
                print(f"\n[+] Found {len(filtered_games)} games with good team confidence!")
                team_confidence_filter.save_to_json('good_team_confidence_predictions.json')
            else:
                print("[-] No games found with good team confidence criteria")

            print("\n[+] Scraping complete!")
            print("[+] Files saved:")
            print("   - high_confidence_predictions.csv")
            print("   - high_confidence_predictions.json")
            if filtered_games:
                print("   - good_team_confidence_predictions.json")
        else:
            print("[-] Failed to fetch page. Check your internet connection or Chrome setup.")

    except Exception as e:
        print(f"\n[ERROR] Fatal error in main: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
