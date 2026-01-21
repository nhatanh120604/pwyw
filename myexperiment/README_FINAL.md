# Pay-What-You-Want (PWYW) Experiment - oTree Implementation

## Section 1: Game Overview

### Introduction

This is an experimental economics study implementing a Pay-What-You-Want (PWYW) pricing mechanism. Two participants are randomly matched in each round to play as Buyer and Seller, trading a hypothetical product where the buyer determines the price.

### Game Structure

**Duration**: 2 rounds total (configurable)
**Players per round**: 2 (one Buyer, one Seller)
**Role assignment**: Roles swap between rounds so each participant experiences both perspectives
**No repeated pairings**: Participants are matched with different partners across rounds

### Player Roles

#### Buyer

- **Starting endowment**: 100 tokens
- **Product utility**: Randomly assigned each round (15-45 tokens) - the value the product provides
- **Decision**: Choose whether to buy the product, and if yes, how much to pay (0-100 tokens)
- **Payoff calculation**:
  - If bought: 100 - amount_paid + product_utility
  - If not bought: 100 (Buyer keeps endowment)

#### Seller

- **Starting endowment**: 0 tokens
- **Production cost**: Randomly assigned each round (1-30 tokens)
- **No active decisions**: Waits for buyer's choice
- **Payoff calculation**:
  - If buyer bought: amount_paid - production_cost
  - If buyer didn't buy: 0

### Treatment Conditions

The experiment includes three pricing conditions, randomized for each participant:

1. **Control**: No suggested price shown
2. **High Suggested Price**: Suggested price of 70 tokens displayed
3. **Low Suggested Price**: Suggested price of 30 tokens displayed

Note: Suggested prices are advisory only; buyers can choose any amount.

### Participant Experience Flow

**Round 1 Only:**

1. **Consent Form**: In-depth informed consent with mandatory checkboxes.
2. **Introduction**: Complete instructions for both roles.
   - Includes detailed payoff explanations with bullet points for clarity.
   - Uses neutral styling with black text for readability.
2. **Comprehension Check**: Seven questions to verify understanding.
   - Includes full instructions in a collapsible section.
   - Must answer correctly to proceed.

**Every Round:**

3. **Buyer**: Decision page (choose to buy and set price).
4. **Seller**: Information page (see role and production cost) → Waiting page.
5. **Results**: Shows transaction details and payoff calculation for your role.

**Final Round Only:**

6. **Questionnaire**:
   - **Part 1**: Decision reflection (Likert scale questions).
   - **Part 2**: Background information (Demographics, Employment, Income).
   - **Strategy Check**: Conditional question asking for strategy name if familiar.
7. **Thank You**:
   - Displays final payment calculation (Show-up fee + Payoff from one random round).
   - Collects banking information for payment transfer.

### Information Structure

- **Complete information**: Both buyer and seller know the product utility and production cost
- **Transparency**: All payoff formulas are explained upfront
- **Fair compensation**: One random round will be selected at the end for actual payment (100 tokens = 20,000 VND) + Show-up fee (20,000 VND).

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

#### Option B: Running with Docker (Terminal Only)

You can run this project on any operating system (Windows, macOS, Linux) using just the terminal.

**1. Install Docker (via Terminal)**

If you don't have Docker installed, you can install it using your system's package manager:

- **Windows** (PowerShell):
  ```powershell
  winget install Docker.DockerDesktop
  ```
- **macOS** (Homebrew):
  ```bash
  brew install --cask docker
  ```
- **Linux** (Ubuntu/Debian):
  ```bash
  sudo apt-get update
  sudo apt-get install docker.io
  ```

*Note: After installation, ensure Docker is running.*

**2. Run the Project**

Open your terminal in the project folder and run these two commands:

1. **Build the image** (only needed once):
   ```bash
   docker build -t pwyw-experiment .
   ```

2. **Run the container**:
   ```bash
   docker run -p 8000:8000 pwyw-experiment
   ```

3. **Access**: Open http://localhost:8000 in your browser.

