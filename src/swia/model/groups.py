"""
groups
Groups module for "Star Wars: Imperial Assault"
"""
from swia.model.abilities import Ability

__author__ = "Valerio Di Gregorio"
__copyright__ = "Copyright 2018, Valerio Di Gregorio"
__date__ = '2018-04-02'


class Group:

    def __init__(self, card, upgrade=None):
        """
        Create a group.
        :param card: Data of the deployment card.
        :param upgrade: Attached skirmish upgrade.
        """
        if 'Skirmish' not in card['data'].get('modes', []):
            raise RuntimeError(f"{card['data']['name']} is not a skirmish card!")
        if 'Skirmish Upgrade' in card['data'].get('traits', []):
            raise RuntimeError(f"{card['data']['name']} is a skirmish upgrade!")
        self._deployment_card = card

        if upgrade is not None:
            if 'Skirmish' not in upgrade['data'].get('modes', []):
                raise RuntimeError(f"{upgrade['data']['name']} is not a skirmish card!")
            if 'Skirmish Upgrade' not in upgrade['data'].get('traits', []):
                raise RuntimeError(f"{upgrade['data']['name']} is a skirmish upgrade!")
            affiliation = upgrade['data']['affiliation']
            if affiliation not in [card['data']['affiliation'], 'Neutral']:
                raise RuntimeError(f"{upgrade['data']['name']} is {affiliation} and "
                                   f"can't be attached to a {card['data']['affiliation']} deployment card!")
        self._skirmish_upgrade = upgrade

        abilities = card['extras']['abilities'] + \
                    (upgrade['extras']['abilities'] if self._skirmish_upgrade is not None else [])
        self._abilities = [Ability.create(ability) for ability in abilities]

    @property
    def full_name(self):
        """
        Retrieve the full name of the group.
        :return: Cost of the ability in surges.
        """
        parts = []
        if self._deployment_card['data']['elite'] and not self._deployment_card['data']['unique']:
            parts.append("Elite " + self._deployment_card['data']['name'])
        else:
            parts.append(self._deployment_card['data']['name'])
        if self._skirmish_upgrade is not None:
            parts.append(self._skirmish_upgrade['data']['name'])
        return " + ".join(parts)

    @property
    def affiliation(self):
        return self._deployment_card['data']['affiliation']

    @property
    def attack_type(self):
        return self._deployment_card['extras']['attack']['type']

    @property
    def attack_pool(self):
        return self._deployment_card['extras']['attack']['pool']

    @property
    def defense_pool(self):
        return self._deployment_card['extras']['defense']['pool']

    def get_abilities(self, ability_type=None, trigger=None, action=None):
        """
        Retrieve all the abilities with specific filters.
        :param ability_type: The type of the ability.
        :param trigger: The trigger used for filtering out abilities.
        :param action: The action used for filtering out abilities.
        :return: All the abilities with the requested filters.
        """
        return [a for a in self._abilities
                if (ability_type is None or ability_type == a.type)
                and (trigger is None or trigger in a.trigger)
                and (action is None or action in a.action)]
