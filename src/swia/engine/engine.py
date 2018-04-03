"""
skirmish_engine
Engine module for "Star Wars: Imperial Assault"
"""

import random
import sys

__author__ = "Valerio Di Gregorio"
__copyright__ = "Copyright 2018, Valerio Di Gregorio"
__date__ = '2018-04-03'


class Context:
    def __init__(self, attacker, defender, attack_range=1, sequence=None, seed=None):
        """
        Create a simulator engine.
        :param seed: Seed for the RNG.
        """
        random.seed(random.randrange(sys.maxsize) if seed is None else seed)
        self.sequence = [] if sequence is None else sequence
        self.actions = 0
        self.damage = 0
        self.runs = 0
        self.attacker = attacker
        self.defender = defender
        self.attack_range = attack_range
        self.stats = {
            "total_damage": {},
            "over_surging": {}
        }

    def collect_attack_results(self, attack):
        """
        Collect results of an attack.
        :param attack: The attack that produced results.
        """
        self.stats['total_damage'][attack.total_damage] = self.stats['total_damage'].get(attack.total_damage, 0) + 1
        self.stats['over_surging'][attack.surge_left] = self.stats['over_surging'].get(attack.surge_left, 0) + 1


class Engine:

    @staticmethod
    def simulate(context):
        """
        Simulate an attack.
        :param context: Context of execution.
        :return: Results of the attack.
        """
        context.actions = 2
        for action_type in context.sequence:
            action_type().perform(context)
        context.runs += 1
