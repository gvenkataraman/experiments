import pygraphviz as pgv

G=pgv.AGraph(directed=True)

G.add_edge('a', 'b', label='x')
G.add_edge('a','c', label='y')

G.write('simple.dot')
