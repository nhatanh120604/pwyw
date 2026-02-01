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
    NUM_ROUNDS = 18

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
    # Dynamic now, calculated in creating_session

    # Payment constants
    SHOW_UP_FEE = 100
    CONVERSION_RATE = 200


class Subsession(BaseSubsession):
    pass


def creating_session(subsession: Subsession):
    """
    Initialize the session:
    - Randomize treatment order for EACH participant
    - Re-match players each round (no repeats)
    - Equal buyers and sellers each round
    """
    # --- 1. SESSION LEVEL SETUP (Round 1 only) ---
    if subsession.round_number == 1:
        # A. Treatment Randomization (Existing)
        # Define all treatment conditions (6 rounds x 3 repeats = 18 rounds)
        # Each block of 6 has: 2 Control, 2 Low, 2 High
        one_block = [C.CONTROL] * 2 + [C.HIGH_SUGGESTED] * 2 + [C.LOW_SUGGESTED] * 2
        all_treatments = one_block * 3

        # EACH participant gets a randomized order of treatments
        # Also assign Rule Groups (A and B) for Role Balancing here
        participants = subsession.session.get_participants()
        random.shuffle(participants) # Shuffle to randomize who gets into Group A vs B

        mid_point = len(participants) // 2

        for i, p in enumerate(participants):
            # 1. Treatment Order
            shuffled_treatments = all_treatments.copy()
            random.shuffle(shuffled_treatments)
            p.vars["treatment_order"] = shuffled_treatments

            # 2. Role Group Assignment (Strict Balance)
            # First half is Group A, Second half is Group B
            if i < mid_point:
                p.vars['role_group'] = 'A'
            else:
                p.vars['role_group'] = 'B'

        # B. Generate Role Schedule for the Session
        # 0 = Group A is Buyer (Group B is Seller)
        # 1 = Group B is Buyer (Group A is Seller)
        # Constraint: In every 6 rounds, exactly 3 are '0' and 3 are '1'
        role_schedule = []
        for _ in range(3): # 3 Blocks
            # Create balanced block [0,0,0, 1,1,1]
            block = [0, 0, 0, 1, 1, 1]
            random.shuffle(block)
            role_schedule.extend(block)

        subsession.session.vars['role_schedule'] = role_schedule

        # C. Select Common Paying Round
        # Select ONE round (1 to 18) that determines payment for EVERYONE
        paying_round = random.randint(1, C.NUM_ROUNDS)
        subsession.session.vars['paying_round'] = paying_round

    # --- 2. MATCHING LOGIC (Every Round) ---

    # Who is the Buyer this round? (Group A or Group B)
    # round_number is 1-indexed, so subtract 1
    current_round_config = subsession.session.vars['role_schedule'][subsession.round_number - 1]
    is_group_A_buyer = (current_round_config == 0)

    # Separate players into Buyers and Sellers list
    buyers = []
    sellers = []

    for p in subsession.get_players():
        # Get their assigned group
        p_group = p.participant.vars['role_group']

        if is_group_A_buyer:
            if p_group == 'A':
                buyers.append(p)
            else:
                sellers.append(p)
        else: # Group B is Buyer
            if p_group == 'B':
                buyers.append(p)
            else:
                sellers.append(p)

    # Basic validation
    if len(buyers) != len(sellers):
        raise ValueError("Error: Uneven number of buyers and sellers. Ensure even number of participants.")

    # Randomize the matching within the groups
    random.shuffle(buyers)
    random.shuffle(sellers)

    # Pair them up
    group_matrix = []
    for b, s in zip(buyers, sellers):
        group_matrix.append([b, s])

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

        # Set utility value for buyer (randomized between 15-45)
        group.product_utility = random.randint(15, 45)

        # Set production cost for seller (randomized between 1-30)
        group.production_cost = random.randint(1, 30)

        # Calculate Suggested Price
        if group.treatment == C.CONTROL:
            group.suggested_price = None
        elif group.treatment == C.LOW_SUGGESTED:
            group.suggested_price = group.production_cost
        elif group.treatment == C.HIGH_SUGGESTED:
            group.suggested_price = round(1.5 * group.production_cost)