#### Testing Checklist

Test the following with 2 demo participants:

- [ ] Introduction displays both Buyer and Seller role descriptions correctly (bullet points, black text).
- [ ] Comprehension check blocks wrong answers and allows reviewing instructions.
- [ ] Buyer sees correct product utility and can make decisions.
- [ ] Price input field only appears when buyer selects "Yes".
- [ ] Seller sees their role information page with a Next button.
- [ ] Seller sees waiting screen after clicking Next.
- [ ] Results page shows correct buyer decision and amount paid.
- [ ] Payoff calculations are accurate (especially "Buyer keeps endowment" if not buying).
- [ ] Roles swap in subsequent rounds.
- [ ] Questionnaire appears after the final round.
- [ ] Questionnaire conditional logic works (Strategy Name field appears only if "Yes" is selected for Familiarity).
- [ ] Thank You page displays correct total payment (Show-up fee + Selected round payoff).
- [ ] Banking information form works.
- [ ] Data exports correctly from admin panel.

#### Data Export

After running a session:

1. Go to admin panel: http://localhost:8000
2. Navigate to "Data" tab
3. Select your session
4. Download as Excel or CSV

**Key variables in the dataset:**

- `subsession.round_number` - Round (1-2)
- `player.role` - Buyer or Seller
- `group.treatment` - control, high_suggested, or low_suggested
- `group.buyer_decision` - True (bought) or False (didn't buy)
- `group.price_paid` - Amount transferred (0-100)
- `player.payoff` - Calculated payoff for that round
- `player.q_fair_price`...`player.q_suggested_quality` - Questionnaire Part 1 responses
- `player.dem_sex`...`player.dem_strategy_name` - Questionnaire Part 2 responses
- `player.bank_name`...`player.account_holder_name` - Banking details

#### Production Deployment

For running actual experiment sessions:

```bash
# Set admin password (Linux/macOS use export, Windows uses set)
export OTREE_ADMIN_PASSWORD=YourSecurePassword

# Enable production mode
export OTREE_PRODUCTION=1

# Run production server on port 8000 (Recommended for testing, no root required)
otree prodserver 8000

# OR run on port 80 (Standard web port, requires sudo/root permissions)
# sudo -E env "PATH=$PATH" otree prodserver 80
```chec

---

### Part B: Customization and Parameters

#### File Structure

```
myexperiment/
├── my_game/
│   ├── __init__.py              # Main game logic (Models, Pages, Payoff logic)
│   ├── ConsentForm.html         # Informed consent page (added)
│   ├── Introduction.html        # Instructions (round 1 only)
│   ├── ComprehensionCheck.html  # Comprehension test (round 1 only)
│   ├── Decision.html            # Buyer decision page
│   ├── SellerInfo.html          # Seller information page
│   ├── Results.html             # Results display
│   ├── Questionnaire.html       # Post-experiment survey
│   └── ThankYou.html            # Final payment and banking info
├── settings.py                  # oTree configuration
└── requirements.txt             # Python dependencies
```

#### Common Customizations

All modifications are made in `my_game/__init__.py`:

##### 1. Change Number of Rounds

**Location**: Line 15

```python
NUM_ROUNDS = 2  # Change to desired number
```

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

##### 4. Modify Payoff Logic

**Location**: `set_payoffs()` method of the `Group` class

Current logic:
- If buyer bought: Buyer gets (100 - price + utility), Seller gets (price - cost)
- If buyer didn't buy: Buyer gets 100 (keeps endowment), Seller gets 0

##### 5. Modify Questionnaire Labels

**Location**: `vars_for_template` method in `Questionnaire` class

Labels for the Likert scale questions are defined in the `labels` dictionary within this method to ensure they render correctly.

#### Technology Stack

- **Framework**: oTree 5.x
- **Language**: Python 3.7+
- **Frontend**: Bootstrap 4 (built into oTree), Custom HTML/CSS for specific formatting
- **Database**: SQLite (development) / PostgreSQL (production recommended)

