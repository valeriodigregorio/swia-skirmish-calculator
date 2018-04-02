"""
cardloader
A card loader for lvisintini/imperial-assault-data collection.
See https://github.com/lvisintini/imperial-assault-data.
"""

import json

__author__ = "Valerio Di Gregorio"
__copyright__ = "Copyright 2018, Valerio Di Gregorio"
__date__ = '2018-04-02'


class CardLoader:

    def __init__(self, path):
        """
        Create a card loader for a cards collection.
        :param path: Path to the cards collection.
        """
        self.data = {}
        for s in ['deployment-cards', 'deployment-extras', 'command-cards']:
            with open(f'{path}/data/{s}.json') as f:
                self.data[s] = json.load(f)

    def _get_card_by_id(self, source, identifier):
        """
        Retrieve a card from the collection by ID.
        :param source: Source of the card.
        :param identifier: ID of the card.
        :return: The card with the specified ID.
        """
        card = self.data[source][identifier]
        if card['id'] != identifier:
            raise IndexError(identifier)
        return card

    def get_deployment_card(self, identifier):
        """
        Retrieve a deployment card from the collection by ID.
        :param identifier: ID of the deployment card.
        :return: The deployment card with the specified ID.
        """
        return self._get_card_by_id('deployment-cards', identifier), \
               self._get_card_by_id('deployment-extras', identifier)

    def get_command_card(self, identifier):
        """
        Retrieve a command card from the collection by ID.
        :param identifier: ID of the command card.
        :return: The command card with the specified ID.
        """
        return self._get_card_by_id('command-cards', identifier)
