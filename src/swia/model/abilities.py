"""
abilities
Abilities module for "Star Wars: Imperial Assault"
"""

import _pickle as pickle

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
            'passive': Ability,
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

    def can_apply(self, attack):
        """
        Check if the ability is applicable.
        :param attack: The attack where the ability is performed.
        :return: True if the ability can be applied. False otherwise.
        """
        return True

    def apply(self, attack):
        """
        Apply this reroll to the attack.
        :param attack: The attack where the ability is performed.
        :return: True if reroll was possible. False otherwise.
        """
        for reroll_type, n in [('attack', self.attack), ('defense', self.defense)]:
            if reroll_type in attack.rerolls_priority:
                priority = attack.rerolls_priority[reroll_type]
                for k, dmg in priority if reroll_type == self.action else reversed(priority):
                    if n == 0:
                        return True
                    roll = attack.rolls[reroll_type][k]
                    if self.can_apply(attack) and (roll is not None) and not roll.rerolled:
                        if reroll_type == self.action:
                            if dmg / 6 < attack.no_rerolls_total_damage:
                                return True
                        else:
                            if dmg / 6 > attack.no_rerolls_total_damage:
                                return True
                        roll.revert(attack)
                        roll.reroll()
                        roll.apply(attack)
                        n -= 1
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
        self.from_attribute = json['from']
        self.to_attribute = json['to']
        self.min_amount = json.get('min', None)
        self.max_amount = json.get('max', None)
        self._skip = False
        super().__init__(json)

    def get_conversion_range(self, attack):
        """
        Retrieve the range of units that can be converted during this attack.
        :param attack: The attack where the conversion is performed.
        :return: The range of units that can be converted as a tuple (min, max).
                 None range if conversion can't be applied.
        """
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

    def can_apply(self, attack):
        """
        Check if the ability is applicable.
        :param attack: The attack where the conversion is performed.
        :return: True if the ability can be applied. False otherwise.
        """
        if self._skip:
            return False
        n = getattr(attack, self.from_attribute['attribute'], 0)
        r = self.get_conversion_range(attack)
        if r is None:
            return False
        c = self.from_attribute.get('amount', 0)
        if c == 0:
            return True
        return n > r[0]

    def _do_apply(self, attack, n):
        if n > 0:
            c = self.from_attribute.get('amount', 0)
            k = 0 if c == 0 else n // c * c
            if k != 0:
                setattr(attack, self.from_attribute['attribute'],
                        getattr(attack, self.from_attribute['attribute'], 0) - k)
            c = self.to_attribute.get('amount', 0)
            k = 0 if c == 0 else n // c * c
            if k != 0:
                setattr(attack, self.to_attribute['attribute'],
                        getattr(attack, self.to_attribute['attribute'], 0) + k)

    def apply(self, attack):
        """
        Apply this conversion to the attack.
        :param attack: The attack where the conversion is performed.
        :return: True if conversion was possible. False otherwise.
        """

        def simulate_conversion(rng):
            total = {}
            self._skip = True
            dump = pickle.dumps(attack, -1)
            for i in rng:
                a = pickle.loads(dump)
                self._do_apply(a, i)
                a.simulate()
                total[i] = a.total_damage
            self._skip = False
            return sorted(total.items(), key=lambda t: (t[1], t[0]), reverse=True)

        if self._skip:
            return False
        r = self.get_conversion_range(attack)
        if r is None:
            return False
        mn, mx = r
        n = mx
        if mn != mx:
            priority = simulate_conversion(range(mn, mx + 1))
            n = {
                'attack': priority[0][0],
                'defense': priority[-1][0],
            }.get(self.action, None)
            if n is None:
                raise AttributeError(self.action)
        self._do_apply(attack, n)
        return True
