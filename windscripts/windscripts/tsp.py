import networkx as nx

#--- TSP Solving Algorithms ---
def tsp_ca(siteGraph):
    mst = nx.minimum_spanning_tree(siteGraph,weight='weight')
    odds = nx.Graph()
    for key, value in mst.degree().iteritems():
        if value % 2 != 0:
            odds.add_node(key)
            for node in odds:
                if node == key: continue
                odds.add_edge(node,key,weight=-siteGraph[node][key]['weight'])
    matches = nx.max_weight_matching(odds, maxcardinality=True)
    perfectMatch = nx.Graph()
    for node in odds:
        perfectMatch.add_node(node)
    for key, value in matches.iteritems():
        perfectMatch.add_edge(key,value,weight=siteGraph[key][value]['weight'])
    eGraph = nx.MultiGraph()
    eGraph.add_nodes_from(mst.nodes())
    eGraph.add_edges_from(mst.edges())
    eGraph.add_edges_from(perfectMatch.edges())
    eulerianpath = list(nx.eulerian_circuit(eGraph))
    #remove repetition
    crossed = []
    path = []
    for t in eulerianpath:
        if 'previous' not in locals():
            previous = t[0]
            continue
        if t[0] not in crossed:
            path.append((previous,t[0]))
            crossed.append(t[0])
            previous = t[0]
    solution = nx.DiGraph()
    solution.add_edges_from(path)
    for edge in solution.edges():
        solution[edge[0]][edge[1]]['weight'] = siteGraph[edge[0]][edge[1]]['weight']
    return solution