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

## Progress
At the moment the genomes are being trained with a screenshot to input method. The average score of all the genomes are quite low, but occasionally there are breakthroughs where an agent is almost beating the first level.

## ToDo
* Create a direct Python-Lua-FCEUX interface. This way it will be possible to read the emulator RAM memory directly. Reading the values of the game, the location of the objects, as well as the ability to advance the emulation frame by frame will maximize the precision, and remove all the ambiguity from the currently sampled down screenshot of the game. Currently have a working Lua-to-Python client-host socket connection. The aim is to have a FCEUX(emulation) <> Lua(RAM reading and emulation control) <> Python(neuroevolution) interface.


# Update 07.05

## Changes:
* Implemented the FCEUX <> Lua <-socket-> Python interface. Therefore:
  * Complete direct control over the emulation;
  * The emulation is two/three times faster than before;
  * No more dependency on screen capture, this means the neuron network receives 100% accurate data input of the game, the      location of objects and statuses. Also the emulation/neuroevolution can be left to run in the background without interruptions.
* Changed the fitness function;
* Changed the running output;

## Progress
The evolution now is a lot faster and more configurations can be tested in a shorter amount of time. Will update if new breakthroughs happen.

## ToDo
* Test different activation functions.
Currently the neuroevolution runs on the 'relu' activation function. Which usually lets the agent take the most confident action, but only one button press at a time. The 'sigmoid' function can prove useful - it would let the agent press more than one button at once. For this I will need to change the action processing -> sending to lua -> receiving and activating at lua.
* Test different population sizes and species compatibility thresholds.
This would result in differently sized specieism and/or with smaller population a faster generation turn-around, which means more mutations.
* Test different mutation rates and starting hidden neuron numbers.
Higher mutation rates would over time speed up the growth of connections/neurons. The other possibility is to kickstart the neuron networks with more hidden neurons from the start.
* Implement a plotting function, which can plot the species' stagnation and fitness levels. Also this could be sent with the status updates through email.
* Implement a graphical view of the neurons firing on the game screen?


# Update 07.09

## Changes:
* Added plotting functions to plot speciation bars and fitness graphs over generations:

![Speciation](https://s8.postimg.cc/i5utfbeh1/plot.png)

![Fitness_change_over_generations](https://s8.postimg.cc/lpgr549h1/fitplot.png)

The plots are then sent to my email with updates after each generation.
