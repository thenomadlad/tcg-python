
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
        >>> _ = g.add_edge('a', 'b')
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
        >>> _ = graph.add_edge('a', 'b')
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
        >>> nodes_order = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        >>> _ = g.add_edge('a', 'b')
        >>> _ = g.add_edge('b', 'c')
        >>> _ = g.add_edge('b', 'c')
        >>> _ = g.add_edge('c', 'd')
        >>> _ = g.add_edge('c', 'e')
        >>> _ = g.add_edge('e', 'f')
        >>> _ = g.add_edge('d', 'g')
        >>> _ = g.add_edge('e', 'g')
        >>> _ = g.add_edge('g', 'c')
        >>> _ = g.add_edge('f', 'h')
        >>> _ = g.add_edge('g', 'h')
        >>> _ = g.add_edge('h', 'a')
        >>> sp = ShortestPaths(g)
        >>> sp.dump_tables(nodes_order)   # doctest: +NORMALIZE_WHITESPACE
        {'a': {'b': 'a', 'c': 'b', 'd': 'c', 'e': 'c', 'f': 'e', 'g': 'e', 'h': 'g'},
         'b': {'a': 'h', 'c': 'b', 'd': 'c', 'e': 'c', 'f': 'e', 'g': 'e', 'h': 'g'},
         'c': {'a': 'h', 'b': 'a', 'd': 'c', 'e': 'c', 'f': 'e', 'g': 'e', 'h': 'g'},
         'd': {'a': 'h', 'b': 'a', 'c': 'g', 'e': 'c', 'f': 'e', 'g': 'd', 'h': 'g'},
         'e': {'a': 'h', 'b': 'a', 'c': 'g', 'd': 'c', 'f': 'e', 'g': 'e', 'h': 'g'},
         'f': {'a': 'h', 'b': 'a', 'c': 'b', 'd': 'c', 'e': 'c', 'g': 'e', 'h': 'f'},
         'g': {'a': 'h', 'b': 'a', 'c': 'g', 'd': 'c', 'e': 'c', 'f': 'e', 'h': 'g'},
         'h': {'a': 'h', 'b': 'a', 'c': 'b', 'd': 'c', 'e': 'c', 'f': 'e', 'g': 'e'}}
        {'a': {'b': 1, 'c': 2, 'd': 3, 'e': 3, 'f': 4, 'g': 4, 'h': 5},
         'b': {'a': 5, 'c': 1, 'd': 2, 'e': 2, 'f': 3, 'g': 3, 'h': 4},
         'c': {'a': 4, 'b': 5, 'd': 1, 'e': 1, 'f': 2, 'g': 2, 'h': 3},
         'd': {'a': 3, 'b': 4, 'c': 2, 'e': 3, 'f': 4, 'g': 1, 'h': 2},
         'e': {'a': 3, 'b': 4, 'c': 2, 'd': 3, 'f': 1, 'g': 1, 'h': 2},
         'f': {'a': 2, 'b': 3, 'c': 4, 'd': 5, 'e': 5, 'g': 6, 'h': 1},
         'g': {'a': 2, 'b': 3, 'c': 1, 'd': 2, 'e': 2, 'f': 3, 'h': 1},
         'h': {'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 4, 'f': 5, 'g': 5}}


        :return: Nothing
        """

        if self.g is None:
            raise Exception("parse can't be called before setting a graph. Call recreate(g)"
                            " with a multi-digraph")

        # initialize maps
        self.distances = {}
        self.paths = {}
        for node in self.g.nodes():
            self.paths[node] = {}
            self.distances[node] = {}

        # get first pass
        for node in self.g.nodes():
            for child in self.g.successors(node):
                if child == node:
                    continue
                self.paths[node][child] = node
                self.distances[node][child] = 1 # TODO: replace following with weight

        # iterate over nodes
        for mid in self.g.nodes():
            for src in self.g.nodes():
                if mid not in self.distances[src]:
                    continue
                for end in self.g.nodes():
                    if src == end:
                        continue
                    if end not in self.distances[mid]:
                        continue
                    if end in self.distances[src] and self.distances[src][end] <= self.distances[src][mid] + self.distances[mid][end]:
                        continue
                    self.distances[src][end] = self.distances[src][mid] + self.distances[mid][end]
                    self.paths[src][end] = self.paths[mid][end]

    def get_shortest_path_length(self, start, end):
        """
        get_shortest_path_length returns the length of the shortest path from the node start to node end of
        the graph. This is the end result of creating and parsing a graph using this class/algorithm. After all
        the parsing, which is O(n^3), this shortest length is delivered by referring to self.distances

        If a start node or end node is not contained in the graph, the function throws a general exception

        >>> import networkx as nx
        >>> mdg = nx.MultiDiGraph()
        >>> _ = mdg.add_edge('start', 'a')
        >>> _ = mdg.add_edge('a', 'b')
        >>> _ = mdg.add_edge('b', 'c')
        >>> _ = mdg.add_edge('c', 'd')
        >>> _ = mdg.add_edge('c', 'e')
        >>> _ = mdg.add_edge('c', 'f')
        >>> _ = mdg.add_edge('c', 'g')
        >>> _ = mdg.add_edge('d', 'h')
        >>> _ = mdg.add_edge('f', 'h')
        >>> _ = mdg.add_edge('g', 'h')
        >>> _ = mdg.add_edge('h', 'e')
        >>> _ = mdg.add_edge('e', 'end')
        >>> _ = mdg.add_edge('end', 'start')
        >>> sp = ShortestPaths(mdg)
        >>> print(sp.get_shortest_path_length('a', 'd'))
        3
        >>> print(sp.get_shortest_path_length('c', 'a'))
        4
        >>> print(sp.get_shortest_path_length('g', 'd'))
        8
        >>> print(sp.get_shortest_path_length('blah', 'd'))
        Traceback (most recent call last):
            ...
        Exception: start node not contained in graph
        >>> print(sp.get_shortest_path_length('d', 'blah'))
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

        if end not in self.distances[start]:
            return None

        return self.distances[start][end]

    def get_shortest_path(self, start, end):
        """
        This function returns the list of nodes that represent the shortest path
        from the node start to node end. If either start node or end node is not
        given, a generic exception is thrown

        >>> import networkx as nx
        >>> mdg = nx.MultiDiGraph()
        >>> _ = mdg.add_edge('start', 'a')
        >>> _ = mdg.add_edge('a', 'b')
        >>> _ = mdg.add_edge('b', 'c')
        >>> _ = mdg.add_edge('c', 'd')
        >>> _ = mdg.add_edge('c', 'e')
        >>> _ = mdg.add_edge('c', 'f')
        >>> _ = mdg.add_edge('c', 'g')
        >>> _ = mdg.add_edge('d', 'h')
        >>> _ = mdg.add_edge('f', 'h')
        >>> _ = mdg.add_edge('g', 'h')
        >>> _ = mdg.add_edge('h', 'e')
        >>> _ = mdg.add_edge('e', 'end')
        >>> _ = mdg.add_edge('end', 'start')
        >>> sp = ShortestPaths(mdg)
        >>> print(sp.get_shortest_path('a', 'd'))  # doctest: +NORMALIZE_WHITESPACE
        ['a', 'b', 'c', 'd']
        >>> print(sp.get_shortest_path('c', 'a'))  # doctest: +NORMALIZE_WHITESPACE
        ['c', 'e', 'end', 'start', 'a']
        >>> print(sp.get_shortest_path('g', 'd') )
        ['g', 'h', 'e', 'end', 'start', 'a', 'b', 'c', 'd']
        >>> print(sp.get_shortest_path('blah', 'd'))
        Traceback (most recent call last):
            ...
        Exception: start node not contained in graph
        >>> print(sp.get_shortest_path('d', 'blah'))
        Traceback (most recent call last):
            ...
        Exception: end node not contained in graph

        :param start: start node, contained in graph g
        :param end: end node, contained in graph g
        :return: list of nodes of graph g
        """

        if self.g is None:
            raise Exception("get_shortest_path can't be called without setting"
                            "a graph. First call recreate(g) with a "
                            "multi-digraph")
        if start not in self.g:
            raise Exception("start node not contained in graph")
        if end not in self.g:
            raise Exception("end node not contained in graph")

        # stack nodes to form a path in reverse
        ret = [end]
        while end in self.paths[start]:
            next_item = self.paths[start][end]
            ret.append(next_item)
            end = next_item

        # if path doesn't end up towards start for some reason
        # these two lines shouldn't be touched
        if ret[-1] != start:
            return None

        ret.reverse()

        return ret

    def dump_tables(self, nodes_order=None):
        """
        Utility function to dump distances and paths to console
        """
        import pprint
        pprint.pprint(self.paths)
        pprint.pprint(self.distances)
