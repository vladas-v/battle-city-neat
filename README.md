# battle-city-neat
A neuroevolution of augmenting topologies learning algorithm to solve playing a NES game Battle-City

# DISCLAIMER
Full credit to CodeReclaimers for the python implementation of NEAT: https://github.com/CodeReclaimers/neat-python.
I modified some classes to suit my needs better and implemented my own interface with the game. Otherwise the neat core programming was done by CodeReclaimers.

For an overview of NEAT: http://neat-python.readthedocs.io/en/latest/neat_overview.html.

# Work in progress
This is a work in progress. I am currently training the genomes for a few months trying different techniques and configurations.

## What I have done is:
* Implemented a screen capture and processing to suit the neural network input. The screen is captured ~30 times per second, rescaled to a smaller image and reshaped as a vector for the neural network input. I also used tesseract OCR to read the score of the end game screen.
* Created an API to communicate with the FCEUX NES emulator.
* Modified the reporting class to send the status and statistics of each generation through e-mail.
* Modified the checkpointing class to save checkpoints at the start of the generation instead of the end, in which case when loading the checkpoint the generation is starting from scratch. Issue opened: https://github.com/CodeReclaimers/neat-python/issues/132.

## ToDo
* Create a direct Lua-FCEUX API. This way it will be possible to read the the emulator RAM memory directly. Reading the values of the game, the location of the objects, as well as the ability to advance the emulation frame by frame will maximize the precision, and remove all the ambiguity from the currently sampled down screenshot of the game. Currently have a working Lua-to-Python client-host socket connection. The aim is to have a FCEUX(emulation) <> Lua(RAM reading and emulation control) <> Python(neuroevolution) API.


## Progress
At the moment the genomes are being trained with a screenshot to input method. The average score of all the genomes are quite low, but occasionally there are breakthroughs where an agent is almost beating the first level.
