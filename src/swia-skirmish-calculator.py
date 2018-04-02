"""
swia-skirmish-calculator
Skirmish Calculator for "Star Wars: Imperial Assault"
"""

import argparse
from swia.utils.cardloader import CardLoader

__author__ = "Valerio Di Gregorio"
__copyright__ = "Copyright 2018, Valerio Di Gregorio"
__date__ = '2018-04-02'


def main():
    """ Main program """
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--attacker",
                        nargs='+', dest="attacker", type=int, required=True,
                        help="IDs of attacker's deployment cards")
    parser.add_argument("-d", "--defender",
                        nargs='+', dest="defender", type=int, required=True,
                        help="IDs of defender's deployment cards")
    args = parser.parse_args()

    loader = CardLoader("lib/imperial-assault-data")
    attacker, attacker_extra = loader.get_deployment_card(args.attacker[0])
    defender, defender_extra = loader.get_deployment_card(args.defender[0])
    print(f'{attacker["name"]} VS {defender["name"]}')


if __name__ == "__main__":
    main()
