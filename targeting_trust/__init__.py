from otree.api import *
from otree.api import widgets
import random
import string

doc = """
2x2 between-groups:
- Trust manipulation: admin counts accurately vs admin estimates with incentive to report high taxes
- Targeting manipulation: automatic allocation vs application-based allocation

Group size: 5 (4 citizens + 1 administrator)
Trust game budget for citizens = standard corpus independent of earned income
"""


class C(BaseConstants):
    NAME_IN_URL = 'targeting_trust'
    PLAYERS_PER_GROUP = 5
    NUM_ROUNDS = 1

    TRUST_MULTIPLIER = 3
    TRUST_BUDGET = cu(100)
    ECU_TO_GBP = 0.01

    SLIDER_PAYMENT = 10          # ECU earned per slider
    TAX_PER_SLIDER = 3           # ECU tax per slider
    ADMIN_BONUS_PER_SLIDER = 1   # ECU admin bonus per reported slider  


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    # randomized at group level
    trust_condition = models.StringField(choices=['count', 'estimate'])
    targeting_condition = models.StringField(choices=['auto', 'apply'])  # auto=pre, apply=self
    total_true_tax = models.CurrencyField(initial=0) 
    total_applied_tax = models.CurrencyField(initial=0)


class Player(BasePlayer):
    #prolific id
    prolific_id = models.StringField(blank=True)

    #consent 
    consent = models.StringField(
        choices=[
            ('agree', 'I agree to participate in this study'),
            ('decline', 'I do not wish to participate')
        ],
        widget=widgets.RadioSelect
    )

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

    # Citizen comprehension fields  
    citizen_quiz_tax = models.IntegerField(
        label="If 10 sliders are reported, generating 100 ECU as gross income, how much tax is collected?",
        blank=True
    )

    citizen_quiz_bonus = models.StringField(
        label="How is the Administrator’s bonus determined?",
        choices=[
            ('accurate', 'They receive a bonus only for accurately counting the sliders'),
            ('percentage', 'They receive a bonus based on the number of sliders they report, regardless of accuracy'),
            ('fixed', 'They receive a fixed payment regardless of the number of sliders you placed or they report')
        ],
        widget=widgets.RadioSelect,
        blank=True
    )

    citizen_quiz_tax_base = models.StringField(
        label="What determines your tax payment?",
        choices=[
            ('completed', 'Each citizen pays a fixed amount irrespective of the number of completed sliders reported by the Administrator'),
            ('reported', 'Each citizen pays tax based on the number of completed sliders reported by the Administrator')
        ],
        widget=widgets.RadioSelect,
        blank=True
    )

    citizen_quiz_attempts = models.IntegerField(initial=0)
    citizen_quiz_failed = models.BooleanField(initial=False)

    # Admin comprehension fields
    admin_quiz_bonus = models.StringField(
        label="How is your bonus determined?",
        choices=[
            ('accuracy', 'I receive 1 ECU for every slider I count accurately'),
            ('percentage', 'I receive 1 ECU for every slider I report'),
            ('fixed', 'I receive a fixed amount regardless of tax')
        ],
        widget=widgets.RadioSelect,
        blank=True
    )

    admin_quiz_tax_base = models.StringField(
        label="What determines each citizen’s tax payment?",
        choices=[
            ('completed', 'Each citizen pays a fixed amount irrespective of the number of completed sliders reported by me'),
            ('reported', 'Each citizen pays tax based on the number of completed sliders reported by me')
        ],
        widget=widgets.RadioSelect,
        blank=True
    )

    admin_quiz_attempts = models.IntegerField(initial=0)
    admin_quiz_failed = models.BooleanField(initial=False)

    # creating fields for real effort task and tax outcome and final income
    effort_points = models.IntegerField(initial=0)
    gross_income = models.CurrencyField(initial=0)
    reported_tasks = models.IntegerField(initial=0)
    true_tax = models.CurrencyField(initial=0)
    applied_tax = models.CurrencyField(initial=0)
    tax_distortion = models.CurrencyField(initial=0)
    net_income_after_tax = models.CurrencyField(initial=0) 
    final_income_gbp = models.CurrencyField(initial=0) 

    # dummy hidden form field for work page
    work_page_completed = models.BooleanField(initial=False)

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

    # targeting decision (only in apply condition)
    apply_transfer = models.StringField(
        label="Do you want to apply for a transfer?",
        choices=[('yes', 'Yes'), ('no', 'No')],
        widget=widgets.RadioSelect,
        blank=True,  # enforced only when shown
    )
    received_transfer = models.CurrencyField(initial=0)

    # Self targeting work task 
    applicant_name = models.StringField(blank=True)
    applicant_age = models.IntegerField(blank=True)
    application_reference = models.StringField(blank=True)
    application_completed = models.BooleanField(initial=False)

    # trust game
    send_amount = models.CurrencyField(
        label="How much do you want to send to the Administrator?",
        min=0,
        blank=False
    )
    amount_returned = models.CurrencyField(initial=0)

    # trust game outcomes 
    income_after_transfer = models.CurrencyField(initial=0)
    tripled_trust_amount = models.CurrencyField(initial=0)
    trust_game_net = models.CurrencyField(initial=0)
    final_income = models.CurrencyField(initial=0)

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

    # post-game survey
    age = models.IntegerField(label="What is your age in years?<span style='color:red;'>*</span>", min=0, max=99, blank=True)

    gender = models.IntegerField(
        label="What is your gender?<span style='color:red;'>*</span>",
        choices=[
        (1, "Male"),
        (2, "Female"),
        (3, "Non-binary"),
        (4, "Prefer not to say"),
        ],
        widget=widgets.RadioSelect,
        blank=False
    )
    income = models.IntegerField(
        label="What is your household income level?<span style='color:red;'>*</span>",
        choices=[
        (1, "Less than £20,000"),
        (2, "£20,000 to £34,999"),
        (3, "£35,000 to £49,999"),
        (4, "£50,000 to £74,999"),
        (5, "£75,000 to £99,999"),
        (6, "Over £100,000"),
        (7, "Prefer not to say"),
        ],
        widget=widgets.RadioSelect,
        blank=False
    )
    education = models.IntegerField(
        label="What is your highest level of education?<span style='color:red;'>*</span>",
        choices=[
        (1, "No degree"),
        (2, "High school"),
        (3, "Bachelor"),
        (4, "Master"),
        (5, "Doctorate"),
        (6, "Prefer not to say"),
        ],
        widget=widgets.RadioSelect,
        blank=False
    )
    pol_lean = models.IntegerField(
        label="In politics, people sometimes talk about 'left' and 'right'. Where would you place yourself? (1 = Left, 7 = Right)<span style='color:red;'>*</span>",
        choices=[
        (1, "1 - Left"),
        (2, "2"),
        (3, "3"),
        (4, "4"),
        (5, "5"),
        (6, "6"),
        (7, "7 - Right"),
        (8, "Prefer not to say / Do not know"),
        ],
        widget=widgets.RadioSelect,
        blank=False
    )
    ac = models.StringField(
        label="Everyone has their favourite colour, but for this question, regardless of your actual preference, please select Green.",
        choices=['Red', 'Blue', 'Purple', 'Green', 'Yellow', 'Another colour'],
        widget=widgets.RadioSelect,
        blank=False
    )
    trust_admin_public_funds = models.IntegerField(
        label="How much do you trust the Administrator you interacted with in this survey to manage public funds? (1 = Not at all, 7 = A great deal)<span style='color:red;'>*</span>",
        choices=[
        (1, "1 - Not at all"),
        (2, "2"),
        (3, "3"),
        (4, "4"),
        (5, "5"),
        (6, "6"),
        (7, "7 - A great deal"),
        (8, "Prefer not to say"),
        ],
        widget=widgets.RadioSelect,
        blank=False
    )
    trust_administration_overall = models.IntegerField(
        label="How much do you trust the Administrator you interacted with in this survey overall? (1 = Not at all, 7 = A great deal)<span style='color:red;'>*</span>",
        choices=[
        (1, "1 - Not at all"),
        (2, "2"),
        (3, "3"),
        (4, "4"),
        (5, "5"),
        (6, "6"),
        (7, "7 - A great deal"),
        (8, "Prefer not to say"),
        ],
        widget=widgets.RadioSelect,
        blank=False
    )
    perceived_fairness = models.IntegerField(
        label="A little while ago, you were paid a part of the taxes collected by your group's Administrator as transfers. Thinking about it, how fair was the process? (1 = Very unfair, 7 = Very fair)<span style='color:red;'>*</span>",
        choices=[
        (1, "1 - Very unfair"),
        (2, "2"),
        (3, "3"),
        (4, "4"),
        (5, "5"),
        (6, "6"),
        (7, "7 - Very fair"),
        (8, "Prefer not to say"),
        ],
        widget=widgets.RadioSelect,
        blank=False
    )
    trust_cit = models.IntegerField(
        label="How much do you trust the other citizens in your group? (1 = Not at all, 7 = A great deal)<span style='color:red;'>*</span>",
        choices=[
        (1, "1 - Not at all"),
        (2, "2"),
        (3, "3"),
        (4, "4"),
        (5, "5"),
        (6, "6"),
        (7, "7 - A great deal"),
        (8, "Prefer not to say / Do not know"),
        ],
        widget=widgets.RadioSelect,
        blank=False
    )
    trust_gov = models.IntegerField(
        label="How much do you trust British governments of any party to place the needs of the nation above the interests of their own political party? (1 = Not at all, 7 = A great deal)<span style='color:red;'>*</span>",
        choices=[
        (1, "1 - Not at all"),
        (2, "2"),
        (3, "3"),
        (4, "4"),
        (5, "5"),
        (6, "6"),
        (7, "7 - A great deal"),
        (8, "Prefer not to say / Do not know"),
        ],
        widget=widgets.RadioSelect,
        blank=False
    )
    fmc = models.IntegerField(
        label="In your group, were transfers distributed automatically or did citizens have to apply?<span style='color:red;'>*</span>",
        choices=[
        (1, "Automatically"),
        (2, "Application-based"),
        (3, "Do not know / Don't remember"),
        ],
        widget=widgets.RadioSelect,
        blank=False
    )
    resp_targ = models.IntegerField(
        label="To what extent was the transfer process designed to respond to citizens' actions? (1 = Not designed to respond to citizens at all, 7 = Completely designed to respond to citizens)<span style='color:red;'>*</span>",
        choices=[
        (1, "1 - Not designed to respond at all"),
        (2, "2"),
        (3, "3"),
        (4, "4"),
        (5, "5"),
        (6, "6"),
        (7, "7 - Completely designed to respond"),
        (8, "Prefer not to say / Do not know"),
        ],
        widget=widgets.RadioSelect,
        blank=False
    )
    agency_targ = models.IntegerField(
        label="To what extent did you feel you had control over whether you received the transfer? (1 = Not control at all, 7 = Complete control)<span style='color:red;'>*</span>",
        choices=[
        (1, "1 - No control at all"),
        (2, "2"),
        (3, "3"),
        (4, "4"),
        (5, "5"),
        (6, "6"),
        (7, "7 - Complete control"),
        (8, "Prefer not to say / Do not know"),
        ],
        widget=widgets.RadioSelect,
        blank=False
    )
    

    def role(self):
        return self.role_str


