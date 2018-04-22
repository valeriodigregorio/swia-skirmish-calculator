"""
abilities
Abilities module for "Star Wars: Imperial Assault"
"""

from swia.engine.actions import Attack

__author__ = "Valerio Di Gregorio"
__copyright__ = "Copyright 2018, Valerio Di Gregorio"
__date__ = '2018-04-02'


class Ability:

    @staticmethod
    def create(data, *args, **kwargs):
        """
        Create an ability from data.
        :param data: Data of the ability.
        :param args: Additional arguments for the specific ability type.
        :param kwargs: Additional keyword arguments for the specific ability type.
        :return: An instance of the ability object.
        """
        ability_type = {
            'defensive_passive': PassiveAbility,
            'offensive_passive': PassiveAbility,
            'defensive_reroll': RerollAbility,
            'offensive_reroll': RerollAbility,
            'defensive_conversion': ConversionAbility,
            'offensive_conversion': ConversionAbility,
            'surge': SurgeAbility
        }.get(data['type'], None)
        if ability_type is None:
            raise ValueError(f"Unsupported ability type '{data['type']}'.")
        return ability_type(data, *args, **kwargs)

    def __init__(self, ability, cost=0):
        """
        Create an ability
        :param ability: Data that describes the ability.
        :param cost: Cost of the ability. Measurement unit depends on the type of the ability.
        """
        self._type = ability.get('type', None)
        if self._type is None:
            raise ValueError(self._type)
        self._cost = cost
        self._effects = ability.get('effects', {})
        self._conditions = set(ability.get('conditions', []))

    @property
    def cost(self):
        """
        Retrieve the cost of the ability.
        :return: Cost of the ability.
        """
        return self._cost

    @property
    def conditions(self):
        """
        Retrieve the list of conditions applied by this ability.
        :return: Set of condition names.
        """
        return self._conditions

    @property
    def effects(self):
        """
        Retrieve the list of effects applied by this ability.
        :return: Mapping of effect name to amount applied.
        """
        return self._effects

    def get_effect(self, name):
        """
        Retrieve the amount of a specific effect applied using the ability.
        :param name: Name of the effect.
        :return: The amount of the effect applied by the ability if used.
        """
        return self._effects.get(name, 0)

    def can_apply_condition(self, name):
        """
        Check if a specific condition is applied using the ability.
        :param name: Name of the condition.
        :return: True if the ability can apply the condition. False otherwise.
        """
        return name in self._conditions

    def can_apply_conditions(self, names):
        """
        Check if a specific conditions are applied using the ability.
        :param names: A list of condition names.
        :return: A tuple with the applicability of each conditions.
        """
        return tuple(self.can_apply_condition(name) for name in names)

    def can_apply(self, availability):
        """
        Check if the ability is applicable.
        :param availability: Units available to pay the cost of the ability.
        :return: True if the ability can be applied. False otherwise.
        """
        return (availability if availability > 0 else 0) >= self.cost

    def apply(self, action):
        """
        Apply the ability to the action.
        :param action: The action where the ability is performed.
        """
        raise NotImplementedError()


class PassiveAbility(Ability):

    def __init__(self, ability):
        """
        Create a passive ability
        :param ability: Data that describes the ability.
        """
        ability_type = ability['type']
        if ability_type != 'offensive_passive' and ability_type != 'defensive_passive':
            raise ValueError(ability_type)
        super().__init__(ability)

    def apply(self, action):
        """
        Apply the ability to the action.
        :param action: The action where the ability is performed.
        """
        # TODO: Handle action triggers
        action.accuracy += self.get_effect('accuracy')
        action.damage += self.get_effect('damage')
        action.surge += self.get_effect('surge')
        action.pierce += self.get_effect('pierce')
        action.block += self.get_effect('block')
        action.evade += self.get_effect('evade')
        action.dodge += self.get_effect('dodge')
        return True


class SurgeAbility(Ability):

    def __init__(self, ability):
        """
        Create a surge ability
        :param ability: Data that describes the ability.
        """
        ability_type = ability['type']
        if ability_type != 'surge':
            raise ValueError(ability_type)
        cost = ability.get('cost', {}).get('surge', 0)
        if cost == 0:
            raise ValueError(f"Surge ability can't have cost zero.")
        super().__init__(ability, cost)

    def apply(self, attack):
        """
        Apply this surge ability to the attack.
        :param attack: The attack where the ability is performed.
        """
        if type(attack) is not Attack:
            raise TypeError("Can't apply a surge ability to an action that isn't an attack action.")
        if self.can_apply(attack.surge_left):
            attack.surge_left -= self.cost
            attack.accuracy += self.get_effect('accuracy')
            attack.damage += self.get_effect('damage')
            attack.surge += self.get_effect('surge')
            attack.pierce += self.get_effect('pierce')
            attack.block += self.get_effect('block')
            attack.evade += self.get_effect('evade')
            attack.dodge += self.get_effect('dodge')
            attack.surge_abilities.append(self)
            return True
        return False


class RerollAbility(Ability):

    def __init__(self, ability):
        ability_type = ability['type']
        if ability_type != 'defensive_reroll' and ability_type != 'offensive_reroll':
            raise ValueError(ability_type)
        self.attack = ability.get('attack', 0)
        self.defense = ability.get('defense', 0)
        if self.attack + self.defense == 0:
            raise ValueError(f"Reroll ability can't reroll zero dice.")
        super().__init__(ability)

    def apply(self, roll):
        """
        Apply this reroll to the attack.
        :param roll: The roll to reroll.
        :return: True if reroll was possible. False otherwise.
        """
        if roll is None or roll['times'] > 0:
            return False
        roll['face'] = roll['die'].roll()
        roll['times'] += 1
        return True


class ConversionAbility(Ability):

    def __init__(self, ability):
        # TODO: Handle conversions
        pass

    def apply(self, attack):
        """
        Apply this conversion to the attack.
        :param attack: The attack where the conversion is performed.
        """
        if type(attack) is not Attack:
            raise TypeError("Can't apply a conversion to an action that isn't an attack action.")
        # TODO: Handle conversions
        return False
