from . import shortest_paths
import networkx as nx

class DuplicationsFinder:
    """

    Given a multi-digraph, this class performs four steps:
    1 - it finds the degree_surplus metric for each node. That is defined as
        out_degree-in_degree for each node.
    2 - Two lists are created - left_set and right_set. If degree_surplus < 0,
        the node is added |degree_surplus| times to left_set. If
        degree_surplus > 0, same is done with right_set. In effect, any node
        that has more out_degree < in_degree ends in left_set and any node
        with out_degree > in_degree ends in right_set.
    3 - A new bipartite weighted-graph is made with every element of left_set
        connected to every element of right_set with weight showing distance
        between the two points.
    4 - A matching is made using networkx's built in maximum_weight_matching
        algorithm. The result is returned as a dict with each each node in
        left_set as key and a list of corresponding matched modes from
        right_set as value. This matching is accessed as self.matching

    This class is used to determine paths that are duplicated in order to
    identify its chinese postman tour of the given multi-digraph.

    Time-complexity:
    Space-complexity:

    """

    def __init__(self, g, sp=None):
        """
        On initialization, DuplicationFinder accepts a non-empty multi-digraph.
        This calls recreate right away with g

        :param g: A non-empty multi-digraph
        :return: Nothing
        """
        self.matching = {}
        self.degree_surplus = {}
        self.left_set = []
        self.right_set = []
        self.g = None
        self.shortest_paths = sp

        self.recreate(g)

    def recreate(self, g):
        """
        This function sets the graph and initializes the processing by calling
        find_matching right away. If g is None, not a multi-digraph or is empty,
        a generic exception is thrown.

        >>> import networkx as nx
        >>> g = nx.MultiDiGraph()
        >>> g.add_edge('a', 'b')
        >>> df = DuplicationsFinder(g)
        >>> df.recreate(None)
        Traceback (most recent call last):
            ...
        Exception: g can't be None-type
        >>> empty = nx.MultiDiGraph()
        >>> df.recreate(empty)
        Traceback (most recent call last):
            ...
        Exception: MultiDiGraph is empty
        >>> graph = nx.Graph()
        >>> graph.add_edge('a', 'b')
        >>> df.recreate(graph)
        Traceback (most recent call last):
            ...
        Exception: g is not a MultiDiGraph

        :param g: Non-empty multi-digraph
        :return: Nothing
        """

        if g is None:
            raise Exception("g can't be None-type")

        if not g.is_multigraph() or not g.is_directed():
            raise Exception("g is not a MultiDiGraph")

        if g.size() == 0:
            raise Exception("MultiDiGraph is empty")

        self.g = g
        self.find_matching()

    def find_matching(self):
        """
        This function finds the degree_surplus metrics, left_sets, right_sets
        and finally calls networkx's maximum_weight_matching algorithm.

        >>> mdg = nx.MultiDiGraph()
        >>> mdg.add_edge('start', 'a')
        >>> mdg.add_edge('a', 'b')
        >>> mdg.add_edge('b', 'c')
        >>> mdg.add_edge('b', 'c')
        >>> mdg.add_edge('c', 'd')
        >>> mdg.add_edge('c', 'e')
        >>> mdg.add_edge('c', 'f')
        >>> mdg.add_edge('c', 'g')
        >>> mdg.add_edge('d', 'h')
        >>> mdg.add_edge('f', 'h')
        >>> mdg.add_edge('g', 'h')
        >>> mdg.add_edge('h', 'e')
        >>> mdg.add_edge('e', 'end')
        >>> mdg.add_edge('end', 'start')
        >>> df = DuplicationsFinder(mdg)
        >>> print df.degree_surplus # doctest: +NORMALIZE_WHITESPACE
        {'a': 0, 'c': 2, 'b': 1, 'e': -1, 'd': 0, 'g': 0, 'f': 0, 'h': -2, 'start': 0, 'end': 0}
        >>> print df.left_set   # doctest: +NORMALIZE_WHITESPACE
        [('e', 0), ('h', 0), ('h', 1)]
        >>> print df.right_set  # doctest: +NORMALIZE_WHITESPACE
        [('c', 0), ('c', 1), ('b', 0)]
        >>> print df.matching   # doctest: +NORMALIZE_WHITESPACE
        {'h': ['b', 'c'], 'e': ['c']}

        :return: Nothing
        """

        if self.g is None:
            raise Exception("find_matching can't be called without a graph "
                            "being set. First call recreate(g) with a "
                            "Non-empty digraph")

        # Step 1 - determine degree_surplus
        for node in self.g.nodes_iter():
            in_degree = self.g.in_degree(node)
            out_degree = self.g.out_degree(node)
            self.degree_surplus[node] = out_degree-in_degree

        # Step 2 - make left_set and right_set
        self.left_set = []
        self.right_set = []
        for node in self.degree_surplus:
            count = self.degree_surplus[node]
            for i in range(abs(count)):
                item = (node, i)
                if count < 0:
                    self.left_set.append(item)
                elif count > 0:
                    self.right_set.append(item)

        # Step 3 - make bipartite graph
        if self.shortest_paths is None:
            sp = shortest_paths.ShortestPaths(self.g)
        else:
            sp = self.shortest_paths
        bpgraph = nx.Graph()
        bpgraph.add_nodes_from(self.left_set, bipartite=0)
        bpgraph.add_nodes_from(self.right_set, bipartite=1)
        for lnode in self.left_set:
            for rnode in self.right_set:
                wt = sp.get_shortest_path_length(lnode[0], rnode[0])
                bpgraph.add_edge(lnode, rnode, weight=wt)

        # Step 4 - find matching
        matches = nx.bipartite.eppstein_matching(bpgraph)
        for source in self.left_set:
            dest = matches[source]
            if source[0] not in self.matching:
                self.matching[source[0]] = []
            self.matching[source[0]].append(dest[0])
