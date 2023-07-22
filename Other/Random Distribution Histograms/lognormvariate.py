from random import lognormvariate

from matplotlib import pyplot

mu = 0
sigma = 0.25
data = [lognormvariate(mu, sigma) for i in range(65536)]

pyplot.hist(data, bins=256)
pyplot.title('lognormvariate distribution')
pyplot.show()