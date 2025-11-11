# Pay-What-You-Want (PWYW) Game - oTree Experiment

## Overview

This is an oTree implementation of a Pay-What-You-Want pricing experiment where 2 participants are randomly matched to play as Buyer and Seller.

## Experiment Design

### Players

- **2 players per group**: Buyer and Seller
- **6 rounds total**
- Roles are swapped between rounds
- Each round has different treatment conditions

### Treatment Conditions

1. **Control** - No suggested price (2 rounds)
2. **High Suggested Price** - Suggested price: 70 tokens (2 rounds)
3. **Low Suggested Price** - Suggested price: 30 tokens (2 rounds)

### Game Mechanics

#### Buyer

- **Endowment**: 100 tokens
- **Decision**: Whether to buy Product A and how much to pay (0-100 tokens)
- **Product Utility**: Randomly assigned each round (40-90 tokens)
- **Payoff**: 100 - [amount paid] + [product utility] (if bought)

#### Seller

- **Endowment**: 0 tokens
- **No decisions**: Waits for buyer's decision
- **Production Cost**: Randomly assigned each round (20-60 tokens)
- **Payoff**: [amount received] - [production cost]

### Page Sequence

1. **Introduction** (Round 1 only) - Explains game rules and roles
2. **Comprehension Check** (Round 1 only) - 2 questions to verify understanding
3. **Decision** (Buyer only) - Buyer makes purchase decision
4. **Wait For Buyer** (Seller only) - Seller waits for buyer's decision
5. **Results** - Shows transaction details and payoffs for both players

## Files Structure

```
my_game/
├── __init__.py           # Main game logic (models, pages, functions)
├── Introduction.html     # Instructions page
├── ComprehensionCheck.html  # Comprehension test
├── Decision.html         # Buyer decision page
├── WaitForBuyer.html    # Seller waiting page
└── Results.html         # Results display
```

## Key Features

### Randomization

- Treatment order is randomized at session start
- Roles swap between rounds ensuring each participant experiences both roles
- Product utility and production costs vary randomly each round

### Comprehension Check

- Participants must answer 2 questions correctly before starting
- Question 1: Tests understanding that sellers cannot reject prices (Answer: False)
- Question 2: Tests understanding that utility changes each round (Answer: False)
- If answered incorrectly, participants are redirected to instructions

### Data Collected

- Round number
- Player role (Buyer/Seller)
- Treatment condition (control/high_suggested/low_suggested)
- Product utility value
- Production cost
- Buyer's decision (buy/not buy)
- Price paid
- Payoffs for both players

## How to Run

### 1. Install oTree

```bash
pip install otree
```

### 2. Navigate to Project Directory

```bash
cd "d:\OneDrive - Fulbright University Vietnam\baihoc\Fall2026\econ-ctam\myexperiment"
```

### 3. Reset Database (first time or after changes)

```bash
otree resetdb
```

### 4. Run Development Server

```bash
otree devserver
```

### 5. Access the Experiment

Open your browser and go to:

- **Admin Interface**: http://localhost:8000
- **Demo**: Click "Demo" next to "Pay-What-You-Want Game"

### 6. For Production/Deployment

```bash
# Set admin password
set OTREE_ADMIN_PASSWORD=your_secure_password

# Run production server
otree prodserver 8000
```

## Testing

### Demo Mode

- Use 2 demo participants
- Test all rounds and role swaps
- Verify payoff calculations

### Things to Test

1. ✓ Introduction page displays correctly
2. ✓ Comprehension check validates answers
3. ✓ Buyer sees decision page with correct utility
4. ✓ Seller sees waiting page with correct production cost
5. ✓ Price field only shows when buyer selects "Yes"
6. ✓ Results show correct payoff calculations
7. ✓ Roles swap between rounds
8. ✓ Treatment conditions vary across rounds
9. ✓ All 6 rounds complete successfully

## Customization Options

### Adjust Number of Rounds

In `__init__.py`, modify:

```python
NUM_ROUNDS = 6  # Change to desired number
```

### Adjust Endowment/Suggested Prices

In `__init__.py`, modify constants:

```python
BUYER_ENDOWMENT = 100
HIGH_SUGGESTED_PRICE = 70
LOW_SUGGESTED_PRICE = 30
```

### Adjust Utility/Cost Ranges

In `creating_session()` function:

```python
group.product_utility = random.randint(40, 90)  # Change range
group.production_cost = random.randint(20, 60)  # Change range
```

### Add More Treatment Conditions

In `creating_session()`, add to treatments list:

```python
treatments = [
    {'treatment': C.CONTROL, 'role_swap': False},
    {'treatment': C.YOUR_NEW_TREATMENT, 'role_swap': False},
    # ... add more
]
```

## Data Export

After running the experiment:

1. Go to admin interface (http://localhost:8000)
2. Click on "Data" tab
3. Download data in Excel or CSV format
4. Key variables: `player.role`, `group.treatment`, `group.buyer_decision`, `group.price_paid`, `player.payoff`

## Notes

- The experiment uses oTree 5.x syntax
- Bootstrap CSS is used for styling (built into oTree)
- JavaScript handles dynamic form display (price field visibility)
- Session variables store treatment sequence
- Participant variables track initial role assignments

## Troubleshooting

### Database errors

```bash
otree resetdb
```

### Port already in use

```bash
# Use a different port
otree devserver 8001
```

### Import errors

```bash
# Reinstall oTree
pip install --upgrade otree
```

## Contact

For questions or issues, refer to oTree documentation: https://otree.readthedocs.io/
