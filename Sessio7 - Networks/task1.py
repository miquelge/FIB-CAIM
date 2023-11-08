from igraph import Graph 
from igraph import plot 
import random
import matplotlib.pyplot as plot
import math

def main():
    n = 1100
    coefficientsClust = []
    avgShortestPaths = []
    probabilities = [0.0001, 0.001, 0.001, 0.001, 0.001, 0.001,
    0.01, 0.01, 0,01, 0.01, 0.01, 0.01, 0.1, 0.1, 0.1, 0.1, 1, 1, 1, 1]
    print(len(probabilities))
    firstCC = 0
    firstASP = 0
    for i in range(0, len(probabilities)):
        wattsStrogats = Graph.Watts_Strogatz(1, n, 3, probabilities[i])
        #Calcular global transitivity aka clustering coefficient
        coefficientsClust.append(wattsStrogats.transitivity_undirected())
        if(i == 0):
            firstCC = coefficientsClust[0]
        coefficientsClust[i] /= firstCC

        avgShortestPaths.append(wattsStrogats.average_path_length(unconn=True))
        #Calcular average shortest path
        if(i == 0):
            firstASP = avgShortestPaths[0]
        avgShortestPaths[i] /= firstASP #normalizar

    print("Clustering Coefficients")
    print(coefficientsClust)
    print()
    print("Average Shortest Paths")
    print(avgShortestPaths)
    print()
    plot.plot(probabilities, coefficientsClust, 's', probabilities, avgShortestPaths, 'o')
    plot.xlabel('Probability')
    plot.xscale('log')
    plot.savefig('plot_task_1.png', bbox_inches='tight')
    plot.show()

main()

##