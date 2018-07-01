import cv2
import numpy as np
import win32gui, win32ui, win32con, win32api
import time
import sys
from directkeys import PressKey, ReleaseKey, P, D, Up, Down, Left, Right
from pytesseract import image_to_string
from PIL import Image
import neat
import os
import pickle
import visualize
from gmail import report_gmail

params = list()
params.append(cv2.IMWRITE_PNG_COMPRESSION)
params.append(8)
black_line = np.zeros((1, 52))
region = (49, 99, 672, 722)

d_out =     [1, 0, 0, 0, 0]
up_out =    [0, 1, 0, 0, 0]
down_out =  [0, 0, 1, 0, 0]
left_out =  [0, 0, 0, 1, 0]
right_out = [0, 0, 0, 0, 1]


def shoot():
    PressKey(D)
    time.sleep(0.009)
    ReleaseKey(D)


def drive_left():
    PressKey(Left)
    ReleaseKey(Right)
    ReleaseKey(Down)
    ReleaseKey(Up)


def drive_right():
    PressKey(Right)
    ReleaseKey(Left)
    ReleaseKey(Down)
    ReleaseKey(Up)


def drive_up():
    PressKey(Up)
    ReleaseKey(Right)
    ReleaseKey(Down)
    ReleaseKey(Left)


def drive_down():
    PressKey(Down)
    ReleaseKey(Right)
    ReleaseKey(Left)
    ReleaseKey(Up)


def nothing():
    ReleaseKey(Down)
    ReleaseKey(Right)
    ReleaseKey(Left)
    ReleaseKey(Up)


def grab_screen(region=None, small_nearest=None):
    hwin = win32gui.GetDesktopWindow()

    if region:
        left, top, x2, y2 = region
        width = x2 - left + 1
        height = y2 - top + 1
    else:
        width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
        height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
        left = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
        top = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)

    hwindc = win32gui.GetWindowDC(hwin)
    srcdc = win32ui.CreateDCFromHandle(hwindc)
    memdc = srcdc.CreateCompatibleDC()
    bmp = win32ui.CreateBitmap()
    bmp.CreateCompatibleBitmap(srcdc, width, height)
    memdc.SelectObject(bmp)
    memdc.BitBlt((0, 0), (width, height), srcdc, (left, top), win32con.SRCCOPY)

    signedIntsArray = bmp.GetBitmapBits(True)
    img = np.fromstring(signedIntsArray, dtype='uint8')
    img.shape = (height, width, 4)

    srcdc.DeleteDC()
    memdc.DeleteDC()
    win32gui.ReleaseDC(hwin, hwindc)
    win32gui.DeleteObject(bmp.GetHandle())
    img = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
    if small_nearest:
        resized_img = cv2.resize(img, (0, 0), fx=0.083333, fy=0.083333, interpolation=cv2.INTER_NEAREST)
    else:
        resized_img = cv2.resize(img, (0, 0), fx=0.33333, fy=0.33333)
        # resized_img = img

    return resized_img


def get_match_score(img):
    sharpening_kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
    img = cv2.resize(img, (0, 0), fx=2, fy=2)
    img = cv2.filter2D(img, -1, sharpening_kernel)
    # cv2.imwrite(r"D:\Work\python\battle_city-neat\img\img-{}.png".format(time.time()), img, params)
    img_new = Image.fromarray(img)
    string = image_to_string(img_new)
    if string:
        try:
            return int(string)
        except Exception as e:
            report_gmail(e)
            cv2.imwrite(r"D:\Work\python\battle_city-neat\img\img-{}.png".format(time.time()), img, params)
            sys.exit()
    else:
        return 0


def reset():
    PressKey(P)
    time.sleep(0.1)
    ReleaseKey(P)
    time.sleep(0.5)


def get_fitness(score, time, eagle):
    fitness = ((time * score) / 100) + time
    if eagle:
        fitness += time*time
    return fitness


def countdown(n):
    for i in range(n-1):
        print(i+1)
        time.sleep(1)
    print('GO')


def eval_genome(genome, config):
    print('Creating NN...')
    # net = neat.nn.FeedForwardNetwork.create(genome, config)
    net = neat.nn.RecurrentNetwork.create(genome, config)

    match_time = 0
    do = None
    eagle = True
    reset()
    time.sleep(0.5)
    while True:
        last_time = time.time()
        screen = grab_screen(region=region, small_nearest=True)

        if np.all(black_line == screen[:, 51]):
            nothing()
            print('GAME OVER')
            time.sleep(0.03)
            screen = grab_screen(region=region)
            total_check_line = screen[173]

            while np.all(total_check_line == screen[173]):
                time.sleep(0.03)
                screen = grab_screen(region=region)
            score = get_match_score(screen[50:70])
            print("SCORE = {}".format(score))
            print("MATCH TIME = {} seconds".format(int(match_time)))
            if not eagle:
                print("EAGLE DESTROYED: NO BONUS 300 TO FITNESS\n")
            break
        if screen[51][26] == 0 and eagle:
            print("EAGLE DESTROYED: NO BONUS 300 TO FITNESS\n")
            eagle = False
        screen_norm = screen / 255
        inputs = screen_norm.ravel()
        action = net.activate(inputs)
        action_array = np.array(action)
        # print(action)
        ind = np.unravel_index(np.argmax(action_array, axis=None), action_array.shape)[0]
        if action == [0, 0, 0, 0, 0]:
            ind = 9
            nothing()
            do = 'DOING NOTHING'
        if ind == 0:
            shoot()
            do = 'SHOOTING'
        elif ind == 3:
            drive_left()
            do = 'DRIVING LEFT'
        elif ind == 4:
            drive_right()
            do = 'DRIVING RIGHT'
        elif ind == 2:
            drive_down()
            do = 'DRIVING DOWN'
        elif ind == 1:
            drive_up()
            do = 'DRIVING UP'

        # winname = "Screen"
        # cv2.namedWindow(winname)  # Create a named window
        # cv2.moveWindow(winname, 800, 30)  # Move it to (40,30)
        # cv2.imshow(winname, screen)
        # if cv2.waitKey(25) & 0xFF == ord('q'):
        #    cv2.destroyAllWindows()
        #    break

        loop_time = time.time() - last_time
        print('{} Loop took: [{}]'.format(do, loop_time))
        # print(loop_time)
        match_time += loop_time

    fitness = get_fitness(score, match_time, eagle)
    print("FITNESS = {}".format(fitness))

    return fitness


def eval_genomes(genomes, config):
    for genome_id, genome in genomes:
        genome.fitness = eval_genome(genome, config)


def run():

    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config')
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)

    print('Creating population...')
    # pop = neat.Population(config)
    pop = neat.Checkpointer.restore_checkpoint('neat-checkpoint-168')
    stats = neat.StatisticsReporter()
    pop.add_reporter(stats)
    pop.add_reporter(neat.StdOutReporter(True))
    pop.add_reporter(neat.Checkpointer(1, 3600))

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
    countdown(3)
    run()

    # while True:
    # screen = grab_screen(region=region, small_nearest=True)
    # print(screen[51][26])
    # sys.exit()
    # cv2.imwrite(r"D:\Work\python\battle_city-neat\img\img-{}.png".format(time.time()), screen, params)