def creating_session(subsession: Subsession):
    pass

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
        share = group.total_applied_tax / len(citizens)
        for p in citizens:
            p.received_transfer = share
    else:
        applicants = [p for p in citizens if p.apply_transfer == 'yes']
        share = (group.total_applied_tax / len(applicants)) if applicants else cu(0)
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

    player.gross_income = cu(player.effort_points * C.SLIDER_PAYMENT)

    return {player.id_in_group: dict(
        effort=player.effort_points,
        gross=float(player.gross_income),
    )}

def debug_treatment(player: Player):
    g = player.group
    return f"Trust={g.trust_condition} | Targeting={g.targeting_condition}"



# -------------------------- PAGES --------------------------

class Consent(Page):
    form_model = 'player'
    form_fields = ['consent']

    @staticmethod
    def live_method(player, data):
        if data.get('consent') == 'decline':
            player.participant.finished = True
        return {}

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.participant.prolific_id = player.participant.label
        if player.consent == 'decline':
            player.participant.finished = True

"""         
    class Consent(Page):
        form_model = 'player'
        form_fields = ['consent']

        def before_next_page(self):
            # Only capture once
            if self.round_number == 1:

                # PROLIFIC PID (already stored automatically)
                self.participant.prolific_id = self.participant.label

        @staticmethod
        def error_message(player, values):
            if values.get('consent') != 'agree':
                return (
                    "As you do not wish to participate in this study, "
                    "please close this survey and return your submission on Prolific "
                    "by selecting the 'Stop without completing' button."
                )


class Consent(Page):
    form_model = 'player'
    form_fields = ['consent']

    def before_next_page(self):
        # Only capture once
        if self.round_number == 1:
            # PROLIFIC PID (already stored automatically)
            self.participant.prolific_id = self.participant.label

    @staticmethod
    def error_message(player, values):
        if values.get('consent') != 'agree':
            return (
                "As you do not wish to participate in this study, "
                "please close this survey and return your submission on Prolific "
                "by selecting the 'Stop without completing' button."
                )
 """


