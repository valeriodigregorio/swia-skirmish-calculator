"""
skirmish_engine
Engine module for "Star Wars: Imperial Assault"
"""

import random
import sys

from swia.engine.actions import Attack

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
            "over_surging": {},
            "avoidance": {},
            "reroll_impact": {}
        }

    def collect_attack_results(self, attack: Attack):
        """
        Collect results from an attack.
        :param attack: The attack that produced results.
        """
        self._collect_sample('total_damage', attack.total_damage)
        self._collect_sample('avoidance', attack.avoidance)
        self._collect_sample('over_surging', attack.surge_left)
        self._collect_sample('reroll_impact', attack.reroll_impact)

    def _collect_sample(self, pki, sample):
        """
        Helper method to collect a new sample for a KPI.
        :param pki: The PKI for the statistics.
        :param sample: The sample to collect.
        """
        self.stats[pki][sample] = self.stats[pki].get(sample, 0) + 1

    def get_statistics(self, pki):
        """
        Retrieve statistics of a given PKI.
        :param pki: The PKI for the statistics.
        :return: Statistics for the indicator as PDF, CDF and average.
        """
        avg = 0
        mn = min(self.stats[pki].keys())
        mx = max(self.stats[pki].keys())
        pdf = [0] * (abs(mn) + abs(mx) + 1)
        cdf = [0] * len(pdf)
        for i in range(0, len(pdf)):
            m = self.stats[pki].get(mn + i, 0)
            pdf[i] = 100 * m
            avg += i * m
            for j in range(0, i + 1):
                cdf[j] += pdf[i]
            pdf[i] /= self.runs
        for i in range(0, len(pdf)):
            cdf[i] /= self.runs
        avg /= self.runs
        return list(range(mn, mx + 1)), pdf, cdf, avg


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
            action = action_type()
            action.perform(context)
            context.collect_attack_results(action)
        context.runs += 1
