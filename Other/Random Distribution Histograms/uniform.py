from random import uniform

from matplotlib import pyplot

low = -2
high = 2
data = [uniform(low, high) for i in range(65536)]

pyplot.hist(data, bins=256)
pyplot.title('uniform distribution')
pyplot.show()