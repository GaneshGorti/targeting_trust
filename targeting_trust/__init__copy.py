from otree.api import *
import random
import string

doc = """
Targeting x Trust experiment (2x2 between groups): 
trust_condition (count vs estimate) x targeting_condition (self vs pre).
"""

class C(BaseConstants):
    NAME_IN_URL = 'targeting_trust'
    PLAYERS_PER_GROUP = 5   # 4 citizens + 1 admin
    NUM_ROUNDS = 1
    TRIANGLE_IMAGE = 'triangles_squares.png'  # put this in _static
    TRUE_TRIANGLES = 47
    TRUE_SQUARES = 31
    TRUST_MULTIPLIER = 3

class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    trust_condition = models.StringField(choices=['count', 'estimate'])
    targeting_condition = models.StringField(choices=['self', 'pre'])

    squares_reported = models.IntegerField(initial=0)
    total_tax = models.CurrencyField(initial=0)

class Player(BasePlayer):
    # roles & identifying info
    is_admin = models.BooleanField(initial=False)
    role_str = models.StringField()
    citizen_code = models.StringField(blank=True)

    # baseline covariates
    age = models.IntegerField(min=18, max=99, blank=True)
    gender = models.StringField(
        label="What is your gender?",
        choices=['Male', 'Female', 'Non-binary', 'Prefer not to say'],
        widget=widgets.RadioSelect,
        blank=False
    )
    income = models.StringField(
        label="What is your household income level?",
        choices=['Less than £20,000', '£20,000 to £34,999', '£35,000 to £49,999', '£50,000 to £74,999', '£75,000 to £99,999', 'Over £100,000', 'Prefer not to say'],
        widget=widgets.RadioSelect,
        blank=False
    )
    education = models.StringField(
        label="What is your highest level of education?",
        choices=['No degree', 'High school', 'Bachelor', 'Master', 'Doctorate'],
        widget=widgets.RadioSelect,
        blank=False
    )
    pol_lean = models.IntegerField(
        label="In politics, people sometimes talk about 'left' and 'right'. Where would you place yourself on this scale? (1 = Left, 7 = Right)",
        choices=[1,2,3,4,5,6,7],
        widget=widgets.RadioSelect,
        blank=False
    )
    ac = models.StringField(
        label="What is your favorite color? Regardless of your actual preference, please select “Purple” to let us know that you are paying attention to the survey.",
        choices=['Red', 'Blue', 'Purple', 'Green', 'Yellow', 'Another colour'],
        widget=widgets.RadioSelect,
        blank=False
    )    

    # real-effort task
    triangles_guess = models.IntegerField(min=0, blank=False)
    gross_income = models.CurrencyField(initial=0)
    net_income = models.CurrencyField(initial=0)
    expected_tax_squares = models.IntegerField(min=0, blank=False)

    # targeting stage
    applied_for_transfer = models.BooleanField(initial=False)
    received_transfer = models.CurrencyField(initial=0)

    # trust game
    send_amount = models.CurrencyField(min=0, blank=False)
    amount_returned = models.CurrencyField(initial=0)

    # outcome survey
    trust_admin_public_funds = models.IntegerField(
        choices=[1,2,3,4,5,6,7], blank=False
    )
    trust_administration_overall = models.IntegerField(
        choices=[1,2,3,4,5,6,7], blank=False
    )
    perceived_fairness = models.IntegerField(
        choices=[1,2,3,4,5,6,7], blank=False
    )

    def role(self):
        return self.role_str

# --- creating_session: assign groups & roles --------------------------

def creating_session(subsession: Subsession):
    groups = subsession.get_groups()
    trust_conds = ['count', 'estimate']
    targ_conds = ['self', 'pre']
    conds = [(t, s) for t in trust_conds for s in targ_conds]
    random.shuffle(conds)

    for i, g in enumerate(groups):
        t, s = conds[i % len(conds)]
        g.trust_condition = t
        g.targeting_condition = s

        players = g.get_players()
        admin = random.choice(players)
        for p in players:
            p.is_admin = (p == admin)
            p.role_str = 'Administrator' if p.is_admin else 'Citizen'
            if not p.is_admin:
                p.citizen_code = _random_code()

def _random_code(length=8):
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

# --- PAGES ------------------------------------------------------------

class Consent(Page):
    pass

class RoleInfo(Page):
    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            role=player.role_str,
            trust_cond=player.group.trust_condition,
            targ_cond=player.group.targeting_condition,
        )

class BaselineSurvey(Page):
    form_model = 'player'
    form_fields = ['age', 'gender', 'income', 'education', 'pol_lean']

class AC(Page):
    form_model = 'player'
    form_fields = ['age', 'gender', 'income', 'education', 'pol_lean']

class CitizenTriangles(Page):
    form_model = 'player'
    form_fields = ['triangles_guess']

    @staticmethod
    def is_displayed(player: Player):
        return not player.is_admin

    @staticmethod
    def vars_for_template(player: Player):
        return dict(image_url=C.TRIANGLE_IMAGE)

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.gross_income = cu(player.triangles_guess)

