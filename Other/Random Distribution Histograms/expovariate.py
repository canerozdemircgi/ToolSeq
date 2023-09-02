from random import expovariate

from matplotlib import pyplot

lambd = 1.5
data = [expovariate(lambd) for i in range(65536)]

pyplot.hist(data, bins=256)
pyplot.title('expovariate distribution')
pyplot.show()