from otree.api import *
import random


doc = """
Pay-What-You-Want (PWYW) Game: 2 participants are randomly matched as Buyer and Seller.
The Buyer decides whether to buy a product and how much to pay.
The Seller receives payment minus production cost.
"""


class C(BaseConstants):
    NAME_IN_URL = "my_game"
    PLAYERS_PER_GROUP = None  # Will vary each round
    NUM_ROUNDS = 2

    # Roles
    BUYER_ROLE = "Buyer"
    SELLER_ROLE = "Seller"

    # Endowments
    BUYER_ENDOWMENT = 100
    SELLER_ENDOWMENT = 0

    # Treatment conditions
    CONTROL = "control"
    HIGH_SUGGESTED = "high_suggested"
    LOW_SUGGESTED = "low_suggested"

    # Suggested prices
    HIGH_SUGGESTED_PRICE = 70
    LOW_SUGGESTED_PRICE = 30

    # Payment constants
    SHOW_UP_FEE = 100
    CONVERSION_RATE = 500


class Subsession(BaseSubsession):
    pass


def creating_session(subsession: Subsession):
    """
    Initialize the session:
    - Randomize treatment order for EACH participant
    - Re-match players each round (no repeats)
    - Equal buyers and sellers each round
    """
    if subsession.round_number == 1:
        # Define all treatment conditions
        all_treatments = [
            C.CONTROL,
            C.CONTROL,
            C.HIGH_SUGGESTED,
            C.HIGH_SUGGESTED,
            C.LOW_SUGGESTED,
            C.LOW_SUGGESTED,
        ]

        # Each participant gets a randomized order of treatments
        for participant in subsession.session.get_participants():
            shuffled = all_treatments.copy()
            random.shuffle(shuffled)
            participant.vars["treatment_order"] = shuffled

            # Track who they've been paired with
            participant.vars["previous_partners"] = []


    # Get all players for this round
    players = subsession.get_players()
    num_players = len(players)

    # Need even number of players
    if num_players % 2 != 0:
        raise ValueError(f"Need even number of participants. Got {num_players}")

    # Shuffle players for random matching
    random.shuffle(players)

    # Split into two equal groups: buyers and sellers
    half = num_players // 2
    potential_buyers = players[:half]
    potential_sellers = players[half:]

    # Try to create pairs avoiding previous partners
    pairs = []
    used_sellers = set()

    for buyer in potential_buyers:
        previous_partners = buyer.participant.vars.get("previous_partners", [])

        # Find a seller this buyer hasn't been paired with
        for seller in potential_sellers:
            if (
                seller.participant.id_in_session not in previous_partners
                and seller.participant.id_in_session not in used_sellers
            ):
                pairs.append((buyer, seller))
                used_sellers.add(seller.participant.id_in_session)

                # Record the pairing
                buyer.participant.vars["previous_partners"].append(
                    seller.participant.id_in_session
                )
                seller.participant.vars.setdefault("previous_partners", []).append(
                    buyer.participant.id_in_session
                )
                break
        else:
            # If can't avoid repeats (shouldn't happen in 6 rounds with enough players)
            # Just pair with any available seller
            for seller in potential_sellers:
                if seller.participant.id_in_session not in used_sellers:
                    pairs.append((buyer, seller))
                    used_sellers.add(seller.participant.id_in_session)
                    break

    # Create groups from pairs
    group_matrix = [[buyer, seller] for buyer, seller in pairs]
    subsession.set_group_matrix(group_matrix)

    # Assign roles and treatments for each group
    for group in subsession.get_groups():
        players_in_group = group.get_players()
        buyer = players_in_group[0]
        seller = players_in_group[1]

        # Assign roles
        buyer.participant.vars[f"role_round_{subsession.round_number}"] = C.BUYER_ROLE
        seller.participant.vars[f"role_round_{subsession.round_number}"] = C.SELLER_ROLE

        # Get treatment for this buyer (from their randomized order)
        buyer_treatment = buyer.participant.vars["treatment_order"][
            subsession.round_number - 1
        ]
        group.treatment = buyer_treatment

        # Set utility value for buyer (randomized between 40-90)
        group.product_utility = random.randint(40, 90)

        # Set production cost for seller (randomized between 20-60)
        group.production_cost = random.randint(20, 60)


