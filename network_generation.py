__author__ = 'smichel', 'ceharvey'

'''
README: modify the values at the bottom of the file 
        (within: if __name__=='__main__') to get VMTR plot output.

Remaining TO-DO: -improve support for representing Moore neighborhood
                 -add settings for additional plot outputs
'''

import igraph # This is the python-igraph package
import argparse
import csv


def setupMoore(numNodes):
    '''Creates a graph structure based on Moore neighborhoods. Auto-adjusts population size to ensure perfect square
    rooting and equalizing edge allocation.'''
    g = igraph.Graph.Lattice([numNodes**(0.5), numNodes**(0.5)], nei=1)

    layout = g.layout_fruchterman_reingold()

    #igraph.Graph.write_svg(g, fname = "stage1moore.svg".format(self.structure), layout = layout) # svg scales much
    # better

    for x in g.vs:
        x["neighbors"] = []
        for y in g.vs:
            if x != y:
                if len([z.index for z in g.vs.select(g.neighbors(x)) if z in g.vs.select(g.neighbors(y))]) >= 2:
                    x["neighbors"].append(y)

    for x in g.vs:
        for y in x["neighbors"]:
            if not g.are_connected(x,y):
                g.add_edge(x,y)
    return g
        
def setupNoNetwork(numNodes):
    '''Creates the desired number of agents, but does not create any edges.'''
    g = igraph.Graph(numNodes)
    return g
    
def setupPowerLaw(numNodes=0, numEdges=0):
    '''Creates a graph with greatly unequal edge distributions. Most nodes will have degree == 0.'''
    g = igraph.Graph.Static_Power_Law(n=numNodes, m = numEdges, exponent_out = 3)
    return g
    
def setupPreferential(numNodes=0, numEdges=0):
    '''Preferential here is based on Barabasi_Albert model. User provides number of nodes and edges desired, and
    this function slightly tweaks the inputs to igraph to create the desired structure.'''
    g = igraph.Graph.Barabasi(n=numNodes, m = numEdges/numNodes)
    return g

def setupRandom(numNodes=0, numEdges=0, probEdges=0):
    '''Random here is an Erdos_Renyi model. User provides number of nodes and either number of edges or probability
    of edges.'''
    if numEdges > 0:
        g = igraph.Graph.Erdos_Renyi(n=numNodes, m = numEdges)

    elif probEdges > 0:
        g = igraph.Graph.Erdos_Renyi(n=numNodes, p = probEdges)
    return g

def setupRingworld(numNodes):
    '''Uses Watts_Strogatz basic values to create a ring-shaped network. Agents are connected only to immediate
    previous and next agent in a ring shape.'''
    g = igraph.Graph.Watts_Strogatz(dim=1, size=numNodes, nei=1, p=0)

    return g

def setupSmallWorld(numNodes, nei=1, probEdges=0):
    '''SmallWorld is based on Watts_Strogatz model. User provides number of nodes (numNodes), distance from each
    neighbor for default connection (nei), and probability of rewiring (probEdges).'''
    g = igraph.Graph.Watts_Strogatz(dim=1, size=numNodes, nei=nei, p = probEdges)
    return g

def setupVonNeumann(numNodes):
    '''Creates a graph structure based on von Neumann neighborhoods. Auto-adjusts population size to ensure perfect
    square rooting.'''
    g = igraph.Graph.Lattice([numNodes**(0.5), numNodes**(0.5)], nei=1)
    return g

def setupNetwork(num_nodes, num_edges, prob_edges, structure):

    ########################################
    #''' VERIFY MINIMUM INPUTS ARE VALID'''#
    ########################################
    if (num_edges == 0 and prob_edges == 0) or (num_edges > 0 and prob_edges > 0):
        print "Please provide a value for numEdges or a value for probEdges. " \
              "One of these is required; you may not supply both."
    elif (prob_edges < 0 or prob_edges > 1) and num_edges == 0:
        print "Please set probEdges to a proportional value between 0 and 1."
    if num_edges == 0:
        print "Please provide a value for numNodes to include in the graph."

    ###############################
    #''' SET NETWORK STRUCTURE '''#
    ###############################
    if num_nodes > 0 and (num_edges > 0 or prob_edges > 0) and structure != "":

        if structure.lower() == "moore":
            g = setupMoore(num_nodes)

        elif structure.lower() == "none":
            g = setupNoNetwork(num_nodes)

        elif structure.lower() == "preferential":
            g = setupPreferential(num_nodes, num_edges)

        elif structure.lower() == "powerlaw":
            g = setupPowerLaw(num_nodes, num_edges)

        elif structure.lower() == "random":
            g = setupRandom(num_nodes, num_edges, prob_edges)

        elif structure.lower() == "ringworld":
            g = setupRingworld(num_nodes)

        elif structure.lower() == "smallworld":
            g = setupSmallWorld(num_nodes)

        elif structure.lower() == "vonneumann":
            g = setupVonNeumann(num_nodes)

        with open("network_data/{}_{}".format(structure, num_nodes), "wb") as f:
            writer = csv.writer(f)
            writer.writerows(g.get_adjlist())

        return g


def write_adjacency(self, f, sep=" ", eol="\n", *args, **kwds):
    """Writes the adjacency matrix of the graph to the given file

    All the remaining arguments not mentioned here are passed intact
    to L{Graph.get_adjacency}.

    @param f: the name of the file to be written.
    @param sep: the string that separates the matrix elements in a row
    @param eol: the string that separates the rows of the matrix. Please
      note that igraph is able to read back the written adjacency matrix
      if and only if this is a single newline character
    """
    if isinstance(f, basestring):
        f = open(f, "w")
    matrix = self.get_adjacency(*args, **kwds)
    for row in matrix:
        f.write(sep.join(map(str, row)))
        f.write(eol)
    f.close()
    

if __name__=='__main__':

    # Necessary Command Line Arguments
    parser = argparse.ArgumentParser(description='Process command line options for the program.')
    parser.add_argument('number_of_persons', help="Number of people for each node to handle", type=int)
    parser.add_argument('network', help="Network Type: none, powerlaw, preferential, random, ringworld, smallworld, "
                                        "vonneumann", type=str)
    args = parser.parse_args()

    # the number of times the model is run per network structure input. One run last the duration of the timeLimit.
    num_runs = 1

    # absolute number of nodes/agents
    num_nodes = args.number_of_persons

    # Used for Random or SmallWorlds; sets probability of an edge between agents (either probEdges or numEdges required
    prob_edges = 0

    # distance within which 2 vertices will be connected. Set to 1 for vonneumann graph
    nei = 1

    # Check Network Type
    network_types = ["none", "powerlaw", "preferential", "random", "ringworld", "smallworld", "vonneumann", "moore"]
    if args.network in network_types:
        num_edges = num_nodes

        setupNetwork(num_nodes, num_edges, prob_edges, args.network)