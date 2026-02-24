from otree.api import *
from otree.api import widgets
import random
import string

doc = """
2x2 between-groups:
- Trust manipulation: admin counts accurately vs admin estimates with incentive to report high taxes
- Targeting manipulation: automatic allocation vs application-based allocation

Group size: 5 (4 citizens + 1 administrator)
Trust game budget for citizens = net income (after tax), before redistribution is revealed.
"""


class C(BaseConstants):
    NAME_IN_URL = 'targeting_trust'
    PLAYERS_PER_GROUP = 5
    NUM_ROUNDS = 1

    TRIANGLE_IMAGE = 'triangles_squares.png'  # place in _static/
    TRUST_MULTIPLIER = 3
    ADMIN_TAX_SHARE = 0.30
    TRUST_BUDGET = cu(10)
    TAX_RATE = 0.3


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    # randomized at group level
    trust_condition = models.StringField(choices=['count', 'estimate'])
    targeting_condition = models.StringField(choices=['auto', 'apply'])  # auto=pre, apply=self

    total_tax = models.CurrencyField(initial=0)


class Player(BasePlayer):
    # identity/role
    is_admin = models.BooleanField(initial=False)
    role_str = models.StringField()
    citizen_code = models.StringField(blank=True)

    #create player identity fields for trust game
    return_to_c1 = models.CurrencyField(min=0, blank=True)
    return_to_c2 = models.CurrencyField(min=0, blank=True)
    return_to_c3 = models.CurrencyField(min=0, blank=True)
    return_to_c4 = models.CurrencyField(min=0, blank=True)

    # admin payoff component (for incentive framing)
    admin_bonus = models.CurrencyField(initial=0)

    # creating fields for real effort task and tax outcome
    effort_points = models.IntegerField(initial=0)
    gross_income = models.CurrencyField(initial=0)
    reported_tasks = models.IntegerField(initial=0)
    true_tax = models.CurrencyField(initial=0)
    applied_tax = models.CurrencyField(initial=0)
    tax_distortion = models.CurrencyField(initial=0)
    net_income_after_tax = models.CurrencyField(initial=0)  

    # trust game outcomes 
    income_after_transfer = models.CurrencyField(initial=0)
    trust_game_net = models.CurrencyField(initial=0)
    final_income = models.CurrencyField(initial=0)

    # citizen real-effort
    #Removing this to make it more interactive
    #triangles_guess = models.IntegerField(
        #label="Please enter your estimate of the number of triangles in the image:",
        #min=0,
        #blank=False
    #)

    # citizen belief/expectation
    expected_tax_squares = models.IntegerField(
        label="What do you think the number of correctly placed sliders reported by the administrator will be?",
        min=0,
        blank=False
    )
    # dummy hidden form field for work page
    work_page_completed = models.BooleanField(initial=False)

    # targeting decision (only in apply condition)
    apply_transfer = models.StringField(
        label="Do you want to apply for a transfer?",
        choices=[('yes', 'Yes'), ('no', 'No')],
        widget=widgets.RadioSelect,
        blank=True,  # enforced only when shown
    )
    received_transfer = models.CurrencyField(initial=0)

    # trust game
    send_amount = models.CurrencyField(
        label="How much do you want to send to the Administrator?",
        min=0,
        blank=False
    )
    amount_returned = models.CurrencyField(initial=0)

    # real effort outcome
    #effort_points = models.IntegerField(initial=0)

    #gross_income = models.CurrencyField(initial=0)
    #net_income = models.CurrencyField(initial=0)

    # what admin reports (tax base)
    report_c1 = models.IntegerField(min=0, blank=True)
    report_c2 = models.IntegerField(min=0, blank=True)
    report_c3 = models.IntegerField(min=0, blank=True)
    report_c4 = models.IntegerField(min=0, blank=True)

    # store citizen specific tax paid
    tax_paid = models.CurrencyField(initial=0)

    # post-game survey (citizens only)
    age = models.IntegerField(label="What is your age?", min=18, max=99, blank=False)

    gender = models.StringField(
        label="What is your gender?",
        choices=['Male', 'Female', 'Non-binary', 'Prefer not to say'],
        widget=widgets.RadioSelect,
        blank=False
    )
    income = models.StringField(
        label="What is your household income level?",
        choices=[
            'Less than £20,000', '£20,000 to £34,999', '£35,000 to £49,999',
            '£50,000 to £74,999', '£75,000 to £99,999', 'Over £100,000',
            'Prefer not to say'
        ],
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
        label="In politics, people sometimes talk about 'left' and 'right'. Where would you place yourself? (1 = Left, 7 = Right)",
        choices=[1, 2, 3, 4, 5, 6, 7],
        widget=widgets.RadioSelect,
        blank=False
    )
    ac = models.StringField(
        label="Everyone has their favourite colour, but for this question, regardless of your actual preference, please select “Purple”.",
        choices=['Red', 'Blue', 'Purple', 'Green', 'Yellow', 'Another colour'],
        widget=widgets.RadioSelect,
        blank=False
    )

    trust_admin_public_funds = models.IntegerField(
        label="How much do you trust the Administrator you interacted with in this survey to manage public funds? (1 = Not at all, 7 = A great deal)",
        choices=[1, 2, 3, 4, 5, 6, 7],
        widget=widgets.RadioSelect,
        blank=False
    )
    trust_administration_overall = models.IntegerField(
        label="How much do you trust the Administrator you interacted with in this survey overall? (1 = Not at all, 7 = A great deal)",
        choices=[1, 2, 3, 4, 5, 6, 7],
        widget=widgets.RadioSelect,
        blank=False
    )
    perceived_fairness = models.IntegerField(
        label="How fair was the redistribution process? (1 = Very unfair, 7 = Very fair)",
        choices=[1, 2, 3, 4, 5, 6, 7],
        widget=widgets.RadioSelect,
        blank=False
    )
    trust_gov = models.IntegerField(
        label="How much do you trust British governments of any party to place the needs of the nation above the interests of their own political party? (1 = Not at all, 7 = A great deal)",
        choices=[1, 2, 3, 4, 5, 6, 7],
        widget=widgets.RadioSelect,
        blank=False
    )
    

    def role(self):
        return self.role_str


