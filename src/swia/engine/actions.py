"""
actions
Actions module for "Star Wars: Imperial Assault"
"""

__author__ = "Valerio Di Gregorio"
__copyright__ = "Copyright 2018, Valerio Di Gregorio"
__date__ = '2018-04-02'


class Action:

    def __init__(self, name, cost=1):
        """
        Create an action.
        :param name: Name of the action.
        :param cost: Cost of the action.
        """
        self.name = name
        self.cost = cost
        self.pierce = 0
        self.accuracy = 0
        self.damage = 0
        self.surge = 0
        self.block = 0
        self.evade = 0
        self.dodge = 0

    def save(self):
        """
        Save state of the attack.
        :return: The saved state of the attack.
        """
        return {'pierce': self.pierce,
                'accuracy': self.accuracy,
                'damage': self.damage,
                'surge': self.surge,
                'block': self.block,
                'evade': self.evade,
                'dodge': self.dodge}

    def load(self, state):
        """
        Load the state of the attack.
        :param state: The state of the attack.
        """
        self.pierce = state['pierce']
        self.accuracy = state['accuracy']
        self.damage = state['damage']
        self.surge = state['surge']
        self.block = state['block']
        self.evade = state['evade']
        self.dodge = state['dodge']

    def _do_perform(self, context):
        """
        Abstract method for performing the action.
        :param context: Context of execution.
        """
        raise NotImplementedError()

    def perform(self, context):
        """
        Perform the action.
        :param context: Context of execution.
        :return: True if the action has been performed. Otherwise False.
        """
        if context.actions > self.cost:
            self._do_perform(context)
            context.actions -= self.cost
            return True
        return False


