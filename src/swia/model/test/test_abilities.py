"""
test_abilities
Test suite for swia.model.abilities module.
"""

import unittest
from parameterized import parameterized

from swia.engine.actions import Attack, Action
from swia.model.abilities import Ability, PassiveAbility, SurgeAbility

__author__ = "Valerio Di Gregorio"
__copyright__ = "Copyright 2018, Valerio Di Gregorio"
__date__ = '2018-04-02'


class TestAbility(unittest.TestCase):

    @parameterized.expand([
        [None, None, TypeError],
        [{"type": "invalid"}, None, ValueError],
        [{"type": "offensive_passive"}, PassiveAbility, None]
    ])
    def test_create(self, data, object_type, exc_type):
        try:
            ability = Ability.create(data)
            self.assertEqual(object_type, type(ability))
        except (TypeError, ValueError) as e:
            self.assertTrue(type(e) is exc_type)


class TestPassiveAbility(unittest.TestCase):

    @parameterized.expand([
        [None, TypeError],
        [{"type": "invalid"}, ValueError],
        [{"type": "offensive_passive"}, None],
        [{"type": "defensive_passive"}, None]
    ])
    def test_init(self, data, exc_type):
        try:
            ability = PassiveAbility(data)
            self.assertEqual(PassiveAbility, type(ability))
        except (TypeError, ValueError) as e:
            self.assertTrue(type(e) is exc_type)

    @parameterized.expand([
        [{"type": "offensive_passive"}, True],
        [{"type": "offensive_passive", "effects": {"damage": 1}}, True],
        [{"type": "defensive_passive", "effects": {"block": 2}}, True]
    ])
    def test_apply(self, data, result):
        attack = Attack()
        ability = Ability.create(data)
        self.assertEqual(PassiveAbility, type(ability))
        applied = ability.apply(attack)
        self.assertEqual(result, applied)
        if data['type'] == 'offensive_passive':
            self.assertEqual(data.get('effects', {}).get('damage', 0), attack.damage)
        if data['type'] == 'defensive_passive':
            self.assertEqual(data.get('effects', {}).get('block', 0), attack.block)


class TestSurgeAbility(unittest.TestCase):

    class ActionMock(Action):

        def __init__(self):
            super().__init__('Mock', 0)

        def _do_perform(self, context):
            pass

    @parameterized.expand([
        [None, TypeError],
        [{"type": "invalid"}, ValueError],
        [{"type": "surge"}, ValueError],
        [{"type": "surge", "cost": {"surge": 0}}, ValueError],
        [{"type": "surge", "cost": {"surge": 1}}, None]
    ])
    def test_init(self, data, exc_type):
        try:
            ability = SurgeAbility(data)
            self.assertEqual(SurgeAbility, type(ability))
            self.assertEqual(data['cost']['surge'], ability.cost)
        except (TypeError, ValueError) as e:
            self.assertTrue(type(e) is exc_type)

    @parameterized.expand([
        [{"type": "surge", "cost": {"surge": 1}}, ActionMock(), 0, False, TypeError],
        [{"type": "surge", "cost": {"surge": 1}}, Attack(), 0, False, None],
        [{"type": "surge", "cost": {"surge": 2}}, Attack(), 1, False, None],
        [{"type": "surge", "cost": {"surge": 2}}, Attack(), 2, True, None],
        [{"type": "surge", "cost": {"surge": 2}, "effect": {"damage": 5}}, Attack(), 3, True, None]
    ])
    def test_apply(self, data, action, surge_left, result, exc_type):
        try:
            ability = Ability.create(data)
            self.assertEqual(SurgeAbility, type(ability))
            action.surge_left = surge_left
            applied = ability.apply(action)
            self.assertEqual(result, applied)
            effect = data.get('effects', {}).get('damage', 0) if applied else 0
            self.assertEqual(effect, action.damage)
        except TypeError as e:
            self.assertTrue(type(e) is exc_type)
