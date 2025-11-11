from os import environ

SESSION_CONFIGS = [
    dict(
        name="pwyw_game",
        display_name="Pay-What-You-Want Game",
        num_demo_participants=6,  # Changed to 6 for proper matching
        app_sequence=["my_game"],
        doc="""
        Pay-What-You-Want pricing experiment with 6+ players.
        Players are randomly matched each round (no repeats).
        Each participant sees treatments in randomized order.
        """,
    ),
]


# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00, participation_fee=0.00, doc=""
)

PARTICIPANT_FIELDS = ["initial_role"]
SESSION_FIELDS = ["treatment_sequence"]

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = "en"

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = "USD"
USE_POINTS = True

ADMIN_USERNAME = "admin"
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get("OTREE_ADMIN_PASSWORD")

DEMO_PAGE_INTRO_HTML = """ """

SECRET_KEY = "4468655963094"