class Attack(Action):

    def __init__(self):
        """
        Create an attack action.
        """
        super().__init__('Attack', 1)
        self.miss = False
        self.total_damage = 0
        self.surge_left = 0
        self.no_rerolls_total_damage = None
        self.surge_abilities = []
        self.attack_rolls = []
        self.defense_rolls = []

    def _do_perform(self, context):
        """
        Perform the action.
        :param context: Context of execution.
        """
        self.__init__()
        self.declare(context)
        self.roll(context)
        self.reroll(context)
        self.apply_modifiers(context)
        self.spend_surges(context)
        self.check_accuracy(context)
        self.calculate_damage(context)

    def declare(self, context):
        """
        Declare target (step 1)
        :param context: Context of execution.
        """
        abilities = context.attacker.get_abilities('offensive_passive') + \
                    context.defender.get_abilities('defensive_passive')
        for ability in abilities:
            ability.apply(self)

    def roll(self, context):
        """
        Roll dice (step 2).
        :param context: Context of execution.
        """
        for rolls, pool in [(self.attack_rolls, context.attacker.attack_pool),
                            (self.defense_rolls, context.defender.defense_pool)]:
            for die in pool:
                rolls.append({'die': die, 'face': die.roll(), 'times': 0})

    def _do_rerolls(self, context, reroll_type):

        def get_simulated_attack():
            a = Attack()
            a.declare(context)
            s = a.save()
            a.attack_rolls = self.attack_rolls
            a.defense_rolls = self.defense_rolls
            return a, s

        def reset_simulated_attack(a, s):
            a.load(s)
            a.miss = False
            a.total_damage = 0
            a.surge_left = 0
            a.surge_abilities = []

        def perform_reroll(rerolls, test):
            for r in rerolls:
                n = {
                    'attack': r.attack,
                    'defense': r.defense
                }.get(reroll_type)
                for k, dmg in priority:
                    if n == 0:
                        break
                    if test(dmg / 6):
                        if r.apply(rolls[k]):
                            n -= 1

        attack, state = get_simulated_attack()
        rolls = {
            'attack': attack.attack_rolls,
            'defense': attack.defense_rolls
        }.get(reroll_type, None)
        if rolls is None:
            raise AttributeError(reroll_type)

        # simulate all possible reroll cases
        total_damage = {}
        current_total_damage = 0
        for i, roll in enumerate(rolls):
            face = roll['face']
            for f in range(roll['die'].faces):
                rolls[i]['face'] = f
                attack.apply_modifiers(context)
                attack.spend_surges(context)
                attack.check_accuracy(context)
                attack.calculate_damage(context, False)
                total_damage[i] = total_damage.get(i, 0) + attack.total_damage
                if f == face:
                    current_total_damage = attack.total_damage
                reset_simulated_attack(attack, state)
                rolls[i]['face'] = face

        priority = sorted(total_damage.items(), key=lambda t: (t[1], t[0]), reverse=True)
        perform_reroll(context.attacker.get_abilities('offensive_reroll'),
                       lambda d: (d > current_total_damage))

        priority = reversed(priority)
        perform_reroll(context.defender.get_abilities('defensive_reroll'),
                       lambda d: (d < current_total_damage))

        return current_total_damage

    def reroll(self, context):
        """
        Reroll dice (step 3).
        :param context: Context of execution.
        """
        rerolls = context.attacker.get_abilities('offensive_reroll') + \
                  context.defender.get_abilities('defensive_reroll')

        for n, t in [(sum(r.attack for r in rerolls), 'attack'),
                     (sum(r.defense for r in rerolls), 'defense')]:
            if n > 0:
                damage = self._do_rerolls(context, t)
                if self.no_rerolls_total_damage is None:
                    self.no_rerolls_total_damage = damage

    def apply_modifiers(self, context):
        """
        Apply modifiers (step 4).
        :param context: Context of execution.
        """
        for r in self.attack_rolls:
            result = r['die'].get_face(r['face'])
            self.accuracy += result.get('accuracy', 0)
            self.damage += result.get('damage', 0)
            self.surge += result.get('surge', 0)

        for r in self.defense_rolls:
            result = r['die'].get_face(r['face'])
            self.block += result.get('block', 0)
            self.evade += result.get('evade', 0)
            self.dodge += result.get('dodge', 0)

        # TODO: Handle modifiers

    def spend_surges(self, context):
        """
        Spend surges (step 5).
        :param context: Context of execution.
        """
        # TODO: parametric priority
        priority = ['damage', 'pierce']

        # retrieve available surges
        self.surge_left = self.surge - self.evade if self.surge > self.evade else 0
        for a in self.surge_abilities:
            self.surge_left -= a.cost

        # retrieve list of applicable abilities not yet applied
        abilities = context.attacker.get_abilities('surge', self.surge_left)
        for a in self.surge_abilities:
            if a in abilities:
                abilities.remove(a)

        # check if it's possible to fulfill the accuracy gap
        # TODO: Prioritize recovery effects
        gap = self._get_accuracy_gap(context.attacker.attack_type, context.attack_range)
        accuracy_abilities = []
        if gap > 0:
            surge_left = self.surge_left
            test_abilities = list(abilities)
            for a in self.surge_abilities:
                if a in test_abilities:
                    test_abilities.remove(a)
            while gap > 0:
                ability = self.get_best_ability(surge_left, test_abilities, ['accuracy'] + priority)
                if ability is None:
                    break
                gap -= ability.get_effect('accuracy')
                accuracy_abilities.append(ability)
                test_abilities.remove(ability)
                surge_left -= ability.cost

        if gap <= 0:
            # if we can fulfill the accuracy gap, let's apply all the selected surge abilities
            for ability in accuracy_abilities:
                ability.apply(self)
                abilities.remove(ability)

        # spend remaining surges
        # TODO: Prioritize conditions
        ability = self.get_best_ability(self.surge_left, abilities, priority)
        while ability is not None:
            ability.apply(self)
            abilities.remove(ability)
            ability = self.get_best_ability(self.surge_left, abilities, priority)

    def check_accuracy(self, context):
        """
        Check accuracy (step 6).
        :param context: Context of execution.
        """
        self.miss = self._get_accuracy_gap(context.attacker.attack_type, context.attack_range) > 0

    def calculate_damage(self, context, collect_results=True):
        """
        Calculate damage (step 7).
        :param context: Context of execution.
        :param collect_results: If True results will be collected at the end of the step. Default is True.
        """
        self.miss = self.miss or (self.dodge > 0)
        if self.miss:
            self.total_damage = 0
        else:
            block = self.block - self.pierce if self.block > self.pierce else 0
            self.total_damage = self.damage - block if self.damage > block else 0
            if self.no_rerolls_total_damage is None:
                self.no_rerolls_total_damage = self.total_damage
        if collect_results:
            context.collect_attack_results(self)

    def get_best_ability(self, surge, abilities, priority):
        """
        Calculate the next best ability to use following a given priority.
        :param surge: The amount of available surges.
        :param abilities: List of possible abilities.
        :param priority: List of effects to prioritize in descending order of priority.
        :return: The best ability to use. None if there's no applicable ability.
        """

        def decorate_ability(a):
            """
            Produces a decorated ability.
            :param a: The ability to decorate.
            :return: A decorated ability as a tuple.
            """
            d = a.get_effect('damage')
            p = a.get_effect('pierce') + self.pierce
            p = self.block if p > self.block else p
            d, p = (0, 0) if self.dodge > 0 else (d, p)
            results = {'accuracy': a.get_effect('accuracy'),
                       'damage': d,
                       'pierce': p,
                       'ability': a}
            result = [results.get(x, 0) for x in (priority + ['ability'])]
            if sum(result[:-1]) <= 0:
                result[-1] = None
            return tuple(result)

        decorated_abilities = sorted([decorate_ability(a) for a in abilities], key=lambda a: a[:-1], reverse=True)
        for decorated_ability in decorated_abilities:
            ability = decorated_ability[-1]
            if ability is not None and ability.can_apply(surge):
                return ability
        return None

    def _get_accuracy_gap(self, attack_type, attack_range):
        """
        Retrieve the extra accuracy required for the attack to hit.
        :param attack_type: Attack type.
        :param attack_range: Distance between attacker and defender.
        :return: The accuracy still needed for the attack to hit.
        """
        if attack_range <= 0:
            raise ValueError(attack_range)
        gap = attack_range - {
            'melee': 1,
            'reach': 2,
            'ranged': self.accuracy
        }[attack_type]
        return gap if gap > 0 else 0
