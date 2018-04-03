"""
test_groups
Test suite for swia.model.groups module.
"""

import unittest

from parameterized import parameterized

from swia.model.groups import Group

__author__ = "Valerio Di Gregorio"
__copyright__ = "Copyright 2018, Valerio Di Gregorio"
__date__ = '2018-04-02'


class TestGroups(unittest.TestCase):

    @parameterized.expand([
        [{"data": {"name": "C", "modes": ["Campaign"]},
          "extras": {}},
         [],
         None, RuntimeError],

        [{"data": {"name": "C", "modes": ["Skirmish"], "traits": ["Skirmish Upgrade"]},
          "extras": {}},
         [],
         None, RuntimeError],

        [{"data": {"name": "C", "modes": ["Skirmish"], "traits": ["Hunter"], "affiliation": "Rebel"},
          "extras": {}},
         [],
         "C", None],

        [{"data": {"name": "C", "modes": ["Skirmish"], "traits": ["Hunter"], "affiliation": "Rebel"},
          "extras": {}}, [{}, {}],
         None, RuntimeError],

        [{"data": {"name": "C", "modes": ["Skirmish"], "traits": ["Hunter"], "affiliation": "Rebel"},
          "extras": {}},
         [{"data": {"name": "U", "modes": ["Campaign"]},
           "extras": {}}],
         None, RuntimeError],

        [{"data": {"name": "C", "modes": ["Skirmish"], "traits": ["Hunter"], "affiliation": "Rebel"},
          "extras": {}},
         [{"data": {"name": "U", "modes": ["Skirmish"], "traits": ["Hunter"]},
           "extras": {}}],
         None, RuntimeError],

        [{"data": {"name": "C", "modes": ["Skirmish"], "traits": ["Hunter"], "affiliation": "Rebel"},
          "extras": {}},
         [{"data": {"name": "U", "modes": ["Skirmish"], "traits": ["Skirmish Upgrade"], "affiliation": "Imperial"},
           "extras": {}}],
         None, RuntimeError],

        [{"data": {"name": "C", "modes": ["Skirmish"], "traits": ["Hunter"], "affiliation": "Rebel"},
          "extras": {}},
         [{"data": {"name": "U", "modes": ["Skirmish"], "traits": ["Skirmish Upgrade"], "affiliation": "Rebel"},
           "extras": {}}],
         "C + U", None],

        [{"data": {"name": "C", "modes": ["Skirmish"], "traits": ["Hunter"], "affiliation": "Rebel"},
          "extras": {}},
         [{"data": {"name": "U", "modes": ["Skirmish"], "traits": ["Skirmish Upgrade"], "affiliation": "Neutral"},
           "extras": {}}],
         "C + U", None]
    ])
    def test_init(self, card, upgrades, name, exc_type):
        try:
            group = Group(card, upgrades)
            self.assertEquals(name, group.name)
        except RuntimeError as e:
            self.assertTrue(type(e) is exc_type)

    @parameterized.expand([
        [{"data": {"name": "C", "modes": ["Skirmish"], "traits": ["Hunter"], "affiliation": "Rebel"},
          "extras": {"abilities": [{"type": "surge", "cost": {"surge": 1}, "effects": {"pierce": 2}},
                                   {"type": "defensive_passive", "effects": {"block": 1}}]}},
         [{"data": {"name": "U", "modes": ["Skirmish"], "traits": ["Skirmish Upgrade"], "affiliation": "Neutral"},
           "extras": {"abilities": [{"type": "offensive_passive", "effects": {"damage": 1}},
                                    {"type": "surge", "cost": {"surge": 2}, "effects": {"damage": 2}}]}}],
         1, 2, 1, 1]
    ])
    def test_get_abilities(self, card, upgrades, surge_1, surge_2, off_passive, def_passive):
        group = Group(card, upgrades)
        self.assertEquals(0, len(group.get_abilities('surge', 0)))
        self.assertEquals(surge_1, len(group.get_abilities('surge', 1)))
        self.assertEquals(surge_2, len(group.get_abilities('surge', 2)))
        self.assertEquals(surge_2, len(group.get_abilities('surge', 3)))
        self.assertEquals(surge_2, len(group.get_abilities('surge')))
        self.assertEquals(off_passive, len(group.get_abilities('offensive_passive')))
        self.assertEquals(off_passive, len(group.get_abilities('offensive_passive', 0)))
        self.assertEquals(off_passive, len(group.get_abilities('offensive_passive', 1)))
        self.assertEquals(off_passive, len(group.get_abilities('offensive_passive', -1)))
        self.assertEquals(def_passive, len(group.get_abilities('defensive_passive')))
        self.assertEquals(def_passive, len(group.get_abilities('defensive_passive', 0)))
        self.assertEquals(def_passive, len(group.get_abilities('defensive_passive', 1)))
        self.assertEquals(def_passive, len(group.get_abilities('defensive_passive', -1)))
