from random import betavariate

from matplotlib import pyplot

alpha = 5
beta = 10
data = [betavariate(alpha, beta) for i in range(65536)]

pyplot.hist(data, bins=256)
pyplot.title('betavariate distribution')
pyplot.show()