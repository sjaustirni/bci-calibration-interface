# Brain-Computer Interface calibration interface

An EMG-controlled interface for BCI calibration with a gamification mode powered via [Brainflow](https://brainflow.org/).

This interface has two modes:
* An instruction-only interface with no feedback
* A gamified interface with EMG feedback

The goal of this project is to provide an interface for subjects performing motor imagery tasks. The gamification mode is intended to provide a more engaging experience for subjects.

## Installation

* Clone the repository
* Install the dependencies with `pip install -r requirements.txt`

## Usage
* Run the interface with `python main.py`
  * There are three scenes available:
    * `--mode setup` will allow you to find the correct EMG threshold for the subject
    * `--mode instruction` will display the scene with bare motor imagery instructions
    * `--mode game` will display the scene with the gamified interface
  * There are a couple of options available, consult `python main.py --help` for more information