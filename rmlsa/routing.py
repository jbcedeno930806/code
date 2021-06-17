import itertools
import networkx as nx
from rmlsa.tools import pairwise, computeFSUs


policyMetric = {
    "Users": "users",
    "Demands": "demands"
}


criterionMetric = {
    "Max.": 0,
    "Sum": 1,
    "Variance": 2
}


def dijkstra(topology):
    kShortestPaths = {}
    kShortestPathsLength = {}
    ksp = topology.getKSPCount()
    metric = topology.graph["routeMetric"]
    for idn1, idn2 in itertools.combinations(topology.nodes, 2):
        paths = __generateShortestRoutes__(topology, idn1, idn2, metric, ksp)
        lengths = topology.getDistance(paths)
        kShortestPaths[idn1, idn2] = paths
        kShortestPaths[idn2, idn1] = [path[::-1] for path in paths]
        kShortestPathsLength[idn1, idn2] = kShortestPathsLength[idn2, idn1] = lengths
    return kShortestPaths, kShortestPathsLength


def baroni(topology, ksp):
    kShortestPaths = {}
    metric = topology.graph["routeMetric"]
    for idn1, idn2 in itertools.combinations(topology.nodes, 2):
        # It is computed the k shortest routes:
        paths = __generateShortestRoutes__(topology, idn1, idn2, metric, ksp)
        sameHopsPaths = [path for path in paths if len(path) == len(paths[0])]
        kShortestPaths[idn1, idn2] = sameHopsPaths
        kShortestPaths[idn2, idn1] = [path[::-1] for path in sameHopsPaths]
    criterion = 0
    return __balanceRoutes__(topology, kShortestPaths, criterion)


def leastLoad(topology, ksp):
    kShortestPaths = __computeAlternativePaths__(topology, ksp)
    criterion = topology.graph["criterion"]
    return __balanceRoutes__(topology, kShortestPaths, criterion)


def directBalance(topology, ksp):
    kShortestPaths = {}
    metric = topology.graph["routeMetric"]
    for idn1, idn2 in itertools.permutations(topology.nodes, 2):
        user = topology.getUsers(idn1, idn2)[0]
        bitrate = user.bitRate
        paths = __generateShortestRoutes__(topology, idn1, idn2, metric, ksp)
        lengths = topology.getDistance(paths)
        modulations = [computeFSUs(bitrate, length)["modulation"] for length in lengths]

        kShortestPaths[idn1, idn2] = [path for index, path in enumerate(paths)
                                      if modulations[index] == modulations[0]]
    criterion = topology.graph["criterion"]
    return __directBalanceRoutes__(topology, kShortestPaths, criterion)


def __computeAlternativePaths__(topology, ksp):
    kShortestPaths = {}
    dmds = {}
    metric = topology.graph["routeMetric"]
    for idn1, idn2 in itertools.permutations(topology.nodes, 2):
        user = topology.getUsers(idn1, idn2)[0]
        bitrate = user.bitRate
        paths = __generateShortestRoutes__(topology, idn1, idn2, metric, ksp)
        lengths = topology.getDistance(paths)
        demands = [computeFSUs(bitrate, length)["demand"] for length in lengths]

        usage = -1
        kShortestPaths[idn1, idn2] = []
        dmds[idn1, idn2] = []
        for path, demand in zip(paths, demands):
            testingUsage = (len(path) - 1) * demand
            if testingUsage < usage or usage == -1:
                usage = testingUsage
                kShortestPaths[idn1, idn2] = [path]
                dmds[idn1, idn2] = [testingUsage]
            elif testingUsage == usage:
                kShortestPaths[idn1, idn2].append(path)
                dmds[idn1, idn2].append(testingUsage)

    total = 0
    for key in dmds.keys():
        total += dmds[key][-1]
    return kShortestPaths


def mixed(topology, ksp):
    kShortestPaths = __computeAlternativePaths__(topology, ksp)
    criterion = topology.graph["criterion"]
    return __directBalanceRoutes__(topology, kShortestPaths, criterion)


def __generateShortestRoutes__(topology, source, target, metric, ksp):
    values = nx.shortest_simple_paths(topology, source, target, metric)
    paths = list(itertools.islice(values, ksp))
    return paths


def __getUsageDemand__(topology, usageMetric, route):
    if usageMetric == "users":
        demand = 1
    else:
        user = topology.getUsers(route[0], route[-1])[0]
        length = topology.getDistance([route])[0]
        demand = computeFSUs(user.bitRate, length)["demand"]
    return demand


