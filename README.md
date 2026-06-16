# Z Code System Scores Predictor Scraper & Betting Guide

## Overview
This project helps you:
1. **Scrape** daily betting predictions from Z Code System Scores Predictor
2. **Understand** the betting predictions and probabilities
3. **Find** where to place your bets with recommended sportsbooks

## About Z Code System Scores Predictor
- **URL**: https://zcodesystem.com/scorespredictor/?hop=sportsmart
- **What it provides**: Daily sports predictions with:
  - Match winner probabilities (Team 1 Win, Draw, Team 2 Win)
  - Predicted scores (first half & final)
  - Confidence scores
  - Betting recommendations

## Files in This Project

### 1. `main.py`
The main web scraper that:
- Fetches predictions from Z Code System
- Extracts game data, probabilities, and confidence scores
- Saves data to CSV and JSON files
- Displays betting site recommendations

**Run it:**
```bash
python main.py
```

### 2. `betting_guide.py`
Comprehensive guide showing:
- All major sportsbooks by region
- Types of bets explained
- Step-by-step how to start betting
- Responsible gambling tips
- Resources for problem gambling

**Run it:**
```bash
python betting_guide.py
```

### 3. `predictions.csv` & `predictions.json`
Output files containing scraped predictions (auto-generated)

## Where to Place Your Bets

