# Pay-What-You-Want (PWYW) Experiment - oTree Implementation

## Section 1: Game Overview

### Introduction

This is an experimental economics study implementing a Pay-What-You-Want (PWYW) pricing mechanism. Two participants are randomly matched in each round to play as Buyer and Seller, trading a hypothetical product where the buyer determines the price.

### Game Structure

**Duration**: 6 rounds total
**Players per round**: 2 (one Buyer, one Seller)
**Role assignment**: Roles swap between rounds so each participant experiences both perspectives
**No repeated pairings**: Participants are matched with different partners across rounds

### Player Roles

#### Buyer

- **Starting endowment**: 100 tokens
- **Product utility**: Randomly assigned each round (40-90 tokens) - the value the product provides
- **Decision**: Choose whether to buy the product, and if yes, how much to pay (0-100 tokens)
- **Payoff calculation**:
  - If bought: 100 - amount_paid + product_utility
  - If not bought: 0

#### Seller

- **Starting endowment**: 0 tokens
- **Production cost**: Randomly assigned each round (20-60 tokens)
- **No active decisions**: Waits for buyer's choice
- **Payoff calculation**:
  - If buyer bought: amount_paid - production_cost
  - If buyer didn't buy: 0

### Treatment Conditions

The experiment includes three pricing conditions, experienced twice each across the 6 rounds in randomized order:

1. **Control** (2 rounds): No suggested price shown
2. **High Suggested Price** (2 rounds): Suggested price of 70 tokens displayed
3. **Low Suggested Price** (2 rounds): Suggested price of 30 tokens displayed

Note: Suggested prices are advisory only; buyers can choose any amount.

### Participant Experience Flow

**Round 1 Only:**

1. Introduction page - Complete instructions for both roles
2. Comprehension check - Two questions to verify understanding
   - Must answer correctly to proceed
   - Can review instructions via collapsible section if needed

**Every Round:** 3. **Buyer**: Decision page (choose to buy and set price)
**Seller**: Information page (see role and production cost) → Waiting page 4. Results page - Shows transaction details and payoff calculation for your role

### Information Structure

- **Complete information**: Both buyer and seller know the product utility and production cost
- **Transparency**: All payoff formulas are explained upfront
- **Fair compensation**: One random round will be selected at the end for actual payment (100 tokens = 50,000 VND)

---

## Section 2: Technical Documentation

### Part A: Running and Testing

#### Installation and Setup

1. **Install oTree** (if not already installed):

```powershell
pip install otree
```

2. **Navigate to the project directory**:

```powershell
cd "your_path_here\pwyw\myexperiment"
```

3. **Initialize the database** (first time only, or after model changes):

```powershell
otree resetdb
```

4. **Start the development server**:

```powershell
otree devserver
```

5. **Access the experiment**:
   - Open browser to: http://localhost:8000
   - Click "Demo" next to "Pay-What-You-Want Game"
   - Open 2 browser windows (or use incognito mode) for testing

#### Testing Checklist

Test the following with 2 demo participants:

- [ ] Introduction displays both Buyer and Seller role descriptions
- [ ] Comprehension check blocks wrong answers and allows reviewing instructions
- [ ] Buyer sees correct product utility and can make decisions
- [ ] Price input field only appears when buyer selects "Yes"
- [ ] Seller sees their role information page with a Next button
- [ ] Seller sees waiting screen after clicking Next
- [ ] Results page shows correct buyer decision and amount paid
- [ ] Results page displays payoff calculation for the player's role only
- [ ] Payoff calculations are accurate
- [ ] Roles swap in subsequent rounds
- [ ] Treatment conditions vary across rounds
- [ ] All 6 rounds complete successfully
- [ ] Data exports correctly from admin panel

#### Data Export

After running a session:

1. Go to admin panel: http://localhost:8000
2. Navigate to "Data" tab
3. Select your session
4. Download as Excel or CSV

**Key variables in the dataset:**