def creating_session(subsession: Subsession):
    groups = subsession.get_groups()
    conds = [(t, s) for t in ['count', 'estimate'] for s in ['auto', 'apply']]
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


def _random_code(length=10):
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def make_work_grid(points):
    # each square represents 1 completed task
    # 10 squares per row
    rows = []
    row = []

    for i in range(points):
        row.append(1)
        if len(row) == 10:
            rows.append(row)
            row = []

    if row:
        rows.append(row)

    return rows

def assign_transfers(group: Group):
    citizens = [p for p in group.get_players() if not p.is_admin]
    if not citizens:
        return

    if group.targeting_condition == 'auto':
        share = group.total_tax / len(citizens)
        for p in citizens:
            p.received_transfer = share
    else:
        applicants = [p for p in citizens if p.apply_transfer == 'yes']
        share = (group.total_tax / len(applicants)) if applicants else cu(0)
        for p in citizens:
            p.received_transfer = share if p in applicants else cu(0)

def citizens_in_order(group: Group):
    return sorted(
        [p for p in group.get_players() if not p.is_admin],
        key=lambda p: p.id_in_group
    )


def live_effort(player: Player, data):
    if player.is_admin:
        return

    if data.get('type') == 'click':
        player.effort_points += 1

    player.gross_income = cu(player.effort_points)

    return {player.id_in_group: dict(
        effort=player.effort_points,
        gross=float(player.gross_income),
    )}

def debug_treatment(player: Player):
    g = player.group
    return f"Trust={g.trust_condition} | Targeting={g.targeting_condition}"



# -------------------------- PAGES --------------------------

class Consent(Page):
    pass


class RoleInfo(Page):
    @staticmethod
    def vars_for_template(player: Player):
        return dict(role=player.role_str)
    
    @staticmethod
    def vars_for_template(player: Player):
        g = player.group
        citizens = [p for p in g.get_players() if not p.is_admin]
    
        return dict(
            role=player.role_str,
            is_admin=player.is_admin,
            trust_condition=g.trust_condition,
            targeting_condition=g.targeting_condition,
            citizens=citizens,
            debug_info=debug_treatment(player)
        )


#Removing this again to make the income generation interactive
#class CitizenTriangles(Page):
    #form_model = 'player'
    #form_fields = ['triangles_guess']

    #@staticmethod
    #def is_displayed(player: Player):
        #return not player.is_admin

    #@staticmethod
    #def vars_for_template(player: Player):
        #return dict(image_url=C.TRIANGLE_IMAGE, admin_tax_share=C.ADMIN_TAX_SHARE)

    #@staticmethod
    #def before_next_page(player: Player, timeout_happened):
        #player.gross_income = cu(player.triangles_guess)

class CitizenWorkTaskInstructions(Page):

    @staticmethod
    def is_displayed(player: Player):
        return not player.is_admin
    
class CitizenWorkTask(Page):
    live_method = live_effort
    form_model = 'player'
    form_fields = ['work_page_completed']

    @staticmethod
    def is_displayed(player: Player):
        return not player.is_admin

