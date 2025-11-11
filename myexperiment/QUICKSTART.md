# Quick Start Guide - PWYW Game

## Run the Experiment

### First Time Setup

```powershell
# Navigate to project directory
cd "d:\OneDrive - Fulbright University Vietnam\baihoc\Fall2026\econ-ctam\myexperiment"

# Reset database (only needed first time or after model changes)
otree resetdb

# Start the server
otree devserver
```

### Access the Experiment

1. Open browser: http://localhost:8000
2. Click "Demo" next to "Pay-What-You-Want Game"
3. Open 2 browser windows (or use incognito for 2nd participant)

## Experiment Flow

### Round Structure (6 rounds total)

- **Rounds 1-2**: Control condition (no suggested price)
- **Rounds 3-4**: High suggested price (70 tokens)
- **Rounds 5-6**: Low suggested price (30 tokens)
- Order is randomized each session
- Roles alternate each round

### Player Experience

**Buyer:**

1. Sees product utility (random 40-90 tokens)
2. Decides: Buy or Not Buy
3. If buying: Sets price (0-100 tokens)
4. Sees payoff results

**Seller:**

1. Sees production cost (random 20-60 tokens)
2. Waits for buyer's decision
3. Sees payoff results

## Key Features Implemented

✅ 2 players (Buyer/Seller)
✅ 6 rounds with role rotation
✅ 3 treatment conditions (control, high, low suggested price)
✅ Randomized order and pairing
✅ Introduction with role descriptions
✅ Comprehension check (2 questions)
✅ Dynamic decision form
✅ Waiting page for seller
✅ Detailed results page
✅ Payoff calculations

## Payoff Formulas

**Buyer:**

- If buys: 100 - price_paid + product_utility
- If not: 100

**Seller:**

- If buyer buys: price_paid - production_cost
- If not: 0

## Data Collection

Export data from admin panel after session:

- All decisions (buy/not buy, prices)
- All payoffs
- Treatment conditions
- Round numbers
- Role assignments

## Common Commands

```powershell
# Start server
otree devserver

# Reset database
otree resetdb

# Run on different port
otree devserver 8001

# Create data export
# Use admin interface: http://localhost:8000 -> Data tab
```

## Customization Quick Reference

File: `my_game/__init__.py`

- **NUM_ROUNDS**: Line 13 (currently 6)
- **BUYER_ENDOWMENT**: Line 21 (currently 100)
- **SUGGESTED_PRICES**: Lines 29-30 (high: 70, low: 30)
- **Utility range**: Line 92 (currently 40-90)
- **Cost range**: Line 95 (currently 20-60)

## Testing Checklist

- [ ] Both roles display correctly
- [ ] Comprehension check blocks incorrect answers
- [ ] Price field shows/hides based on buy decision
- [ ] Seller waits for buyer
- [ ] Payoffs calculate correctly
- [ ] All 6 rounds complete
- [ ] Roles swap between rounds
- [ ] Treatment conditions vary
- [ ] Data exports correctly

## Troubleshooting

**Error: Port in use**

```powershell
otree devserver 8001
```

**Error: Database locked**

```powershell
otree resetdb
```

**Error: Import otree.api failed**

```powershell
pip install --upgrade otree
```

**Pages not updating**

- Refresh browser (Ctrl+F5)
- Clear browser cache
- Restart otree server
