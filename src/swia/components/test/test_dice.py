"""
test_dice
Test suite for swia.components.dice module.
"""

import unittest
from parameterized import parameterized
from swia.components.dice import Die

__author__ = "Valerio Di Gregorio"
__copyright__ = "Copyright 2018, Valerio Di Gregorio"
__date__ = '2018-04-02'


class TestDie(unittest.TestCase):

    @parameterized.expand([
        [{}, AttributeError],
        [{'a': [1, 2], 'b': [1]}, AttributeError],
        [{'a': [1, 2], 'b': [3, 4]}, None]
    ])
    def test_init(self, attributes, exc_type):
        try:
            Die('test', attributes)
        except AttributeError as e:
            self.assertTrue(type(e) is exc_type)
