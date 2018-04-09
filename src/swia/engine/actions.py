"""
actions
Actions module for "Star Wars: Imperial Assault"
"""

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
        self.name = name
        self.cost = cost
        self.pierce = 0
        self.accuracy = 0
        self.damage = 0
        self.surge = 0
        self.block = 0
        self.evade = 0
        self.dodge = 0

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
        self.surge_abilities = []

    def _do_perform(self, context):
        """
        Perform the action.
        :param context: Context of execution.
        """
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
        abilities = context.attacker.get_abilities('offensive_passive')
        for ability in abilities:
            ability.apply(self)
        abilities = context.defender.get_abilities('defensive_passive')
        for ability in abilities:
            ability.apply(self)

    def roll(self, context):
        """
        Roll dice (step 2).
        :param context: Context of execution.
        """
        offense_roll = Die.roll_pool(context.attacker.attack_pool)
        defense_roll = Die.roll_pool(context.defender.defense_pool)
        self.accuracy += offense_roll.get('accuracy', 0)
        self.damage += offense_roll.get('damage', 0)
        self.surge += offense_roll.get('surge', 0)
        self.block += defense_roll.get('block', 0)
        self.evade += defense_roll.get('evade', 0)
        self.dodge += defense_roll.get('dodge', 0)

    def reroll(self, context):
        """
        Reroll dice (step 3).
        :param context: Context of execution.
        """
        # TODO: Handle rerolls
        pass

    def apply_modifiers(self, context):
        """
        Apply modifiers (step 4).
        :param context: Context of execution.
        """
        # TODO: Handle modifiers
        pass

    def spend_surges(self, context):
        """
        Spend surges (step 5).
        :param context: Context of execution.
        """
        # retrieve available surges and abilities
        self.surge_left = self.surge - self.evade if self.surge > self.evade else 0

        # check if it's possible to fulfill the accuracy gap
        # TODO: Prioritize recovery effects
        gap = self._get_accuracy_gap(context.attacker.attack_type, context.attack_range)
        accuracy_abilities = []
        if gap > 0:
            surge_left = self.surge_left
            abilities = context.attacker.get_abilities('surge', surge_left)
            while gap > 0:
                ability = self.get_best_ability(surge_left, abilities, ['accuracy', 'damage', 'pierce'])
                if ability is None:
                    break
                gap -= ability.get_effect('accuracy')
                accuracy_abilities.append(ability)
                abilities.remove(ability)
                surge_left -= ability.cost

        abilities = context.attacker.get_abilities('surge', self.surge_left)
        if gap <= 0:
            # if we can fulfill the accuracy gap, let's apply all the selected surge abilities
            for ability in accuracy_abilities:
                ability.apply(self)
                abilities.remove(ability)

        # spend remaining surges
        # TODO: Prioritize conditions
        ability = self.get_best_ability(self.surge_left, abilities, ['damage', 'pierce'])
        while ability is not None:
            ability.apply(self)
            abilities.remove(ability)
            ability = self.get_best_ability(self.surge_left, abilities, ['damage', 'pierce'])

    def check_accuracy(self, context):
        """
        Check accuracy (step 6).
        :param context: Context of execution.
        """
        self.miss = self._get_accuracy_gap(context.attacker.attack_type, context.attack_range) > 0

    def calculate_damage(self, context):
        """
        Calculate damage (step 7).
        :param context: Context of execution.
        """
        self.miss = self.miss or (self.dodge > 0)
        if self.miss:
            self.total_damage = 0
        else:
            block = self.block - self.pierce if self.block > self.pierce else 0
            self.total_damage += self.damage - block if self.damage > block else 0
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
            result = [{
                'accuracy': a.get_effect('accuracy'),
                'damage': d,
                'pierce': p,
                'ability': a,
            }.get(x, 0) for x in (priority + ['ability'])]
            if sum(result[:-1]) <= 0:
                result[-1] = None
            return tuple(result)

        decorated_abilities = [decorate_ability(a) for a in abilities]
        for decorated_ability in sorted(decorated_abilities, key=lambda a: a[:-1], reverse=True):
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