class NoConsent(Page):
    
    @staticmethod
    def is_displayed(player):
        return player.consent == 'decline'
    

class LobbyWait(WaitPage):
    wait_for_all_groups = True
    timeout_seconds = 600

    @staticmethod
    def after_all_players_arrive(subsession):
        
        # Get only consenting players
        active = [
            p for p in subsession.get_players()
            if p.participant.finished == False
        ]

        # Shuffle for random group assignment
        random.shuffle(active)

        # Form clean groups of 5
        group_matrix = [
            active[i:i+5]
            for i in range(0, len(active) - len(active) % 5, 5)
        ]

        # Set groups in oTree
        subsession.set_group_matrix(group_matrix)

        # Your existing condition randomization — completely unchanged
        conds = [(t, s) for t in ['count', 'estimate'] for s in ['auto', 'apply']]
        random.shuffle(conds)

        for i, g in enumerate(subsession.get_groups()):
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


class RoleInfo(Page):
    
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
    
    @staticmethod
    def vars_for_template(player: Player):

        if player.group.trust_condition == 'count':
            admin_rule = (
                "The Administrator assigned to your group has been instructed "
                "to count the number of correctly placed sliders accurately and received a bonus of 1 ECU for every slider counted correctly."
            )
        else:
            admin_rule = (
                "The Administrator assigned to your group has been instructed "
                "to estimate the number of correctly placed sliders, and received a bonus of 1 ECU for every slider they report. Reporting a higher number results in a higher bonus."
            )

        return dict(admin_rule=admin_rule)


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
                "You receive a bonus equal to 1 ECU for every slider you count correctly."
            )
        else:
            text = (
                "You will see each participant’s completed sliders for 10 seconds and estimate "
                "the number completed. You receive a bonus of 1 ECU for every slider you report."
            )

        return dict(example_text=text)


