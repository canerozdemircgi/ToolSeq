from random import gauss

from matplotlib import pyplot

mu = 100
sigma = 50
data = [gauss(mu, sigma) for i in range(65536)]

pyplot.hist(data, bins=256)
pyplot.title('gauss distribution')
pyplot.show()