- `subsession.round_number` - Round (1-6)
- `player.role` - Buyer or Seller
- `group.treatment` - control, high_suggested, or low_suggested
- `group.product_utility` - Utility value shown to buyer
- `group.production_cost` - Cost shown to seller
- `group.buyer_decision` - True (bought) or False (didn't buy)
- `group.price_paid` - Amount transferred (0-100)
- `player.payoff` - Calculated payoff for that round

#### Production Deployment

For running actual experiment sessions:

```powershell
# Set admin password
set OTREE_ADMIN_PASSWORD=YourSecurePassword

# Enable production mode
set OTREE_PRODUCTION=1

# Run production server (port 80 for standard web access)
otree prodserver 80
```

---

### Part B: Customization and Parameters

#### File Structure

```
myexperiment/
├── my_game/
│   ├── __init__.py              # Main game logic
│   ├── Introduction.html        # Instructions (round 1 only)
│   ├── ComprehensionCheck.html  # Comprehension test (round 1 only)
│   ├── Decision.html            # Buyer decision page
│   ├── SellerInfo.html          # Seller information page
│   └── Results.html             # Results display
├── settings.py                  # oTree configuration
└── requirements.txt             # Python dependencies
```

#### Common Customizations

##### 0. Change Number of Demo Participants

**File**: `settings.py`
**Location**: Line 6

```python
num_demo_participants=6,  # Current setting
```

Change to any **even number** (must be even for Buyer-Seller pairing):

```python
num_demo_participants=2,   # For 2 players (1 pair)
num_demo_participants=4,   # For 4 players (2 pairs)
num_demo_participants=6,   # For 6 players (3 pairs)
num_demo_participants=8,   # For 8 players (4 pairs)
```

This controls how many participant links appear in the demo mode.

---

All other modifications are made in `my_game/__init__.py`:

##### 1. Change Number of Rounds

**Location**: Line 15

```python
NUM_ROUNDS = 6  # Change to desired number
```

Note: If changing rounds, also update treatment distribution in `creating_session()` function (around line 50).

##### 2. Adjust Endowments

**Location**: Lines 22-23

```python
BUYER_ENDOWMENT = 100   # Buyer starting tokens
SELLER_ENDOWMENT = 0    # Seller starting tokens
```

##### 3. Modify Suggested Prices

**Location**: Lines 31-32

```python
HIGH_SUGGESTED_PRICE = 70   # High suggested price
LOW_SUGGESTED_PRICE = 30    # Low suggested price
```

##### 4. Change Product Utility Range

**Location**: Line 146 in `creating_session()` function

```python
group.product_utility = random.randint(40, 90)  # Min 40, Max 90
```

Example: For utility between 50-100:

```python
group.product_utility = random.randint(50, 100)
```

##### 5. Change Production Cost Range

**Location**: Line 149 in `creating_session()` function

```python
group.production_cost = random.randint(20, 60)  # Min 20, Max 60
```

Example: For cost between 10-50:

```python
group.production_cost = random.randint(10, 50)
```

##### 6. Modify Payoff Logic

**Location**: Lines 168-179 in `set_payoffs()` method of the `Group` class

Current logic:

- If buyer bought: Buyer gets (100 - price + utility), Seller gets (price - cost)
- If buyer didn't buy: Both get 0

To change (e.g., buyer keeps endowment if not buying):

```python
def set_payoffs(self):
    buyer = [p for p in self.get_players() if p.role() == C.BUYER_ROLE][0]
    seller = [p for p in self.get_players() if p.role() == C.SELLER_ROLE][0]

    if self.buyer_decision and self.price_paid is not None:
        buyer.payoff = C.BUYER_ENDOWMENT - self.price_paid + self.product_utility
        seller.payoff = self.price_paid - self.production_cost
    else:
        # Modified: buyer keeps endowment if not buying
        buyer.payoff = C.BUYER_ENDOWMENT
        seller.payoff = 0
```

##### 7. Adjust Treatment Distribution

**Location**: Lines 50-57 in `creating_session()` function

Current distribution (2 rounds each):

```python
all_treatments = [
    C.CONTROL,
    C.CONTROL,
    C.HIGH_SUGGESTED,
    C.HIGH_SUGGESTED,
    C.LOW_SUGGESTED,
    C.LOW_SUGGESTED,
]
```

Example: For 3 control rounds, 2 high, 1 low (6 rounds total):

```python
all_treatments = [
    C.CONTROL,
    C.CONTROL,
    C.CONTROL,
    C.HIGH_SUGGESTED,
    C.HIGH_SUGGESTED,
    C.LOW_SUGGESTED,
]
```

##### 8. Add New Treatment Condition

1. Define constant in the `C` class (around line 27):

```python
MEDIUM_SUGGESTED = "medium_suggested"
MEDIUM_SUGGESTED_PRICE = 50
```

2. Add to treatment list in `creating_session()`:

```python
all_treatments = [
    C.CONTROL,
    C.HIGH_SUGGESTED,
    C.MEDIUM_SUGGESTED,
    C.LOW_SUGGESTED,
    C.CONTROL,
    C.MEDIUM_SUGGESTED,
]
```

3. Update the `Decision` page logic (around line 269):

```python
suggested_price=(
    C.HIGH_SUGGESTED_PRICE if player.group.treatment == C.HIGH_SUGGESTED
    else C.MEDIUM_SUGGESTED_PRICE if player.group.treatment == C.MEDIUM_SUGGESTED
    else C.LOW_SUGGESTED_PRICE
)
```

##### 9. Modify Comprehension Questions

**Location**: Lines 186-196 in the `Player` class

To change questions or answers:

```python
comp_q1 = models.BooleanField(
    label="Your new question text here.",
    choices=[[True, "True"], [False, "False"]],
)
```

Then update validation logic in `ComprehensionCheck` page (around line 228):

```python
def error_message(player: Player, values):
    if values["comp_q1"] is not True or values["comp_q2"] is not False:  # Adjust expected answers
        return "Error message..."
```

#### Advanced Customizations

##### Change Page Sequence

**Location**: Lines 302-310

```python
page_sequence = [
    Introduction,
    ComprehensionCheck,
    Decision,
    SellerInfo,
    WaitForBuyer,
    ResultsWaitPage,
    Results,
]
```

To add/remove/reorder pages, modify this list. Each page must have a corresponding class defined above.

##### Modify Role Assignment Logic

**Location**: Lines 122-142 in `creating_session()` function

Current: Roles swap each round with no repeated pairings.

To keep same roles throughout:

```python
# In round 1, assign roles
if subsession.round_number == 1:
    for i, player in enumerate(players):
        role = C.BUYER_ROLE if i < half else C.SELLER_ROLE
        player.participant.vars["fixed_role"] = role

# All rounds use the fixed role
def role(self):
    return self.participant.vars.get("fixed_role", C.BUYER_ROLE)
```

#### Troubleshooting

**Database Issues**:

```powershell
otree resetdb
```

**Port Already in Use**:

```powershell
otree devserver 8001  # Use different port
```

**Changes Not Appearing**:

- Restart the oTree server
- Hard refresh browser (Ctrl+F5)
- Clear browser cache

**Import Errors**:

```powershell
pip install --upgrade otree
```

#### Technology Stack

- **Framework**: oTree 5.x
- **Language**: Python 3.7+
- **Frontend**: Bootstrap 4 (built into oTree)
- **Database**: SQLite (development) / PostgreSQL (production recommended)
- **Features**: Dynamic forms with JavaScript, responsive design

---

## Additional Resources

- **oTree Documentation**: https://otree.readthedocs.io/
- **oTree Forum**: https://groups.google.com/g/otree
- **Bootstrap Documentation**: https://getbootstrap.com/docs/4.6/

For questions specific to this implementation, refer to the inline comments in `my_game/__init__.py`.
