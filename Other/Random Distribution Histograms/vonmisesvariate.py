from random import vonmisesvariate

from matplotlib import pyplot

mu = 0
kappa = 4
data = [vonmisesvariate(mu, kappa) for i in range(65536)]

pyplot.hist(data, bins=256)
pyplot.title('vonmisesvariate distribution')
pyplot.show()