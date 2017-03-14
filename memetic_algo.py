import sys
from app.GeneticAlgorithmPureTT import GeneticAlgorithmPureTT
import utils.load_data as load_data
from app.FitnessFunctionTT import FitnessFunctionTT as fftt


# def main():


runtime = sys.argv[-1]

data = load_data.load(sys.argv[1:-1])
fitness_model = fftt(data)
#
mutation_prob = 0.001
pop_size = 1
ga = GeneticAlgorithmPureTT(data, pop_size, mutation_prob,
                            fitness_model=fitness_model)



    # pass

#
# if __name__ == "__main__":
#     main()
