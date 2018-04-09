"""
test_actions
Test suite for swia.engine.actions module.
"""

import unittest

from parameterized import parameterized

from swia.engine.actions import Attack
from swia.engine.engine import Context
from swia.model.groups import Group

__author__ = "Valerio Di Gregorio"
__copyright__ = "Copyright 2018, Valerio Di Gregorio"
__date__ = '2018-04-02'


def make_context(attacker_abilities={}, defender_abilities={}, surge_abilities=[], attack_type="melee", attack_range=1):
    attacker = {
        "data": {"name": "Attacker", "modes": ["Skirmish"], "traits": [], "affiliation": "Rebel"},
        "extras": {"attack": {"type": attack_type, "pool": []},
                   "abilities": [{"type": "offensive_passive", "effects": {}}]}}
    defender = {
        "data": {"name": "Attacker", "modes": ["Skirmish"], "traits": [], "affiliation": "Imperial"},
        "extras": {"defense": {"pool": []},
                   "abilities": [{"type": "defensive_passive", "effects": {}}]}}
    for k, v in attacker_abilities.items():
        attacker['extras']['abilities'][0]['effects'][k] = v
    for a in surge_abilities:
        attacker['extras']['abilities'].append(a)
    for k, v in defender_abilities.items():
        defender['extras']['abilities'][0]['effects'][k] = v
    return Context(Group(attacker, []), Group(defender, []), attack_range, [Attack], 0)


class TestAttack(unittest.TestCase):

    @parameterized.expand([
        [{}, {}],
        [{"damage": 1, "surge": 1, "accuracy": 2}, {"block": 1, "evade": 1, "dodge": 0}]
    ])
    def test_declare(self, attacker_abilities, defender_abilities):
        attack = Attack()
        context = make_context(attacker_abilities, defender_abilities)
        attack.declare(context)
        for a in ["pierce", "damage", "surge", "accuracy"]:
            self.assertEqual(attacker_abilities.get(a, 0), getattr(attack, a))
        for a in ["block", "evade", "dodge"]:
            self.assertEqual(defender_abilities.get(a, 0), getattr(attack, a))

    @parameterized.expand([
        [{}, {}],
        [{"damage": 1, "surge": 1, "accuracy": 2}, {"block": 1, "evade": 1, "dodge": 0}]
    ])
    def test_roll(self, attacker_abilities, defender_abilities):
        attack = Attack()
        context = make_context(attacker_abilities, defender_abilities)
        attack.declare(context)
        attack.roll(context)
        for a in ["damage", "surge", "accuracy"]:
            self.assertEqual(attacker_abilities.get(a, 0), getattr(attack, a))
        for a in ["block", "evade", "dodge"]:
            self.assertEqual(defender_abilities.get(a, 0), getattr(attack, a))

    # TODO: test_spend_surges

    @parameterized.expand([
        [{}, "melee", 1, True],
        [{}, "melee", 1, True],
        [{}, "melee", 2, False],
        [{}, "reach", 1, True],
        [{}, "reach", 2, True],
        [{}, "reach", 3, False],
        [{}, "ranged", 1, False],
        [{"accuracy": 3}, "ranged", 2, True],
        [{"accuracy": 3}, "ranged", 3, True],
        [{"accuracy": 3}, "ranged", 4, False]
    ])
    def test_check_accuracy(self, attacker_abilities, attack_type, attack_range, hit):
        attack = Attack()
        context = make_context(attacker_abilities, attack_type=attack_type, attack_range=attack_range)
        attack.declare(context)
        attack.check_accuracy(context)
        self.assertEqual(hit, not attack.miss)

    @parameterized.expand([
        [{}, {}, 0],
        [{"damage": 1}, {}, 1],
        [{"damage": 1}, {"dodge": 1}, 0],
        [{"damage": 1}, {"evade": 1}, 1],
        [{"damage": 1}, {"block": 1}, 0],
        [{"damage": 1}, {"block": 2}, 0],
        [{"damage": 1, "pierce": 1}, {}, 1],
        [{"damage": 1, "pierce": 1}, {"block": 1}, 1],
        [{"damage": 1, "pierce": 1}, {"block": 2}, 0],
        [{"damage": 1, "pierce": 1}, {"block": 3}, 0],
    ])
    def test_calculate_damage(self, attacker_abilities, defender_abilities, total_damage):
        attack = Attack()
        context = make_context(attacker_abilities, defender_abilities)
        attack.declare(context)
        attack.calculate_damage(context)
        self.assertEqual(total_damage, attack.total_damage)
