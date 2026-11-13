from random import weibullvariate

from matplotlib import pyplot

alpha = 1
beta = 1.5
data = [weibullvariate(alpha, beta) for i in range(65536)]

pyplot.hist(data, bins=256)
pyplot.title('weibullvariate distribution')
pyplot.show()