class WaitForWork(WaitPage):
    pass

class AdminInstructions(Page):

    @staticmethod
    def is_displayed(player: Player):
        return player.is_admin
    
class AdminExample(Page):

    @staticmethod
    def is_displayed(player: Player):
        return player.is_admin

    @staticmethod
    def vars_for_template(player: Player):
        g = player.group

        if g.trust_condition == 'count':
            text = (
                "You will review each participant’s completed sliders and count them accurately. "
                "You receive a bonus for performing this task correctly."
            )
        else:
            text = (
                "You will see each participant’s completed sliders for 10 seconds and estimate "
                "the number completed. You receive a bonus equal to a percentage of the total tax collected."
            )

        return dict(example_text=text)

class AdminSquares(Page):
    form_model = 'player'
    form_fields = ['report_c1','report_c2','report_c3','report_c4']

    @staticmethod
    def is_displayed(player: Player):
        return player.is_admin

    @staticmethod
    def vars_for_template(player: Player):
        g = player.group
        citizens = [p for p in g.get_players() if not p.is_admin]

        if g.trust_condition == 'count':
            instruction_text = (
                "You must carefully review each citizen's activity record and COUNT "
                "how many tasks they completed."
            )
        else:
            instruction_text = (
                "You must QUICKLY assess each citizen's activity record and ESTIMATE "
                "how many tasks they completed. Your bonus increases when you report higher completed tasks. "
            )

        rows = []
        for i, c in enumerate(citizens, start=1):
            rows.append(dict(
                code=c.citizen_code,
                blocks=list(range(c.effort_points)),
                field=f"report_c{i}"
            ))

        return dict(
            rows=rows,
            instruction_text=instruction_text,
            admin_tax_share_display=f"{C.ADMIN_TAX_SHARE:.2f}"
        )

    @staticmethod
    def before_next_page(player: Player, timeout_happened):

        g = player.group
        citizens = [p for p in g.get_players() if not p.is_admin]

        reports = [
            player.report_c1,
            player.report_c2,
            player.report_c3,
            player.report_c4
        ]

        total_tax = cu(0)

        for c, r in zip(citizens, reports):
            if r is None:
                r = 0

            # Storing reported tasks
            c.reported_tasks = r 
            # Storing true tax (30%)
            c.true_tax = cu(C.TAX_RATE * c.effort_points)
            # Admin estimated tax 
            c.applied_tax = cu(C.TAX_RATE * r)
            # Tax distortion
            c.tax_distortion = c.applied_tax - c.true_tax
            # Net income after admin tax
            c.net_income_after_tax = max(cu(0), c.gross_income - c.applied_tax)
            
            total_tax += c.applied_tax

        total_applied_tax = sum(p.applied_tax for p in citizens)
        
        total_true_tax = sum(p.true_tax for p in citizens)

        player.admin_bonus = cu(C.ADMIN_TAX_SHARE) * total_applied_tax

    @staticmethod
    def error_message(player: Player, values):
        g = player.group
        if g.trust_condition != 'count':
                return  # only enforce in count condition

        citizens = [p for p in g.get_players() if not p.is_admin]

        reports = [
            values.get('report_c1'),
            values.get('report_c2'),
            values.get('report_c3'),
            values.get('report_c4'),
            ]

        for c, r in zip(citizens, reports):
            if r != c.effort_points:
                return "In this condition, you must count the completed sliders accurately."
        
#class AdminSquares(Page):
    #form_model = 'group'
    #form_fields = ['squares_reported']

    #@staticmethod
    #def is_displayed(player: Player):
     #   return player.is_admin

    #@staticmethod
    #def vars_for_template(player: Player):
        #g = player.group
        #if g.trust_condition == 'count':
            #instr = (
                #"Please COUNT the squares as accurately as you can. "
                #"You will receive a bonus for accuracy."
            #)
        #else:
         #   instr = (
          #      "Please ESTIMATE the squares. "
           #     "You will receive a bonus for reporting a HIGH number."
           # )
        #return dict(
         #   image_url=C.TRIANGLE_IMAGE,
          #  admin_instructions=instr,
           # admin_tax_share=C.ADMIN_TAX_SHARE
        #)


    #@staticmethod
    #def before_next_page(player: Player, timeout_happened):
    #    g = player.group
     #   n_citizens = len([p for p in g.get_players() if not p.is_admin])
      #  g.total_tax = sum([cu(0.2 * p.effort_points) for p in g.get_players() if not p.is_admin])
       # player.admin_bonus = cu(C.ADMIN_TAX_SHARE) * g.total_tax


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
                "The Administrator was instructed to count the number of correctly placed sliders "
                "and received a bonus to report the correct sliders count accurately."
            )
        else:
            msg = (
                "The Administrator was instructed to estimate the number of correctly placed sliders "
                "and received a bonus that was a percentage of their reported correct sliders count."
            )
        return dict(trust_message=msg, admin_tax_share=C.ADMIN_TAX_SHARE)

    #@staticmethod
    #def before_next_page(player: Player, timeout_happened):
    #    g = player.group
    #    tax_per_citizen = cu(g.squares_reported)
    #    player.net_income = max(cu(0), player.gross_income - tax_per_citizen)

