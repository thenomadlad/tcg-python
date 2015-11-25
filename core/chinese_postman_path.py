import shortest_paths, duplications_finder
import copy

class ChinesePostmanPath:
    """
    Given a multi-digraph, this class finds the minimal-length tour of the graph that covers every
    edge at least once.
    1 - a ShortestPaths instance is created
    2 - DuplicationsFinder is used to find which paths to duplicate
    3 - the paths found in 2 are duplicated
    4 - a tour is found by performing a depth-first search

    Space complexity:
    Time complexity:
    """

    def __init__(self, g, start, end):
        """
        On initiation, the paths are found to

        >>> import networkx as nx
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
        >>> sp = ChinesePostmanPath(mdg, 'start', 'end')
        >>> print sp.shortest_tour


        :param g:
        :param start:
        :param end:
        :return:
        """
        self.g = g
        self.shortest_paths = None
        self.duplications_finder = None
        self.to_duplicate = None

        self.start = start
        self.end = end
        self.shortest_tour = None

        self.find_tour()

    def duplicate_paths(self):
        self.duplications_finder = duplications_finder.DuplicationsFinder(self.g, self.shortest_paths)
        self.to_duplicate = self.duplications_finder.matching

        for key in self.to_duplicate:
            dests = self.to_duplicate[key]
            for dest in dests:
                path = self.shortest_paths.get_shortest_path(key, dest)
                for i in xrange(len(path)-1):
                    self.g.add_edge(path[i], path[i+1])

    def find_tour(self):
        self.shortest_paths = shortest_paths.ShortestPaths(self.g)
        self.duplicate_paths()

        class FindTourHelper:
            path = []

            def __init__(self):
                self.len = 0

            def add_node(self, n):
                FindTourHelper.path.append(n)
                self.len += 1

            def __len__(self):
                return len(FindTourHelper.path)

            def __contains__(self, item):
                return FindTourHelper.path.__contains__(item)

            def get_path(self):
                return copy.copy(FindTourHelper.path)

            def __del__(self):
                for i in xrange(self.len):
                    FindTourHelper.path.pop()

        def recursive_helper(start, graph):
            path = FindTourHelper()
            path.add_node(start)

            if len(path) == graph.number_of_nodes():
                for item in graph.nodes_iter():
                    if item not in path:
                        return None
                return path.get_path()

            for item in graph.neighbors_iter(start):
                path_list = recursive_helper(item, graph)
                if path_list:
                    return path_list

        if self.start not in self.g.neighbors(self.end):
            self.g.add_edge(self.end, self.start)
        self.shortest_tour = recursive_helper(self.start, self.g)
