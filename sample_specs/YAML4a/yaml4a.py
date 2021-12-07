from dagsim.base import Graph, Generic
from scipy.stats import beta, binom


def add_if_diseased(base, signal, state):
    return base + (signal if state is True else 0)


def fas_wrapper(signal):
    return binom.rvs(100, signal)


def plate_wrapper(additional):
    output = []
    for i in range(additional[2]):
        output.append(binom.rvs(*additional[:2]))
    return output


diseaseState = Generic(name="diseaseState", function=binom.rvs, additional_params=[1, 0.5])
baseFreq = Generic(name="baseFreq", function=plate_wrapper, additional_params=[[100, 0.1, 10]], plates=["distinctKmers"])
signalPriorP = Generic(name="signalPriorP", function=beta.rvs, additional_params=[0.2, 1], plates=["distinctKmers"])
freq = Generic(name="freq", parents=[baseFreq, signalPriorP, diseaseState], function=add_if_diseased,
               plates=["distinctKmers"])
freqAdditiveSignal = Generic(name="freqAdditiveSignal", parents=[signalPriorP], function=fas_wrapper,
                             plates=["distinctKmers"])

# listOfNodes = [diseaseState, baseFreq, signalPriorP, freq, freqAdditiveSignal]
listOfNodes = [diseaseState, baseFreq]
my_graph = Graph("yaml4a", list_nodes=listOfNodes)
my_graph.draw()
n = my_graph.simulate(num_samples=5, csv_name="test")
print(n)