class Group(BaseGroup):
    treatment = models.StringField()
    product_utility = models.IntegerField()
    production_cost = models.IntegerField()
    buyer_decision = models.BooleanField(
        label="Do you want to buy Product A?", choices=[[True, "Yes"], [False, "No"]]
    )
    price_paid = models.IntegerField(
        label="How many tokens out of your 100-token endowment would you like to transfer to the seller?",
        min=0,
        max=C.BUYER_ENDOWMENT,
        blank=True,
    )

    def set_payoffs(self):
        """Calculate payoffs for buyer and seller"""
        buyer = [p for p in self.get_players() if p.role() == C.BUYER_ROLE][0]
        seller = [p for p in self.get_players() if p.role() == C.SELLER_ROLE][0]

        if self.buyer_decision and self.price_paid is not None:
            # Buyer bought the product
            buyer.payoff = C.BUYER_ENDOWMENT - self.price_paid + self.product_utility
            seller.payoff = self.price_paid - self.production_cost
        else:
            # Buyer did not buy: both payoffs are 0
            buyer.payoff = C.BUYER_ENDOWMENT
            seller.payoff = 0


class Player(BasePlayer):
    # Comprehension check answers
    comp_q1 = models.BooleanField(
        label="As a Seller, you have the option to either Accept or Reject the price offering made by the Buyer.",
        choices=[[True, "True"], [False, "False"]],
    )
    comp_q2 = models.BooleanField(
        label="As a Buyer, your utility for the product will remain the same in every round of the experiment.",
        choices=[[True, "True"], [False, "False"]],
    )
    comp_q3 = models.StringField(
        label="3. What happens if the Buyer chooses NOT to buy Product A?",
        choices=[
            ["a", "a) The Buyer keeps their endowment, and the Seller receives 0."],
            ["b", "b) The Buyer pays a small penalty fee."],
            ["c", "c) The Buyer receives the utility of the product anyway."],
            ["d", "d) Both the Buyer and the Seller receive 0 for that round."],
        ],
        widget=widgets.RadioSelect,
    )
    comp_q4 = models.StringField(
        label="4. Is it possible for the Seller to have a negative payoff in a round?",
        choices=[
            ["a", "a) No, the Seller always makes a profit."],
            ["b", "b) No, the lowest the Seller can earn is 0."],
            ["c", "c) Yes, if the Buyer pays an amount lower than the production cost."],
            ["d", "d) Yes, if the Buyer decides not to buy the product."],
        ],
        widget=widgets.RadioSelect,
    )
    comp_q5 = models.BooleanField(
        label="5. The Seller starts every round with an endowment of 100 tokens.",
        choices=[[True, "True"], [False, "False"]],
    )
    comp_q6 = models.StringField(
        label="6. Regarding the information shown on screen, which of the following is correct?",
        choices=[
            ["a", "a) The Buyer can see the Seller's production cost."],
            ["b", "b) The Seller can see the Buyer's utility value."],
            [
                "c",
                "c) The Buyer sees their own utility, and the Seller sees their own production cost.",
            ],
            [
                "d",
                "d) The Buyer sees their own utility value and the Seller’s production cost.",
            ],
        ],
        widget=widgets.RadioSelect,
    )
    comp_q7 = models.BooleanField(
        label="7. If the Buyer decides to buy the product, they receive the product at whatever price they pay.",
        choices=[[True, "True"], [False, "False"]],
    )

    # Questionnaire Part 1
    q_fair_price = models.IntegerField(
        label="My price paid for the product was fair toward the seller.",
        choices=[1, 2, 3, 4, 5, 6, 7],
        widget=widgets.RadioSelectHorizontal,
    )
    q_felt_good = models.IntegerField(
        label="I felt good about the price I paid.",
        choices=[1, 2, 3, 4, 5, 6, 7],
        widget=widgets.RadioSelectHorizontal,
    )
    q_fair_to_seller = models.IntegerField(
        label="I paid a higher price because I wanted to be fair to the seller.",
        choices=[1, 2, 3, 4, 5, 6, 7],
        widget=widgets.RadioSelectHorizontal,
    )
    q_guilty_low_price = models.IntegerField(
        label="Paying a low price would have made me feel guilty.",
        choices=[1, 2, 3, 4, 5, 6, 7],
        widget=widgets.RadioSelectHorizontal,
    )
    q_reward_seller = models.IntegerField(
        label="I paid a higher amount to reward the seller for their generosity.",
        choices=[1, 2, 3, 4, 5, 6, 7],
        widget=widgets.RadioSelectHorizontal,
    )
    q_obligated_fair = models.IntegerField(
        label="I felt obligated to pay a fair price because the seller trusted me.",
        choices=[1, 2, 3, 4, 5, 6, 7],
        widget=widgets.RadioSelectHorizontal,
    )
    q_suggested_influenced = models.IntegerField(
        label="The suggested price influenced the amount I decided to pay.",
        choices=[1, 2, 3, 4, 5, 6, 7],
        widget=widgets.RadioSelectHorizontal,
    )
    q_suggested_guide = models.IntegerField(
        label="I used the suggested price as a guide for what was appropriate to pay.",
        choices=[1, 2, 3, 4, 5, 6, 7],
        widget=widgets.RadioSelectHorizontal,
    )
    q_suggested_quality = models.IntegerField(
        label="I believe the suggested price reflects the true quality of the product.",
        choices=[1, 2, 3, 4, 5, 6, 7],
        widget=widgets.RadioSelectHorizontal,
    )

    # Questionnaire Part 2
    dem_sex = models.StringField(
        label="1. What is your sex?",
        choices=["Male", "Female"],
        widget=widgets.RadioSelect,
    )
    dem_age = models.IntegerField(label="2. How old are you?", min=18, max=100)
    dem_employment = models.StringField(
        label="3. What is your current employment status? (Select all that apply)",
        blank=True,
    )
    dem_income = models.StringField(
        label="4. Please indicate your net monthly income (Your total take-home pay after taxes, or the total money available to you including salary, allowances, and support):",
        choices=[
            "< 5,000,000 VND",
            "5,000,000 - 10,000,000 VND",
            "10,000,000 - 15,000,000 VND",
            "15,000,000 - 20,000,000 VND",
            "> 20,000,000 VND",
        ],
        widget=widgets.RadioSelect,
    )
    dem_familiar = models.StringField(
        label="5. Are you familiar with the pricing strategy that is implemented in the experiment?",
        choices=["Yes", "No"],
        widget=widgets.RadioSelect,
    )
    dem_strategy_name = models.StringField(
        label="(If Yes) What do you usually call this pricing strategy?", blank=True
    )

    # Banking Information
    bank_name = models.StringField(
        label="Bank Name:",
        blank=False,
    )
    account_number = models.StringField(
        label="Account Number:",
        blank=False,
    )
    account_holder_name = models.StringField(
        label="Account Holder Name:",
        blank=False,
    )

    def role(self):
        """Return the role for this player in current round"""
        return self.participant.vars.get(
            f"role_round_{self.round_number}", C.BUYER_ROLE
        )

    def comp_check_failed(self):
        """Check if comprehension questions were answered correctly"""
        return self.comp_q1 is not False or self.comp_q2 is not False


