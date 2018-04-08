"""
swia-skirmish-calculator
Skirmish Calculator for "Star Wars: Imperial Assault"
"""

import argparse
import sys
import time

from swia.engine.actions import Attack
from swia.engine.engine import Engine, Context
from swia.model.groups import Group
from swia.model.cardloader import CardLoader

__author__ = "Valerio Di Gregorio"
__copyright__ = "Copyright 2018, Valerio Di Gregorio"
__date__ = '2018-04-02'


def get_deployment_card(loader, card, upgrades):
    card = loader.get_deployment_card(card)
    upgrades = [loader.get_deployment_card(i) for i in upgrades]
    return Group(card, upgrades)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--attacker",
                        nargs='+', dest="attacker", type=int, required=True,
                        help="IDs of attacker's deployment cards.")
    parser.add_argument("-d", "--defender",
                        nargs='+', dest="defender", type=int, required=True,
                        help="IDs of defender's deployment cards.")
    parser.add_argument("-r", "--range", dest="range", type=int, required=True,
                        help="Distance between attacker and defender.")
    parser.add_argument("-n", "--runs", dest="runs", type=int, required=False, default=20000,
                        help="Number of runs.")
    parser.add_argument("-s", "--seed", dest="seed", type=int, required=False, default=None,
                        help="Seed for the RNG.")
    args = parser.parse_args()

    loader = CardLoader()
    attacker_card = get_deployment_card(loader, args.attacker[0], args.attacker[1:])
    defender_card = get_deployment_card(loader, args.defender[0], args.defender[1:])

    print(f"+{'-'*(len(attacker_card.name)+2)}+    +{'-'*(len(defender_card.name)+2)}+")
    print(f"| {attacker_card.name} | VS | {defender_card.name} |")
    print(f"+{'-'*(len(attacker_card.name)+2)}+    +{'-'*(len(defender_card.name)+2)}+\n")

    context = Context(attacker_card, defender_card, args.range, [Attack], args.seed)
    n = len(attacker_card.name) + len(defender_card.name) + 3
    start_time = time.time()
    for i in range(args.runs):
        Engine.simulate(context)
        p = ((i + 1) * 100 // args.runs)
        c = ((i + 1) * n // args.runs)
        sys.stdout.write(f"\r[{'X'*c}{' '*(n-c)}] [{'' if p == 100 else ' '}{p}%]")
        sys.stdout.flush()
    print()
    elapsed_time = time.time() - start_time
    print(f"\nElapsed time: {int(elapsed_time*100)/100}s")

    stats = [
        {
            "name": "Total damage",
            "stat": "total_damage",
            "unit": "damage"
        },
        {
            "name": "Over-surging",
            "stat": "over_surging",
            "unit": "surge"
        }
    ]

    for stat in stats:
        print(f"\n{'-'*(len(attacker_card.name)+len(defender_card.name)+12)}")
        print(f"{stat['name']} @ range {args.range} ({args.runs} runs)")
        print(f"{'-'*(len(attacker_card.name)+len(defender_card.name)+12)}")

        total = 0
        for k in range(0, max(context.stats[stat['stat']].keys()) + 1):
            m = context.stats[stat['stat']].get(k, 0)
            print(f"{k}: {100*m/args.runs}%")
            total += k * m
        print(f"\nAverage: {total/args.runs} {stat['unit']}(s)")


if __name__ == "__main__":
    main()
