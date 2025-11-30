"""
QUICK REFERENCE: WHERE TO BET ON Z CODE SYSTEM PREDICTIONS
=============================================================
"""

SPORTSBOOKS = {
    # TIER 1: Best Overall
    "BET365": {
        "url": "https://www.bet365.com",
        "region": "International (UK, Europe, Canada, etc.)",
        "rating": "⭐⭐⭐⭐⭐ - #1 Worldwide",
        "markets": ["Match Winner", "Over/Under", "BTTS", "Correct Score", "Live Betting"],
        "min_deposit": "$5-10",
        "bonus": "Welcome bonus available"
    },
    
    # TIER 1: Betting Exchange
    "Betfair": {
        "url": "https://www.betfair.com",
        "region": "International (not USA)",
        "rating": "⭐⭐⭐⭐⭐ - Best Prices",
        "markets": ["Betting Exchange", "Live Odds", "In-Play Markets"],
        "min_deposit": "$5",
        "bonus": "Exchange commission on profits"
    },
    
    # TIER 2: Classic Bookmaker
    "William Hill": {
        "url": "https://www.williamhill.com",
        "region": "UK, Europe, International",
        "rating": "⭐⭐⭐⭐ - Historic Brand",
        "markets": ["Match Betting", "Goal Markets", "Asian Handicap"],
        "min_deposit": "$10",
        "bonus": "Welcome bonus"
    },
    
    # TIER 2: Professional Bettors
    "Pinnacle Sports": {
        "url": "https://www.pinnaclesports.com",
        "region": "International (not USA)",
        "rating": "⭐⭐⭐⭐ - Best Limits",
        "markets": ["All major types", "No betting limits"],
        "min_deposit": "$5",
        "bonus": "No bonuses - best odds instead"
    },
    
    # TIER 3: International Operator
    "Betano": {
        "url": "https://www.betano.com",
        "region": "Europe, Latin America, Africa",
        "rating": "⭐⭐⭐⭐ - Reliable",
        "markets": ["1X2", "Over/Under", "Asian Handicap", "Live Betting"],
        "min_deposit": "$5",
        "bonus": "Welcome bonus available"
    },
    
    # USA-SPECIFIC: DraftKings
    "DraftKings (USA)": {
        "url": "https://www.draftkings.com",
        "region": "USA (most states)",
        "rating": "⭐⭐⭐⭐⭐ - Legal & Regulated",
        "markets": ["Moneyline", "Spread", "Over/Under", "Props", "Parlays"],
        "min_deposit": "$5-25",
        "bonus": "Welcome bonus typically $100+"
    },
    
    # USA-SPECIFIC: FanDuel
    "FanDuel (USA)": {
        "url": "https://www.fanduel.com",
        "region": "USA (most states)",
        "rating": "⭐⭐⭐⭐ - User-Friendly",
        "markets": ["Moneyline", "Props", "Parlays", "Live Betting"],
        "min_deposit": "$5-10",
        "bonus": "Welcome bonus"
    },
    
    # USA-SPECIFIC: BetMGM
    "BetMGM (USA)": {
        "url": "https://www.betmgm.com",
        "region": "USA (select states)",
        "rating": "⭐⭐⭐⭐ - MGM Quality",
        "markets": ["All major types"],
        "min_deposit": "$10",
        "bonus": "Welcome offer"
    },
    
    # USA-SPECIFIC: Caesars
    "Caesars Sportsbook (USA)": {
        "url": "https://www.caesars.com/sportsbook",
        "region": "USA (select states)",
        "rating": "⭐⭐⭐⭐ - Las Vegas Operator",
        "markets": ["All major types"],
        "min_deposit": "$10-20",
        "bonus": "Welcome bonus"
    }
}

QUICK_BET_TYPES = {
    "1X2 / Moneyline": "Predict: Home Win (1), Draw (X), or Away Win (2)",
    "Over/Under": "Predict: More or less than set goals (e.g., 2.5 goals)",
    "BTTS": "Predict: Both Teams To Score - Yes or No",
    "Correct Score": "Predict: Exact final score (high odds, high risk)",
    "Asian Handicap": "Predict: With handicap to level uneven matchups",
    "Live Betting": "Bet: While match is happening, odds change live",
    "First Goal Scorer": "Predict: Which player scores first goal",
    "Parlay": "Combine: Multiple bets - all must win for payout"
}

