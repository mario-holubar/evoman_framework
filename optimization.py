####################
# Use this file to run an optimization algorithm: either NEAT or SANE
# Specify the number of runs if you want to run more than one individual optimization

# User arguments: 
#   1) algorithm (NEAT or SANE or ESP)
#   2) enemy number (1-8) or multiple enemies (1-8)
#   3) number of optimizations to run (1-10) (default: 1)

# The program will ask how many generations the algorithm should run

# The experiment name, and therefore location of the logs, is created by default as follows:
# optimizations/[algorithm]_e#_gen# where [algorithm] is NEAT or SANE, e# indicates enemy number and gen# indicates number of generations
# Inside this folder, each individual run will create a folder run# that will contain the logs for this run

# The algorithm will save its best solution in the run# folder. If you want to run this solution separately:
# Move the file to 'solutions' folder and run run_specialist.py
####################

# imports framework
from multiprocessing.sharedctypes import Value
import sys, os
import configparser
from time import time

# Comment this out to show the game window
os.environ["SDL_VIDEODRIVER"] = "dummy"

sys.path.insert(0, 'evoman') 
from environment import Environment
from NEAT_controller import NeatController
from demo_controller import player_controller
from NEAT_specialist import NEAT_Spealist
from SANE_specialist import SANE_Specialist
from ESP import ESP

# Read command line arguments
if len(sys.argv) < 3 or len(sys.argv) > 5:
    sys.exit("Error: please specify:\n1) the algorithm (NEAT, SANE or ESP) \n2) the enemy (1-8) OR the enemies (123 = enemy 1, 2 and 3)\n3) number of individual optimizations (1-10) (default:1)\n4) the number of generations per run (default: 30)")

# First argument must indicate the algorithm - 'NEAT' or 'SANE' or 'ESP'
algorithm = sys.argv[1].upper()
if algorithm not in ['NEAT', 'SANE', 'ESP']:
    sys.exit("Error: please specify the algorithm using 'NEAT' or 'SANE' or 'ESP' for upgraded SANE")

# Load config
if algorithm in ['SANE', 'ESP']:
    config = configparser.RawConfigParser()
    config.read(f'{algorithm}.cfg')
    cfg = dict(config.items(algorithm))

# Second argument must specify the enemy to be trained on - integer from 1 - 8
try:
    enemy = int(sys.argv[2])
except TypeError:
    sys.exit("Error: please specify the enemy using an integer from 1 to 8 OR an integer containing multiple enemies from 1-8 (eg. 123 = enemies 1,2,3).")

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

# Third argument must indicate the number of optimizations to run (default: 1)
if len(sys.argv) >= 4:
    try:
        runs = int(sys.argv[3])
    except TypeError:
        sys.exit("Error: please specify how many optimizations you want to run (1-10). Default: 1")
        
    if not(runs > 0 and runs < 11):
        sys.exit("Error: please specify how many optimizations you want to run (1-10). Default: 1")
else:
    runs = 1

print(runs, "individual experiment(s) will be run.")



# Fourth argument indicates the number of generations per run (default: 30)
if len(sys.argv) >= 5:
    try:
        gens = int(sys.argv[4])
    except TypeError:
        sys.exit("Error: please specify how many generations you want to run. Default: 30")
else:
    gens = 30

# Default experiment name. Comment to specify your own
experiment_name = "optimizations/" + algorithm + "_e" + sys.argv[2] + "_gen" + str(gens)
#experiment_name = "optimizations/[insert name here]"
print("Logs will be saved at:", experiment_name)

if not os.path.exists(experiment_name):
    os.makedirs(experiment_name)
    
# Initialize environment
if mode == 'no':
    enemies = [enemy]

# Select controller according to the algorithm
if algorithm == 'NEAT': control = NeatController()
elif algorithm == 'SANE': control = player_controller(int(cfg['neurons_per_network']))
elif algorithm == 'ESP': control = player_controller(int(cfg['n_subpopulations']))

env = Environment(experiment_name=experiment_name,
                  multiplemode=mode,
                  enemies=enemies,
                  playermode="ai",
                  player_controller=control,            
                  enemymode="static",
                  level=2,
                  logs = "off",
                  speed="fastest")
    
# Run the optimizations the specified number of times
# Each run gets their own folder run# inside the original folder
for it in range(1,runs+1):
    print("\nSTARTING RUN:", it)
    run_name = experiment_name + "/run" + str(it)
    if not os.path.exists(run_name):
        os.makedirs(run_name)
    env.update_parameter("experiment_name", run_name)
    
    # Create a path for the pickle file, so the algorithm knows where to save it
    picklepath = run_name + "/" + algorithm + "_e" + str(enemy) + ".pkl"
    logpath = run_name + "/data_run_" + str(it-1) + ".txt"
    
    tstart = time()
    
    if algorithm == 'NEAT':
        optimizer = NEAT_Spealist(env, gens, picklepath, logpath)
    elif algorithm == 'SANE':
        optimizer = SANE_Specialist(env, gens, picklepath, logpath, cfg)
    elif algorithm == 'ESP':
        optimizer = ESP(env, gens, picklepath, logpath, cfg)
    
    tend = time()
    diff = int(tend - tstart)
    print(f"Total time for run {it}: {diff // 60}:{diff % 60}")
    
    


