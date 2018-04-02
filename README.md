# "Star Wars: Imperial Assault" Skirmish Calculator

## Installation

Download the code from the repository:

`git clone https://github.com/valeriodigregorio/swia-skirmish-calculator.git`

You are suggested to use Continuum Anaconda (https://www.continuum.io/downloads) and also install all the requirements:

`pip install -r requirements.txt`

## Usage

~~~~
$ python swia-skirmish-calculator.py -h
usage: swia-skirmish-calculator.py [-h]

Star Wars Imperial Assault Calculator.

optional arguments:
  -h, --help            show this help message and exit
~~~~

## Development guidelines

### Pre-Commit Hook

Install the pre-commit hook from your workspace root using the following command:

`ln -s ../../pre-commit.sh .git/hooks/pre-commit`

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