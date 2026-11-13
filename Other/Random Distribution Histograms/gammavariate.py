from random import gammavariate

from matplotlib import pyplot

alpha = 9
beta = 0.5
data = [gammavariate(alpha, beta) for i in range(65536)]

pyplot.hist(data, bins=256)
pyplot.title('gammavariate distribution')
pyplot.show()