class AdminComprehension(Page):
    form_model = 'player'
    form_fields = [
        'admin_quiz_bonus',
        'admin_quiz_tax_base'
    ]

    @staticmethod
    def is_displayed(player: Player):
        return player.is_admin

    @staticmethod
    def error_message(player, values):

        if player.group.trust_condition == 'count':
            correct_bonus = 'accuracy'
        else:
            correct_bonus = 'percentage'

        correct_tax_base = 'reported'

        # increment attempts
        player.admin_quiz_attempts += 1

        incorrect = (
            values['admin_quiz_bonus'] != correct_bonus
            or values['admin_quiz_tax_base'] != correct_tax_base
        )

        if incorrect:

            # If this is the 3rd failed attempt
            if player.admin_quiz_attempts >= 3:
                player.admin_quiz_failed = True
                return None  # allow progression

            return "One or more answers are incorrect. Please review the example and try again."

        # If correct → allow progression
        return None


class AdminQuizFeedback(Page):

    @staticmethod
    def is_displayed(player: Player):
        return player.is_admin and player.admin_quiz_failed

    @staticmethod
    def vars_for_template(player: Player):

        if player.group.trust_condition == 'count':
            admin_correct_bonus = (
                "I receive 1 ECU for every slider I count accurately."
            )
        else:
            admin_correct_bonus = (
                "I receive 1 ECU for every slider I report."
            )

        admin_correct_tax_base = (
            "Each citizen pays tax based on the number of completed sliders reported by me."
        )

        return dict(
            correct_bonus=admin_correct_bonus,
            correct_tax_base=admin_correct_tax_base, 
        )
    

