RouteAlgorithms = {
    "Dijkstra": "Dijkstra",
    "Baroni": "Baroni",
    "From File": "From File",
    "LeastLoad": "LeastLoad",
    "DirectBalance": "DirectBalance",
    "Mixed": "Mixed"
}

RouteMetric = {
    "Length": "length",
    "Hops": None
}

LinkUsage = {
    "Users": "users",
    "Demands": "demands"
}

Order = {
    "AS_IS": "N",
    "ASCENDING": "A",
    "DESCENDING": "D",
    "RANDOM": "R",
    "IN_LOOP": "I"
}

PolicyOrder = {
    'hopsOrder': "L",
    'demandsOrder': "B",
    'loadOrder': "RL",
    'bitrateOrder': "BR",
}

Priority = {
    "PATHS": "PATHS",
    "USERS": "USERS"
}


def pairwise(iterable):
    """s -> (s0,s1), (s1,s2), (s2, s3), ..."""
    import itertools
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)


modulationList = ["BPSK", "QPSK", "8QAM", "16QAM", "32QAM", "64QAM"]
# Bit Rate vs Distance table: row -> Distance; columns -> Bit Rate
table_BitRate_vs_Distance = [[1, 4, 8, 32, 80],  # distance 4000km
                             [1, 2, 4, 16, 40],  # distance 2000km
                             [1, 2, 3, 11, 27],  # distance 1000km
                             [1, 1, 2, 8, 20],  # distance 500km
                             [1, 1, 2, 7, 16],  # distance 250km
                             [1, 1, 2, 6, 14]]  # distance 125km


def computeFSUs(bitRate, distance) -> dict:
    # Here is obtained the transmission bitrate index:
    if bitRate == 10:
        v = 0
    elif bitRate == 40:
        v = 1
    elif bitRate == 100:
        v = 2
    elif bitRate == 400:
        v = 3
    else:  # bitRate == 1000
        v = 4

    # Here is obtained the modulation and the distance index:
    if distance <= 80:
        u = 5
    elif 125 < distance <= 240:
        u = 4
    elif 250 < distance <= 560:
        u = 3
    elif 500 < distance <= 1360:
        u = 2
    elif 1000 < distance <= 2720:
        u = 1
    else:  # 2720 < distance <= 5520
        u = 0

    return {"demand": table_BitRate_vs_Distance[u][v],
            "modulation": modulationList[u]}


def sortUsers(graph, orders: dict) -> list:
    from rmlsa.graph import Topology
    import numpy as np
    # Important:
    # orders must contain the sorting metrics in order of priority.

    graph: Topology = graph
    sortedUsers = []
    routes = graph.getRoutes()
    routesLength = graph.routesLength
    users = graph.users

    for routeIndex in range(graph.getKSPCount()):
        steps = []
        loads = []
        demands = []
        bitrate = []
        for user in users:
            steps.append(len(routes[user.source, user.destination][routeIndex]) - 1)
            distance = routesLength[user.source, user.destination][routeIndex]
            fsusDemand = computeFSUs(user.bitRate, distance)["demand"]
            routeHops = len(user.route)
            demands.append(fsusDemand)
            loads.append(fsusDemand * routeHops)
            bitrate.append(user.bitRate)

        # users = [0, 1, 2, 3, 4]
        # steps = [6, 4, 5, 6, 6]
        # demands = [20, 10, 30, 5, 10]

        users_sorted = []
        keysInverted = [key for key in orders][::-1]
        for i, order_key in enumerate(keysInverted):
            if order_key == 'hopsOrder':
                toSort = steps.copy()
            elif order_key == 'demandsOrder':
                toSort = demands.copy()
            elif order_key == 'loadOrder':
                toSort = loads.copy()
            else:
                toSort = bitrate.copy()

            if orders[order_key] == "AS_IS":
                indexes = np.array(range(len(users)))
            elif orders[order_key] == "ASCENDING":
                # indexes = np.argsort(np.array(toSort), kind="stable")
                indexes = np.array(_sort(toSort, 'A'))
            else:
                indexes = np.array(_sort(toSort, 'D'))

            steps = [steps[index] for index in indexes]
            demands = [demands[index] for index in indexes]
            loads = [loads[index] for index in indexes]
            bitrate = [bitrate[index] for index in indexes]
            if i == 0:
                users_sorted = [users[index] for index in indexes]
            else:
                users_sorted = [users_sorted[index] for index in indexes]

        sortedUsers.append(users_sorted)

    return sortedUsers


def _sort(data: list, typo: str):
    indexes = [*range(len(data))]
    c = len(data)-1
    while c != 0:
        for x in range(c):
            a = data[x]
            b = data[x+1]
            if typo == 'D':
                if b > a:  # descendente
                    data[x] = data[x+1]
                    data[x+1] = a
                    i = indexes[x]
                    indexes[x] = indexes[x+1]
                    indexes[x + 1] = i
            if typo == 'A':
                if b < a:  # ascendente
                    data[x] = data[x+1]
                    data[x+1] = a
                    i = indexes[x]
                    indexes[x] = indexes[x+1]
                    indexes[x + 1] = i
        c -= 1
    return indexes











