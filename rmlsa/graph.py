from typing import List
import itertools
from rmlsa.components import User
import networkx as nx
from rmlsa.tools import pairwise
import numpy as np
from .routing import dijkstra, directBalance, baroni, leastLoad, mixed


class Topology(nx.DiGraph):

    def __init__(self, **attr):
        nx.DiGraph.__init__(self)
        self.attr = attr  # Cache of all possible attributes

        if "name" in attr:
            self.graph['name'] = attr["name"]
        else:
            self.graph['name'] = "Unknown"

        if "totalDistance" in attr:
            self.graph['totalDistance'] = attr["totalDistance"]
        else:
            self.graph['totalDistance'] = 0

        if "users" in attr:
            self.users = attr["users"]
        else:
            self.users = []

        if "routes" in attr:
            self.routes = attr["routes"]
        else:
            self.routes = {}

        if "routesLength" in attr:
            self.routesLength = attr["routesLength"]
        else:
            self.routesLength = {}

        if "linksFSUs" in attr:
            self.linksFSUs = attr["linksFSUs"]
        else:
            self.linksFSUs = {}

        self.links_id = {}
        self.graph['method'] = "Baroni"
        self.graph['usageMetric'] = "users"
        self.graph['routeMetric'] = "Length"
        self.graph['ksp'] = 1
        self.graph['scale'] = 1
        self.graph['seed'] = 0
        self.graph['cores'] = 1
        self.graph['fsus'] = 320



    def setName(self, name):
        self.graph['name'] = name

    def getUsers(self, u=None, v=None):
        if u is None and v is None:
            return self.users
        elif u is not None and v is None:
            return [user for user in self.users if user.source == u]
        elif u is None and v is not None:
            return [user for user in self.users if user.destination == v]
        else:  # u is not None and v is not None:
            return [user for user in self.users if user.source == u and user.destination == v]

    def getNodesCount(self):
        return len(self.nodes())

    def getLinksCount(self):
        return len(self.edges())

    def getKSPCount(self):
        if "ksp" in self.graph:
            return self.graph['ksp']
        else:
            return None

    def getFSUsCount(self):
        if "fsus" in self.graph:
            return self.graph['fsus']
        else:
            return None

    def getCoresCount(self):
        if "cores" in self.graph:
            return self.graph['cores']
        else:
            return None

    def getRoutes(self, fromNode: int = None, toNode: int = None):
        if fromNode is None:
            return self.routes
        elif fromNode is not None and toNode is None:
            data = {}
            for node in self.nodes:
                if node != fromNode:
                    data[node] = self.routes[fromNode, node]
            return data
        else:
            return self.routes[fromNode, toNode]

    def getTotalCapacity(self):
        return self.getCoresCount()*self.getLinksCount()*self.getFSUsCount()

    def createRoute(self, route: list, iden="links_id"):
        if iden != "links_id":
            realRoute = route
        else:
            realRoute = []
            for index, idLink in enumerate(route):
                startNode, endNode = self.links_id[idLink]
                if index == 0:
                    realRoute.append(startNode)
                realRoute.append(endNode)
        return [realRoute], self.getDistance([realRoute])

    def getLinksId(self, path):
        return [self[u][v]["id"] for (u, v) in pairwise(path)]

    def init(self, seed=0):
        for (u, v) in self.edges():
            self.linksFSUs[u, v] = [[True] * self.getFSUsCount() for k in range(self.getCoresCount())]
        np.random.seed(seed)
        self.users = []
        for userId, (u, v) in enumerate(itertools.permutations(self.nodes, 2)):
            bitRate = np.random.choice([10, 40, 100, 400, 1000])
            self.users.append(User(userId, u, v, bitRate))
        self.routes, self.routesLength = self.__buildPaths__()
        self.updateUsersRoutes()

    def build(self, method: str = "From File", usageMetric: str = "users", routeMetric: str = "hops",
              kspCount: int = 1, scale: float = 1.0, seed: int = 0, coresCount: int = 1, fsusCount: int = 320,
              criterion="Max."):
        self.graph['method'] = method
        self.graph['usageMetric'] = usageMetric
        self.graph['routeMetric'] = routeMetric
        self.graph['ksp'] = kspCount
        self.graph['scale'] = scale
        self.graph['seed'] = seed
        self.graph['cores'] = coresCount
        self.graph['fsus'] = fsusCount
        self.graph['criterion'] = criterion
        # self.init(seed)

        return self

    def updateUsersRoutes(self):
        for user in self.users:
            s = user.source
            d = user.destination
            user.update(self.routes[s, d][0], self.routesLength[s, d][0])

    def __buildPaths__(self):
        method = self.graph["method"]
        if method == "Dijkstra":
            return dijkstra(self)

        elif method == "LeastLoad":
            # El mío:
            return leastLoad(self, 5)

        elif method == "DirectBalance":
            # El del tutor:
            return directBalance(self, 5)

        elif method == "From File":
            return self.loadRoutesFromFile()
            # return self.routes, self.routesLength

        elif method == "Mixed":
            return mixed(self, 5)

        else:  # method == "Baroni"
            return baroni(self, 5)

    def getDistance(self, paths: List[list]):
        distance = []
        scale = self.graph["scale"]
        for path in paths:
            total_length = 0
            for i in range(len(path) - 1):
                source, target = path[i], path[i + 1]
                edge = self[source][target]
                length = edge['length']
                total_length += length
            distance.append(total_length*scale)
        return distance

    def copy(self, as_view=False):
        links_id = self.links_id.copy()
        copied = super().copy(as_view)
        copied.links_id = links_id
        return copied

    def add_edge(self, u_of_edge, v_of_edge, **attr):
        if "id" in attr:
            self.links_id[attr["id"]] = [u_of_edge, v_of_edge]
        super().add_edge(u_of_edge, v_of_edge, **attr)

    def loadRoutesFromFile(self):
        with open(self.graph["fileDir"], 'r') as file_lines:
            # gets only lines that do not start with the # character
            lines = [value for value in file_lines if not value.startswith('#') if not value.startswith("\n")]
            entries = __readEntries__(lines[0])
            nLinks = entries[1]
            return self.readRoutes(lines, nLinks)

    def readRoutes(self, lines, nLinks):
        routes = {}
        routesLength = {}

        if len(lines) > nLinks + 1:
            for line in lines[nLinks + 1::]:
                entries = __readEntries__(line)
                fromNode = entries[0]
                toNode = entries[1]
                if fromNode != toNode:
                    route = entries[3::]
                    routes[fromNode, toNode], routesLength[fromNode, toNode] = self.createRoute(route, iden="links_id")
            return routes, routesLength
        else:
            return baroni(self, 5)


