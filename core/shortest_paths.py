
class ShortestPaths:
    """

    ShortestPaths is a class for floyd-warshall algorithm calculation of shortest paths, where it stores the
    calculated path lengths and paths. This is used in this program for calculating bipartite matching
    when attempting to duplicate edges for use in constructing the "chinese postman" solution.
    Time complexity: O(n^3)
    Space complexity: O(n^2)

    """

    def __init__(self, g):
        """
        On initialization, ShortestPath accepts a nonempty multigraph (g) and generates the path lengths etc.
        by calling recreate(g) straight away.

        :param g: nonempty multigraph
        :return: Nothing
        """

        self.distances = {}
        self.paths = {}

        self.g = None
        self.recreate(g)

    def recreate(self, g):
        """
        Refill populates the object's graph with g, and calls on parser to complete creating. If g is empty or
        not a multigraph, a generic exception is thrown

        >>> import networkx as nx
        >>> g = nx.MultiDiGraph()
        >>> g.add_edge('a', 'b')
        >>> sp = ShortestPaths(g)
        >>> sp.recreate(None)
        Traceback (most recent call last):
            ...
        Exception: g can't be None-type
        >>> empty = nx.MultiDiGraph()
        >>> sp.recreate(empty)
        Traceback (most recent call last):
            ...
        Exception: MultiDiGraph is empty
        >>> graph = nx.Graph()
        >>> graph.add_edge('a', 'b')
        >>> sp.recreate(graph)
        Traceback (most recent call last):
            ...
        Exception: g is not a MultiDiGraph

        :param g: Non-empty multigraph
        :return: Nothing
        """

        if g is None:
            raise Exception("g can't be None-type")

        if not g.is_multigraph() or not g.is_directed():
            raise Exception("g is not a MultiDiGraph")

        if g.size() == 0:
            raise Exception("MultiDiGraph is empty")

        self.g = g
        self.parse()

    def parse(self):
        """
        This call is a utility to calculate all n^2 path lengths and shortest paths using Dijkstra's
        algorithm and keeping distances and paths in memory (in self.distances and self.paths). Note that
        self.paths array is not actually an array of paths, but self.paths[a][b] = "last node before b in
        path a->b". See better explanation in find_path(a, b).

        >>> import networkx as nx
        >>> g = nx.MultiDiGraph()
        >>> g.add_edge('a', 'b')
        >>> sp = ShortestPaths(g)
        >>> sp.parse()
        >>> print sp.distances  # doctest: +NORMALIZE_WHITESPACE
        {'a': {'a': 0, 'b': 1}, 'b': {'a': 0, 'b': 0}}
        >>> print sp.paths  # doctest: +NORMALIZE_WHITESPACE
        {'a': {'a': None, 'b': 'a'}, 'b': {'a': None, 'b': None}}

        :return: Nothing
        """

        if self.g is None:
            raise Exception("parse can't be called before setting a graph. Call recreate(g)"
                            " with a multi-digraph")

        # initialize data
        temp_dist = {}
        temp_paths = {}
        for node in self.g.nodes_iter():
            self.distances[node] = {}
            self.paths[node] = {}
            temp_dist[node] = {}
            temp_paths[node] = {}

            children = self.g.neighbors(node)
            for next_node in self.g.nodes_iter():
                if next_node in children:
                    temp_dist[node][next_node] = 1          # replace with weight if necessary
                    temp_paths[node][next_node] = node
                else:
                    temp_dist[node][next_node] = 0
                    temp_paths[node][next_node] = None

        for node in self.g.nodes_iter():
            temp_dist[node][node] = 0
            temp_paths[node][node] = None

        # repeatedly multiply adjacency matrix with itself until no more possible
        for i in xrange(self.g.size()+1):
            for item in temp_dist:
                for item2 in temp_dist[item]:
                    self.distances[item][item2] = temp_dist[item][item2]
                    self.paths[item][item2] = temp_paths[item][item2]

            for node in self.g.nodes_iter():
                for child in self.g.neighbors(node):
                    for gchild in self.g.neighbors(child):
                        new_dist = temp_dist[node][child] + temp_dist[child][gchild]
                        if temp_dist[node][gchild] == 0 or temp_dist[node][gchild] > new_dist:
                            temp_dist[node][gchild] = new_dist
                            temp_paths[node][gchild] = child

            for node in self.g.nodes_iter():
                temp_dist[node][node] = 0
                temp_paths[node][node] = None

    def get_shortest_path_length(self, start, end):
        """
        get_shortest_path_length returns the length of the shortest path from the node start to node end of
        the graph. This is the end result of creating and parsing a graph using this class/algorithm. After all
        the parsing, which is O(n^3), this shortest length is delivered by referring to self.distances

        If a start node or end node is not contained in the graph, the function throws a general exception

        >>> import networkx as nx
        >>> g = nx.MultiDiGraph()
        >>> g.add_edge('a', 'b')
        >>> g.add_edge('a', 'b')
        >>> g.add_edge('b', 'c')
        >>> g.add_edge('c', 'b')
        >>> g.add_edge('c', 'd')
        >>> g.add_edge('a', 'd')
        >>> sp = ShortestPaths(g)
        >>> print sp.get_shortest_path_length('a', 'd')
        1
        >>> print sp.get_shortest_path_length('b', 'd')
        2
        >>> print sp.get_shortest_path_length('e', 'd')
        Traceback (most recent call last):
            ...
        Exception: start node not contained in graph
        >>> print sp.get_shortest_path_length('b', 'f')
        Traceback (most recent call last):
            ...
        Exception: end node not contained in graph

        :param start: start node, contained in graph g
        :param end: end node, contained in graph g
        :return: path length of shortest path from start to end in graph
        """

        if self.g is None:
            raise Exception("get_shortest_path_length can't be called without setting a graph. "
                            "First call recreate(g) with a multi-digraph")

        if start not in self.g:
            raise Exception("start node not contained in graph")
        if end not in self.g:
            raise Exception("end node not contained in graph")

        return self.distances[start][end]

    def get_shortest_path(self, start, end):
        """
        This function returns the list of nodes that represent the shortest path from the node start to node end.

        If either start node or end node is not given, a generic exception is thrown

        >>> import networkx as nx
        >>> g = nx.MultiDiGraph()
        >>> g.add_edge('a', 'b')
        >>> g.add_edge('a', 'b')
        >>> g.add_edge('b', 'c')
        >>> g.add_edge('c', 'b')
        >>> g.add_edge('c', 'd')
        >>> g.add_edge('a', 'd')
        >>> sp = ShortestPaths(g)
        >>> print sp.get_shortest_path('a', 'd')
        ['a', 'd']
        >>> print sp.get_shortest_path('b', 'd')
        ['b', 'c', 'd']
        >>> print sp.get_shortest_path('e', 'd')
        Traceback (most recent call last):
            ...
        Exception: start node not contained in graph
        >>> print sp.get_shortest_path_length('b', 'f')
        Traceback (most recent call last):
            ...
        Exception: end node not contained in graph

        :param start: start node, contained in graph g
        :param end: end node, contained in graph g
        :return: list of nodes of graph g
        """

        if self.g is None:
            raise Exception("get_shortest_path can't be called without setting a graph. "
                            "First call recreate(g) with a multi-digraph")

        if start not in self.g:
            raise Exception("start node not contained in graph")
        if end not in self.g:
            raise Exception("end node not contained in graph")

        ret = [end]
        while self.paths[start][end] is not None:
            ret.append(self.paths[start][end])
            end = self.paths[start][end]
        ret.reverse()

        return ret