class AdminInstructionsRefresh(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.is_admin 


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
            admin_bonus_display = C.ADMIN_BONUS_PER_SLIDER
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
            c.true_tax = cu(C.TAX_PER_SLIDER * c.effort_points)
            # Admin estimated tax 
            c.applied_tax = cu(C.TAX_PER_SLIDER * r)
            # Tax distortion
            c.tax_distortion = c.applied_tax - c.true_tax
            # Net income after admin tax
            c.net_income_after_tax = max(cu(0), c.gross_income - c.applied_tax)
            
            # Using applied tax for total tax calculation since that's what admin reports and what citizens see
            total_tax += c.applied_tax

        g.total_applied_tax = sum(p.applied_tax for p in citizens)
        
        g.total_true_tax = sum(p.true_tax for p in citizens)

        total_reported = sum(r or 0 for r in reports)
        player.admin_bonus = cu(total_reported * C.ADMIN_BONUS_PER_SLIDER)

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
                return "Please count the completed sliders accurately."
        
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
                "The Administrator was shown a visual record of the number of correctly placed sliders "
                "and was later asked to count the number of correctly placed sliders. "
                "The Administrator receives a bonus of 1 ECU for every slider counted correctly."
            )
        else:
            msg = (
                "The Administrator was shown the visual record of the number of correctly placed sliders " 
                "for 10 seconds and was later asked to estimate the number of correctly placed sliders. "
                "The Administrator received a bonus equal to 1 ECU for every slider they report. "
                "Because the Administrator’s bonus depends on the number of sliders they report, "
                "reporting a higher number results in a higher bonus. "
                "The number the Administrator reports is also used to calculate the tax deducted from your income. "
            )
        return dict(trust_message=msg, 
                    tasks_completed=player.effort_points)

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
                gross=100,
                tax=30,
                net=70,
                condition="Remember, the Administrator was asked to count the correctly placed sliders accurately and received 1 ECU for every slider they count correctly as a bonus. Your tax is calculated based on this reported slider count."
            )
        else:
            example = dict(
                completed=10,
                reported=12,
                gross=100,
                tax=36,
                net=64,
                condition="Remember, the Administrator was asked to estimate the number of correctly placed sliders and received 1 ECU for every slider they report. Your tax is calculated based on this reported slider count. "
            )

        return dict(example=example)
    

class CitizenComprehension(Page):
    form_model = 'player'
    form_fields = [
        'citizen_quiz_tax',
        'citizen_quiz_bonus',
        'citizen_quiz_tax_base'
    ]

    @staticmethod
    def is_displayed(player: Player):
        return not player.is_admin

    @staticmethod
    def error_message(player, values):

        correct_tax = 30
        correct_tax_base = 'reported'

        if player.group.trust_condition == 'count':
            correct_bonus = 'accurate'
        else:
            correct_bonus = 'percentage'

        # increment attempts
        player.citizen_quiz_attempts += 1

        incorrect = (
            values['citizen_quiz_tax'] != correct_tax
            or values['citizen_quiz_bonus'] != correct_bonus
            or values['citizen_quiz_tax_base'] != correct_tax_base
        )

        if incorrect:

            # If this is the 3rd failed attempt
            if player.citizen_quiz_attempts >= 3:
                player.citizen_quiz_failed = True
                return None  # allow progression

            return "One or more answers are incorrect. Please review the example and try again."

        # If correct → allow progression
        return None


class CitizenQuizFeedback(Page):

    @staticmethod
    def is_displayed(player: Player):
        return not player.is_admin and player.citizen_quiz_failed

    @staticmethod
    def vars_for_template(player: Player):

        correct_tax = 30

        if player.group.trust_condition == 'count':
            correct_bonus = (
                "They receive a bonus only for accurately counting the sliders. "
            )
        else:
            correct_bonus = (
                "They receive a bonus based on the number of sliders they report, regardless of accuracy. "
            )

        correct_tax_base = (
            "Each citizen pays tax based on the number of completed sliders reported by the Administrator. "
        )

        return dict(
            correct_tax=correct_tax,
            correct_bonus=correct_bonus,
            correct_tax_base=correct_tax_base
        )


