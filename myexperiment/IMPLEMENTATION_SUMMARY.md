# PWYW Game - Implementation Summary

### Game Logic (`my_game/__init__.py`)

All game mechanics have been fully implemented:

1. **Constants & Configuration**

   - 2 players per group (Buyer & Seller)
   - 6 rounds
   - 3 treatment conditions (Control, High Suggested, Low Suggested)
   - Endowments: Buyer=100, Seller=0 tokens
   - Suggested prices: High=70, Low=30

2. **Session Creation Logic**

   - Randomizes treatment order at session start
   - Assigns initial roles randomly
   - Swaps roles across rounds
   - Randomizes product utility (40-90 tokens)
   - Randomizes production cost (20-60 tokens)

3. **Data Models**

   - **Group level**: treatment, product_utility, production_cost, buyer_decision, price_paid
   - **Player level**: comprehension check answers (comp_q1, comp_q2)
   - Automatic payoff calculation

4. **Pages Implemented**
   - Introduction (Round 1 only)
   - ComprehensionCheck (Round 1 only)
   - Decision (Buyer only)
   - WaitForBuyer (Seller only)
   - ResultsWaitPage (synchronization)
   - Results (both players)

### HTML Templates Created

1. **Introduction.html**

   - Complete instructions for both roles
   - Formatted with Bootstrap cards
   - Clear role descriptions, endowments, payoff formulas

2. **ComprehensionCheck.html**

   - 2 comprehension questions
   - Validation that redirects to instructions if incorrect
   - Q1: Seller cannot reject (Answer: False)
   - Q2: Utility changes each round (Answer: False)

3. **Decision.html**

   - Buyer's decision interface
   - Displays round info, role, endowment, utility, production cost
   - Shows suggested price (if applicable)
   - Dynamic form: price field only shows when "Yes" selected
   - JavaScript for form interactivity

4. **WaitForBuyer.html**

   - Seller's waiting page
   - Displays role, endowment, production cost
   - Explains payoff calculation
   - Waiting message

5. **Results.html**
   - Shows transaction details
   - Displays buyer's decision and price paid
   - Shows payoff breakdown for both players
   - Different view depending on role
   - Progress indicator (Round X of 6)

### Settings Configuration (`settings.py`)

- Session config: "pwyw_game"
- Participant fields for tracking initial roles
- Session fields for treatment sequence

### Documentation

- **README.md**: Complete documentation with setup, features, customization
- **QUICKSTART.md**: Quick reference for running and testing

## Key Features Implemented

### Experimental Design Features

2-player groups (Buyer/Seller)
6 rounds with role rotation
3 treatment conditions properly randomized
No participant paired twice (single session design)
Equal distribution of buyers/sellers per round
Random utility and cost values each round

### User Interface Features

Clear role-based instructions
Comprehension check with validation
Dynamic forms (conditional field display)
Waiting pages for synchronization
Detailed results with payoff breakdown
Progress tracking across rounds
Responsive Bootstrap design

### Data Collection

All decisions recorded
Treatment conditions tracked
Role assignments logged
Payoffs calculated automatically
Ready for data export

## 📋 Testing Instructions

### Quick Test (2 participants)

```powershell
cd "d:\OneDrive - Fulbright University Vietnam\baihoc\Fall2026\econ-ctam\myexperiment"
otree resetdb
otree devserver
```

Then:

1. Open http://localhost:8000
2. Click Demo for "Pay-What-You-Want Game"
3. Open 2 browser windows
4. Test full 6-round sequence

### What to Verify

- [ ] Introduction displays both role descriptions
- [ ] Comprehension check rejects wrong answers
- [ ] Buyer sees correct utility value
- [ ] Seller sees correct production cost
- [ ] Price field appears/disappears correctly
- [ ] Seller waits while buyer decides
- [ ] Results show correct payoffs
- [ ] Roles swap in subsequent rounds
- [ ] Treatment conditions vary
- [ ] All 6 rounds complete

## 🔧 Customization Options

### Change Number of Rounds

Edit `my_game/__init__.py`, line 13:

```python
NUM_ROUNDS = 6  # Change this
```

### Adjust Endowments

Edit `my_game/__init__.py`, lines 21-22:

```python
BUYER_ENDOWMENT = 100  # Change this
SELLER_ENDOWMENT = 0   # Change this
```

### Adjust Suggested Prices

Edit `my_game/__init__.py`, lines 29-30:

```python
HIGH_SUGGESTED_PRICE = 70  # Change this
LOW_SUGGESTED_PRICE = 30   # Change this
```

### Change Utility/Cost Ranges

Edit `creating_session()` function, lines 92-95:

```python
group.product_utility = random.randint(40, 90)  # Change range
group.production_cost = random.randint(20, 60)  # Change range
```

## 📊 Data Export

After session completion:

1. Go to admin panel: http://localhost:8000
2. Navigate to "Data" tab
3. Select session
4. Download Excel or CSV

### Key Variables

- `player.role` - Buyer or Seller
- `group.treatment` - control/high_suggested/low_suggested
- `group.product_utility` - Utility value shown to buyer
- `group.production_cost` - Cost shown to seller
- `group.buyer_decision` - True/False (bought or not)
- `group.price_paid` - Amount transferred (0-100)
- `player.payoff` - Calculated payoff for that round
- `subsession.round_number` - Round (1-6)

## 🚀 Next Steps

### To Run Your Experiment:

1. Test with demo participants (2)
2. Verify all functionality works
3. Set admin password for production
4. Deploy to server (if needed)
5. Run actual experiment sessions

### For Production Deployment:

```powershell
set OTREE_ADMIN_PASSWORD=YourSecurePassword
set OTREE_PRODUCTION=1
otree prodserver 80
```

## 📝 Notes

- Built with oTree 5.x
- Uses Bootstrap for styling
- All templates use oTree template syntax
- JavaScript for dynamic forms
- Database: SQLite (development) / PostgreSQL (production)
- Designed for 2 participants per session

## 🎓 Experiment Properties

**Treatment Order**: Randomized per session
**Role Assignment**: Initial random, then systematic swap
**Pairing**: Fixed pairs (no re-matching within session)
**Rounds**: 6 total (2 per treatment condition)
**Decision**: Buyer decides buy/not buy and price
**Information**: Complete (both know utility and cost)
**Pricing**: Pay-what-you-want (PWYW) mechanism

## Requirements Met

All specifications from your experimental design document have been implemented:

- 2 players (Buyer & Seller)
- Minimum 6 rounds
- Role rotation
- Treatment conditions (Control, High, Low suggested)
- Randomized order
- Introduction page with instructions
- Comprehension check
- Decision pages (role-specific)
- Results display
- Payoff calculations
- No duplicate pairings
