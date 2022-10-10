####################
# This file creates a boxplot for BOTH algorithms against ONE enemy.
# So, the boxplot contains two boxes, one for NEAT, one for SANE
####################

import numpy as np
import matplotlib.pyplot as plt

# GAINS FOR ENEMY 3
list_gain_NEAT = [38, 46, 64, 32, 58, 
                  66, 42, 36, 32, 60] # ONE MORE NEEDED

list_gain_SANE = [32, 56, 44, 20, 32,
                  28, 46, 14, 40, 28]

# GAINS FOR ENEMY 4
# list_gain_NEAT = [50.8, 50.2, 50.2, 24.4, 33.4, 
#              47.8, 53.8, 52, 47.2, 56.2] 

# list_gain_SANE = [68.2, -30, -30, -30, -10,
#                   -40, -40, 19.6, -30, -60]

# GAINS FOR ENEMY 6
# list_gain_NEAT = [38.2, 43.6, 78.4, 53.8, 49.6,
#              45.4, 38.8, 29.2, 74.2, 85.0] 

# list_gain_SANE = [57.18, 57.4, 66.49, 65.82, 48.38,
#                   66.14, 66.57, 65.43, 55.33, 66.29]


both = [list_gain_NEAT, list_gain_SANE]

plt.boxplot(both, labels=['NEAT', 'SANE'])

# Change number to match the enemy the data is for
plt.title("Individual gain of NEAT and SANE against enemy 3", fontsize=15)
plt.ylabel("Individual gain", fontsize=17)
plt.xticks(fontsize=17)
plt.show()