class AdminSquares(Page):
    form_model = 'group'
    form_fields = ['squares_reported']

    @staticmethod
    def is_displayed(player: Player):
        return player.is_admin

    @staticmethod
    def vars_for_template(player: Player):
        g = player.group
        if g.trust_condition == 'count':
            instr = (
                "You must COUNT the number of squares as accurately as possible. "
                "Your bonus depends on matching the true number closely."
            )
        else:
            instr = (
                "You must ESTIMATE the number of squares. "
                "Your bonus increases when you report a HIGHER number than the true "
                "count."
            )
        return dict(
            image_url=C.TRIANGLE_IMAGE,
            admin_instructions=instr,
        )

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        g = player.group
        n_citizens = len([p for p in g.get_players() if not p.is_admin])
        g.total_tax = cu(g.squares_reported * n_citizens)

class WaitForTax(WaitPage):
    pass

class CitizenTaxInfo(Page):
    form_model = 'player'
    form_fields = ['expected_tax_squares']

    @staticmethod
    def is_displayed(player: Player):
        return not player.is_admin

    @staticmethod
    def vars_for_template(player: Player):
        g = player.group
        if g.trust_condition == 'count':
            msg = (
                "In this group, the Administrator was instructed and incentivised "
                "to COUNT the number of squares (taxes) as accurately as possible."
            )
        else:
            msg = (
                "In this group, the Administrator was instructed and incentivised "
                "to OVER-ESTIMATE the number of squares (taxes)."
            )
        return dict(trust_message=msg)

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        g = player.group
        tax_per_citizen = cu(g.squares_reported)
        player.net_income = max(cu(0), player.gross_income - tax_per_citizen)

class Targeting(Page):
    form_model = 'player'

    @staticmethod
    def is_displayed(player: Player):
        return not player.is_admin

    @staticmethod
    def get_form_fields(player: Player):
        if player.group.targeting_condition == 'self':
            return ['applied_for_transfer']
        else:
            return []

    @staticmethod
    def vars_for_template(player: Player):
        g = player.group
        is_self = (g.targeting_condition == 'self')
        if is_self:
            header = "Self-targeting"
            body = (
                "In this round, the administrator has determined that the collected "
                "taxes will be redistributed. You have the option to apply for this "
                "transfer.\n\nTo apply, you must complete a short administrative task: "
                "copy the generated (fake) demographic and bank details from a sample "
                "form onto a blank form."
            )
        else:
            header = "Pre-targeting"
            body = (
                "In this round, the administrator has determined that the collected "
                "taxes will be redistributed to everyone automatically. The administrator "
                "will identify all citizens and assign the available transfer funds to them "
                "proportionally."
            )
        total_income = player.net_income
        return dict(
            is_self=is_self,
            header=header,
            body=body,
            net_income=total_income,
        )

class WaitTargeting(WaitPage):
    after_all_players_arrive = 'assign_transfers'

    @staticmethod
    def assign_transfers(group: Group):
        if group.targeting_condition == 'pre':
            citizens = [p for p in group.get_players() if not p.is_admin]
            if citizens:
                share = group.total_tax / len(citizens)
            else:
                share = cu(0)
            for p in citizens:
                p.received_transfer = share
        else:
            citizens = [p for p in group.get_players() if not p.is_admin]
            applicants = [p for p in citizens if p.applied_for_transfer]
            if applicants:
                share = group.total_tax / len(applicants)
            else:
                share = cu(0)
            for p in citizens:
                if p in applicants:
                    p.received_transfer = share
                else:
                    p.received_transfer = cu(0)

class CitizenTrustGame(Page):
    form_model = 'player'
    form_fields = ['send_amount']

    @staticmethod
    def is_displayed(player: Player):
        return not player.is_admin

    @staticmethod
    def vars_for_template(player: Player):
        total_income = player.net_income + player.received_transfer
        return dict(
            total_income=total_income,
            mult=C.TRUST_MULTIPLIER,
        )

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        total_income = player.net_income + player.received_transfer
        if player.send_amount > total_income:
            player.send_amount = total_income

class WaitForSends(WaitPage):
    pass

class AdminTrustDecisions(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.is_admin

    @staticmethod
    def vars_for_template(player: Player):
        group = player.group
        citizens = [p for p in group.get_players() if not p.is_admin]
        return dict(citizens=citizens)

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        request = player._session.get_http_request()
        post_data = request.POST
        group = player.group
        citizens = [p for p in group.get_players() if not p.is_admin]
        for p in citizens:
            field_name = f"return_{p.id_in_group}"
            if field_name in post_data:
                try:
                    val = float(post_data[field_name])
                except ValueError:
                    val = 0
                p.amount_returned = cu(val)

class WaitForReturns(WaitPage):
    pass

class OutcomeSurvey(Page):
    form_model = 'player'
    form_fields = [
        'trust_admin_public_funds',
        'trust_administration_overall',
        'perceived_fairness',
    ]

    @staticmethod
    def is_displayed(player: Player):
        return not player.is_admin

page_sequence = [
    Consent,
    RoleInfo,
    BaselineSurvey,
    AC,
    CitizenTriangles,
    AdminSquares,
    WaitForTax,
    CitizenTaxInfo,
    Targeting,
    WaitTargeting,
    CitizenTrustGame,
    WaitForSends,
    AdminTrustDecisions,
    WaitForReturns,
    OutcomeSurvey,
]