class RevealTax(Page):

    @staticmethod
    def is_displayed(player: Player):
        return not player.is_admin

    @staticmethod
    def vars_for_template(player: Player):
        g = player.group

        if g.trust_condition == 'count':
            explanation_text = (
                "The Administrator was instructed to count correctly placed sliders accurately."
            )
        else:
            explanation_text = (
                "The Administrator estimated the number of completed sliders after briefly viewing the activity record of your correctly placed sliders."
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
                "The taxes collected by the administrator will be distributed as transfers through an application process. "
                "All citizens may apply to receive this amount. "
                "Collected tax revenue will be redistributed equally among those who apply in your group. "
                "To receive a transfer, you must complete a short administrative task."
            )
        else:
            header = "Transfer allocation"
            body = (
                "The taxes collected by the administrator will be distributed as transfers automatically. "
                "All citizens are automatically enrolled to receive this amount. "
                "Collected tax revenue will be redistributed equally among all citizens in your group. "
                "No application is required."
            )
        return dict(
            is_apply=is_apply,
            header=header,
            body=body,
            net_income=player.net_income_after_tax
        )


class ApplicationTask(Page):

    form_model = 'player'
    form_fields = ['applicant_name', 'applicant_age', 'application_reference']

    @staticmethod
    def is_displayed(player):
        return (
            not player.is_admin
            and player.group.targeting_condition == 'apply'
            and player.apply_transfer == 'yes'
        )

    @staticmethod
    def vars_for_template(player):
        import random
        names = ["Alex Morgan", "Taylor Reed", "Jordan Blake", "Casey Patel", "Riley Khan"]
        return dict(
            suggested_name=random.choice(names),
            suggested_age=random.randint(25, 55),
            ref_code=random.randint(10000, 99999)
        )

    @staticmethod
    def error_message(player, values):
        if not values['applicant_name'] or not values['applicant_age'] or not values['application_reference']:
            return "Please complete all fields to submit your application."

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.application_completed = True


class WaitTargeting(WaitPage):
    after_all_players_arrive = assign_transfers

    @staticmethod
    def assign_transfers(group: Group):
        citizens = [p for p in group.get_players() if not p.is_admin]
        if not citizens:
            return

        if group.targeting_condition == 'auto':
            share = group.total_applied_tax / len(citizens)
            for p in citizens:
                p.received_transfer = share
        else:
            applicants = [
                p for p in citizens
                if p.apply_transfer == 'yes' and p.application_completed
            ]
            share = (group.total_applied_tax / len(applicants)) if applicants else cu(0)
            for p in citizens:
                p.received_transfer = share if p in applicants else cu(0)


class TransferOutcome(Page):

    @staticmethod
    def is_displayed(player: Player):
        return not player.is_admin

    @staticmethod
    def vars_for_template(player: Player):

        g = player.group

        if g.targeting_condition == 'auto':
            status = "automatic"

        elif player.apply_transfer == 'yes' and player.application_completed:
            status = "applied_success"

        else:
            status = "did_not_apply"

        return dict(
            status=status,
            received_transfer=player.received_transfer
        )


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


class WaitForSends(WaitPage):

    @staticmethod
    def after_all_players_arrive(group: Group):

        citizens = [p for p in group.get_players() if not p.is_admin]

        for c in citizens:
            c.tripled_trust_amount = c.send_amount * C.TRUST_MULTIPLIER