class Group(BaseGroup):
    treatment = models.StringField()
    product_utility = models.IntegerField()
    production_cost = models.IntegerField()
    suggested_price = models.IntegerField(blank=True)
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

        # Calculate potential payoffs logic
        if self.buyer_decision and self.price_paid is not None:
            # Buyer bought the product
            buyer_val = C.BUYER_ENDOWMENT - self.price_paid + self.product_utility
            seller_val = self.price_paid - self.production_cost
        else:
            # Buyer did not buy
            buyer_val = C.BUYER_ENDOWMENT
            seller_val = 0

        # Store potential payoff for data analysis
        buyer.potential_payoff = buyer_val
        seller.potential_payoff = seller_val

        # ONLY set the official player.payoff if this is the chosen paying round
        # This ensures the "Total Payments" in admin interface is correct strategy-wise
        paying_round = self.session.vars.get('paying_round')

        if self.round_number == paying_round:
            buyer.payoff = buyer_val
            seller.payoff = seller_val
        else:
            buyer.payoff = 0
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
        label="What happens if the Buyer chooses NOT to buy Product A?",
        choices=[
            ["a", "The Buyer keeps their endowment, and the Seller receives 0."],
            ["b", "The Buyer pays a small penalty fee."],
            ["c", "The Buyer receives the utility of the product anyway."],
            ["d", "Both the Buyer and the Seller receive 0 for that round."],
        ],
        widget=widgets.RadioSelect,
    )
    comp_q4 = models.StringField(
        label="Is it possible for the Seller to have a negative payoff in a round?",
        choices=[
            ["a", "No, the Seller always makes a profit."],
            ["b", "No, the lowest the Seller can earn is 0."],
            ["c", "Yes, if the Buyer pays an amount lower than the production cost."],
            ["d", "Yes, if the Buyer decides not to buy the product."],
        ],
        widget=widgets.RadioSelect,
    )
    comp_q5 = models.BooleanField(
        label="The Seller starts every round with an endowment of 100 tokens.",
        choices=[[True, "True"], [False, "False"]],
    )
    comp_q6 = models.StringField(
        label="Regarding the information shown on screen, which of the following is correct?",
        choices=[
            ["a", "The Buyer can see the Seller's production cost."],
            ["b", "The Seller can see the Buyer's utility value."],
            [
                "c",
                "The Buyer sees their own utility, and the Seller sees their own production cost.",
            ],
            [
                "d",
                "The Buyer sees their own utility value and the Seller’s production cost.",
            ],
        ],
        widget=widgets.RadioSelect,
    )
    comp_q7 = models.BooleanField(
        label="If the Buyer decides to buy the product, they receive the product at whatever price they pay.",
        choices=[[True, "True"], [False, "False"]],
    )

    # For data analysis: store the payoff this player WOULD have gotten in this round
    potential_payoff = models.CurrencyField()

    # Consent Form Fields
    consent_1 = models.BooleanField(
        label="1. I have read and understood the Purpose of the Research.",
        widget=widgets.CheckboxInput,
    )
    consent_2 = models.BooleanField(
        label="2. I have read and understood what I will be asked to do in the research.",
        widget=widgets.CheckboxInput,
    )
    consent_3 = models.BooleanField(
        label="3. I have read and understood the potential Benefits to me.",
        widget=widgets.CheckboxInput,
    )
    consent_4 = models.BooleanField(
        label="4. I have read and understood the potential Risks and Discomforts.",
        widget=widgets.CheckboxInput,
    )
    consent_5 = models.BooleanField(
        label="5. I have read and understood that my participation is completely Voluntary.",
        widget=widgets.CheckboxInput,
    )
    consent_6 = models.BooleanField(
        label="6. I have read and understood that my Withdrawal from the Study will not have any repercussion.",
        widget=widgets.CheckboxInput,
    )
    consent_7 = models.BooleanField(
        label="7. I have read and understood the Data Collection method(s).",
        widget=widgets.CheckboxInput,
    )
    consent_8 = models.BooleanField(
        label="8. I have read and understood about the steps taken to ensure Confidentiality.",
        widget=widgets.CheckboxInput,
    )
    consent_9 = models.BooleanField(
        label="9. I have read and understood that I can ask the research team to answer any Questions and concerns about the research and my participation.",
        widget=widgets.CheckboxInput,
    )
    consent_10 = models.BooleanField(
        label="10. I have read and understood that the research study has been approved by Fulbright University Vietnam’s Institutional Review Board (IRB).",
        widget=widgets.CheckboxInput,
    )
    consent_final = models.BooleanField(
        label="I have read and fully understood the contents of this form and had time to ask my questions, and hereby give my informed consent to the researchers and affirm my willingness to participate in the research described above in this form.",
        widget=widgets.CheckboxInput,
    )

    # Questionnaire Part 1
    q_fair_price = models.IntegerField(
        label="My price paid for the product was fair toward the seller.",
        choices=[
            [1, "1 - Strongly Disagree"],
            [2, "2"],
            [3, "3"],
            [4, "4"],
            [5, "5"],
            [6, "6"],
            [7, "7 - Strongly Agree"],
        ],
        widget=widgets.RadioSelectHorizontal,
    )
    q_felt_good = models.IntegerField(
        label="I felt good about the price I paid.",
        choices=[
            [1, "1 - Strongly Disagree"],
            [2, "2"],
            [3, "3"],
            [4, "4"],
            [5, "5"],
            [6, "6"],
            [7, "7 - Strongly Agree"],
        ],
        widget=widgets.RadioSelectHorizontal,
    )
    q_fair_to_seller = models.IntegerField(
        label="I paid a higher price because I wanted to be fair to the seller.",
        choices=[
            [1, "1 - Strongly Disagree"],
            [2, "2"],
            [3, "3"],
            [4, "4"],
            [5, "5"],
            [6, "6"],
            [7, "7 - Strongly Agree"],
        ],
        widget=widgets.RadioSelectHorizontal,
    )
    q_guilty_low_price = models.IntegerField(
        label="Paying a low price would have made me feel guilty.",
        choices=[
            [1, "1 - Strongly Disagree"],
            [2, "2"],
            [3, "3"],
            [4, "4"],
            [5, "5"],
            [6, "6"],
            [7, "7 - Strongly Agree"],
        ],
        widget=widgets.RadioSelectHorizontal,
    )
    q_reward_seller = models.IntegerField(
        label="I paid a higher amount to reward the seller for their generosity.",
        choices=[
            [1, "1 - Strongly Disagree"],
            [2, "2"],
            [3, "3"],
            [4, "4"],
            [5, "5"],
            [6, "6"],
            [7, "7 - Strongly Agree"],
        ],
        widget=widgets.RadioSelectHorizontal,
    )
    q_obligated_fair = models.IntegerField(
        label="I felt obligated to pay a fair price because the seller trusted me.",
        choices=[
            [1, "1 - Strongly Disagree"],
            [2, "2"],
            [3, "3"],
            [4, "4"],
            [5, "5"],
            [6, "6"],
            [7, "7 - Strongly Agree"],
        ],
        widget=widgets.RadioSelectHorizontal,
    )
    q_suggested_influenced = models.IntegerField(
        label="The suggested price influenced the amount I decided to pay.",
        choices=[
            [1, "1 - Strongly Disagree"],
            [2, "2"],
            [3, "3"],
            [4, "4"],
            [5, "5"],
            [6, "6"],
            [7, "7 - Strongly Agree"],
        ],
        widget=widgets.RadioSelectHorizontal,
    )
    q_suggested_guide = models.IntegerField(
        label="I used the suggested price as a guide for what was appropriate to pay.",
        choices=[
            [1, "1 - Strongly Disagree"],
            [2, "2"],
            [3, "3"],
            [4, "4"],
            [5, "5"],
            [6, "6"],
            [7, "7 - Strongly Agree"],
        ],
        widget=widgets.RadioSelectHorizontal,
    )
    q_suggested_quality = models.IntegerField(
        label="I believe the suggested price reflects the true quality of the product.",
        choices=[
            [1, "1 - Strongly Disagree"],
            [2, "2"],
            [3, "3"],
            [4, "4"],
            [5, "5"],
            [6, "6"],
            [7, "7 - Strongly Agree"],
        ],
        widget=widgets.RadioSelectHorizontal,
    )

    # Questionnaire Part 2
    dem_sex = models.StringField(
        label="1. What is your sex?",
        choices=["Male", "Female", "Prefer not to say"],
        widget=widgets.RadioSelect,
    )
    dem_age = models.StringField(
        label="2. How old are you?",
        choices=[str(i) for i in range(18, 31)] + ["30+", "Prefer not to say"],
    )
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
            "Prefer not to say",
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


