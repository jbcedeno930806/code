from .tools import computeFSUs


class User(object):
    def __init__(self, userId, source, destination, bitRate):
        object.__init__(self)
        self.userId = userId
        self.source = source
        self.destination = destination
        self.bitRate = bitRate
        self.route = []
        self.distance = 0
        self.modulation = ""
        self.demand = 0

        self.state = {
            "isAssigned": False,
            "sIndex": 0,
            "core": 0
        }

    def setState(self, isAssigned: bool, sIndex: int, core: int):

        self.state["isAssigned"] = isAssigned
        self.state["sIndex"] = sIndex
        self.state["core"] = core


    def update(self, route, distance):
        computed = computeFSUs(self.bitRate, distance)
        self.demand = computed["demand"]
        self.modulation = computed["modulation"]
        self.route = route
        self.distance = distance


    def getId(self):
        return self.userId

    def getState(self):
        return self.state
