# "Star Wars: Imperial Assault" Skirmish Calculator
A Monte Carlo simulator for "Star Wars" Imperial Assault" skirmish.

## Installation

Download the code from the repository:

`git clone https://github.com/valeriodigregorio/swia-skirmish-calculator.git`

## Usage

You can show at any time the usage by running:

~~~~
$ python swia-skirmish-calculator.py -h
usage: swia-skirmish-calculator.py [-h] -a ATTACKER [ATTACKER ...] -d DEFENDER
                                   [DEFENDER ...] -r RANGE [-n RUNS] [-s SEED]

optional arguments:
  -h, --help            show this help message and exit
  -a ATTACKER [ATTACKER ...], --attacker ATTACKER [ATTACKER ...]
                        IDs of attacker's deployment cards (in order: card,
                        upgrade)
  -d DEFENDER [DEFENDER ...], --defender DEFENDER [DEFENDER ...]
                        IDs of defender's deployment cards (in order: card,
                        upgrade)
  -r RANGE, --range RANGE
                        distance between attacker and defender
  -n RUNS, --runs RUNS  number of runs
  -s SEED, --seed SEED  seed for the RNG
~~~~

In example:

~~~~
$ python.exe swia-skirmish-calculator.py -a 70 -d 25 147 -r 3 -n 5000 -s 0
+-------------------+    +--------------------------------+
| Elite Jet Trooper | VS | Darth Vader + Driven by Hatred |
+-------------------+    +--------------------------------+

[XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX] [100%]

-----------------------------------------------------------
Total damage @ range 3 (5000 runs)
-----------------------------------------------------------

PDF:
0: 30.1%
1: 28.94%
2: 28.38%
3: 11.56%
4: 1.02%

CDF:
0: 100.0%
1: 69.9%
2: 40.96%
3: 12.58%
4: 1.02%

Average: 1.2446 damage(s)

-----------------------------------------------------------
Avoidance @ range 3 (5000 runs)
-----------------------------------------------------------

PDF:
0: 2.2%
1: 10.82%
2: 34.42%
3: 34.8%
4: 15.94%
5: 1.82%

CDF:
0: 100.0%
1: 97.8%
2: 86.98%
3: 52.56%
4: 17.76%
5: 1.82%

Average: 2.5692 damage(s)

-----------------------------------------------------------
Over-surging @ range 3 (5000 runs)
-----------------------------------------------------------

PDF:
0: 89.52%
1: 10.48%

CDF:
0: 100.0%
1: 10.48%

Average: 0.1048 surge(s)

-----------------------------------------------------------
Reroll impact @ range 3 (5000 runs)
-----------------------------------------------------------

PDF:
-1: 5.36%
0: 57.9%
1: 26.32%
2: 9.38%
3: 1.04%

CDF:
-1: 100.0%
0: 94.64%
1: 36.74%
2: 10.42%
3: 1.04%

Average: 0.4284 damage(s)
~~~~

## License

~~~~
Copyright 2018, Valerio Di Gregorio

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
~~~~