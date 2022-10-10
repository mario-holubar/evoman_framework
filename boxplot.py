####################
# This file creates a boxplot for BOTH algorithms against ONE enemy.
# So, the boxplot contains two boxes, one for NEAT, one for SANE
####################

import numpy as np
import matplotlib.pyplot as plt

# Fill in the values for NEAT here
list_gain_NEAT = [32.103, 89.18932, 25.812, 49.1834, 67.1283, 
             49.81934, 84.8192, 91.1230, 48.1903, 85.12903]

# Fill in the values for SANE here
list_gain_SANE = [23.2305, 49.1283, 34.2030, 10.2390, 39.023,
                  59.2903, 34.249, 21.394, 22.2939, 45.1390]

both = [list_gain_NEAT, list_gain_SANE]

plt.boxplot(both, labels=['NEAT', 'SANE'])

# Change number to match the enemy the data is for
plt.title("Individual gain of NEAT and SANE against enemy 3", fontsize=15)
plt.xlabel("Generation", fontsize=17)
plt.ylabel("Individual gain", fontsize=17)
plt.show()