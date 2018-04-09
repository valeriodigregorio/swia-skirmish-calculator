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
            "over_surging": {},
            "mitigation": {}
        }

    def collect_attack_results(self, attack):
        """
        Collect results from an attack.
        :param attack: The attack that produced results.
        """
        # assess evaded damage
        evaded_damage = 0
        evaded_surge = attack.surge if attack.evade > attack.surge else attack.evade
        abilities = self.attacker.get_abilities('surge', evaded_surge)
        for a in attack.surge_abilities:
            if a in abilities:
                abilities.remove(a)
        ability = attack.get_best_ability(evaded_surge, abilities, ['damage', 'pierce'])
        while ability is not None:
            evaded_surge -= ability.cost
            evaded_damage += ability.get_effect('damage')
            abilities.remove(ability)
            ability = attack.get_best_ability(evaded_surge, abilities, ['damage', 'pierce'])

        # assess blocked damage
        blocked_damage = attack.block - attack.pierce if attack.block > attack.pierce else 0
        blocked_damage = attack.damage if blocked_damage > attack.damage else blocked_damage

        # collect samples
        self._collect_sample('total_damage', attack.total_damage)
        self._collect_sample('over_surging', attack.surge_left)
        self._collect_sample('mitigation', blocked_damage + evaded_damage)

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
        pdf = [0] * (max(self.stats[pki].keys()) + 1)
        cdf = [0] * len(pdf)
        for i in range(0, len(pdf)):
            m = self.stats[pki].get(i, 0)
            pdf[i] = 100 * m
            avg += i * m
            for j in range(0, i + 1):
                cdf[j] += pdf[i]
            pdf[i] /= self.runs
        for i in range(0, len(cdf)):
            cdf[i] /= self.runs
        avg /= self.runs
        return pdf, cdf, avg


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