class CitizenExample(Page):

    @staticmethod
    def is_displayed(player: Player):
        return not player.is_admin

    @staticmethod
    def vars_for_template(player: Player):
        g = player.group

        if g.trust_condition == 'count':
            example = dict(
                completed=10,
                reported=10,
                gross=10,
                tax=3,
                net=7,
                condition="The Administrator was instructed to count completed sliders accurately and received a fixed bonus."
            )
        else:
            example = dict(
                completed=10,
                reported=12,
                gross=10,
                tax=3.6,
                net=6.4,
                condition="The Administrator was instructed to estimate the number of completed sliders and received a bonus equal to a percentage of total tax collected."
            )

        return dict(example=example)

class RevealTax(Page):

    @staticmethod
    def is_displayed(player: Player):
        return not player.is_admin

    @staticmethod
    def vars_for_template(player: Player):
        g = player.group

        if g.trust_condition == 'count':
            explanation_text = (
                "In this round, the Administrator was instructed to count completed sliders accurately."
            )
        else:
            explanation_text = (
                "In this round, the Administrator estimated the number of completed sliders after briefly viewing the activity record."
            )

        return dict(
            reported_for_you=player.reported_tasks,
            tax_paid=player.applied_tax,
            gross_income=player.gross_income,
            net_income=player.net_income_after_tax,
            explanation_text=explanation_text,
            trust_condition=g.trust_condition,
        )

class AC(Page):
    form_model = 'player'
    form_fields = [
        'ac']

class Targeting(Page):
    form_model = 'player' 

    @staticmethod
    def is_displayed(player: Player):
        return not player.is_admin

    @staticmethod
    def get_form_fields(player: Player):
        if player.group.targeting_condition == 'apply':
            return ['apply_transfer']
        return []

    @staticmethod
    def error_message(player: Player, values):
        if player.group.targeting_condition == 'apply' and not values.get('apply_transfer'):
            return "Please choose whether you want to apply for a transfer."

    @staticmethod
    def vars_for_template(player: Player):
        g = player.group
        is_apply = (g.targeting_condition == 'apply')
        if is_apply:
            header = "Transfer application"
            body = (
                "You may now chose to apply to receive a transfer from the administrator. Collected tax revenue will be redistributed equally to people who have applied for a transfer. "
                "To apply, you must complete a short administrative task."
            )
        else:
            header = "Transfer allocation"
            body = (
                "You have been automatically selected to receive a transfer from the administrator. Collected tax revenue will be redistributed equally to everyone in your group."
                " No application is needed."
            )
        return dict(
            is_apply=is_apply,
            header=header,
            body=body,
            net_income=player.net_income_after_tax
        )

class WaitTargeting(WaitPage):
    after_all_players_arrive = assign_transfers

    @staticmethod
    def assign_transfers(group: Group):
        citizens = [p for p in group.get_players() if not p.is_admin]
        if not citizens:
            return

        if group.targeting_condition == 'auto':
            share = group.total_tax / len(citizens)
            for p in citizens:
                p.received_transfer = share
        else:
            applicants = [p for p in citizens if p.apply_transfer == 'yes']
            share = (group.total_tax / len(applicants)) if applicants else cu(0)
            for p in citizens:
                p.received_transfer = share if p in applicants else cu(0)


class CitizenTrustGame(Page):
    form_model = 'player'
    form_fields = ['send_amount']

    @staticmethod
    def is_displayed(player: Player):
        return not player.is_admin

    @staticmethod
    def vars_for_template(player: Player):
        return dict(trust_budget=float(C.TRUST_BUDGET), mult=C.TRUST_MULTIPLIER)

    @staticmethod
    def error_message(player: Player, values):
        if values['send_amount'] > C.TRUST_BUDGET:
            return f"You cannot send more than your available amount ({C.TRUST_BUDGET} ECU)."

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if player.send_amount > player.net_income:
            player.send_amount = player.net_income


class WaitForSends(WaitPage):
    pass


