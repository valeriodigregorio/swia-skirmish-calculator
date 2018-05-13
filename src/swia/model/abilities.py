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
    def create(data):
        """
        Create an ability from data.
        :param data: Data of the ability.
        :return: An instance of the ability object.
        """
        ability_type = {
            'surge': SurgeAbility,
            'reroll': RerollAbility,
            'conversion': ConversionAbility,
        }.get(data['type'], None)
        if ability_type is None:
            raise ValueError(f"Unsupported ability type '{data['type']}'.")
        return ability_type(data)

    def __init__(self, json):
        """
        Create an ability
        :param json: Data model that describes the ability in JSON.
        """
        self._type = json.get('type', None)
        if self._type is None:
            raise ValueError(self._type)
        self._model = json
        self.effects = self._model.get('effects', {})
        for key in ['accuracy', 'damage', 'surge', 'pierce', 'block', 'evade', 'dodge']:
            self.effects[key] = self.effects.get(key, 0)

    @property
    def type(self):
        return self._model['type']

    @property
    def trigger(self):
        return self._model['trigger']

    @property
    def action(self):
        return self._model['action']

    def can_apply(self, action):
        """
        Check if the ability is applicable.
        :param action: The action where the ability is performed.
        :return: True if the ability can be applied. False otherwise.
        """
        raise NotImplementedError()

    def apply(self, action):
        """
        Apply the ability to the action.
        :param action: The action where the ability is performed.
        """
        raise NotImplementedError()


class SurgeAbility(Ability):

    def __init__(self, json):
        """
        Create a surge ability
        :param json: Data model that describes the ability in JSON.
        """
        ability_type = json['type']
        if ability_type != 'surge':
            raise ValueError(ability_type)
        super().__init__(json)

    @property
    def cost(self):
        """
        Retrieve the cost of the ability.
        :return: Cost of the ability.
        """
        return self._model.get('cost', 0)

    def can_apply(self, attack):
        """
        Check if the ability is applicable.
        :param attack: The attack where the ability is performed.
        :return: True if the ability can be applied. False otherwise.
        """
        if type(attack) is not Attack:
            return False
        return attack.surge_left >= self.cost

    def apply(self, attack):
        """
        Apply this surge ability to the attack.
        :param attack: The attack where the ability is performed.
        """
        if self.can_apply(attack):
            for key in ['accuracy', 'damage', 'surge', 'pierce', 'block', 'evade', 'dodge']:
                setattr(attack, key, getattr(attack, key) + self.effects[key])
            return True
        return False


class RerollAbility(Ability):

    def __init__(self, json):
        """
        Create a reroll ability
        :param json: Data model that describes the ability in JSON.
        """
        ability_type = json['type']
        if ability_type != 'reroll':
            raise ValueError(ability_type)
        if json.get('attack', 0) + json.get('defense', 0) == 0:
            raise ValueError(f"Reroll ability can't reroll zero dice.")
        super().__init__(json)

    @property
    def attack(self):
        return self._model.get('attack', 0)

    @property
    def defense(self):
        return self._model.get('defense', 0)

    def can_apply(self, roll):
        """
        Check if the ability is applicable.
        :param roll: The roll to reroll.
        :return: True if the ability can be applied. False otherwise.
        """
        return (roll is not None) and (roll['times'] == 0)

    def apply(self, roll):
        """
        Apply this reroll to the attack.
        :param roll: The roll to reroll.
        :return: True if reroll was possible. False otherwise.
        """
        if self.can_apply(roll):
            roll['face'] = roll['die'].roll()
            roll['times'] += 1
            return True
        return False


class ConversionAbility(Ability):

    def __init__(self, json):
        """
        Create a conversion ability
        :param json: Data model that describes the ability in JSON.
        """
        ability_type = json['type']
        if ability_type != 'conversion':
            raise ValueError(ability_type)
        self.offensive = json['action'] == 'attack'
        self.defensive = json['action'] == 'defense'
        if not (self.offensive or self.defensive):
            raise ValueError(ability_type)
        self.from_attribute = json['from']
        self.to_attribute = json['to']
        self.min_amount = json.get('min', None)
        self.max_amount = json.get('max', None)
        super().__init__(json)

    def can_apply(self, attack):
        """
        Apply this conversion to the attack.
        :param attack: The attack where the conversion is performed.
        :return: None if conversion can't be applied. Otherwise the number of conversions that can be applied
                 as a tuple (min, max).
        """
        if type(attack) is not Attack:
            return None
        n = getattr(attack, self.from_attribute['attribute'])
        if n < 0:
            n = 0
        mx = self.max_amount if self.max_amount is not None else n
        mn = self.min_amount if self.min_amount is not None else mx
        if n < mx:
            mx = n
        if n < mn:
            return None
        return mn, mx

    def apply(self, attack, n):
        """
        Apply this conversion to the attack.
        :param attack: The attack where the conversion is performed.
        :param n: Number of units to be converted.
        :return: True if conversion was possible. False otherwise.
        """
        if type(attack) is not Attack:
            raise TypeError("Can't apply a conversion to an action that isn't an attack action.")
        k = n // self.from_attribute.get('quantity', 1)
        n = getattr(attack, self.from_attribute['attribute'])
        c = k * self.from_attribute.get('amount', 0)
        setattr(attack, self.from_attribute['attribute'], n - c)
        n = getattr(attack, self.to_attribute['attribute'])
        c = k * self.to_attribute.get('amount', 0)
        setattr(attack, self.to_attribute['attribute'], n + c)
        return True
