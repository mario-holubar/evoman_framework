import numpy as np
import pickle
from tqdm import tqdm

class ESP():
    def __init__(self, env, gens, picklepath, logpath, cfg, mode):
        self.env = env
        self.picklepath = picklepath
        self.logpath = logpath
        self.multiple = mode
        self.n_subpopulations = int(cfg['n_subpopulations'])
        self.neurons_per_subpopulation = int(cfg['neurons_per_subpopulation'])
        self.n_networks = int(cfg['n_networks'])
        self.mutation_sigma = float(cfg['mutation_sigma'])

        self.n_inputs = env.get_num_sensors()
        self.n_bias = 1
        self.n_outputs = 5
        self.weights_per_neuron = self.n_inputs + self.n_bias + self.n_outputs
        self.pop = np.random.uniform(-1, 1, (self.n_subpopulations, self.neurons_per_subpopulation, self.weights_per_neuron))
        self.best_network_fitness = 0.0

        with open(logpath, 'w') as logfile:
            logfile.write("")

        self.esp_execute(gens)

    # Create network from list of neuron indices
    def create_network(self, select):
        # Get neurons
        neurons = self.pop[select]
        # Arrange weights to work with demo_controller
        out_slice = self.n_bias + self.n_inputs
        net = np.concatenate([
            neurons[:,:self.n_bias], # hidden neuron bias
            neurons[:,self.n_bias:out_slice], # input weights
            np.zeros(self.n_outputs), # output bias
            neurons[:,out_slice:] # output weights
            ], None)
        return net

    # Create networks and run the simulation, then assign fitness to neurons
    def evaluate(self):
        neuron_fitnesses = np.zeros((self.n_subpopulations, self.neurons_per_subpopulation))
        network_fitnesses = np.zeros(self.n_networks)
        counts = np.zeros((self.n_subpopulations, self.neurons_per_subpopulation))

        for i in tqdm(range(self.n_networks), leave=False):
            # Select random neurons to form a network
            select = np.random.choice(self.neurons_per_subpopulation, self.n_subpopulations)
            select = (np.arange(self.n_subpopulations), select)
            counts[select] += 1
            net = self.create_network(select)
            # Evaluate network
            fitness, _, _, _, = self.env.play(pcont=net)
            if self.multiple == 'yes':
                fitness = self.env.cons_multi(values=fitness)
            network_fitnesses[i] = fitness
            # Save network if it is better than all previous ones
            if fitness > self.best_network_fitness:
                with open(self.picklepath, 'wb') as f:
                    pickle.dump((self.n_subpopulations, net), f)
                self.best_network_fitness = fitness
            # Add fitness to each neuron's cumulative fitness value
            neuron_fitnesses[select] += fitness
        
        # Set counts to be at least 1 to prevent division by 0
        counts = counts + (counts == 0)
        # Return average fitness of each neuron and fitnesses of the networks
        return neuron_fitnesses / counts, network_fitnesses

    # Tournament selection with k=2. sorted_pop should be sorted by fitness from high to low
    def tournament_selection(self, sorted_pop):
        c0 = np.random.randint(0, len(sorted_pop))
        c1 = np.random.randint(0, len(sorted_pop))
        return sorted_pop[min(c0, c1)]

    # One-point crossover of neurons' weights
    def crossover(self, p0, p1):
        '''s = np.random.randint(0, len(p0))
        c0 = p0.copy()
        c0[s:] = p1[s:]
        c1 = p1.copy()
        c1[s:] = p0[s:]
        return c0, c1'''
        s = np.random.choice([0, 1], p0.shape)
        c0 = s * p0 + (1 - s) * p1
        c1 = s * p1 + (1 - s) * p0
        return c0, c1

    # Mutate the whole population by adding some Gaussian noise to all weights
    def mutate_all(self):
        self.pop += np.random.normal(0, self.mutation_sigma, self.pop.shape)

    # Perform parent selection, crossover and mutation
    def new_gen(self, fitnesses):
        '''offspring = list(survivors)
        for i, p0 in enumerate(parents):
            p1 = parents[np.random.randint(i+1)]
            c0, c1 = self.crossover(p0, p1)
            offspring.append(c0)
            offspring.append(c1)'''
        all_offspring = []
        #print(fitnesses.mean(1) - fitnesses.mean())
        for i in range(self.n_subpopulations):
            # Sort population in descending order by fitness (best first)
            sorted_pop = self.pop[i, np.argsort(-fitnesses[i])]
            # Create offspring
            survivors = sorted_pop[:int(0.5*self.neurons_per_subpopulation)]
            parents = sorted_pop[:int(0.25*self.neurons_per_subpopulation)]
            #new = np.random.normal(0, 0.5, (int(0.125*self.neurons_per_subpopulation), self.weights_per_neuron))
            offspring = list(survivors)
            #offspring += list(new)
            for i, p0 in enumerate(parents):
                p1 = parents[np.random.randint(i+1)]
                c0, c1 = self.crossover(p0, p1)
                offspring.append(c0)
                offspring.append(c1)
            '''while len(offspring) < self.neurons_per_subpopulation:
                p0 = self.tournament_selection(parents)
                p1 = self.tournament_selection(parents)
                c0, _ = self.crossover(p0, p1)
                offspring.append(c0)'''
            all_offspring.append(offspring)

        assert(np.array(all_offspring).shape == self.pop.shape)
        self.pop = np.array(all_offspring)
        self.mutate_all()

    # Log fitness stats
    def log(self, gen, network_fitnesses):
        fmin = network_fitnesses.min()
        fmean = network_fitnesses.mean()
        fmax = network_fitnesses.max()
        print(f"Generation {gen + 1} done. min: {fmin:.2f}, max: {fmax:.2f}, avg: {fmean:.2f}")
        with open(self.logpath, 'a') as logfile:
            logfile.write(f"{fmean} {fmax}\n")

    # Run the GA
    def esp_execute(self, n_gens):
        for gen in range(n_gens):
            neuron_fitnesses, network_fitnesses = self.evaluate()
            self.log(gen, network_fitnesses)
            self.new_gen(neuron_fitnesses)