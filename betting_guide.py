"""
WHERE TO PLACE YOUR BETS - Complete Guide
Based on Z Code System Scores Predictor Predictions
"""

def display_betting_options():
    """Display all betting options and platforms"""
    
    print("\n" + "="*90)
    print(" "*20 + "🎯 COMPLETE BETTING GUIDE FOR SPORTS PREDICTIONS")
    print("="*90)
    
    # Section 1: Top Sportsbooks by Region
    print("\n" + "📌 TOP SPORTSBOOKS BY REGION".center(90))
    print("-"*90)
    
    sportsbooks = {
        "🌍 WORLDWIDE/INTERNATIONAL": {
            "BET365": {
                "url": "https://www.bet365.com",
                "countries": "UK, Europe, Latin America, Canada (most regions)",
                "popular_markets": "Match Winner, Over/Under, BTTS, Correct Score, Live Betting",
                "reputation": "One of the largest with best odds",
                "bonus": "Welcome Bonus available"
            },
            "Betfair": {
                "url": "https://www.betfair.com",
                "countries": "International (UK-based, restricted in USA)",
                "popular_markets": "Betting Exchange, Live Odds, In-Play Markets",
                "reputation": "Betting exchange with best prices",
                "bonus": "Welcome offers available"
            },
            "William Hill": {
                "url": "https://www.williamhill.com",
                "countries": "UK, Europe, International",
                "popular_markets": "Match Betting, Goal Markets, Asian Handicap",
                "reputation": "Established brand, trusted since 1934",
                "bonus": "Welcome bonus"
            },
            "Pinnacle Sports": {
                "url": "https://www.pinnaclesports.com",
                "countries": "Nearly all countries (no USA)",
                "popular_markets": "All major betting types",
                "reputation": "High limits, best for serious bettors",
                "bonus": "No bonuses but best odds"
            },
            "1xBet": {
                "url": "https://www.1xbet.com",
                "countries": "International (extensive coverage)",
                "popular_markets": "Huge variety of markets",
                "reputation": "Large variety, many payment methods",
                "bonus": "Generous welcome bonus"
            },
            "Betano": {
                "url": "https://www.betano.com",
                "countries": "Europe, Latin America, Africa",
                "popular_markets": "1X2, Over/Under, Asian Handicap",
                "reputation": "Growing operator, reliable",
                "bonus": "Welcome bonus available"
            }
        },
        
        "🇺🇸 USA ONLY": {
            "DraftKings": {
                "url": "https://www.draftkings.com",
                "countries": "USA (most states)",
                "popular_markets": "Moneyline, Spread, Over/Under, Parlays, Props",
                "reputation": "Legal, regulated, huge variety",
                "bonus": "Welcome offer available"
            },
            "FanDuel": {
                "url": "https://www.fanduel.com",
                "countries": "USA (most states)",
                "popular_markets": "Moneyline, Props, Parlays, Live Betting",
                "reputation": "Legal, regulated, user-friendly",
                "bonus": "Welcome bonus"
            },
            "BetMGM": {
                "url": "https://www.betmgm.com",
                "countries": "USA (select states)",
                "popular_markets": "All major bet types",
                "reputation": "MGM brand, reliable",
                "bonus": "Welcome offer"
            },
            "Caesars Sportsbook": {
                "url": "https://www.caesars.com/sportsbook",
                "countries": "USA (select states)",
                "popular_markets": "All major betting types",
                "reputation": "Las Vegas operator, trusted",
                "bonus": "Welcome bonus"
            }
        },
        
        "🇨🇦 CANADA": {
            "Bet365": {
                "url": "https://www.bet365.com",
                "countries": "Canada",
                "popular_markets": "All major markets",
                "reputation": "#1 globally",
                "bonus": "Welcome bonus"
            },
            "DraftKings": {
                "url": "https://www.draftkings.com",
                "countries": "Canada (some provinces)",
                "popular_markets": "All major types",
                "reputation": "Growing in Canada",
                "bonus": "Promotions available"
            }
        },
        
        "🇬🇧 UK/EUROPE": {
            "SkyBet": {
                "url": "https://www.skybet.com",
                "countries": "UK",
                "popular_markets": "Match Betting, Markets",
                "reputation": "UK broadcaster, well-known",
                "bonus": "Available"
            },
            "Ladbrokes": {
                "url": "https://www.ladbrokes.com",
                "countries": "UK, Europe",
                "popular_markets": "All major types",
                "reputation": "Historic UK bookmaker",
                "bonus": "Welcome bonus"
            }
        }
    }
    
    for region, books in sportsbooks.items():
        print(f"\n{region}")
        print("-" * 90)
        for book_name, details in books.items():
            print(f"\n  💎 {book_name}")
            print(f"     🌐 Website: {details['url']}")
            print(f"     📍 Available: {details['countries']}")
            print(f"     📊 Markets: {details['popular_markets']}")
            print(f"     ⭐ Reputation: {details['reputation']}")
            print(f"     🎁 {details['bonus']}")
    
    # Section 2: Bet Types Explained
    print("\n\n" + "="*90)
    print(" "*25 + "📋 TYPES OF BETS EXPLAINED")
    print("="*90)
    
    bet_types = {
        "1️⃣  MONEYLINE (Match Winner)": {
            "description": "Predict which team will win the match",
            "example": "Team A (1.50) vs Team B (2.50) - Bet on one to win",
            "odds_meaning": "1.50 = $50 profit on $100 bet | 2.50 = $150 profit on $100 bet",
            "best_for": "Match predictions with confidence"
        },
        "2️⃣  OVER/UNDER GOALS": {
            "description": "Predict if total goals will be over or under a number",
            "example": "Over 2.5 Goals vs Under 2.5 Goals",
            "odds_meaning": "Score prediction: 3+ goals = Over wins | 1-2 goals = Under wins",
            "best_for": "Predicting goal totals"
        },
        "3️⃣  DRAW BETTING": {
            "description": "Bet that the match will end in a tie",
            "example": "Draw at 3.50 odds",
            "odds_meaning": "Available in soccer/football, rare in other sports",
            "best_for": "When you expect a low-scoring tie"
        },
        "4️⃣  BOTH TEAMS TO SCORE (BTTS)": {
            "description": "Both teams score at least one goal",
            "example": "BTTS Yes/No",
            "odds_meaning": "Yes = both teams score | No = one or zero teams score",
            "best_for": "Attacking teams that defend poorly"
        },
        "5️⃣  CORRECT SCORE": {
            "description": "Predict the exact final score",
            "example": "2-1, 3-1, etc.",
            "odds_meaning": "Much higher odds due to difficulty",
            "best_for": "High-risk, high-reward bets"
        },
        "6️⃣  ASIAN HANDICAP": {
            "description": "One team gets a virtual head start/disadvantage",
            "example": "-1 goal for favorites, +1 for underdogs",
            "odds_meaning": "Levels the playing field between unequal teams",
            "best_for": "When one team is heavily favored"
        },
        "7️⃣  LIVE/IN-PLAY BETTING": {
            "description": "Bet during the match with changing odds",
            "example": "Odds update in real-time as game progresses",
            "odds_meaning": "Odds change based on match events",
            "best_for": "Reactive betting during matches"
        },
        "8️⃣  PARLAYS/ACCUMULATORS": {
            "description": "Combine multiple bets into one (all must win)",
            "example": "Bet on 3 games, all must win to cash out",
            "odds_meaning": "Multiplied odds = higher reward but higher risk",
            "best_for": "Risk-takers seeking big payouts"
        },
    }
    
    for bet_type, details in bet_types.items():
        print(f"\n{bet_type}")
        print(f"  📝 {details['description']}")
        print(f"  💡 Example: {details['example']}")
        print(f"  🔢 Odds: {details['odds_meaning']}")
        print(f"  ✅ Best for: {details['best_for']}")
    
    # Section 3: Step-by-Step How to Bet
    print("\n\n" + "="*90)
    print(" "*20 + "🚀 STEP-BY-STEP: HOW TO START BETTING")
    print("="*90)
    
    steps = [
        ("1. CHOOSE A SPORTSBOOK", [
            "✓ Check if it's legal in your country/state",
            "✓ Verify it's licensed and regulated",
            "✓ Compare odds and welcome bonuses",
            "✓ Pick one with good customer reviews"
        ]),
        ("2. CREATE AN ACCOUNT", [
            "✓ Go to the sportsbook website",
            "✓ Click 'Sign Up' or 'Register'",
            "✓ Provide email, username, password",
            "✓ Fill in personal information (name, DOB, address)",
            "✓ Verify your identity (may require documents)"
        ]),
        ("3. VERIFY YOUR ACCOUNT", [
            "✓ Confirm email address",
            "✓ Upload ID and proof of address if required",
            "✓ Wait for approval (usually instant to 24 hours)"
        ]),
        ("4. DEPOSIT MONEY", [
            "✓ Go to 'Deposit' or 'Cashier'",
            "✓ Choose payment method (Credit Card, E-wallet, Bank Transfer)",
            "✓ Enter amount (start small)",
            "✓ Confirm transaction"
        ]),
        ("5. FIND PREDICTIONS", [
            "✓ Use Z Code System Scores Predictor",
            "✓ Look for games with high confidence scores",
            "✓ Review the predicted probabilities"
        ]),
        ("6. PLACE YOUR BETS", [
            "✓ Navigate to the sport/league (Soccer, Football, etc.)",
            "✓ Find the game from your predictions",
            "✓ Click on the odds you want",
            "✓ Enter your stake amount",
            "✓ Review the bet and confirm"
        ]),
        ("7. TRACK YOUR BETS", [
            "✓ Check your bet slip or 'Open Bets'",
            "✓ Monitor live scores",
            "✓ Withdraw winnings when ready"
        ])
    ]
    
    for step_title, step_details in steps:
        print(f"\n{step_title}:")
        for detail in step_details:
            print(f"  {detail}")
    
    # Section 4: Important Warnings
    print("\n\n" + "="*90)
    print(" "*30 + "⚠️  IMPORTANT WARNINGS")
    print("="*90)
    
    warnings = [
        "🔴 ONLY BET WITH MONEY YOU CAN AFFORD TO LOSE",
        "🔴 Gambling is ADDICTIVE - Set limits on what you spend",
        "🔴 Check LOCAL LAWS - Not legal everywhere",
        "🔴 Must be 18+ (21+ in some US states)",
        "🔴 Odds VARY between sportsbooks - Always compare",
        "🔴 NO prediction is 100% accurate",
        "🔴 Start SMALL - Don't bet large amounts until experienced",
        "🔴 Use OFFICIAL sportsbooks only - Avoid illegal sites",
        "🔴 Predictions based on DATA may still be wrong",
        "🔴 Watch out for PROBLEM GAMBLING - There's help available"
    ]
    
    for warning in warnings:
        print(f"  {warning}")
    
    # Section 5: Responsible Betting
    print("\n\n" + "="*90)
    print(" "*25 + "💚 RESPONSIBLE BETTING TIPS")
    print("="*90)
    
    tips = [
        ("Set a Budget", "Decide how much money you can afford to lose each month"),
        ("Use Limits", "Most sportsbooks let you set deposit/loss limits"),
        ("Track Bets", "Keep records of all your bets and results"),
        ("Take Breaks", "Don't bet every single day"),
        ("Avoid Chasing Losses", "Don't try to win back losses with bigger bets"),
        ("Don't Bet When Emotional", "Only bet with a clear head"),
        ("Diversify Bets", "Don't put all money on one game"),
        ("Learn the Odds", "Understand probability before betting"),
        ("Use Stop Losses", "Accept losses and move on"),
        ("Seek Help if Needed", "Organizations like Gamblers Anonymous offer support")
    ]
    
    for tip_title, tip_detail in tips:
        print(f"\n  💡 {tip_title}")
        print(f"     → {tip_detail}")
    
    # Section 6: Resources and Help
    print("\n\n" + "="*90)
    print(" "*25 + "📞 HELP & RESOURCES")
    print("="*90)
    
    resources = [
        ("Gamblers Anonymous", "https://www.gamblersanonymous.org", "Support for problem gambling"),
        ("NCPG (National Council on Problem Gambling)", "https://www.ncpg.org", "1-800-GAMBLER (USA)"),
        ("UK Gambling Commission", "https://www.gamblingcommission.org.uk", "UK gambling regulator"),
        ("Responsible Gambling Council", "https://www.responsiblegambling.org", "Canada"),
        ("BeGambleAware", "https://www.begambleaware.org", "UK resources"),
    ]
    
    for org, website, description in resources:
        print(f"\n  🔗 {org}")
        print(f"     Website: {website}")
        print(f"     Info: {description}")
    
    print("\n\n" + "="*90)
    print(" "*25 + "✅ YOU'RE READY TO START!")
    print("="*90)
    print("""
    Remember:
    1. Start with small bets to learn
    2. Use predictions as guidance, not guaranteed wins
    3. Bet responsibly and have fun
    4. Never chase losses
    5. Enjoy the game!
    """)
    print("="*90 + "\n")


if __name__ == "__main__":
    display_betting_options()
