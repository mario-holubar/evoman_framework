####################
# Use this file to run a known solution for an algorithm 1-5 times (default 1)
# The solution file must be located in the solutions folder and follow the following naming format: algorithm_e#.txt or algorithm_e#.pkl
# Where algorithm = NEAT or SANE, and # is the enemy number 1-8
# Alternatively, change the name in the code to specify a different file

# User arguments: 
#   1) algorithm (NEAT or SANE) 
#   2) enemy number (1-8) 
#   3) number of games to run (1-5) (default: 1)

# The framework creates a directory based on 'experiment_name' where it saves the evoman logs and output
# The program will output a file that contains the individual gain per iteration as well as the average gain over all iterations

####################

# imports framework
import sys, os
import numpy as np
from statistics import mean
sys.path.insert(0, 'evoman') 
from environment import Environment
from NEAT_controller import NeatController
from demo_controller import player_controller
import pickle

# Read command line arguments
if not(len(sys.argv) > 2 and len(sys.argv) < 6):
    sys.exit("Error: please specify:\n1) the algorithm (NEAT or SANE or ESP)\n2)the enemy (1-8) OR the enemies, 123 = enemy 1, 2\n3) the number of games to run (1-5) (default: 1)\n4) If you want to play against all enemies, add 'all'. This will find a solutionfile based on the enemies specified, and run it against all 8 enemies.")

# First argument must indicate the algorithm - 'NEAT' or 'SANE'
algorithm = sys.argv[1]

if algorithm == 'neat': 
    algorithm = 'NEAT'

if algorithm == 'sane': 
    algorithm = 'SANE'

if algorithm == 'esp':
    algorithm = 'ESP'

if not(algorithm == 'NEAT' or algorithm == 'SANE' or algorithm == 'ESP'):
    sys.exit("Error: please specify the algorithm using 'NEAT' or 'SANE'.")


# Second argument must specify the enemy to be trained on - integer from 1 - 8
try:
    enemy = int(sys.argv[2])
except TypeError:
    sys.exit("Error: please specify the enemy using an integer from 1 to 8.")
    
# Check if one or multiple enemies were provided
if enemy > 0 and enemy < 9:
    mode = 'no'
    print("You have selected the following settings:\nAlgorithm:", algorithm, "\nMultiple mode?", mode, "\nEnemy: ", enemy)
else:
    mode = 'yes'
    enemy = str(enemy)
    enemies = []
    # Add all enemies to a list
    for e in enemy:
        if int(e) < 9:
            enemies.append(int(e))
    print("You have selected the following settings:\nAlgorithm:", algorithm, "\nMultiple mode?", mode, "\nEnemies: ", enemies)


# Third argument must specify how many times to run the solution - integer between 1 and 5 (optional)
if len(sys.argv) > 3:
    try:
        iterations = int(sys.argv[3])
    except TypeError:
        sys.exit("Error: please specify how many games to run using an integer between 1 and 5. Default: 1")
    
    #print("Third argument: ", iterations)
        
    if not(iterations > 0 and iterations < 6):
        sys.exit("Error: please specify how many games to run using an integer between 1 and 5. Default: 1")
else:
    iterations = 1

# Fourth argument should be 'all' if running on all 8 enemies (optional)
all = 'no'
if len(sys.argv) == 5:
    all_enemies = [1,2,3,4,5,6,7,8]
    enemies = [1]
    mode = 'no'
    all = 'yes'
    print("Running against all 8 enemies")

print("\n")
print(iterations, "game(s) will be played.")


# Create relevant file names and environment
# Default experiment name. Comment to specify your own. Cleanest to start with optimizations/
experiment_name = "specialists/" + algorithm + "_e" + str(enemy) + "_i" + str(iterations)
#experiment_name = "optimizations/[insert name here]"

# Default solutionfile. Comment to specify your own
solutionfile = "solutions/" + algorithm + "_e" + str(enemy) + ".pkl"
#solutionfile = "solutions/[insert name here]"

gain_path = experiment_name + "/gain.txt"
print("Logs will be saved at:", experiment_name)
print("Individual gain will be saved at:", gain_path)
print("Make sure that the required file containing the solution is found at", solutionfile)

if not os.path.exists(experiment_name):
    os.makedirs(experiment_name)

# Select controller according to the algorithm
if algorithm == 'NEAT': control = NeatController()
else:
    (n_neurons, sane_weights) = pickle.load(open(solutionfile, 'rb'))
    control = player_controller(n_neurons)

if all == 'no': 
    enemies = [enemy]
    
env = Environment(experiment_name=experiment_name,
                  multiplemode=mode,
                  playermode="ai",
                  enemies = enemies,
				  player_controller= control,
			  	  speed="fastest", # fastest or normal
				  enemymode="static",
				  level=2)

# Search for solution
if not os.path.exists(solutionfile):
    sys.exit("No solution found.")

# select solution
if algorithm == "NEAT":
    sol = pickle.load(open(solutionfile, "rb"))
else:
    sol = sane_weights

# clear gain file in case of previous data
file = open(gain_path, "a")
file.truncate(0)

list_gain = []
if all == 'yes':
    for game in all_enemies:
        env.update_parameter("enemies", [game])
        f, p, e, t = env.play(sol)
        gain = p - e
        list_gain.append(gain)
        file = open(gain_path, "a")
        file.write(str(gain))
        file.write("\n")
        file.close()
else:    
    for it in range(1,iterations+1):
        print('\n ITERATION NUMBER '+str(it)+' \n')
        # speed up runs after the first one
        if it == 2: env.update_parameter("speed", "fastest")
        
        f, p, e, t = env.play(sol)
        
        # calculate individual gain
        #energy_player = env.get_playerlife()
        #energy_enemy = env.get_enemylife()
            
        gain = p - e
        print("Individual gain for iteration", it, "is", str(gain))
        
        # save to file
        file = open(gain_path, "a")
        file.write(str(gain))
        file.write("\n")
        file.close()
            
        # add to list
        list_gain.append(gain) 

    # Calculate average if applicable
    if it > 1:
        average = mean(list_gain)
        file = open(gain_path, "a")
        file.write("AVERAGE: ")
        file.write(str(average))
        file.close()
    