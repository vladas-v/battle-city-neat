import numpy as np
import time
import sys
import neat
import os
import pickle
import visualize
import socket
from gmail import report_gmail


def shoot():
    conn.send("A\n".encode())


def drive_left():
    conn.send("left\n".encode())


def drive_right():
    conn.send("right\n".encode())


def drive_up():
    conn.send("up\n".encode())


def drive_down():
    conn.send("down\n".encode())


def nothing():
    conn.send("nothing\n".encode())


def get_fitness(score, frames, eagle_dead):
    frames = frames / 100
    fitness = int(((frames * score) / 100) + frames)
    if eagle_dead == "false":
        bonus = int(frames * frames / 10)
        print("ZERO LIVES LEFT. GAME OVER.")
        print("BASE SURVIVED - BONUS POINTS: {}".format(bonus))
        fitness += bonus
    else:
        print("BASE DESTROYED. GAME OVER.")
    print("FITNESS = {}".format(fitness))
    print("===============================")
    return fitness


def eval_genome(genome, config):
    net = neat.nn.FeedForwardNetwork.create(genome, config)
    # net = neat.nn.RecurrentNetwork.create(genome, config)

    while True:
        received = conn.recv(4096).decode().split(",")
        if received[0] != "end":
            inputs = np.array(received).astype(int)
        else:
            frames = int(received[1])
            score = int(received[2])
            eagle_dead = received[3]
            break

        inputs = np.true_divide(inputs, 255)
        action = net.activate(inputs)
        action_array = np.array(action)
        ind = np.unravel_index(np.argmax(action_array, axis=None), action_array.shape)[0]
        if action == [0, 0, 0, 0, 0]:
            ind = 9
            nothing()
        if ind == 0:
            shoot()
        elif ind == 3:
            drive_left()
        elif ind == 4:
            drive_right()
        elif ind == 2:
            drive_down()
        elif ind == 1:
            drive_up()

    fitness = get_fitness(score, frames, eagle_dead)

    return fitness


def eval_genomes(genomes, config):
    genome_num = 0
    for genome_id, genome in genomes:
        genome_num += 1
        print("RUNNING GENOME NUMBER {}".format(genome_num))
        genome.fitness = eval_genome(genome, config)


def run():
    s = socket.socket()
    port = 1247
    host = "127.0.0.1"

    s.bind((host, port))
    print("Waiting for connection...")

    s.listen()
    global conn
    conn, addr = s.accept()
    print("Connection accepted from " + repr(addr[1]))

    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config')
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)

    print('Creating population...')
    pop = neat.Population(config)
    # pop = neat.Checkpointer.restore_checkpoint('neat-checkpoint-196')
    stats = neat.StatisticsReporter()
    pop.add_reporter(stats)
    pop.add_reporter(neat.StdOutReporter(True))
    pop.add_reporter(neat.Checkpointer(5, 3600))

    # print('Evaluating genomes...')

    winner = pop.run(eval_genomes)

    # Save the winner.
    with open('winner-recurrent', 'wb') as f:
        pickle.dump(winner, f)

    print(winner)

    visualize.plot_stats(stats, ylog=True, view=True, filename="feedforward-fitness.svg")
    visualize.plot_species(stats, view=True, filename="feedforward-speciation.svg")

    node_names = {-1: 'x', -2: 'dx', -3: 'theta', -4: 'dtheta', 0: 'control'}
    visualize.draw_net(config, winner, True, node_names=node_names)

    visualize.draw_net(config, winner, view=True, node_names=node_names,
                       filename="winner-feedforward.gv")
    visualize.draw_net(config, winner, view=True, node_names=node_names,
                       filename="winner-feedforuuward-enabled.gv", show_disabled=False)
    visualize.draw_net(config, winner, view=True, node_names=node_names,
                       filename="winner-feedforward-enabled-pruned.gv", show_disabled=False, prune_unused=True)


if __name__ == '__main__':
    run()