class AdminTrustDecisions(Page):
    form_model = 'player'
    form_fields = ['return_to_c1', 'return_to_c2', 'return_to_c3', 'return_to_c4']

    @staticmethod
    def is_displayed(player: Player):
        return player.is_admin

    @staticmethod
    def vars_for_template(player: Player):
        citizens = citizens_in_order(player.group)
        tripled = [c.tripled_trust_amount for c in citizens]
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
            c.trust_game_net =  C.TRUST_BUDGET - c.send_amount + c.amount_returned

            # Final income
            c.final_income = c.income_after_transfer + c.trust_game_net

            # In GBP 
            c.final_income_gbp = c.final_income * C.ECU_TO_GBP


        # ---- Admin ----
        total_sent_tripled = sum(c.send_amount * C.TRUST_MULTIPLIER for c in citizens)
        total_returned = sum(c.amount_returned for c in citizens)

        admin.trust_game_net = total_sent_tripled - total_returned

        admin.final_income = admin.admin_bonus + admin.trust_game_net

        admin.final_income_gbp = admin.final_income * C.ECU_TO_GBP


class RevealIncomeAndTransfers(Page):

    @staticmethod
    def vars_for_template(player: Player):

        if player.is_admin:
            return dict(
                is_admin=True,
                admin_bonus=player.admin_bonus,
                trust_payoff=player.trust_game_net,
                final_income=player.final_income,
                final_income_gbp=player.final_income_gbp
            )

        else:
            return dict(
                is_admin=False,
                effort_points=player.effort_points,
                gross_income=player.gross_income,
                reported_tasks=player.reported_tasks,
                applied_tax=player.applied_tax,
                net_income_after_tax=player.net_income_after_tax,
                received_transfer=player.received_transfer,
                income_after_transfer=player.income_after_transfer,
                trust_budget=C.TRUST_BUDGET,
                sent=player.send_amount,
                returned=player.amount_returned,
                trust_payoff=player.trust_game_net,
                final_income=player.final_income,
                final_income_gbp=player.final_income_gbp,
            )


class PostSurveyPart1(Page):
    form_model = 'player'

    @staticmethod
    def is_displayed(player):
        return not player.is_admin

    def get_form_fields(self):
        import random
        # Randomise outcome measures
        randomised_fields = [
            'trust_admin_public_funds',
            'trust_administration_overall',
            'trust_cit',
        ]
        random.shuffle(randomised_fields)
        
        # Fixed order fields
        fixed_fields = [
            'perceived_fairness',
            'trust_gov',  
            'fmc',                 
            'resp_targ',           
            'agency_targ',        
        ]
        
        return randomised_fields + fixed_fields

    @staticmethod
    def error_message(player, values):
        for field in values:
            if values.get(field) in [None, '', []]:
                return "Please answer all questions marked with <span style='color:red;'>*</span> before continuing."


class PostSurveyPart2(Page):
    form_model = 'player'

    @staticmethod
    def is_displayed(player):
        return not player.is_admin

    form_fields = [
        'pol_lean',
        'age',
        'gender',
        'income',
        'education',
    ]

    @staticmethod
    def error_message(player, values):
        for field in values:
            if values.get(field) in [None, '', []]:
                return "Please answer all questions marked with <span style='color:red;'>*</span> before continuing."


class PostSurveyAdmin(Page):
    form_model = 'player'

    @staticmethod
    def is_displayed(player):
        return player.is_admin

    form_fields = [
        'trust_gov',
        'pol_lean',
        'age',
        'gender',
        'income',
        'education',
    ]

    @staticmethod
    def error_message(player, values):
        for field in values:
            if values.get(field) in [None, '', []]:
                return "Please answer all questions marked with <span style='color:red;'>*</span> before continuing."
    

class ThankYou(Page):
    pass


page_sequence = [
    Consent,
    NoConsent,
    LobbyWait,
    RoleInfo,

    CitizenWorkTaskInstructions,
    CitizenWorkTask,
    WaitForWork,
    AdminInstructions,
    AdminExample,
    AdminComprehension,
    AdminQuizFeedback,
    AdminInstructionsRefresh,
    AdminSquares,
    WaitForTax,     

    CitizenTaxInfo,
    CitizenExample,
    CitizenComprehension,
    CitizenQuizFeedback,
    RevealTax,
    AC,
    Targeting,
    ApplicationTask,
    WaitTargeting,

    TransferOutcome,
    CitizenTrustGame,
    WaitForSends,
    AdminTrustDecisions,
    WaitForReturns,

    PostSurveyPart1,
    PostSurveyPart2,
    PostSurveyAdmin,
    RevealIncomeAndTransfers,
    ThankYou
]
