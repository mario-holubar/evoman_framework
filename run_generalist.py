# 1 ask for algorithm + enemy group (esp, neat, both)
# 2 find folder containing folders of run0 - run9
# create environment with all correct settings
# create loop for all 10 runs
# create loop for all 8 games
# enemy 5 needs 5 games
# for each game, compute gain
# after all 8 games are done, compute average game and store it in file and list

# after all 10 solutions have had their average gain calculated
# if both algorithms: create boxplot with these values
# if one algorithm: print list format containing 10 gain values to file

import sys, os
import numpy as np
from statistics import mean
from os import path
sys.path.insert(0, 'evoman') 
from environment import Environment
from NEAT_controller import NeatController
from demo_controller import player_controller
import pickle

# Comment this out to show the game window
os.environ["SDL_VIDEODRIVER"] = "dummy"

# Read command line arguments
if not(len(sys.argv) == 3):
    sys.exit("Error: please specify:\n1) the algorithm (ESP, NEAT, or BOTH)\n2)the enemy group (123 = enemy 1,2 and 3")


# First argument must indicate the algorithm - 'NEAT' or 'SANE'
algorithm = sys.argv[1].upper()

if not(algorithm in ["NEAT", "ESP", "BOTH"]):
    sys.exit("Error: please specify the algorithm using 'NEAT', 'ESP' or 'BOTH'.")

# Second argument must specify the enemy to be trained on - integer from 1 - 8
try:
    enemy = int(sys.argv[2])
except TypeError:
    sys.exit("Error: please specify the enemy group using an integer containing the enemy numbers.")
    
enemy = str(enemy)

# Create relevant file names and environment
# Default experiment name. Comment to specify your own. Cleanest to start with optimizations/
experiment_name = "best_solutions/" + algorithm + "_e" + enemy
#experiment_name = "optimizations/[insert name here]"

# Solution folder and file name
solutionfolder = "best_solutions/" + algorithm + "_e" + enemy
solutionfile = algorithm + "_e" + enemy + ".pkl"

gain_path = experiment_name + "/gain.txt"
print("Logs will be saved at:", experiment_name)
print("Individual gain will be saved at:", gain_path)
print("Make sure that the run folders containing the best solutions are found at", solutionfolder)

if not os.path.exists(experiment_name):
    os.makedirs(experiment_name)

if algorithm == 'NEAT': control = NeatController()
else: control = player_controller(10)
    
env = Environment(experiment_name=experiment_name,
                  playermode="ai",
                  enemies = [1],
                  player_controller= control,
			  	  speed="fastest", # fastest or normal
				  enemymode="static",
				  level=2)

# List that will contain the average gain of each solution
average_gains = []

# gain file will contain every gain value of each enemy and run
file = open(gain_path, "a")
file.truncate(0)
file = open(gain_path, "a")

for run in range(1,11):
    # Check if there is a solution
    solution_for_run = solutionfolder + "/run" + str(run) + "/" + solutionfile
    print("Loading solution file... " + solution_for_run)
    if path.exists(solution_for_run):
        s = "Gains for run: " + str(run) + "\n"
        file.write(s)
        # Select solution
        if algorithm == "NEAT":
            sol = pickle.load(open(solution_for_run, "rb"))
        else:
            (n_neurons, sane_weights) = pickle.load(open(solution_for_run, 'rb'))
            sol = sane_weights
        
        game_gains = []
        # run games against each enemy
        for game in range(1,9):
            env.update_parameter("enemies", [game])
            if game != 5:
                f, p, e, t = env.play(sol)
                gain = p - e
                s = str(gain) + "\n"
                file.write(s)
                game_gains.append(gain)
            else:
                # run 5 games against enemy 5 to account for randomness
                gains_for_5 = []
                for i in range(0,5):
                    f, p, e, t = env.play(sol)
                    gain = p - e
                    gains_for_5.append(gain)
                # calculate average of the 5 runs
                gain = mean(gains_for_5)
                s = str(gain) + "\n"
                file.write(s)
                game_gains.append(gain)
        average_gain = mean(game_gains)
        average_gains.append(average_gain)
    else: 
        print("Unable to find solution for run", run)
        break

s = "\n\nAverage gains of all runs: \n" + str(average_gains)
file.write(s)
file.close()

print("Average gains of each run: " + str(average_gains))