class AdminTrustDecisions(Page):
    form_model = 'player'
    form_fields = ['return_to_c1', 'return_to_c2', 'return_to_c3', 'return_to_c4']

    @staticmethod
    def is_displayed(player: Player):
        return player.is_admin

    @staticmethod
    def vars_for_template(player: Player):
        citizens = citizens_in_order(player.group)
        tripled = [c.send_amount * C.TRUST_MULTIPLIER for c in citizens]
        fields = ['return_to_c1', 'return_to_c2', 'return_to_c3', 'return_to_c4']
        rows = list(zip(citizens, tripled, fields))
        return dict(rows=rows)

    @staticmethod
    def error_message(player: Player, values):
        citizens = citizens_in_order(player.group)
        fields = ['return_to_c1', 'return_to_c2', 'return_to_c3', 'return_to_c4']
        for c, f in zip(citizens, fields):
            if values.get(f) is not None:
                max_return = c.send_amount * C.TRUST_MULTIPLIER
                if values[f] > max_return:
                    return f"You cannot return more than {max_return} ECU."

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        citizens = citizens_in_order(player.group)
        returns = [
            player.return_to_c1,
            player.return_to_c2,
            player.return_to_c3,
            player.return_to_c4,
        ]
        for c, r in zip(citizens, returns):
            c.amount_returned = r if r is not None else cu(0)



class WaitForReturns(WaitPage):

    @staticmethod
    def after_all_players_arrive(group: Group):

        citizens = [p for p in group.get_players() if not p.is_admin]
        admin = [p for p in group.get_players() if p.is_admin][0]

        # ---- Citizens ----
        for c in citizens:

            # Income after transfer
            c.income_after_transfer = c.net_income_after_tax + c.received_transfer

            # Trust game effect
            c.trust_game_net =  c.TRUST_BUDGET - c.send_amount + c.amount_returned

            # Final income
            c.final_income = c.income_after_transfer + c.trust_game_net

        # ---- Admin ----
        total_sent_tripled = sum(c.send_amount * C.TRUST_MULTIPLIER for c in citizens)
        total_returned = sum(c.amount_returned for c in citizens)

        admin.trust_game_net = total_sent_tripled - total_returned

        admin.final_income = admin.admin_bonus + admin.trust_game_net


class RevealIncomeAndTransfers(Page):
    @staticmethod
    def vars_for_template(player: Player):

        if player.is_admin:
            return dict(
                is_admin=True,
                admin_bonus=player.admin_bonus,
                trust_payoff=player.payoff,
                final_income=player.admin_bonus + player.payoff,
            )

        else:
            income_after_transfer = player.net_income_after_tax + player.received_transfer

            return dict(
                is_admin=False,
                gross_income=player.gross_income,
                applied_tax=player.applied_tax,
                net_income_after_tax=player.net_income_after_tax,
                received_transfer=player.received_transfer,
                income_after_transfer=income_after_transfer,
                trust_budget=C.TRUST_BUDGET,
                sent=player.send_amount,
                returned=player.amount_returned,
                trust_payoff=player.payoff,
                final_income=income_after_transfer + player.payoff,
            )


class PostSurvey(Page):
    form_model = 'player'

    @staticmethod
    def is_displayed(player: Player):
        return True   # allow admin and citizens

    @staticmethod
    def get_form_fields(player: Player):

        if player.is_admin:
            return [
                'age',
                'gender',
                'income',
                'education',
                'pol_lean'
            ]

        else:
            return [
                'trust_admin_public_funds',
                'trust_administration_overall',
                'perceived_fairness',
                'trust_gov',
                'age',
                'gender',
                'income',
                'education',
                'pol_lean'
            ]
#class PostSurvey(Page):
#    form_model = 'player'
#    form_fields = [
#        'trust_admin_public_funds', 'trust_administration_overall', 'perceived_fairness', 'trust_gov',
#        'age', 'gender', 'income', 'education', 'pol_lean'
#    ]

    #@staticmethod
    #def is_displayed(player: Player):
    #    return not player.is_admin
    
class ThankYou(Page):
    pass


page_sequence = [
    Consent,
    RoleInfo,

    CitizenWorkTaskInstructions,
    CitizenWorkTask,
    WaitForWork,
    AdminInstructions,
    AdminExample,
    AdminSquares,
    WaitForTax,     

    CitizenTaxInfo,
    CitizenExample,
    RevealTax,
    AC,
    Targeting,
    WaitTargeting,

    CitizenTrustGame,
    WaitForSends,
    AdminTrustDecisions,
    WaitForReturns,

    PostSurvey,
    RevealIncomeAndTransfers,
    ThankYou
]
