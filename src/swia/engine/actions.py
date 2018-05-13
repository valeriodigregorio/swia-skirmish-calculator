"""
actions
Actions module for "Star Wars: Imperial Assault"
"""

import copy

from swia.model.dice import Die

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
        self._name = name
        self._cost = cost

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
        if context.actions > self._cost:
            self._do_perform(context)
            context.actions -= self._cost
            return True
        return False


class Attack(Action):

    def __init__(self):
        """
        Create an attack action.
        """
        super().__init__('Attack', 1)

        # Attributes
        self.pierce = 0
        self.accuracy = 0
        self.damage = 0
        self.surge = 0
        self.block = 0
        self.evade = 0
        self.dodge = 0

        # Operational
        self._miss = False
        self._attack_rolls = []
        self._defense_rolls = []
        self._surge_abilities = []

        # Stats
        self._total_damage = 0
        self._avoidance = 0
        self._surge_left = 0
        self._no_rerolls_total_damage = None

        # Attack
        self._step = 0
        self.steps = {
            1: Attack.declare,
            2: Attack.roll,
            3: Attack.reroll,
            4: Attack.apply_modifiers,
            5: Attack.spend_surges,
            6: Attack.check_accuracy,
            7: Attack.calculate_damage,
        }

    @property
    def current_step(self):
        return self._step

    @property
    def miss(self):
        return self._miss

    @property
    def total_damage(self):
        return self._total_damage

    @property
    def avoidance(self):
        return self._avoidance

    @property
    def surge_left(self):
        return self._surge_left

    @property
    def reroll_impact(self):
        return self._total_damage - self._no_rerolls_total_damage

    def _do_perform(self, context):
        self.__init__()
        self._perform_attack(context)
        self._calculate_avoidance(context)

    def _perform_attack(self, context, from_step=1):
        """
        Perform the action.
        :param context: Context of execution.
        :param from_step: Perform the attack starting from a specific step, skipping the previous.
        """
        self._step = from_step
        while True:
            step = self.steps.get(self._step, None)
            if step is None:
                break
            step(self, context)
            self._step += 1

    def _calculate_avoidance(self, context):
        # save stats
        total_damage = self.total_damage
        surge_left = self.surge_left
        no_rerolls_total_damage = self._no_rerolls_total_damage

        # assess blocked damage
        blocked_damage = self.block - self.pierce if self.block > self.pierce else 0
        avoided_damage = self.damage if blocked_damage > self.damage else blocked_damage

        # repeat steps 5-7 as if no evade and dodges were applied
        self.evade = 0
        self.dodge = 0
        self._perform_attack(context, 5)

        # assess evaded/dodged damage
        avoided_damage += self.total_damage - total_damage

        # revert stats
        self._total_damage = total_damage
        self._avoidance = avoided_damage
        self._surge_left = surge_left
        self._no_rerolls_total_damage = no_rerolls_total_damage

    def declare(self, context):
        """
        Declare target (step 1)
        :param context: Context of execution.
        """
        pass

    def roll(self, context):
        """
        Roll dice (step 2).
        :param context: Context of execution.
        """
        for rolls, pool in [(self._attack_rolls, context.attacker.attack_pool),
                            (self._defense_rolls, context.defender.defense_pool)]:
            if pool is not None:
                for die in pool:
                    die = Die.create(die)
                    rolls.append({'die': die, 'face': die.roll(), 'times': 0})

    def _reset_simulated_attack(self, attack):
        self.pierce = attack.pierce
        self.accuracy = attack.accuracy
        self.damage = attack.damage
        self.surge = attack.surge
        self.block = attack.block
        self.evade = attack.evade
        self.dodge = attack.dodge
        self._miss = attack._miss
        self._total_damage = attack._total_damage
        self._surge_left = attack._surge_left
        self._no_rerolls_total_damage = attack._no_rerolls_total_damage
        self._attack_rolls = attack._attack_rolls
        self._defense_rolls = attack._defense_rolls
        self._surge_abilities = []

    def _do_rerolls(self, context, reroll_type):

        def simulate_rerolls():
            rolls = getattr(self, "_{}_rolls".format(reroll_type), None)
            if rolls is None:
                raise AttributeError(reroll_type)

            total = {}
            current = 0
            a = Attack()
            for i, roll in enumerate(rolls):
                face = roll['face']
                for f in range(roll['die'].faces):
                    a._reset_simulated_attack(self)
                    rolls[i]['face'] = f
                    a._perform_attack(context, 4)
                    total[i] = total.get(i, 0) + a._total_damage
                    if f == face:
                        current = a._total_damage
                rolls[i]['face'] = face
            return total, current

        def perform_reroll(rerolls, test):
            rolls = getattr(self, "_{}_rolls".format(reroll_type), None)
            if rolls is None:
                raise AttributeError(reroll_type)

            for r in rerolls:
                n = getattr(r, reroll_type, None)
                for k, dmg in priority:
                    if n == 0:
                        break
                    if test(dmg / 6):
                        if r.apply(self, rolls[k]):
                            n -= 1

        total_damage, current_total_damage = simulate_rerolls()
        priority = sorted(total_damage.items(), key=lambda t: (t[1], t[0]), reverse=True)
        abilities = context.attacker.get_abilities(ability_type='reroll', trigger=self.current_step, action='attack')
        perform_reroll(abilities, lambda d: (d > current_total_damage))

        priority = reversed(priority)
        abilities = context.defender.get_abilities(ability_type='reroll', trigger=self.current_step, action='defense')
        perform_reroll(abilities, lambda d: (d < current_total_damage))

        return current_total_damage

    def reroll(self, context):
        """
        Reroll dice (step 3).
        :param context: Context of execution.
        """
        # TODO handle anything different than rerolls that applies at this step
        abilities = context.attacker.get_abilities(ability_type='reroll',
                                                   action='attack',
                                                   trigger=self.current_step) + \
                    context.defender.get_abilities(ability_type='reroll',
                                                   action='defense',
                                                   trigger=self.current_step)

        rerolls = {
            'attack': 0,
            'defense': 0
        }
        for a in abilities:
            rerolls['attack'] += a.attack
            rerolls['defense'] += a.defense

        for reroll_type, n in rerolls.items():
            if n > 0:
                damage = self._do_rerolls(context, reroll_type)
                if self._no_rerolls_total_damage is None:
                    self._no_rerolls_total_damage = damage

    def apply_modifiers(self, context):
        """
        Apply modifiers (step 4).
        :param context: Context of execution.
        """

        def simulate_conversion(ability, conversion_range):
            attack = copy.deepcopy(self)
            attack.declare(context)
            total = {}
            for i in conversion_range:
                attack._reset_simulated_attack(self)
                ability.apply(self, i)
                attack._perform_attack(context, 5)
                total[i] = total.get(i, 0) + attack._total_damage
            return total

        for r in self._attack_rolls:
            result = r['die'].get_face(r['face'])
            self.accuracy += result.get('accuracy', 0)
            self.damage += result.get('damage', 0)
            self.surge += result.get('surge', 0)

        for r in self._defense_rolls:
            result = r['die'].get_face(r['face'])
            self.block += result.get('block', 0)
            self.evade += result.get('evade', 0)
            self.dodge += result.get('dodge', 0)

        # TODO handle anything different than conversions that applies at this step
        conversions = context.attacker.get_abilities(ability_type='conversion',
                                                     action='attack',
                                                     trigger=self.current_step) + \
                      context.defender.get_abilities(ability_type='conversion',
                                                     action='defense',
                                                     trigger=self.current_step)

        for conversion in conversions:
            r = conversion.can_apply(self)
            if r is not None:
                n = r[1]
                if r[0] != r[1]:
                    total_damage = simulate_conversion(conversion, range(r[0], r[1] + 1))
                    if conversion.offensive:
                        n = max(total_damage, key=total_damage.get)
                    if conversion.defensive:
                        n = min(total_damage, key=total_damage.get)
                if n > 0:
                    conversion.apply(self, n)

    def spend_surges(self, context):
        """
        Spend surges (step 5).
        :param context: Context of execution.
        """
        # TODO: Parametric priority
        priority = ['damage', 'pierce']

        # retrieve available surges
        self._surge_left = self.surge - self.evade if self.surge > self.evade else 0
        for a in self._surge_abilities:
            self._surge_left -= a.cost

        # retrieve list of applicable abilities not yet applied
        # TODO handle anything different than attacker's surge abilities that applies at this step
        abilities = context.attacker.get_abilities(ability_type='surge', action='attack', trigger=self.current_step)
        for a in self._surge_abilities:
            if a in abilities:
                abilities.remove(a)

        # check if it's possible to fulfill the accuracy gap
        # TODO: Prioritize recovery effects
        gap = self._get_accuracy_gap(context.attacker.attack_type, context.attack_range)
        accuracy_abilities = []
        if gap > 0:
            surge_left = self._surge_left
            test_abilities = list(abilities)
            for a in self._surge_abilities:
                if a in test_abilities:
                    test_abilities.remove(a)
            while gap > 0:
                ability = self.get_best_ability(test_abilities, ['accuracy'] + priority)
                if ability is None:
                    break
                gap -= ability.effects['accuracy']
                accuracy_abilities.append(ability)
                test_abilities.remove(ability)
                self._surge_left -= ability.cost
            self._surge_left = surge_left

        if gap <= 0:
            # if we can fulfill the accuracy gap, let's apply all the selected surge abilities
            for ability in accuracy_abilities:
                ability.apply(self)
                self._surge_left -= ability.cost
                self._surge_abilities.append(ability)
                abilities.remove(ability)

        # spend remaining surges
        # TODO: Prioritize conditions
        ability = self.get_best_ability(abilities, priority)
        while ability is not None:
            ability.apply(self)
            self._surge_left -= ability.cost
            self._surge_abilities.append(ability)
            abilities.remove(ability)
            ability = self.get_best_ability(abilities, priority)

    def check_accuracy(self, context):
        """
        Check accuracy (step 6).
        :param context: Context of execution.
        """
        self._miss = self._get_accuracy_gap(context.attacker.attack_type, context.attack_range) > 0

    def calculate_damage(self, context):
        """
        Calculate damage (step 7).
        :param context: Context of execution.
        """
        self._miss = self._miss or (self.dodge > 0)
        if self._miss:
            self._total_damage = 0
        else:
            block = self.block - self.pierce if self.block > self.pierce else 0
            self._total_damage = self.damage - block if self.damage > block else 0

        if self._no_rerolls_total_damage is None:
            self._no_rerolls_total_damage = self._total_damage

    def get_best_ability(self, abilities, priority):
        """
        Calculate the next best ability to use following a given priority.
        :param abilities: List of possible abilities.
        :param priority: List of effects to prioritize in descending order of priority.
        :return: The best ability to use. None if there's no applicable ability.
        """

        def decorate_ability(a, pr):
            """
            Produces a decorated ability.
            :param a: The ability to decorate.
            :param pr: List of effects to prioritize in descending order of priority.
            :return: A decorated ability as a tuple.
            """
            if self.dodge > 0:
                d = 0
                p = 0
            else:
                d = a.effects['damage']
                p = a.effects['pierce'] + self.pierce
                p = self.block if p > self.block else p
            res = {
                'accuracy': a.effects['accuracy'],
                'damage': d,
                'pierce': p
            }
            return [res[x] for x in pr], a

        abilities = sorted([decorate_ability(a, priority) for a in abilities], key=lambda a: a[:-1], reverse=True)
        for decoration, ability in abilities:
            if sum(decoration) > 0:
                if ability.can_apply(self):
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