### 🌍 BEST INTERNATIONAL SPORTSBOOKS
1. **BET365** (https://www.bet365.com)
   - Available: UK, Europe, Latin America, Canada
   - Markets: Match Winner, Over/Under, BTTS, Correct Score, Live Betting
   - Rating: #1 globally, best odds

2. **Betfair** (https://www.betfair.com)
   - Available: International (UK-based)
   - Markets: Betting Exchange, Live Odds, In-Play
   - Rating: Best prices on betting exchange

3. **William Hill** (https://www.williamhill.com)
   - Available: UK, Europe, International
   - Markets: Match Betting, Goal Markets, Asian Handicap
   - Rating: Trusted since 1934

4. **Pinnacle Sports** (https://www.pinnaclesports.com)
   - Available: Nearly all countries (except USA)
   - Markets: All major betting types
   - Rating: Best for serious bettors, no limits

5. **Betano** (https://www.betano.com)
   - Available: Europe, Latin America, Africa
   - Markets: 1X2, Over/Under, Asian Handicap, Live Betting
   - Rating: Reliable, growing operator

### 🇺🇸 USA ONLY
1. **DraftKings** (https://www.draftkings.com) - Legal, regulated, most states
2. **FanDuel** (https://www.fanduel.com) - User-friendly, most states
3. **BetMGM** (https://www.betmgm.com) - MGM brand, select states
4. **Caesars Sportsbook** (https://www.caesars.com/sportsbook) - Las Vegas operator

### 🇨🇦 CANADA
- **Bet365** - Available nationwide
- **DraftKings** - Growing availability in provinces

## Types of Bets Explained

### 1. **MONEYLINE (Match Winner)**
- Bet on which team wins
- Example: Team A at 1.50 odds wins you $50 profit on $100 bet
- Best for: Confident predictions

### 2. **OVER/UNDER GOALS**
- Predict if total goals will be over or under a number
- Example: Over 2.5 goals
- Best for: Predicting goal totals

### 3. **DRAW**
- Bet that match ends in a tie
- Best for: Low-scoring predictions

### 4. **BOTH TEAMS TO SCORE (BTTS)**
- Both teams score at least one goal
- Best for: Attacking teams with weak defense

### 5. **CORRECT SCORE**
- Predict exact final score (e.g., 2-1)
- Best for: High-risk, high-reward bets

### 6. **ASIAN HANDICAP**
- One team gets virtual head start/disadvantage
- Best for: When one team heavily favored

### 7. **LIVE/IN-PLAY BETTING**
- Bet during the match with changing odds
- Best for: Reactive betting

### 8. **PARLAYS/ACCUMULATORS**
- Combine multiple bets (all must win)
- Best for: Risk-takers, big payouts

## How to Start Betting

### Step 1: Choose a Sportsbook
- Check if legal in your country/state
- Verify it's licensed and regulated
- Compare odds and welcome bonuses

### Step 2: Create Account
- Go to website, click "Sign Up"
- Provide email, username, password
- Enter personal info (name, DOB, address)

### Step 3: Verify Account
- Confirm email
- Upload ID and proof of address if needed
- Wait for approval (usually instant)

### Step 4: Deposit Money
- Go to "Deposit" or "Cashier"
- Choose payment method (Card, E-wallet, Bank Transfer)
- Enter amount

### Step 5: Find Predictions
- Use Z Code System Scores Predictor
- Look for high confidence scores
- Review predicted probabilities

### Step 6: Place Your Bet
- Navigate to the sport/game
- Click the odds you want
- Enter your stake amount
- Confirm bet

### Step 7: Track & Withdraw
- Check your open bets
- Monitor live scores
- Withdraw winnings

## Understanding Confidence Scores

From Z Code System predictions:
- **60-100%**: High confidence - strong prediction
- **40-60%**: Medium confidence - moderate prediction
- **Below 40%**: Low confidence - risky prediction

**Tip**: Focus on games with 60%+ confidence for better results

## Important Warnings ⚠️

🔴 **ONLY BET MONEY YOU CAN AFFORD TO LOSE**
🔴 Gambling is addictive - set limits
🔴 Check local laws - not legal everywhere
🔴 Must be 18+ (21+ in some US states)
🔴 Odds vary between sportsbooks - always compare
🔴 NO prediction is 100% accurate
🔴 Start small, don't bet large amounts immediately
🔴 Use ONLY official, licensed sportsbooks
🔴 Predictions can still be wrong despite data

## Responsible Betting Tips 💚

1. **Set a Budget** - Decide how much you can afford to lose per month
2. **Use Limits** - Most sportsbooks let you set deposit/loss limits
3. **Track Bets** - Keep records of all bets and results
4. **Take Breaks** - Don't bet every single day
5. **Avoid Chasing Losses** - Don't try to win back losses with bigger bets
6. **Don't Bet When Emotional** - Only bet with a clear head
7. **Diversify Bets** - Don't put everything on one game
8. **Learn the Odds** - Understand probability before betting
9. **Use Stop Losses** - Accept losses and move on
10. **Seek Help** - Organizations like Gamblers Anonymous offer support

## Getting Help 📞

If you're struggling with gambling:
- **Gamblers Anonymous**: https://www.gamblersanonymous.org
- **NCPG (USA)**: https://www.ncpg.org - Call 1-800-GAMBLER
- **UK Gambling Commission**: https://www.gamblingcommission.org.uk
- **Responsible Gambling Council (Canada)**: https://www.responsiblegambling.org
- **BeGambleAware (UK)**: https://www.begambleaware.org

## Requirements

```bash
pip install requests beautifulsoup4 pandas
```

Or run:
```bash
python -m pip install -r requirements.txt
```

## Usage

```bash
# Run the scraper
python main.py

# Display betting guide
python betting_guide.py
```

## Output Files

- `predictions.csv` - All predictions in spreadsheet format
- `predictions.json` - All predictions in JSON format

## Key Takeaways

✅ **Z Code System Scores Predictor** provides daily betting predictions
✅ **Most popular sportsbooks**: BET365, Betfair, William Hill, Pinnacle
✅ **Best bet types**: Moneyline, Over/Under, BTTS, Asian Handicap
✅ **Always bet responsibly** - only what you can afford to lose
✅ **Compare odds** between multiple sportsbooks for best value
✅ **Start small** until you gain experience
✅ **Focus on high confidence** predictions (60%+)

## Disclaimer

This tool is for informational purposes only. Sports predictions are never guaranteed to be accurate. Always:
- Check your local gambling laws
- Verify the legality of online betting in your jurisdiction
- Bet responsibly
- Only use licensed, regulated sportsbooks
- Seek professional help if you develop problem gambling habits

---

**Made with ❤️ for sports betting enthusiasts**

*Remember: Bet smart, bet safe, bet responsibly!*


Commands — from a fresh terminal

# 1. Activate the virtual environment (always do this first)
.\venv\Scripts\activate

# 2. Scrape predictions (football + tennis)
python run_all.py

# 3. Open the dashboard in your browser
python serve.py
That's all you need for normal use. For individual scrapers:


# Football only
python -m sports.football.scraper

# Tennis only
python -m sports.tennis.scraper

# Update match results (after games finish)
python update_results.py