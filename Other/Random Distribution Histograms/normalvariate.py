from random import normalvariate

from matplotlib import pyplot

mu = 100
sigma = 50
data = [normalvariate(mu, sigma) for i in range(65536)]

pyplot.hist(data, bins=256)
pyplot.title('normalvariate distribution')
pyplot.show()