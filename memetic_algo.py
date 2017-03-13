import sys
from app.GeneticAlgorithmPureTT import GeneticAlgorithmPureTT
import utils.load_data as load_data


# def main():


runtime = sys.argv[-1]

data = load_data.load(sys.argv[1:-1])
#
mutation_prob = 0.001
pop_size = 10
ga = GeneticAlgorithmPureTT(data, pop_size, mutation_prob)



    # pass

#
# if __name__ == "__main__":
#     main()
