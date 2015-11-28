import shortest_paths, duplications_finder

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
        >>> mdg.add_edge('start', 'a', key=0)
        >>> mdg.add_edge('a', 'b', key=1)
        >>> mdg.add_edge('b', 'c', key=2)
        >>> mdg.add_edge('b', 'c', key=3)
        >>> mdg.add_edge('c', 'd', key=4)
        >>> mdg.add_edge('c', 'e', key=5)
        >>> mdg.add_edge('c', 'f', key=6)
        >>> mdg.add_edge('c', 'g', key=7)
        >>> mdg.add_edge('d', 'h', key=8)
        >>> mdg.add_edge('f', 'h', key=9)
        >>> mdg.add_edge('g', 'h', key=10)
        >>> mdg.add_edge('h', 'e', key=11)
        >>> mdg.add_edge('h', 'b', key=12)
        >>> mdg.add_edge('e', 'end', key=13)
        >>> mdg.add_edge('end', 'start', key=14)
        >>> sp = ChinesePostmanPath(mdg, 'start', 'end')
        >>> print sp.shortest_tour  # doctest: +NORMALIZE_WHITESPACE
        [('start', 'a', 0, {}), ('a', 'b', 1, {}), ('b', 'c', 16, {}), 
         ('c', 'e', 5, {}), ('e', 'end', 17, {}), ('end', 'start', 14, {}), 
         ('start', 'a', 19, {}), ('a', 'b', 20, {}), ('b', 'c', 2, {}), 
         ('c', 'd', 4, {}), ('d', 'h', 8, {}), ('h', 'b', 12, {}), 
         ('b', 'c', 3, {}), ('c', 'g', 7, {}), ('g', 'h', 10, {}), 
         ('h', 'b', 15, {}), ('b', 'c', 21, {}), ('c', 'f', 6, {}), 
         ('f', 'h', 9, {}), ('h', 'e', 11, {}), ('e', 'end', 13, {})]

        :param g:
        :param start:
        :param end:
        :return:
        """
        self.g = g
        self.s_paths = None
        self.dup_finder = None
        self.to_duplicate = None

        self.start = start
        self.end = end
        self.shortest_tour = None

        self.find_tour()

    def duplicate_paths(self):
        """
        On calling, the graph in the ChinesePostnamPath will have edges
        duplicated until a chinese postman path can be searched for

        :return: nothing
        """
        self.dup_finder = duplications_finder.DuplicationsFinder(self.g, self.s_paths)
        self.to_duplicate = self.dup_finder.matching

        for src, dests in self.to_duplicate.iteritems():
            for dest in dests:
                path = self.s_paths.get_shortest_path(src, dest)
                for i in xrange(len(path)-1):
                    self.g.add_edge(path[i], path[i+1], key=self.g.size())

    def find_tour(self):
        self.s_paths = shortest_paths.ShortestPaths(self.g)
        self.duplicate_paths()
        self.g.remove_edge('end', 'start')

        path = []
        edge_keys = set()

        cur_node = self.start
        stuck = False
        while not stuck and len(path) < self.g.size():
            stuck = True
            for item in self.g.out_edges(cur_node, keys=True, data=True):
                if item[2] not in edge_keys:
                    stuck = False
                    path.append(item)
                    edge_keys.add(item[2])
                    cur_node = item[1]
                    break
        
        if stuck:
            self.shortest_tour = None
        else:
            self.shortest_tour = path

