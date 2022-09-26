####################
# This file can be used to calculate the average and standard deviation for mean and max fitness per generation, over 10 runs
# Given a directory path that includes files consisting of mean, maximum fitness of each generation per line
# The file names should contain the numbers from 0 to 9 for run 1-10, the rest of the name does not matter
# As long as it only contains that one number and no other numbers

# User arguments: 
#   1) algorithm (NEAT or SANE) 
#   2) enemy number (1-8) 
#   3) path to the data files (default: data/algorithm_e#.txt where algorithm = standard or SANE and # is the enemy number)

# The output file will be saved in the given directory containing average_mean, std_mean, average_max, std_max

# To test, data/standard_e1 contains 10 files with some random data to run the program on. 
# Run Python calculate_stats.py standard 1
####################

import numpy as np
import sys, os, fnmatch
from statistics import mean 
import matplotlib.pyplot as plt

# Read command line arguments
if not(len(sys.argv) == 3 or len(sys.argv) == 4):
    sys.exit("Error: please specify:\n1) the algorithm (NEAT or SANE)\n2) the enemy (1-8)\n3) the path to the data files (default: data/algorithm_e# where algorithm = 'NEAT' or 'SANE' and # is the enemy number)")

# First argument must indicate the algorithm - 'standard' or 'SANE'
algorithm = sys.argv[1]

if algorithm == 'sane': 
    algorithm = 'SANE'

if algorithm == 'neat': 
    algorithm = 'NEAT'

#print("First argument: ", algorithm)

if not(algorithm == 'NEAT' or algorithm == 'SANE'):
    sys.exit("Error: please specify the algorithm using 'NEAT' or 'SANE'.")

# Second argument must specify the enemy to be trained on - integer from 1 - 8
try:
    enemy = int(sys.argv[2])
except TypeError:
    sys.exit("Error: please specify the enemy using an integer from 1 to 8.")
    
#print("Second argument: ", enemy)

if not(enemy > 0 and enemy < 9):
    sys.exit("Error: please specify the enemy using an integer from 1 to 8.")
    
# Third argument must specify the path containing the data files (optional)
if (len(sys.argv) == 4):
    path = sys.argv[3]

    if not os.path.exists(path):
        sys.exit("Error: please specify a valid path, for example data/NEAT_e3 for the NEAT algorithm, 3rd enemy.")
else:
    path = "data/" + algorithm + "_e" + str(enemy)


print("Calculating average and std of 10 runs for", algorithm, "algorithm against enemy", str(enemy) + " using data in", path)

# Dictionary that will contain key-value pairs where the key is the run # and value is the list of contents
run_dict = {}
# Read files with data from all 10 runs
for it in range(0,10):
    pattern = "*" + str(it) + "*.txt"
    for file in os.listdir(path):
        # For the matching file, add the content to the dictionary as a list
        if fnmatch.fnmatch(file, pattern):
            file_path = path + "/" + file
            with open(file_path) as f:
                run_dict[it] = f.read().splitlines()
            
# Create output file
output_file = path + "/#output.txt"
print("Results will be saved at", output_file)
out = open(output_file, "a")
out.truncate(0) # clear file
out.write("average_mean std_mean average_max std_max\n")

# Create empty lists
list_average_mean = np.array([])
list_std_mean = np.array([])
list_average_max = np.array([])
list_std_max = np.array([])


generations = len(run_dict[0])
# Loop through each generation
for generation in range(0, generations):
    list_mean = []
    list_max = []
    # Loop through each run
    for run in range(0,10):
        both = run_dict[run][generation].split()
        list_mean.append(float(both[0]))
        list_max.append(float(both[1]))
    # Calculate average and std
    average_mean = mean(list_mean)
    std_mean = np.std(list_mean)
    average_max = mean(list_max)
    std_max = np.std(list_max)
    
    # Write results to file
    stats = str(average_mean) + " " + str(std_mean) + " " + str(average_max) + " " + str(std_max) + "\n"
    out.write(stats)
    
    # Save results in list
    list_average_mean = np.append(list_average_mean, average_mean)
    list_std_mean = np.append(list_std_mean, std_mean)
    list_average_max = np.append(list_average_max, average_max)
    list_std_max = np.append(list_std_max, std_max)
    
out.close()
print("Calculations successfull")
print("Creating line plot..")

# Create fitness plot
# Shows average and std of the mean and max fitness per generation

plt.plot(list_average_mean, color = 'red', label='mean')
plt.fill_between(range(len(list_average_mean)), list_average_mean - list_std_mean, 
                 list_average_mean + list_std_mean, color = 'red', alpha=0.1, label="_noLegend_")

plt.plot(list_average_max, color= 'blue', label='max')
plt.fill_between(range(len(list_average_max)), list_average_max-list_std_max, 
                 list_average_max + list_std_max, color = 'blue', alpha=0.1, label="_noLegend_")

plt.xlabel("Generation", fontsize=17)
plt.ylabel("Fitness", fontsize=17)
title = "Fitness plot of " + algorithm + " algorithm against enemy " + str(enemy)
plt.title(title, fontsize=15)
plt.legend(loc="upper left", fontsize=15)

plt.show()



# -> 10 runs per enemy with the same algorithm parameters etc. is required for the report
# for the report, we calculate the average and std for the mean and maximum of the fitness, per generation
    # SO for each generation, and each run: 
    # 1. What is the mean fitness of the population in this generation?
    # 2. What is the maximum fitness of the population in this generation?
    
    # THEN for each generation:
    # 1. What is the AVERAGE across all runs of the mean fitness in this generation?
    # 2. What is the AVERAGE across all runs of the maximum fitness in this generation?
    
    # Then do the same for standard deviation per generation
    
# each of these 10 runs will come up with a 'best solution' (= highest player energy or individual gain), so we have 10 'best solutions' per enemy for each algorithm
# run each solution 5 times (using run_specialist.py)