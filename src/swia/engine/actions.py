"""
actions
Actions module for "Star Wars: Imperial Assault"
"""

import _pickle as pickle

from swia.model.dice import Die

__author__ = "Valerio Di Gregorio"
__copyright__ = "Copyright 2018, Valerio Di Gregorio"
__date__ = '2018-04-02'


class Roll:

    def __init__(self, color):
        self._die = Die.create(color)
        self._face = self._die.roll()
        self._times = 0

    @property
    def die(self):
        return self._die

    @property
    def face(self):
        return self._face

    @property
    def rerolled(self):
        return self._times > 0

    def reroll(self, face=None, simulated=False):
        if self.rerolled:
            raise RuntimeError("Can't reroll a die twice.")
        if face is None:
            face = self._die.roll()
        self._face = face
        if not simulated:
            self._times += 1

    def apply(self, action):
        for attribute, value in self._die.get_face(self._face).items():
            setattr(action, attribute, getattr(action, attribute, 0) + value)

    def revert(self, action):
        for attribute, value in self._die.get_face(self._face).items():
            setattr(action, attribute, getattr(action, attribute, 0) - value)


class Action:

    def __init__(self, name, context, cost=1):
        """
        Create an action.
        :param name: Name of the action.
        :param cost: Cost of the action.
        """
        self.context = context
        self._name = name
        self._cost = cost

    def _do_perform(self):
        """
        Abstract method for performing the action.
        """
        raise NotImplementedError()

    def perform(self):
        """
        Perform the action.
        :return: True if the action has been performed. Otherwise False.
        """
        if self.context.actions > self._cost:
            self._do_perform()
            self.context.actions -= self._cost
            return True
        return False


