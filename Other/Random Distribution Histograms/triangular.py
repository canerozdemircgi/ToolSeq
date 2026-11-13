from random import triangular

from matplotlib import pyplot

low = -2
high = 2
mode = 0
data = [triangular(low, high, mode) for i in range(65536)]

pyplot.hist(data, bins=256)
pyplot.title('triangular distribution')
pyplot.show()