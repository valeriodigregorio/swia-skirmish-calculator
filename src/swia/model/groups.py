"""
groups
Groups module for "Star Wars: Imperial Assault"
"""

from swia.model.abilities import Ability
from swia.model.dice import Die

__author__ = "Valerio Di Gregorio"
__copyright__ = "Copyright 2018, Valerio Di Gregorio"
__date__ = '2018-04-02'


class Group:

    def __init__(self, card, upgrades):
        """
        Create a group.
        :param card: Data of the deployment card.
        :param upgrades: Additional data for the attached skirmish upgrades.
        """
        self._abilities = {}

        # parse deployment card data
        if 'Skirmish' not in card['data'].get('modes', []):
            raise RuntimeError(f"{card['data']['name']} is not a skirmish card!")
        if 'Skirmish Upgrade' in card['data'].get('traits', []):
            raise RuntimeError(f"{card['data']['name']} is a skirmish upgrade!")
        self._add_abilities(card['extras'].get('abilities', []))
        self._affiliation = card['data']['affiliation']
        self._name = [("Elite " if card['data']['elite'] and not card['data']['unique'] else "") + card['data']['name']]

        # parse skirmish upgrade cards data
        # TODO: allow use of more than one upgrade if applicable during the round (e.g. from figure close to this group)
        if len(upgrades) > 1:
            raise RuntimeError(f"Can't attach more than one skirmish upgrade!")
        for upgrade in upgrades:
            if 'Skirmish' not in upgrade['data'].get('modes', []):
                raise RuntimeError(f"{upgrade['data']['name']} is not a skirmish card!")
            if 'Skirmish Upgrade' not in upgrade['data'].get('traits', []):
                raise RuntimeError(f"{upgrade['data']['name']} is a skirmish upgrade!")
            affiliation = upgrade['data']['affiliation']
            if affiliation not in [self._affiliation, 'Neutral']:
                raise RuntimeError(f"{upgrade['data']['name']} is {affiliation} and "
                                   f"can't be attached to a {self._affiliation} deployment card!")
            self._add_abilities(upgrade['extras'].get('abilities', []))
            self._name += [upgrade['data']['name']]

        # set group full name
        self._name = " + ".join(self.name)

        # set attacker's properties
        attack = card['extras'].get('attack', {})
        self._attack_type = attack.get('type', None)
        self._attack_pool = list(Die.create(color) for color in attack.get('pool', []))

        # set defender's properties
        defense = card['extras'].get('defense', {})
        self._defense_pool = list(Die.create(color) for color in defense.get('pool', []))

    @property
    def name(self):
        """
        Retrieve the full name of the group.
        :return: Cost of the ability in surges.
        """
        return self._name

    @property
    def attack_type(self):
        """
        Retrieve the attack type of the group.
        :return: The attack type.
        """
        return self._attack_type

    @property
    def attack_pool(self):
        """
        Retrieve the attack pool of the group.
        :return: A list of attack dice.
        """
        return self._attack_pool

    @property
    def defense_pool(self):
        """
        Retrieve the defense pool of the group.
        :return: A list of defense dice.
        """
        return self._defense_pool

    def _add_abilities(self, abilities):
        """
        Helper method to add abilities to this group.
        :param abilities: List of abilities to add.
        """
        for ability in abilities:
            a = Ability.create(ability)
            if ability['type'] not in self._abilities.keys():
                self._abilities[ability['type']] = []
            self._abilities[ability['type']].append(a)

    def get_abilities(self, ability_type, availability=None):
        """
        Retrieve all the applicable abilities of a specific type.
        :param ability_type: Type of abilities to retrieve.
        :param availability: Units available to pay the cost of the ability. If None the applicability test is skipped.
        :return: All the applicable abilities of the requested type.
        """
        if availability is None:
            return list(self._abilities.get(ability_type, []))
        else:
            return list(a for a in self._abilities.get(ability_type, []) if a.can_apply(availability))
