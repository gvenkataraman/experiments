from pylab import plot, show, savefig

coords = [(index, 2 * index) for index in xrange(5)]

for x, y in coords:
    plot(x, y, marker='+', color='r')

savefig('output.gif')
