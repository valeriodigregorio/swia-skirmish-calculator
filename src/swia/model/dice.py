"""
dice
Dice module for "Star Wars: Imperial Assault"
"""

import random

__author__ = "Valerio Di Gregorio"
__copyright__ = "Copyright 2018, Valerio Di Gregorio"
__date__ = '2018-04-02'


class Die:

    @staticmethod
    def create(die_type):
        """
        Create a die of a specific type.
        :param die_type: Type of the die.
        :return: An instance of the die object.
        """
        return {
            'blue': Blue(),
            'green': Green(),
            'red': Red(),
            'yellow': Yellow(),
            'black': Black(),
            'white': White(),
        }.get(die_type, None)

    def __init__(self, name, attributes):
        """
        Create a generic die.
        :param name: Name of the die.
        :param attributes: One or more attributes associated to the faces of the die.
        """
        if len(attributes.keys()) == 0:
            raise AttributeError('attributes')
        self.faces = None
        for key, value in attributes.items():
            n = len(value)
            if self.faces is not None and self.faces != n:
                raise AttributeError(f"attributes[{key}]")
            self.faces = n
        self.name = name
        self.attributes = attributes

    def roll(self):
        """
        Roll the die.
        :return: The result of the roll.
        """
        f = random.randint(1, self.faces) - 1
        roll = {}
        for a, v in self.attributes.items():
            roll[a] = v[f]
        return roll

    @staticmethod
    def roll_pool(dice):
        """
        Roll a dice pool and aggregate results.
        :param dice: Dice pool.
        :return: The aggregated results of the roll.
        """
        result = {}
        for die in dice:
            for a, v in die.roll().items():
                result[a] = result.get(a, 0) + v
        return result


class Blue(Die):

    def __init__(self):
        """
        Create a blue die for "Star Wars: Imperial Assault".
        """
        attributes = {
            'damage': [0, 1, 2, 1, 2, 1],
            'accuracy': [2, 2, 3, 3, 4, 5],
            'surge': [1, 0, 0, 1, 0, 0]
        }
        super().__init__('Blue', attributes)


class Green(Die):

    def __init__(self):
        """
        Create a green die for "Star Wars: Imperial Assault".
        """
        attributes = {
            'damage': [0, 1, 2, 1, 2, 2],
            'accuracy': [1, 1, 1, 2, 2, 3],
            'surge': [1, 1, 0, 1, 0, 0],
        }
        super().__init__('Green', attributes)


class Red(Die):

    def __init__(self):
        """
        Create a red die for "Star Wars: Imperial Assault".
        """
        attributes = {
            'damage': [1, 2, 2, 2, 3, 3],
            'accuracy': [0, 0, 0, 0, 0, 0],
            'surge': [0, 0, 0, 1, 0, 0]
        }
        super().__init__('Red', attributes)


class Yellow(Die):

    def __init__(self):
        """
        Create a yellow die for "Star Wars: Imperial Assault".
        """
        attributes = {
            'damage': [0, 1, 2, 1, 0, 1],
            'accuracy': [0, 0, 1, 1, 2, 2],
            'surge': [1, 2, 0, 1, 1, 0]
        }
        super().__init__('Yellow', attributes)


class Black(Die):

    def __init__(self):
        """
        Create a black die for "Star Wars: Imperial Assault".
        """
        attributes = {
            'block': [1, 1, 2, 2, 3, 0],
            'evade': [0, 0, 0, 0, 0, 1],
            'dodge': [0, 0, 0, 0, 0, 0]
        }
        super().__init__('Black', attributes)


class White(Die):

    def __init__(self):
        """
        Create a white die for "Star Wars: Imperial Assault".
        """
        attributes = {
            'block': [0, 1, 0, 1, 1, 0],
            'evade': [0, 0, 1, 1, 1, 0],
            'dodge': [0, 0, 0, 0, 0, 1]
        }
        super().__init__('White', attributes)