STEP_BY_STEP_QUICK = """
1. Go to sportsbook website (e.g., BET365.com)
2. Click "Sign Up" and create account
3. Verify email and identity
4. Make deposit (start with $10-50)
5. Find Z Code System prediction
6. Navigate to that game in sportsbook
7. Click odds, enter stake, confirm bet
8. Check your bet slip
9. Monitor game result
10. Withdraw winnings!
"""

HIGHEST_CONFIDENCE_PREDICTIONS_FIRST = """
✅ When reviewing Z Code Scores Predictor:
1. FIRST: Look at games with 70%+ confidence
2. Then: Check if your sportsbook has this game
3. Next: Compare odds between 2-3 sportsbooks
4. Then: Decide if odds match prediction probability
5. Finally: Place your bet

Remember: Higher confidence = higher chance of accuracy
But NOTHING is guaranteed!
"""

BETTING_LIMITS = {
    "Beginner": "$10-50 per bet",
    "Intermediate": "$50-200 per bet",
    "Advanced": "$200+ per bet (after experience)"
}

RESPONSIBLE_BETTING_CHECKLIST = [
    "☐ I have set a monthly budget",
    "☐ I only bet money I can afford to lose",
    "☐ I have NOT chased losses today",
    "☐ I understand the odds I'm betting on",
    "☐ I have compared odds across 2+ sportsbooks",
    "☐ I have not bet more than my limit",
    "☐ I checked that the sportsbook is legal in my location",
    "☐ I am not betting while emotional or under the influence",
    "☐ I have taken breaks and not bet daily",
    "☐ I know when to stop for the day"
]

if __name__ == "__main__":
    print("\n" + "="*80)
    print("QUICK REFERENCE: WHERE TO BET ON SPORTS PREDICTIONS")
    print("="*80)
    
    print("\n📌 BEST SPORTSBOOKS:")
    print("-"*80)
    for sportsbook, details in SPORTSBOOKS.items():
        print(f"\n{sportsbook}")
        print(f"  🌐 {details['url']}")
        print(f"  🗺️  {details['region']}")
        print(f"  ⭐ {details['rating']}")
        print(f"  📊 Markets: {', '.join(details['markets'][:3])}...")
        print(f"  💰 Min Deposit: {details['min_deposit']}")
        print(f"  🎁 {details['bonus']}")
    
    print("\n\n📋 BET TYPES QUICK GUIDE:")
    print("-"*80)
    for bet_type, description in QUICK_BET_TYPES.items():
        print(f"  • {bet_type}: {description}")
    
    print("\n\n🚀 STEP-BY-STEP QUICK GUIDE:")
    print("-"*80)
    print(STEP_BY_STEP_QUICK)
    
    print("\n\n📊 BEST STRATEGY:")
    print("-"*80)
    print(HIGHEST_CONFIDENCE_PREDICTIONS_FIRST)
    
    print("\n\n💰 BETTING LIMITS BY EXPERIENCE:")
    print("-"*80)
    for level, limit in BETTING_LIMITS.items():
        print(f"  • {level}: {limit}")
    
    print("\n\n✅ RESPONSIBLE BETTING CHECKLIST:")
    print("-"*80)
    for check in RESPONSIBLE_BETTING_CHECKLIST:
        print(f"  {check}")
    
    print("\n\n" + "="*80)
    print("❌ NEVER DO THIS:")
    print("  ✗ Bet money you need for bills")
    print("  ✗ Chase losses with bigger bets")
    print("  ✗ Bet when emotional or drunk")
    print("  ✗ Trust a prediction 100%")
    print("  ✗ Ignore local gambling laws")
    print("  ✗ Use unlicensed sportsbooks")
    print("  ✗ Bet the same amount every single day")
    print("="*80 + "\n")
