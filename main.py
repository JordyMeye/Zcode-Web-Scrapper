import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
from datetime import datetime
import re
import time
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
            # Setup Chrome options
            chrome_options = Options()
            chrome_options.add_argument('--start-maximized')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            # Initialize Chrome WebDriver
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.set_page_load_timeout(30)
            
            # Load the page
            driver.get(self.url)
            
            # Wait for page to load and data to be rendered (max 20 seconds)
            try:
                WebDriverWait(driver, 20).until(
                    lambda driver: driver.execute_script('return document.readyState') == 'complete'
                )
            except:
                pass  # Continue anyway if timeout
            
            # Additional wait for any dynamic content
            time.sleep(2)
            
            # Get page source after JavaScript execution
            page_source = driver.page_source
            return page_source
            
        except Exception as e:
            print(f"Error fetching page with Selenium: {e}")
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
            # Extract data from columns
            date_time = cols[0].get_text(strip=True)
            team1 = cols[1].get_text(strip=True)
            team2 = cols[2].get_text(strip=True)
            
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
                date_time = match.group(1)
                team1 = match.group(2).strip()
                odds1 = match.group(3)
                team2 = match.group(4).strip()
                odds2 = match.group(5)
                
                # Get position for context extraction
                match_start = match.start()
                match_end = match.end()
                
                # Extract context - look back for league/sport and ahead for predictions
                context_before = text[max(0, match_start - 300):match_start]
                context_after = text[match_start:min(len(text), match_end + 1500)]
                context = context_before + context_after
                
                # Extract league name from date_time or context
                # Try to extract league from the beginning of date_time which may contain league info
                league = "Unknown"
                
                # Parse date_time to extract league (format is usually "LeagueDatetime")
                if date_time and not date_time[0].isdigit():
                    # Extract text before the date pattern
                    date_pattern = r'^([^0-9]*?)(\d{1,2}(?:st|nd|rd|th)\s+\w+\s+\d{4})'
                    league_match = re.match(date_pattern, date_time)
                    if league_match:
                        league = league_match.group(1).strip()
                        if not league:
                            league = "Unknown"
                
                # If still unknown, look in context
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


def main():
    """Main function to run the scraper"""
    print("[*] Starting Z Code System Scores Predictor Scraper...")
    print("[+] Filtering: Confidence >= 60%")
    print("[+] Target URL: https://zcodesystem.com/scorespredictor/?hop=sportsmart\n")
    
    # Initialize scraper with 60% minimum confidence
    scraper = ScoresPredictorScraper(min_confidence=60)
    
    # Fetch and parse page
    print("[*] Fetching webpage...")
    html = scraper.fetch_page()
    
    if html:
        print("[+] Page fetched successfully!")
        print("[*] Extracting predictions (60%+ confidence)...\n")
        scraper.extract_predictions(html)
        
        # Display results as JSON
        print("="*80)
        print("HIGH CONFIDENCE PREDICTIONS (60%+) - JSON FORMAT")
        print("="*80)
        scraper.display_json_results()
        
        # Save to files
        print("\n" + "="*80)
        print("[*] Saving data...")
        scraper.save_to_csv('high_confidence_predictions.csv')
        scraper.save_to_json('high_confidence_predictions.json')
        
        print("\n[+] Scraping complete!")
        print("[+] Files saved:")
        print("   - high_confidence_predictions.csv")
        print("   - high_confidence_predictions.json")
    else:
        print("[-] Failed to fetch the webpage")


if __name__ == "__main__":
    main()