class Attack(Action):

    def __init__(self, context):
        """
        Create an attack action.
        """
        super().__init__('Attack', context, 1)

        # Attributes
        self.pierce = 0
        self.accuracy = 0
        self.damage = 0
        self.surge = 0
        self.block = 0
        self.evade = 0
        self.dodge = 0

        # Operational
        self.rolls = {'attack': [], "defense": []}
        self.rerolls_priority = {'attack': [], "defense": []}
        self._surge_abilities = []
        self.miss = False

        # Stats
        self.total_damage = 0
        self.avoidance = 0
        self.surge_left = 0
        self.no_rerolls_total_damage = None

        # Attack
        self.current_step = 1
        self.steps = {
            1: Attack.declare,
            2: Attack.roll,
            3: Attack.reroll,
            4: Attack.apply_modifiers,
            5: Attack.spend_surges,
            6: Attack.check_accuracy,
            7: Attack.calculate_damage,
        }

    def _do_perform(self):
        self.simulate()
        self._calculate_avoidance()

    def simulate(self):
        """
        Perform the action.
        """
        while True:
            step = self.steps.get(self.current_step, None)
            if step is None:
                break
            step(self)
            self.current_step += 1

    def _calculate_avoidance(self):
        # save stats
        total_damage = self.total_damage
        surge_left = self.surge_left
        no_rerolls_total_damage = self.no_rerolls_total_damage

        # assess blocked damage
        blocked_damage = self.block - self.pierce if self.block > self.pierce else 0
        avoided_damage = self.damage if blocked_damage > self.damage else blocked_damage

        # repeat steps 5-7 as if no evade and dodges were applied
        self.current_step = 5
        self.evade = 0
        self.dodge = 0
        self.simulate()

        # assess evaded/dodged damage
        avoided_damage += self.total_damage - total_damage

        # revert stats
        self.total_damage = total_damage
        self.avoidance = avoided_damage
        self.surge_left = surge_left
        self.no_rerolls_total_damage = no_rerolls_total_damage

    def declare(self):
        """
        Declare target (step 1).
        """
        for ability in self.context.attacker.get_abilities(action='attack', trigger=self.current_step) + \
                       self.context.defender.get_abilities(action='defense', trigger=self.current_step):
            ability.apply(self)

    def roll(self):
        """
        Roll dice (step 2).
        """
        for ability in self.context.attacker.get_abilities(action='attack', trigger=self.current_step) + \
                       self.context.defender.get_abilities(action='defense', trigger=self.current_step):
            ability.apply(self)

        for pool_type, pool in [('attack', self.context.attacker.attack_pool),
                                ('defense', self.context.defender.defense_pool)]:
            if pool is not None:
                for die in pool:
                    roll = Roll(die)
                    roll.apply(self)
                    self.rolls[pool_type].append(roll)

    def reroll(self):
        """
        Reroll dice (step 3).
        """

        def simulate_rerolls(side):
            total = {}
            current = 0
            dump = pickle.dumps(self, -1)
            for i, r in enumerate(self.rolls[side]):
                for f in range(r.die.faces):
                    attack = pickle.loads(dump)
                    attack.rolls[side][i].revert(attack)
                    attack.rolls[side][i].reroll(f)
                    attack.rolls[side][i].apply(attack)
                    attack.current_step += 1
                    attack.simulate()
                    if i not in total:
                        total[i] = 0
                    total[i] += attack.total_damage
                    if f == r.face:
                        current = attack.total_damage
            p = sorted(total.items(), key=lambda t: (t[1], t[0]), reverse=True)
            return p, current

        n_rerolls = {'attack': 0, 'defense': 0}
        for a in self.context.attacker.get_abilities(ability_type='reroll',
                                                     action='attack',
                                                     trigger=self.current_step) + \
                 self.context.defender.get_abilities(ability_type='reroll',
                                                     action='defense',
                                                     trigger=self.current_step):
            n_rerolls['attack'] += a.attack
            n_rerolls['defense'] += a.defense

        self.rerolls_priority = {}
        for reroll_type in ['attack', 'defense']:
            if n_rerolls[reroll_type] > 0:
                self.rerolls_priority[reroll_type], self.no_rerolls_total_damage = \
                    simulate_rerolls(reroll_type)

        for ability in self.context.attacker.get_abilities(action='attack', trigger=self.current_step) + \
                       self.context.defender.get_abilities(action='defense', trigger=self.current_step):
            ability.apply(self)

    def apply_modifiers(self):
        """
        Apply modifiers (step 4).
        """
        for ability in self.context.attacker.get_abilities(action='attack', trigger=self.current_step) + \
                       self.context.defender.get_abilities(action='defense', trigger=self.current_step):
            ability.apply(self)

    def spend_surges(self):
        """
        Spend surges (step 5).
        """
        # TODO: Parametric priority
        priority = ['damage', 'pierce']

        # retrieve available surges
        self.surge_left = self.surge - self.evade if self.surge > self.evade else 0
        for a in self._surge_abilities:
            self.surge_left -= a.cost

        # retrieve list of applicable abilities not yet applied
        # TODO handle anything different than attacker's surge abilities that applies at this step
        abilities = self.context.attacker.get_abilities(ability_type='surge',
                                                        action='attack',
                                                        trigger=self.current_step)
        for a in self._surge_abilities:
            if a in abilities:
                abilities.remove(a)

        # check if it's possible to fulfill the accuracy gap
        # TODO: Prioritize recovery effects
        gap = self._get_accuracy_gap(self.context.attacker.attack_type, self.context.attack_range)
        accuracy_abilities = []
        if gap > 0:
            surge_left = self.surge_left
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
                self.surge_left -= ability.cost
            self.surge_left = surge_left

        if gap <= 0:
            # if we can fulfill the accuracy gap, let's apply all the selected surge abilities
            for ability in accuracy_abilities:
                ability.apply(self)
                self.surge_left -= ability.cost
                self._surge_abilities.append(ability)
                abilities.remove(ability)

        # spend remaining surges
        # TODO: Prioritize conditions
        ability = self.get_best_ability(abilities, priority)
        while ability is not None:
            ability.apply(self)
            self.surge_left -= ability.cost
            self._surge_abilities.append(ability)
            abilities.remove(ability)
            ability = self.get_best_ability(abilities, priority)

    def check_accuracy(self):
        """
        Check accuracy (step 6).
        """
        self.miss = self._get_accuracy_gap(self.context.attacker.attack_type, self.context.attack_range) > 0

    def calculate_damage(self):
        """
        Calculate damage (step 7).
        """
        self.miss = self.miss or (self.dodge > 0)
        if self.miss:
            self.total_damage = 0
        else:
            block = self.block - self.pierce if self.block > self.pierce else 0
            self.total_damage = self.damage - block if self.damage > block else 0

        if self.no_rerolls_total_damage is None:
            self.no_rerolls_total_damage = self.total_damage

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