def loadGraph(fileDir: str) -> Topology:
    import os
    baseName = os.path.basename(fileDir)
    fileName, ext = os.path.splitext(baseName)
    graph = None
    if ext == ".txt":
        graph = Topology()
        graph.graph["name"] = fileName
        graph.graph["fileDir"] = fileDir
        graph.graph["totalDistance"] = 0
        id_link = 0
        with open(fileDir, 'r') as file_lines:
            # gets only lines that do not start with the # character
            lines = [value for value in file_lines if not value.startswith('#') if not value.startswith("\n")]
            nLinks = 0
            for idx, line in enumerate(lines):
                if idx == 0:
                    entries = __readEntries__(line)
                    numNodes = entries[0]
                    nLinks = entries[1]

                    for nodeId in range(0, numNodes):
                        # graph.add_node(str(nodeId), name=str(nodeId))
                        graph.add_node(nodeId, name=nodeId)
                elif idx < nLinks+1:
                    entries = __readEntries__(line)
                    graph.graph["totalDistance"] += 2*entries[2]
                    graph.add_edge(entries[0], entries[1], id=id_link, weight=1, length=entries[2])
                    graph.add_edge(entries[1], entries[0], id=id_link+1, weight=1, length=entries[2])
                    id_link += 2
            # graph.routes, graph.routesLength = graph.readRoutes(lines, nLinks)
            # graph.init()
    return graph


def __readEntries__(line: str, sep: str = " ") -> list:
    line = line.replace("\t", ' ')
    entries = []
    last = " "
    current = ""
    for char in line:
        if char != sep and char != "\n":
            current = current+char
        elif char == sep and last != sep or char == "\n":
            entries.append(int(current))
            current = ""
        last = char
    return entries


def exportGraph():
    pass