def __balanceRoutes__(topology, kShortestPaths: dict, criterion):
    routesIdSelected = {}
    linksUsage = [0] * len(topology.edges())
    kShortestPathsLength = {}
    keys = sortRoutes(topology, kShortestPaths, [byLoad, byHops], ["d", "d"])

    for key in keys:
        routesIdSelected[key] = 0
        route = kShortestPaths[key][routesIdSelected[key]]
        linksUsage = __updateUsage__(topology, route, linksUsage)[0]

    wasChanged = True
    while wasChanged:
        wasChanged = False
        for key in keys:
            if key[0] == 18 and key[1] == 6:
                a=2
            route = kShortestPaths[key][routesIdSelected[key]]
            linksUsage = __updateUsage__(topology, route, linksUsage, False)[0]
            routeId, linksUsage = balanceCriterion(topology, kShortestPaths[key],
                                                   linksUsage, criterion, routesIdSelected[key])
            if routeId != routesIdSelected[key]:
                wasChanged = True
                routesIdSelected[key] = routeId


    for idn1, idn2 in itertools.permutations(topology.nodes, 2):
        paths = [kShortestPaths[idn1, idn2][routesIdSelected[idn1, idn2]]]
        lengths = topology.getDistance(paths)
        kShortestPaths[idn1, idn2] = paths
        kShortestPathsLength[idn1, idn2] = lengths

    return kShortestPaths, kShortestPathsLength


def __directBalanceRoutes__(topology, kShortestPaths: dict, criterion):
    keys = sortRoutes(topology, kShortestPaths, [byLoad, byHops], ["d", "d"])
    routesIdSelected = {}
    linksUsage = [0] * len(topology.edges())
    kShortestPathsLength = {}
    for key in keys:
        routesIdSelected[key], linksUsage = balanceCriterion(topology, kShortestPaths[key], linksUsage, criterion)
    for key in kShortestPaths.keys():
        paths = [kShortestPaths[key][routesIdSelected[key]]]
        lengths = topology.getDistance(paths)
        kShortestPaths[key] = paths
        kShortestPathsLength[key] = lengths
    return kShortestPaths, kShortestPathsLength


def balanceCriterion(topology, nodeRoutes, currentUsage, criterion, currentIdSelected=None):
    usageCriterionList = []
    usageList = []
    for routeId in range(len(nodeRoutes)):
        route = nodeRoutes[routeId]
        result = __updateUsage__(topology, route, currentUsage)
        usageList.append(result[0])

        criterionValue = criterion + 1
        usageCriterionList.append(result[criterionValue])

    minCriterion = min(usageCriterionList)
    minsIndexes = [i for i in range(len(usageCriterionList)) if usageCriterionList[i] == minCriterion]
    if currentIdSelected is not None and currentIdSelected in minsIndexes:
        i = currentIdSelected
    else:
        i = minsIndexes[0]
    return i, usageList[i]


def __updateUsage__(topology, route, linksUsage, isAdding=True):
    import math
    usageMetric = topology.graph["usageMetric"]
    edgesOfRoute = [(x, y) for x, y in pairwise(route)]
    edgesIdOfRoute = [topology.get_edge_data(edge[0], edge[1])["id"] for edge in edgesOfRoute]
    newLinksUsage = linksUsage.copy()
    demand = int(__getUsageDemand__(topology, usageMetric, route))
    for edgeId in edgesIdOfRoute:
        if isAdding:
            newLinksUsage[edgeId] += demand
        else:
            newLinksUsage[edgeId] -= demand

    if isAdding:
        routeUsage = [newLinksUsage[edgeId] for edgeId in edgesIdOfRoute]
        totalRouteUsage = sum(routeUsage)
        maxRouteUsage = max(routeUsage)

        # Calcular la varianza:
        totalMean = round(sum(linksUsage[::1]) / len(linksUsage), 2)
        maxUsage = max(linksUsage)
        if maxUsage == 0:
            linksCost = [1 for edgeId in edgesIdOfRoute]
        else:
            linksCost = [math.exp((linksUsage[edgeId] - totalMean)/maxUsage) for edgeId in edgesIdOfRoute]
        # linksCost = [(linksUsage[edgeId] - totalMean)**2 for edgeId in edgesIdOfRoute]
        routeCost = sum(linksCost)
        # routeCost = math.exp(routeMean - totalMean)
    else:
        # routeUsage = [linksUsage[edgeId] for edgeId in edgesIdOfRoute]
        totalRouteUsage = None
        maxRouteUsage = None
        routeCost = None

    return newLinksUsage, maxRouteUsage, totalRouteUsage, routeCost


def sortRoutes(topology, kshortesPath: dict, funcMetrics, policies):
    import numpy as np
    funcMetrics = funcMetrics[::-1]
    routes = [kshortesPath[key][0] for key in kshortesPath.keys()]
    keysList = list(kshortesPath.keys())

    indexesList = []
    for i in range(len(funcMetrics)):
        values = []
        for route in routes:
            values.append(funcMetrics[i](topology, route))
        if policies[i] == "a":
            sortedIndexes = np.argsort(np.array(values), kind="stable")
        else:
            sortedIndexes = np.argsort(np.array(values), kind="stable")[::-1]
        indexesList.append(sortedIndexes)
    for i in range(1, len(funcMetrics)):
        keysList = [keysList[index] for index in indexesList[i]]
    return keysList


def byLoad(topology, route):
    u = route[0]
    v = route[-1]
    user = topology.getUsers(u, v)[0]
    hops = len(route)
    distance = topology.getDistance([route])[0]
    demand = computeFSUs(user.bitRate, distance)["demand"]
    load = hops * demand
    return load


def byHops(topology, route):
    return len(route)

