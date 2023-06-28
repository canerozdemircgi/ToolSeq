from random import paretovariate

from matplotlib import pyplot

alpha = 3
data = [paretovariate(alpha) for i in range(65536)]

pyplot.hist(data, bins=256)
pyplot.title('paretovariate distribution')
pyplot.show()