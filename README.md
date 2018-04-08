# "Star Wars: Imperial Assault" Skirmish Calculator
A Monte Carlo simulator for "Star Wars" Imperial Assault" skirmish.

## Installation

Download the code from the repository:

`git clone https://github.com/valeriodigregorio/swia-skirmish-calculator.git`

You are suggested to use Continuum Anaconda (https://www.continuum.io/downloads) and also install all the requirements:

`pip install -r requirements.txt`

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
$ python swia-skirmish-calculator.py -a 22 160 -d 25 147 -r 3 -n 20000 -s 0
+-----------------------------+    +--------------------------------+
| Chewbacca + Wookiee Avenger | VS | Darth Vader + Driven by Hatred |
+-----------------------------+    +--------------------------------+

[XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX] [100%]

Elapsed time: 1.74s

---------------------------------------------------------------------
Total damage @ range 3 (20000 runs)
---------------------------------------------------------------------
0: 4.73%
1: 7.855%
2: 15.08%
3: 22.45%
4: 22.865%
5: 16.325%
6: 8.225%
7: 2.15%
8: 0.32%

Average: 3.4541 damage(s)

---------------------------------------------------------------------
Over-surging @ range 3 (20000 runs)
---------------------------------------------------------------------
0: 73.07%
1: 22.12%
2: 4.54%
3: 0.27%

Average: 0.3201 surge(s)
~~~~

## Guidelines

### Pre-Push Hook

Install the pre-push hook from your workspace root using the following command:

`ln -s ../../pre-push.sh .git/hooks/pre-push`

### Unit test run

Run all unit tests with this script:

`./run-test.sh`

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