class ConsentForm(Page):
    form_model = "player"
    form_fields = [
        "consent_1",
        "consent_2",
        "consent_3",
        "consent_4",
        "consent_5",
        "consent_6",
        "consent_7",
        "consent_8",
        "consent_9",
        "consent_10",
        "consent_final",
    ]

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player):
        import datetime
        return dict(date_today=datetime.date.today().strftime("%Y-%m-%d"))


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
            comp_q1=False,
            comp_q2=False,
            comp_q3="a",
            comp_q4="c",
            comp_q5=False,
            comp_q6="c",
            comp_q7=True,
        )

        num_wrong = 0
        for key, answer in solutions.items():
            if values[key] != answer:
                num_wrong += 1

        if num_wrong > 0:
            return (
                f"You have {num_wrong} incorrect answer(s). "
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
            suggested_price=player.group.field_maybe_none("suggested_price"),
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
            buyer_payoff=buyer.potential_payoff,
            seller_payoff=seller.potential_payoff,
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
    # form_fields = ["bank_name", "account_number", "account_holder_name"]

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS

    @staticmethod
    def vars_for_template(player: Player):
        # Retrieve the common paying round selected in creating_session
        selected_round_number = player.session.vars['paying_round']

        # Get the player object for that specific round
        selected_round = player.in_round(selected_round_number)

        payoff_selected_round = selected_round.payoff or 0

        # Ensure payoff is not negative for total calculation if that's the rule,
        # but usually negative payoff is deducted from show-up fee.
        # The prompt implies: "Including Show-up Fee plus Payoff from Selected Round"

        total_tokens = C.SHOW_UP_FEE + payoff_selected_round

        # Ensure total payment is not negative
        if total_tokens < 0:
            total_tokens = 0

        total_payment_vnd = total_tokens * C.CONVERSION_RATE

        # Fetch history for the table
        history = []
        for p in player.in_all_rounds():
            history.append(
                dict(
                    round_number=p.round_number,
                    role=p.role(),
                    payoff=int(p.potential_payoff),
                    is_selected=(p.round_number == selected_round_number),
                )
            )

        return dict(
            participant_id=player.participant.code,
            selected_round_number=selected_round.round_number,
            payoff_selected_round=payoff_selected_round,
            show_up_fee=C.SHOW_UP_FEE,
            show_up_fee_vnd=f"{C.SHOW_UP_FEE * C.CONVERSION_RATE:,.0f}",
            earnings_from_round_vnd=f"{payoff_selected_round * C.CONVERSION_RATE:,.0f}",
            total_tokens=total_tokens,
            total_payment_vnd=f"{total_payment_vnd:,.0f}",
            history=history,
        )


page_sequence = [
    ConsentForm,
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
