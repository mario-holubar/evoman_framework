# imports framework
import sys, os
import neat
sys.path.insert(0, 'evoman')
from environment import Environment
import numpy as np
from NEAT_controller import NeatController
from generation_reporter import generation_reporter
import pickle

# np.set_printoptions(threshold=sys.maxsize) # remove console array truncation

# initializes environment with ai player using random controller, playing against static enemy
# default environment fitness is assumed for experiment

# game.state_to_log()  # checks environment state

class NEAT_Spealist():
    def __init__(self, env, gens, picklepath, logpath, mode):
        neat_dir = os.path.dirname(__file__)
        neat_path = os.path.join(neat_dir, "NEAT-config.txt")
        
        self.game = env
        self.gens = gens
        self.picklepath = picklepath
        self.logpath = logpath
        self.multiple = mode
        
        self.neat_execute(neat_path)
        
    # all information from each game state
    # all of this interacts with numpy.float64 out of Environment.py
    def game_state(self, game, x):
        fitness, phealth, ehealth, time = game.play(pcont=x)
        if self.multiple == 'yes':
            fitness = game.cons_multi(values=fitness)
            return fitness
        return fitness

    def genome_evaluation(self, genomes, config):
        for n_gen, x in genomes:
            x.fitness = 0
            x.fitness = self.game_state(self.game, x)

    # engages the NEAT algorithm, see NEAT-Config.txt for details
    def neat_execute(self, neat_config):
        config = neat.config.Config(neat.DefaultGenome,
                                    neat.DefaultReproduction,
                                    neat.DefaultSpeciesSet,
                                    neat.DefaultStagnation,
                                    neat_config)

        # generation divider for dynamic tuning
        gsec1 = 10
        gsec2 = 5
        gsec3 = (10+(self.gens-25))
        if self.gens < 25:
            if self.gens > 14:
                gsec1 = 10
                gsec2 = 5
                gsec3 = (self.gens-15)
            elif self.gens < 4:  # with the current divide less than 4 would cause issues with retaining pops
                sys.exit("Please pick a generation size of 4 or more.")
            else:
                gsec1 = 1
                gsec2 = 1
                gsec3 = (self.gens-2)

        # sets up the starting population
        pop = neat.Population(config)
        
        pop.add_reporter(neat.StdOutReporter(True))
        s = neat.StatisticsReporter()
        pop.add_reporter(s)
        # pop.add_reporter(neat.Checkpointer(self.gens))  # Checkpoints for recovey, inconvenient when running multiple
        # our reporter, to report mean/max fitness for each generation
        pop.add_reporter(generation_reporter(self.logpath))

        # Run first segment of the algorithm
        pop.run(self.genome_evaluation, gsec1)

        # Run second segment of the algorithm
        neat_dir = os.path.dirname(__file__)
        neat_path2 = os.path.join(neat_dir, "NEAT-config2.txt")

        config2 = neat.config.Config(neat.DefaultGenome,
                                    neat.DefaultReproduction,
                                    neat.DefaultSpeciesSet,
                                    neat.DefaultStagnation,
                                    neat_path2)

        pop2 = neat.Population(config2, initial_state=(pop.population, pop.species, pop.generation))

        pop2.add_reporter(neat.StdOutReporter(True))
        pop2.add_reporter(s)
        # pop2.add_reporter(neat.Checkpointer(self.gens))
        pop2.add_reporter(generation_reporter(self.logpath))

        pop2.run(self.genome_evaluation, gsec2)

        # Run third segment of the algorithm
        neat_path3 = os.path.join(neat_dir, "NEAT-config3.txt")

        config3 = neat.config.Config(neat.DefaultGenome,
                                     neat.DefaultReproduction,
                                     neat.DefaultSpeciesSet,
                                     neat.DefaultStagnation,
                                     neat_path3)

        pop3 = neat.Population(config3, initial_state=(pop2.population, pop2.species, pop2.generation))

        pop3.add_reporter(neat.StdOutReporter(True))
        pop3.add_reporter(s)
        # pop2.add_reporter(neat.Checkpointer(self.gens))
        pop3.add_reporter(generation_reporter(self.logpath))

        winner = pop3.run(self.genome_evaluation, gsec3)
        
        # save the winner
        with open(self.picklepath, "wb") as f:
            pickle.dump(winner,f)
            f.close()
        print("Saved the best solution at", self.picklepath)
        
        