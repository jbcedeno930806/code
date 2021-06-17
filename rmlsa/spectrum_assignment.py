from rmlsa.tools import *
from rmlsa.metrics import *


AlgNames = {
    "FIRST_FIT": "FIRST_FIT",
    "PARCEL_FIT": "PARCEL_FIT",
    "SLIDING_FIT": "SLIDING_FIT",
    "TOPOLOGY_FIT": "TOPOLOGY_FIT"
}


class BaseAlgorithm(object):
    def __init__(self, graph: Topology, orders: dict, algName):
        object.__init__(self)
        self.graph = graph
        self.metrics = None
        self.orders = orders
        self.abbr = ''

        for keyOrder in orders:
            if orders[keyOrder] != 'AS_IS':
                self.abbr = self.abbr + Order[orders[keyOrder]] + PolicyOrder[keyOrder] + '-'
        self.abbr += algName

        
        # self.orders = [Order[orders[0]], Order[orders[1]], Order[orders[2]], Order[orders[3]]]
        # # Por el momento, quitar luego para cuando se combinen varios metodos de orden
        # if self.orders[0] == Order["DESCENDING"]:
        #     self.abbr = "DB-" + algName
        # elif self.orders[1] == Order["DESCENDING"]:
        #     self.abbr = "DL-" + algName
        # elif self.orders[2] == Order["DESCENDING"]:
        #     self.abbr = "RD-" + algName
        # else:
        #     self.abbr = "BR-" + algName


    def fit(self, user, ksp, core, s1: int, s2: int) -> bool:

        routes = self.graph.getRoutes()
        userRoute = routes[user.source, user.destination][ksp]
        routeDistance = self.graph.routesLength[user.source, user.destination][ksp]
        userData = computeFSUs(user.bitRate, routeDistance)
        demand = userData["demand"]

        linksOfRoute = [(x, y) for (x, y) in pairwise(userRoute)]
        toCompared = [True] * demand
        linkState: list = []
        for index, (u, v) in enumerate(linksOfRoute):
            data: list = self.graph.linksFSUs[u, v][core]
            if index == 0:
                linkState = data.copy()
            else:
                linkState = [linkState[i] and data[i] for i in range(len(linkState))]
        for sIndex in range(s1, s2 - demand + 1):
            if linkState[sIndex:sIndex + demand] == toCompared:
                for (u, v) in linksOfRoute:
                    # The user is assigned:
                    self.graph.linksFSUs[u, v][core][sIndex: sIndex + demand] = [False] * demand
                # The user data is updated:
                self.graph.users[user.getId()].setState(True, sIndex, core)  # demand, userData["modulation"], userRoute
                return True
        return False

    # def computeMetrics(self):
    #     return SolutionMetrics(graph=self.graph)

    def setTopology(self, graph: Topology):
        self.graph = graph


class FirstFit(BaseAlgorithm):
    def __init__(self, graph: Topology, orders: dict, priority):
        BaseAlgorithm.__init__(self, graph, orders, "FF")

        self.priority = priority

    def resolve(self):
        sortedUsers = sortUsers(self.graph, self.orders)
        if self.priority == Priority["PATHS"]:
            for core in range(self.graph.getCoresCount()):
                for userIndex, user in enumerate(sortedUsers[0]):
                    if not self.graph.users[user.getId()].getState()["isAssigned"]:
                        for ksp in range(self.graph.getKSPCount()):
                            if self.fit(user, ksp, core, 0, self.graph.getFSUsCount()):
                                break

        else:  # if self.priority == Priority["USERS"]:
            for core in range(self.graph.getCoresCount()):
                for ksp in range(self.graph.getKSPCount()):
                    for userIndex, user in enumerate(sortedUsers[ksp]):
                        if not self.graph.users[user.getId()].getState()["isAssigned"]:
                            self.fit(user, ksp, core, 0, self.graph.getFSUsCount())


        return self.graph


class ParcelFit(BaseAlgorithm):
    def __init__(self, graph: Topology, orders: dict, priority):
        BaseAlgorithm.__init__(self, graph, orders, "PF")

        self.priority = priority

    def resolve(self):
        import math
        sortedUsers = sortUsers(self.graph, self.orders)
        attempts = [0, 1]
        if self.priority == Priority["PATHS"]:
            for core in range(self.graph.getCoresCount()):
                for parcel in range(math.ceil(self.graph.getFSUsCount()/80)):  # Fix hard code!
                    for attempt in attempts:
                        for userIndex, user in enumerate(sortedUsers[0]):
                            if not self.graph.users[user.getId()].getState()["isAssigned"]:
                                if attempt == 0:
                                    end = (parcel+1)*80
                                else:
                                    end = (parcel + 2) * 80
                                for ksp in range(self.graph.getKSPCount()):
                                    if self.fit(user, ksp, core, parcel*80, end):
                                        break

        # First we try to assign all users in each possible parcel, then we analyze another route:
        else:  # if self.priority == Priority["USERS"]:
            for core in range(self.graph.getCoresCount()):
                for ksp in range(self.graph.getKSPCount()):
                    for parcel in range(math.ceil(self.graph.getFSUsCount()/80)):  # Fix hard code!
                        for attempt in attempts:
                            for userIndex, user in enumerate(sortedUsers[ksp]):
                                if not self.graph.users[user.getId()].getState()["isAssigned"]:
                                    if attempt == 0:
                                        end = (parcel + 1) * 80
                                    else:
                                        end = (parcel + 2) * 80
                                    if self.fit(user, ksp, core, parcel * 80, end):
                                        continue

        return self.graph


class SlidingFit(BaseAlgorithm):
    def __init__(self, graph: Topology, orders: dict, priority):
        BaseAlgorithm.__init__(self, graph, orders, "SF")

        self.priority = priority

    def resolve(self):
        usersAssigned = 0
        usersCount = len(self.graph.getUsers())
        sortedUsers = sortUsers(self.graph, self.orders)
        if self.priority == Priority["PATHS"]:
            for core in range(self.graph.getCoresCount()):
                for s1 in range(self.graph.getFSUsCount() - 80):  # Fix hard code!
                    if usersAssigned == usersCount:
                        break
                    for userIndex, user in enumerate(sortedUsers[0]):
                        if not self.graph.users[user.getId()].getState()["isAssigned"]:
                            for ksp in range(self.graph.getKSPCount()):
                                if self.fit(user, ksp, core, s1, s1+80):
                                    usersAssigned += 1
                                    break

        else:  # if self.priority == Priority["USERS"]
            for core in range(self.graph.getCoresCount()):
                for ksp in range(self.graph.getKSPCount()):
                    for s1 in range(self.graph.getFSUsCount() - 80):  # Fix hard code!
                        if usersAssigned == usersCount:
                            break
                        for userIndex, user in enumerate(sortedUsers[ksp]):
                            if not self.graph.users[user.getId()].getState()["isAssigned"]:
                                if self.fit(user, ksp, core, s1, s1 + 80):
                                    usersAssigned += 1

        return self.graph


# class TopologyFit(BaseAlgorithm):
#     def __init__(self, graph: Topology):
#         BaseAlgorithm.__init__(self, graph, orders, "FF")
#         # self.abbr = "SF-" + Order[orders[0]] + Order[orders[1]]
#
#     def resolve(self):
#         pass