# PAGES
class Introduction(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1


class ComprehensionCheck(Page):
    form_model = "player"
    form_fields = [
        "comp_q1",
        "comp_q2",
        "comp_q3",
        "comp_q4",
        "comp_q5",
        "comp_q6",
        "comp_q7",
    ]

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def error_message(player: Player, values):
        """Validate comprehension check answers and show error with link to instructions if incorrect"""
        solutions = dict(
            comp_q1=True,
            comp_q2=False,
            comp_q3="a",
            comp_q4="c",
            comp_q5=False,
            comp_q6="c",
            comp_q7=True,
        )

        if values != solutions:
            return (
                "One or more answers are incorrect. "
                'Please <a href="#" id="showInstructionsLink">review the instructions</a> and try again.'
                "<script>setTimeout(function(){var l=document.getElementById('showInstructionsLink');if(l){l.onclick=function(e){e.preventDefault();var c=document.getElementById('instructionsCollapse');if(c){c.classList.add('show');c.scrollIntoView({behavior:'smooth'});}}}},0);</script>"
            )


class Decision(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.role() == C.BUYER_ROLE

    form_model = "group"

    @staticmethod
    def get_form_fields(player: Player):
        """Show price field only if buyer chooses to buy"""
        return ["buyer_decision", "price_paid"]

    @staticmethod
    def error_message(player: Player, values):
        """Validate that price is provided if buyer chooses to buy"""
        if values["buyer_decision"] and values["price_paid"] is None:
            return "Please enter how many tokens you want to transfer to the seller."

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        """Set price to 0 if buyer chose not to buy"""
        if not player.group.buyer_decision:
            player.group.price_paid = 0

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            endowment=C.BUYER_ENDOWMENT,
            utility=player.group.product_utility,
            production_cost=player.group.production_cost,
            treatment=player.group.treatment,
            suggested_price=(
                C.HIGH_SUGGESTED_PRICE
                if player.group.treatment == C.HIGH_SUGGESTED
                else C.LOW_SUGGESTED_PRICE
            ),
        )


class SellerInfo(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.role() == C.SELLER_ROLE

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            endowment=C.SELLER_ENDOWMENT, production_cost=player.group.production_cost
        )


class WaitForBuyer(WaitPage):
    @staticmethod
    def is_displayed(player: Player):
        return player.role() == C.SELLER_ROLE


class ResultsWaitPage(WaitPage):
    @staticmethod
    def after_all_players_arrive(group: Group):
        group.set_payoffs()


class Results(Page):
    @staticmethod
    def vars_for_template(player: Player):
        buyer = [p for p in player.group.get_players() if p.role() == C.BUYER_ROLE][0]
        seller = [p for p in player.group.get_players() if p.role() == C.SELLER_ROLE][0]

        # Handle None price_paid when buyer doesn't buy
        price_paid = player.group.field_maybe_none("price_paid") or 0

        return dict(
            is_buyer=player.role() == C.BUYER_ROLE,
            buyer_decision=player.group.buyer_decision,
            price_paid=price_paid,
            utility=player.group.product_utility,
            production_cost=player.group.production_cost,
            buyer_payoff=buyer.payoff,
            seller_payoff=seller.payoff,
            endowment=(
                C.BUYER_ENDOWMENT
                if player.role() == C.BUYER_ROLE
                else C.SELLER_ENDOWMENT
            ),
        )


class Questionnaire(Page):
    form_model = "player"
    form_fields = [
        "q_fair_price",
        "q_felt_good",
        "q_fair_to_seller",
        "q_guilty_low_price",
        "q_reward_seller",
        "q_obligated_fair",
        "q_suggested_influenced",
        "q_suggested_guide",
        "q_suggested_quality",
        "dem_sex",
        "dem_age",
        "dem_employment",
        "dem_income",
        "dem_familiar",
        "dem_strategy_name",
    ]

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS

    @staticmethod
    def vars_for_template(player: Player):
        # Randomize the order of Part 1 questions
        q_field_names = [
            "q_fair_price",
            "q_felt_good",
            "q_fair_to_seller",
            "q_guilty_low_price",
            "q_reward_seller",
            "q_obligated_fair",
            "q_suggested_influenced",
            "q_suggested_guide",
            "q_suggested_quality",
        ]
        random.shuffle(q_field_names)

        labels = {
            "q_fair_price": "My price paid for the product was fair toward the seller.",
            "q_felt_good": "I felt good about the price I paid.",
            "q_fair_to_seller": "I paid a higher price because I wanted to be fair to the seller.",
            "q_guilty_low_price": "Paying a low price would have made me feel guilty.",
            "q_reward_seller": "I paid a higher amount to reward the seller for their generosity.",
            "q_obligated_fair": "I felt obligated to pay a fair price because the seller trusted me.",
            "q_suggested_influenced": "The suggested price influenced the amount I decided to pay.",
            "q_suggested_guide": "I used the suggested price as a guide for what was appropriate to pay.",
            "q_suggested_quality": "I believe the suggested price reflects the true quality of the product.",
        }

        q_fields = []
        for name in q_field_names:
            q_fields.append(dict(name=name, label=labels[name]))

        return dict(q_fields=q_fields)


class ThankYou(Page):
    form_model = "player"
    form_fields = ["bank_name", "account_number", "account_holder_name"]

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS

    @staticmethod
    def vars_for_template(player: Player):
        # Select a random round for payment
        # We use the participant's ID to seed the random choice so it's consistent if they refresh
        # But here we just need to pick one.
        # Let's pick a random round from all rounds played by this participant
        all_rounds = player.in_all_rounds()
        selected_round = random.choice(all_rounds)

        payoff_selected_round = selected_round.payoff or 0

        # Ensure payoff is not negative for total calculation if that's the rule,
        # but usually negative payoff is deducted from show-up fee.
        # The prompt implies: "Including Show-up Fee plus Payoff from Selected Round"

        total_tokens = C.SHOW_UP_FEE + payoff_selected_round

        # Ensure total payment is not negative
        if total_tokens < 0:
            total_tokens = 0

        total_payment_vnd = total_tokens * C.CONVERSION_RATE

        return dict(
            selected_round_number=selected_round.round_number,
            payoff_selected_round=payoff_selected_round,
            show_up_fee=C.SHOW_UP_FEE,
            total_tokens=total_tokens,
            total_payment_vnd=f"{total_payment_vnd:,.0f}",
        )


page_sequence = [
    Introduction,
    ComprehensionCheck,
    Decision,
    SellerInfo,
    WaitForBuyer,
    ResultsWaitPage,
    Results,
    Questionnaire,
    ThankYou,
]
