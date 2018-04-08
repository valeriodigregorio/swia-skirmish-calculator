"""
test_cardloader
Test suite for swia.utils.cardloader module.
"""

import unittest
from parameterized import parameterized
from swia.model.cardloader import CardLoader

__author__ = "Valerio Di Gregorio"
__copyright__ = "Copyright 2018, Valerio Di Gregorio"
__date__ = '2018-04-02'


class TestCardLoader(unittest.TestCase):

    def setUp(self):
        self.loader = CardLoader()

    @parameterized.expand([
        [None, None, TypeError],
        [-1, None, IndexError],
        [999999, None, IndexError],
        [22, "Chewbacca", None],
    ])
    def test_get_deployment_card(self, i, result, exc_type):
        try:
            card = self.loader.get_deployment_card(i)
            self.assertEqual(result, card['data']['name'])
        except (IndexError, TypeError) as e:
            self.assertTrue(type(e) is exc_type)

    @parameterized.expand([
        [None, None, TypeError],
        [-1, None, IndexError],
        [999999, None, IndexError],
        [96, "Lure of the Dark Side", None],
    ])
    def test_get_command_card(self, i, result, exc_type):
        try:
            card = self.loader.get_command_card(i)
            self.assertEqual(result, card['name'])
        except (IndexError, TypeError) as e:
            self.assertTrue(type(e) is exc_type)
