from rmlsa.graph import Topology
import matplotlib.pyplot as plt
from typing import List
import math


class SolutionMetrics(dict):
    def __init__(self, name="unknown", graph: Topology = None) -> None:
        super().__init__()
        self["name"] = name
        # Number of assigned users:
        self["assignedUsers"] = 0

        # Nuevos:
        # Total network distance (km):
        self["totalDistance"] = 0
        # assigned bitrate in Gbps:
        self["assignedBitrate"] = 0
        # porcentual assigned bitrate in Gbps:
        self["porcentualBitrate"] = 0

        # Total demanded bitrate:
        self["totalBitrate"] = 0
        # Average of bits assigned/link:
        self["bits_per_link"] = 0
        # Total number of assigned users hops:
        self["totalHops"] = 0
        # Numero promedio de saltos por enlaces:
        self["hops_per_assUser"] = 0
        # Numero de nodos:
        self["network_nodes"] = 0
        # Numero de enlaces:
        self["network_links"] = 0

        # Total FSUs demanded by all users:
        self["demandedFSUs"] = 0
        # Number of FSUs assigned of the total demanded:
        self["assignedFSUs"] = 0
        # Number of unassigned FSUs:
        self["unassignedFSUs"] = 0
        # Number of unassigned FSUs in percent:
        self["unassignedFSU_per_ciento"] = 0

        # Number of fragmented FSUs:
        self["fragmentedFSUs"] = 0
        # Number of free/unused FSUs of the network's capacity
        self["freeFSUs"] = 0
        # Relative Capacity:
        self["relativeCapacity"] = 0
        # Number of assigned users and its corresponding modulation:
        self["modulation"] = {"BPSK": 0, "QPSK": 0, "8QAM": 0, "16QAM": 0, "32QAM": 0, "64QAM": 0}
        # Number of assigned FSUs and its corresponding modulation:
        self["usedVsMod"] = {"BPSK": 0, "QPSK": 0, "8QAM": 0, "16QAM": 0, "32QAM": 0, "64QAM": 0}
        # Number of users:
        self["users"] = 0
        # Total Network Capacity:
        self["capacity"] = 0

        self["efficiency"] = 0
        self["fragmented_per_ciento"] = 0
        self["assignedUsers_per_ciento"] = 0
        self["assignedFSUs_per_ciento"] = 0
        self["freeFSUs_per_ciento"] = 0

        self["lrc_coef"] = 0
        self["ldc_coef"] = 0

        self["lrc_mean"] = 0
        self["ldc_mean"] = 0

        if graph is not None:
            self.__initialize__(graph)


    def __initialize__(self, graph):
        self["users"] = len(graph.users)
        self["capacity"] = graph.getTotalCapacity()
        self["totalDistance"] = graph.graph["totalDistance"]
        self["network_nodes"] = graph.getNodesCount()
        self["network_links"] = graph.getLinksCount()

        for userIndex, user in enumerate(graph.users):
            userState = user.getState()
            assigned = userState["isAssigned"]
            modulation = user.modulation
            demand = user.demand
            load = demand * (len(user.route)-1)
            self["demandedFSUs"] += load
            self["totalBitrate"] += user.bitRate
            if assigned:
                self["assignedUsers"] += 1
                self["assignedFSUs"] += load
                self["assignedBitrate"] += user.bitRate
                self["modulation"][modulation] += 1
                self["totalHops"] += len(user.route)-1
                self["usedVsMod"][modulation] += demand * (len(user.route)-1)
            else:
                pass
                # Llenar aqui para los usuarios no asignados


        # Computing the coeficients:
        linkRelativeCapacity = {}
        linkDemandedCapacity = {}

        for (u, v) in graph.edges():
            linkCapacity: list = graph.linksFSUs[u, v]
            for core in range(graph.getCoresCount()):
                a = linkCapacity[core][::-1].copy()
                if False in a:
                    lastUsed = a.index(False)
                else:
                    lastUsed = graph.getFSUsCount()

                self["freeFSUs"] += lastUsed

                linkRelativeCapacity[u, v] = graph.getFSUsCount() - lastUsed
                linkDemandedCapacity[u, v] = 0
                for x in a:
                    if x is False:
                        linkDemandedCapacity[u, v] += 1
                break

        self.computeCoeficients(linkRelativeCapacity, linkDemandedCapacity, graph.getLinksCount())

        self["bits_per_link"] = round(self["assignedBitrate"]/self["network_links"], 2)
        self["porcentualBitrate"] = round(self["assignedBitrate"] / self["totalBitrate"], 4)*100
        self["hops_per_assUser"] = round(self["totalHops"] / self["assignedUsers"], 2)
        self["relativeCapacity"] = self["capacity"] - self["freeFSUs"]
        self["fragmentedFSUs"] = self["relativeCapacity"] - self["assignedFSUs"]
        self["unassignedFSUs"] = self["demandedFSUs"] - self["assignedFSUs"]

        self["unassignedFSU_per_ciento"] = round(self["unassignedFSUs"] / self["demandedFSUs"], 4)*100

        self["efficiency"] = round(self["assignedFSUs"] / self["relativeCapacity"], 4)*100

        scenario1Capacity = 320*self["network_links"]*graph.getCoresCount()
        if scenario1Capacity == self["capacity"]:
            self["fragmented_per_ciento"] = round(self["fragmentedFSUs"] / self["capacity"], 4)*100
        else:
            self["fragmented_per_ciento"] = round(self["fragmentedFSUs"] / self["relativeCapacity"], 4) * 100

        self["assignedUsers_per_ciento"] = round(self["assignedUsers"] / self["users"], 4) * 100

        self["assignedFSUs_per_ciento"] = round(self["assignedFSUs"] / self["demandedFSUs"], 4) * 100
        self["freeFSUs_per_ciento"] = round(self["freeFSUs"] / self["capacity"], 4) * 100


    def computeCoeficients(self, linkRelativeCapacity, linkDemandedCapacity, linksCount):

        lrc_mean = 0
        ldc_mean = 0
        lrc_variance = 0
        ldc_variance = 0

        for key in linkRelativeCapacity.keys():
            lrc_mean += linkRelativeCapacity[key]
            ldc_mean += linkDemandedCapacity[key]

        lrc_mean /= linksCount
        ldc_mean /= linksCount

        for key in linkRelativeCapacity.keys():
            lrc_variance += (linkRelativeCapacity[key] - lrc_mean) ** 2
            ldc_variance += (linkDemandedCapacity[key] - ldc_mean) ** 2

        lrc_variance /= linksCount
        ldc_variance /= linksCount

        lrc_variance = lrc_variance**0.5
        ldc_variance = ldc_variance**0.5

        self["lrc_coef"] = lrc_variance / lrc_mean
        self["ldc_coef"] = ldc_variance / ldc_mean

        self["lrc_mean"] = lrc_mean
        self["ldc_mean"] = ldc_mean


    def users(self) -> int:
        return self["users"]

    def assignedUsers(self) -> int:
        return self["assignedUsers"]

    def modulation(self) -> dict:
        return self["modulation"]

    def assignedBitrate(self) -> int:
        return self["assignedBitrate"]

    def capacity(self) -> int:
        return self["capacity"]

    def usedVsMod(self) -> dict:
        return self["usedVsMod"]

    def used(self) -> int:
        return self["assignedFSUs"]

    def fragmented(self) -> int:
        return self["fragmentedFSUs"]

    def relative(self) -> int:
        return self["relativeCapacity"]

    def freeFSUs(self) -> int:
        return self["freeFSUs"]

    def unAssignedFSUs(self):
        return self["demandedFSUs"]-self["assignedFSUs"]

    def demandedFSUs(self):
        return self["demandedFSUs"]

    def efficiency(self) -> float:
        return round(100 * self["assignedFSUs"] / self["relativeCapacity"], 2)

    def best(self) -> float:
        from math import sqrt
        return sqrt(self.efficiency()/100 * self["assignedUsers"] / self["users"] * self["assignedFSUs"] / self["capacity"])

    def nonAssignedFSUs(self):
        pass

    def bitsPerLinks(self):
        return self["bits_per_link"]

    def hopsPerUsers(self):
        return self["hops_per_assUser"]

    def totalBitrate(self):
        return self["totalBitrate"]

    def __add__(self, other):
        self["users"] += other["users"]
        self["assignedUsers"] += other["assignedUsers"]
        for key in self["modulation"].keys():
            self["modulation"][key] += other["modulation"][key]
            self["usedVsMod"][key] += other["usedVsMod"][key]
        self["assignedBitrate"] += other["assignedBitrate"]
        self["capacity"] += other["capacity"]
        self["assignedFSUs"] += other["assignedFSUs"]
        self["fragmentedFSUs"] += other["fragmentedFSUs"]
        self["relativeCapacity"] += other["relativeCapacity"]
        self["freeFSUs"] += other["freeFSUs"]
        self["demandedFSUs"] += other["demandedFSUs"]
        self["network_nodes"] += other["network_nodes"]
        self["network_links"] += other["network_links"]
        self["totalHops"] += other["totalHops"]
        self["bits_per_link"] += other["bits_per_link"]
        self["hops_per_assUser"] += other["hops_per_assUser"]
        self["totalBitrate"] += other["totalBitrate"]
        self["totalDistance"] += other["totalDistance"]
        self["porcentualBitrate"] += other["porcentualBitrate"]

        self["unassignedFSUs"] += other["unassignedFSUs"]
        self["efficiency"] += other["efficiency"]
        self["fragmented_per_ciento"] += other["fragmented_per_ciento"]
        self["assignedUsers_per_ciento"] += other["assignedUsers_per_ciento"]
        self["assignedFSUs_per_ciento"] += other["assignedFSUs_per_ciento"]
        self["freeFSUs_per_ciento"] += other["freeFSUs_per_ciento"]
        self["unassignedFSU_per_ciento"] += other["unassignedFSU_per_ciento"]

        self["lrc_coef"] += other["lrc_coef"]
        self["ldc_coef"] += other["ldc_coef"]
        self["lrc_mean"] += other["lrc_mean"]
        self["ldc_mean"] += other["ldc_mean"]

        return self

    def __truediv__(self, number: int):
        self["users"] = round(self["users"] / number, 2)
        self["assignedUsers"] = round(self["assignedUsers"] / number, 2)
        for key in self["modulation"].keys():
            self["modulation"][key] = round(self["modulation"][key] / number, 2)
            self["usedVsMod"][key] = round(self["usedVsMod"][key] / number, 2)
        self["assignedBitrate"] = round(self["assignedBitrate"] / number, 2)
        self["capacity"] = round(self["capacity"] / number, 2)
        self["assignedFSUs"] = round(self["assignedFSUs"] / number, 2)
        self["fragmentedFSUs"] = round(self["fragmentedFSUs"] / number, 2)
        self["relativeCapacity"] = round(self["relativeCapacity"] / number, 2)
        self["freeFSUs"] = round(self["freeFSUs"] / number, 2)
        self["demandedFSUs"] = round(self["demandedFSUs"] / number, 2)
        self["bits_per_link"] = round(self["bits_per_link"] / number, 2)
        self["hops_per_assUser"] = round(self["hops_per_assUser"] / number, 2)
        self["totalBitrate"] = round(self["totalBitrate"] / number, 2)
        self["network_nodes"] = round(self["network_nodes"] / number, 2)
        self["network_links"] = round(self["network_links"] / number, 2)
        self["totalHops"] = round(self["totalHops"] / number, 2)
        self["totalDistance"] = round(self["totalDistance"] / number, 2)
        self["porcentualBitrate"] = round(self["porcentualBitrate"] / number, 2)

        self["efficiency"] = round(self["efficiency"] / number, 2)
        self["fragmented_per_ciento"] = round(self["fragmented_per_ciento"] / number, 2)
        self["assignedUsers_per_ciento"] = round(self["assignedUsers_per_ciento"] / number, 2)

        self["assignedFSUs_per_ciento"] = round(self["assignedFSUs_per_ciento"] / number, 2)
        self["freeFSUs_per_ciento"] = round(self["freeFSUs_per_ciento"] / number, 2)
        self["unassignedFSUs"] = round(self["unassignedFSUs"] / number, 2)

        self["unassignedFSU_per_ciento"] = round(self["unassignedFSU_per_ciento"] / number, 2)

        self["lrc_coef"] = round(self["lrc_coef"] / number, 4)
        self["ldc_coef"] = round(self["ldc_coef"] / number, 4)
        self["lrc_mean"] = round(self["lrc_mean"] / number, 4)
        self["ldc_mean"] = round(self["ldc_mean"] / number, 4)
        return self


def toCSV(outputDir, manager):
    __checkFile__(outputDir)
    metricList = manager.getMetrics()
    outputDir += "metricsCoef.csv"
    with open(outputDir, 'a') as file:
        position = file.tell()
        text = ""
        if position == 0:
            for idx, metric in enumerate(metricList[0].keys()):
                if metric == "name":
                    text += "Strategies\\Metrics"
                else:
                    text += str(metric)
                text += ";"
        text += "\n"

        for strategy in metricList:
            text += strategy["name"] + ";"
            for metric in metricList[0].keys():
                if metric == "name":
                    continue
                if type(strategy[metric]) is dict:
                    for key in strategy[metric].keys():
                        text += str(strategy[metric][key]) + "|"
                else:
                    text += str(strategy[metric])
                text += ";"
            # text += "\n"

        text = text.replace(".", ",")
        file.write(text)
        file.close()


        # csvFormated = "Metrics"
        # for strategy in metricList:
        #     csvFormated += ";" + strategy["name"]
        # csvFormated += "\n"
        # for metric in metricList[0].keys():
        #     if metric == "name":
        #         continue
        #     for idx, strategy in enumerate(metricList):
        #         if idx == 0:
        #             line = str(metric)+";"
        #         else:
        #             line = ""
        #         if type(strategy[metric]) is dict:
        #             for key in strategy[metric].keys():
        #                 line += str(strategy[metric][key]) + "|"
        #         else:
        #             line += str(strategy[metric])
        #         csvFormated += line + ";"
        #     csvFormated += "\n"
        #
        # file.write(csvFormated)
        # file.close()


    # def createCSVFormWithReport(self, reports, classifier, resampling, feature):
    #     csvFormated = ''
    #     for label in reports:
    #         if label != 'accuracy' or (label == 'macro avg' and reports[label]['f1-score'] == 0):
    #             precision = reports[label]['precision']
    #             recall = reports[label]['recall']
    #             fscore = reports[label]['f1-score']
    #             csvFormated += classifier + ';' + resampling + ';' + feature + ';' + str(label) + ';' + str(
    #                 precision) + ';' + str(recall) + ';' + str(fscore) + '\n'
    #     return csvFormated



class SolutionManager(object):
    def __init__(self) -> None:
        super().__init__()
        # This is what I want to save:
        self.solutionList:List[Solution] = []

    def addSolution(self, solution):
        self.solutionList.append(solution)

    def getMetrics(self):
        metricsList = []
        for solution in self.solutionList:
            metricsList.append(solution.generateMetrics())
        return metricsList

    def compareWith(self, algName, outputDir, scenario, figSize):
        namesList = []
        metricsList = []
        for solution in self.solutionList:
            if algName in solution.name:
                metricsList.insert(0, solution.generateMetrics())
            else:
                metricsList.append(solution.generateMetrics())
                namesList.append(solution.name)

        if scenario == 1:
            assignedDif = self.compareAssignedUsers(metricsList)
            label = "Assigned Users Comparisson"
            self.makeFigComparisson(namesList, metricsList, outputDir, scenario, figSize, "AssignedUsers", assignedDif,
                                    label)
            fsusDif = self.compareUnassignedFSUs(metricsList)
            label = "Unassigned FSUs Comparisson"
            self.makeFigComparisson(namesList, metricsList, outputDir, scenario, figSize, "UnassignedFSUs", fsusDif,
                                    label)
        else:
            capacityDif = self.compareRelCapacity(metricsList)
            label = "Capacity Saved Comparisson"
            self.makeFigComparisson(namesList, metricsList, outputDir, scenario, figSize, "relCapacity", capacityDif,
                                    label)

    def makeFigComparisson(self, algNames, metricsList, outputDir, scenario, figSize, outputName, differences, label):
        import tikzplotlib
        __checkFile__(outputDir)
        # outputNames = ["AssignedUsers", "relCapacity", "UnassignedFSUs", "Efficiency"]
        vis = Visualization(metricsList)
        vis.fontsize = vis.upperLabelSize = "large"
        fig, ax = plt.subplots()
        ax.margins(x=0.01, y=0)
        plt.grid()
        vis.plotComparisson(ax, algNames, differences, label, scenario)

        output = outputDir + outputName
        # If w & h are set, the fig size its determined by the specified values:
        tikzplotlib.save(output + ".tex", axis_width=figSize[0], axis_height=figSize[1])
        __fixTex__(output + ".tex", vis)

    def compareAssignedUsers(self, metricList: List[SolutionMetrics]):
        assigned = 0
        diference = []
        for index, metric in enumerate(metricList):
            if index == 0:
                assigned = metric.assignedUsers()
            else:
                diference.append(metric.assignedUsers()-assigned)
        return diference

    def compareUnassignedFSUs(self, metricList: List[SolutionMetrics]):
        assigned = 0
        diference = []
        for index, metric in enumerate(metricList):
            if index == 0:
                assigned = metric.unAssignedFSUs()
            else:
                diference.append(metric.unAssignedFSUs() - assigned)
        return diference

    def compareRelCapacity(self, metricList: List[SolutionMetrics]):
        relative = 0
        diference = []
        for index, metric in enumerate(metricList):
            if index == 0:
                relative = metric.relative()
            else:
                diference.append(relative - metric.relative())
        return diference

    @staticmethod
    def loadPkl(fileDir):
        import pickle
        manager = SolutionManager()
        with open(fileDir, "rb") as f:
            manager.solutionList = pickle.load(f)
        return manager

    def toPkl(self, outputDir):
        import pickle
        addr = outputDir + "metrics.pkl"
        with open(addr, 'wb') as f:
            pickle.dump(self.solutionList, f)

    def toTex(self, outputDir, scenario, figSize=('8.25cm', '7.5cm')):
        import tikzplotlib

        metricsList = self.getMetrics()
        __checkFile__(outputDir)
        outputNames = ["AssignedUsers", "relCapacity", "UnassignedFSUs", "Efficiency"]
        vis = Visualization(metricsList)
        vis.fontsize = vis.upperLabelSize = "large"
        if figSize[0] != "8.25cm":
            vis.upperLabelSize = "small"
            vis.rotation = 90
        for index in range(4):
            fig, ax = plt.subplots()
            ax.margins(x=0.01, y=0)

            plt.grid(axis='y', linestyle='--')
            if index == 0:
                vis.__assigned__(ax)
            elif index == 1:
                vis.__capacity__(ax, scenario)
            elif index == 2:
                vis.__unAssignedFSUs__(ax)
            else:
                vis.__efficiency__(ax)

            output = outputDir + outputNames[index]
            # If w & h are set, the fig size its determined by the specified values:
            tikzplotlib.save(output + ".tex", axis_width=figSize[0], axis_height=figSize[1])
            __fixTex__(output + ".tex", vis)


class Solution(object):
    def __init__(self, name: str) -> None:
        super().__init__()
        self.name = name
        self.instances = []

    def addInstance(self, instance):
        self.instances.append(instance)

    def generateMetrics(self):
        metrics = SolutionMetrics(self.name)
        for instance in self.instances:
            metrics += SolutionMetrics(graph=instance)
        metrics /= len(self.instances)
        return metrics


class Visualization(object):
    def __init__(self, metricsList: List[SolutionMetrics]) -> None:
        super().__init__()
        self.metricsList = metricsList
        self.colors = {
            "BPSK": "#5986C9",
            "QPSK": "#E96363",
            "8QAM": "#E9AC63",
            "16QAM": "#68AEB5",
            "32QAM": "#2BD584",
            "64QAM": "#78786E",
            "fragmented": "#CC7812",
            "efficiency": "#5986C9",
        }
        self.width = 0.6
        self.legends = []
        self.xticks = []
        self.ticksLabelSize = 6.5
        self.figsize = (8, 6)
        self.fontsize = 5.5
        self.labelSize = 7.5
        self.upperLabelSize = 5
        self.rotation = 45
        self.ylabels = []
        self.yticks = []

    def Assigned(self):
        fig, ax = plt.subplots(figsize=self.figsize)
        self.__assigned__(ax)
        plt.show()

    def __assigned__(self, ax):
        self.legends = []
        yLimit = 0
        for metric in self.metricsList:
            bottom = 0
            name = metric["name"]
            ax, bottom = self.__fillData__(ax, name, metric.modulation(), bottom)
            yLimit = max(bottom, yLimit)
        ax.set_ylabel(r'Number of Attended Users ($|\mathcal{A}|$)', fontsize=self.labelSize)
        ax.set_xlabel('Spectrum Assignment Strategy', fontsize=self.labelSize)

        totalUser = self.metricsList[0].users()
        self.__fillExtraData__(ax, yLimit, totalUser)

    def Capacity(self, scenario):
        fig, ax = plt.subplots(figsize=self.figsize)
        self.__capacity__(ax, scenario)
        plt.show()

    def __capacity__(self, ax, scenario: int):
        self.legends = []
        yLimit = 0
        for metric in self.metricsList:
            name = metric["name"]
            bottom = 0
            ax, bottom = self.__fillData__(ax, name, metric.usedVsMod(), bottom)
            if "fragmented" in self.legends:
                ax.bar(name, metric.fragmented(), bottom=bottom, width=self.width, edgecolor='k', linewidth=0.2,
                       color=self.colors["fragmented"])
            else:
                self.legends.append("fragmented")
                ax.bar(name, metric.fragmented(), bottom=bottom, width=self.width, label=r"$\mathcal{W}$",
                       edgecolor='k', linewidth=0.2, color=self.colors["fragmented"])
            yLimit = max(bottom + metric.fragmented(), yLimit)

        ax.set_ylabel(r'Relative Network Capacity ($\hat{\mathcal{C}}_{\mathcal{A}}$)', fontsize=self.labelSize)
        ax.set_xlabel('Spectrum Assignment Strategy', fontsize=self.labelSize)

        if scenario == 2:
            total = yLimit
        else:
            total = self.metricsList[0].capacity()
        self.__fillExtraData__(ax, yLimit, total, notation=True)
        # rectangles = ax.patches
        # rects = []
        # new = True
        # x = 0
        # last = None
        # for rect in rectangles:
        #     if new:
        #         last = rect
        #         x = rect.get_x()
        #         new = False
        #         continue
        #     if x == rect.get_x():
        #         last = rect
        #     else:
        #         new = True
        #         rects.append(last)
        # rects.append(last)
        # self.autolabel(rects, ax, True)

    def Efficiency(self):
        fig, ax = plt.subplots(figsize=self.figsize)
        self.__efficiency__(ax)
        plt.show()

    def __efficiency__(self, ax):
        self.legends = []
        yLimit = 100
        for metric in self.metricsList:
            name = metric["name"]
            self.xticks.append(name)
            ax.bar(name, metric.efficiency(), width=self.width, edgecolor='k', linewidth=0.2,
                   color=self.colors["efficiency"])
        ax.set_ylabel(r"Spectrum Efficiency ($\eta_{SA}$)", fontsize=self.labelSize)
        ax.set_xlabel('Spectrum Assignment Strategy', fontsize=self.labelSize)
        rects = ax.patches
        self.autolabel(rects, ax)
        self.__fillExtraData__(ax, yLimit, yLimit)

    def __unAssignedFSUs__(self, ax):
        self.legends = []
        yLimit = 0
        for metric in self.metricsList:
            name = metric["name"]
            self.xticks.append(name)
            unassigneds = metric.unAssignedFSUs()
            yLimit = max(unassigneds, yLimit)
            ax.bar(name, metric.unAssignedFSUs(), width=self.width, edgecolor='k', linewidth=0.2,
                   color=self.colors["efficiency"])
        ax.set_ylabel(r"Unassigned FSUs", fontsize=self.labelSize)
        ax.set_xlabel('Spectrum Assignment Strategy', fontsize=self.labelSize)
        # rects = ax.patches
        # self.autolabel(rects, ax)
        self.__fillExtraData__(ax, yLimit, yLimit, notation=True)

    def plotComparisson(self, ax, algNames, differences, yLabel, scenario):
        self.legends = []
        yMax = 0
        yMin = 0
        for index, data in enumerate(differences):
            if data > yMax:
                yMax = data
            if data < yMin:
                yMin = data

            name = algNames[index]
            self.xticks.append(name)
            ax.bar(name, data, width=self.width, edgecolor='k', linewidth=0.2,
                   color=self.colors["efficiency"])
        ax.set_ylabel(yLabel, fontsize=self.labelSize)
        ax.set_xlabel('Spectrum Assignment Strategy', fontsize=self.labelSize)

        maxValue = max(yMax, abs(yMin))
        if yMax > abs(yMin):
            step = math.ceil(yMax / 2)
            yticks = [k * step for k in range(2)]
            yticks.append(yMax)
            # if abs(yMin) >= 0.2*step:
            if yMin != 0:
                yticks.insert(0, -1*(int(abs(yMin)/step) + 1)*step)
            # marginBottom = yticks[0] - 0.02 * maxValue
            # marginTop = yticks[-1] - 0.02 * maxValue
        else:
            step = math.ceil(yMin / 2)
            yticks = [k * step for k in range(2)]
            yticks.insert(0, yMin)
            # if yMax >= 0.2*abs(step):
            if yMax != 0:
                yticks.append((int(yMax / abs(step)) + 1) * abs(step))
            else:
                yticks.append(0)
        marginBottom = yticks[0] - 0.02 * maxValue
        marginTop = yticks[-1] + 0.02 * maxValue

        yticks.insert(0, marginBottom)
        yticks.append(marginTop)
        plt.ylim((marginBottom, marginTop))

        self.yticks = yticks

        if scenario == 1:
            self.ylabels = self.createLabels(yticks, yMax, False)
        else:
            self.ylabels = self.createLabels(yticks, yMax, True)
        ax.set_yticks(yticks)

        ax.set_yticklabels(self.ylabels, fontsize=self.ticksLabelSize)
        ax.set_xticklabels(self.xticks, fontsize=self.ticksLabelSize, rotation=self.rotation)
        if self.legends:
            plt.legend(loc=0, fontsize=self.fontsize, ncol=len(self.legends), columnspacing=0.8,
                       handlelength=0.8, handletextpad=0.2)  #
        self.xticks = []

    def __fillData__(self, ax, name, data, bottom):
        self.xticks.append(name)
        for modulation in data.keys():
            y = data[modulation]
            if y != 0:
                if modulation in self.legends:
                    ax.bar(name, y, bottom=bottom, width=self.width, edgecolor='k', linewidth=0.2,
                           color=self.colors[modulation])
                else:
                    self.legends.append(modulation)
                    ax.bar(name, y, bottom=bottom, width=self.width, label=modulation, linewidth=0.2,
                           edgecolor='k', color=self.colors[modulation])
            bottom += y
        return ax, bottom

    def __fillExtraData__(self, ax, yLimit, total, notation=False):
        if yLimit > 0.6 * total:
            step = math.ceil(total / 5)
            yticks = [k * step for k in range(5)]
            top = total
            yticks.append(total)
        else:
            step = math.ceil(yLimit / 4)
            yticks = [k * step for k in range(5)]
            top = math.ceil(step*5.5)
            yticks.append(top)

        marginBottom = -0.01 * yticks[-1]
        marginTop = 1.02 * top
        yticks.insert(0, marginBottom)
        yticks.append(marginTop)
        plt.ylim((marginBottom, marginTop))
        ax.set_yticks(yticks)
        self.yticks = yticks
        self.ylabels = self.createLabels(yticks, total, notation)
        ax.set_yticklabels(self.ylabels, fontsize=self.ticksLabelSize)
        ax.set_xticklabels(self.xticks, fontsize=self.ticksLabelSize, rotation=self.rotation)

        if self.legends:
            plt.legend(loc=0, fontsize=self.fontsize, ncol=len(self.legends), columnspacing=0.8,
                       handlelength=0.8, handletextpad=0.2)
        self.xticks = []

    def createLabels(self, yticks, total, notation):
        wasZero = False
        i = -1
        labels = []
        for index, l in enumerate(yticks):
            if l == 0:
                if not wasZero:
                    wasZero = True
                else:
                    i = index
                    continue
            if index == 0 or index == len(yticks) - 1:
                labels.append("")
            else:
                if index == len(yticks) - 2:
                    value = total
                else:
                    value = l
                if notation:
                    labels.append(self.expFormat(value))
                else:
                    labels.append("{:.0f}".format(value))

        if i != -1:
            yticks.pop(i)

        return labels

    def autolabel(self, rects, ax, stackBar=False):
        """Funcion para agregar una etiqueta con el valor en cada barra"""
        for rect in rects:
            # if not stackBar:
            height = rect.get_height()
            xy = (rect.get_x() + rect.get_width() / 2, height+0.01*height)
            xytext = (0, 1)  # 1 points vertical offset
            label = '{:.2f}'.format(height)

            #     Este codigo era para colocar el monto de FSUs fragmentados en el grafico del Capacity
            # else:
            #     xy = (rect.get_x() + rect.get_width() / 2, 0.3*height + rect.get_y())
            #     xytext = (0, 0)
            #     label = self.expFormat(height)

            ax.annotate(label,
                        xy=xy,
                        xytext=xytext,  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom',
                        fontsize=self.upperLabelSize)

    @staticmethod
    def expFormat(value):
        formatted = "{:.1e}".format(value)
        if "+0" in formatted:
            formatted = formatted.replace("+0", "")
        if "0.0e0" in formatted:
            formatted = "0"
        # if ".0" in formatted:
        #     formatted = formatted.replace(".0", "")
        return formatted


def __checkFile__(baseDir, fileName=None):
    import os
    if not os.path.exists(baseDir):
        os.makedirs(baseDir)
    if fileName is not None:
        if not os.path.exists(fileName):
            with open(fileName, 'w') as file:
                file.close()


# def __writeMetric__(file, algName, metric=None, line: str = "None", isFirst: bool = True, legend: bool = False):
#     if isFirst:
#         data = "({0}, {1})".format(algName, str(metric))
#         output = "\\addplot+ [ybar] coordinates {" + data + "};\n"
#     else:
#         if not legend:
#             info = line.split("};\n")
#             data = "({0}, {1})".format(algName, str(metric)) + "};\n"
#             info[-1] = data
#         else:
#             info = line.split("};")
#             info[-2] = info[-2] + ","
#             data = algName + "};"
#             info[-1] = data
#         output = " ".join(info)
#
#     file.write(output)
#
#
# def plotAssigned(baseDir: str, metrics: SolutionMetrics, algName: str):
#     fileName = baseDir + "Assigned.txt"
#     __checkFile__(baseDir, fileName)
#     with open(fileName, 'r+') as file:
#         lines = [line for line in file if not line.startswith('#')]
#         file.seek(0)
#         modMetrics = metrics.modulation()
#         if len(lines) == 0:
#             for modulation in modMetrics:
#                 __writeMetric__(file, algName, modMetrics[modulation])
#             file.write("symbolic x coords={" + algName + "};")
#
#         else:
#             modMetricsValues = list(modMetrics.values())
#             for index, line in enumerate(lines):
#                 if index != len(lines)-1:
#                     __writeMetric__(file, algName, modMetricsValues[index], line, False)
#                 else:
#                     __writeMetric__(file, algName, None, line, False, True)
#         file.close()
#
#
# def plotRelCapacity(baseDir: str, metrics: SolutionMetrics, algName: str):
#     fileName = baseDir + "Capacity.txt"
#     __checkFile__(baseDir, fileName)
#
#     with open(fileName, 'r+') as file:
#         lines = [line for line in file if not line.startswith('#')]
#         file.seek(0)
#         usedMetrics = metrics.usedVsMod()
#
#         if len(lines) == 0:
#             for modulation in usedMetrics:
#                 __writeMetric__(file, algName, usedMetrics[modulation])
#             __writeMetric__(file, algName, metrics.fragmented())
#             file.write("symbolic x coords={" + algName + "};")
#
#         else:
#             modMetricsValues = list(usedMetrics.values())
#             for index, line in enumerate(lines):
#                 if index < len(lines)-2:
#                     __writeMetric__(file, algName, modMetricsValues[index], line, False)
#                 elif index < len(lines)-1:
#                     __writeMetric__(file, algName, metrics.fragmented(), line, False)
#                 else:
#                     __writeMetric__(file, algName, None, line, False, True)
#         file.close()
#
#
# def plotEfficiency(baseDir: str, metrics: SolutionMetrics, algName: str):
#     fileName = baseDir + "Efficiency.txt"
#     __checkFile__(baseDir, fileName)
#
#     with open(fileName, 'r+') as file:
#         lines = [line for line in file if not line.startswith('#')]
#         file.seek(0)
#
#         if len(lines) == 0:
#             __writeMetric__(file, algName, metrics.efficiency())
#             file.write("symbolic x coords={" + algName + "};")
#
#         else:
#             for index, line in enumerate(lines):
#                 if index == 0:
#                     __writeMetric__(file, algName, metrics.efficiency(), line, False)
#                 else:
#                     __writeMetric__(file, algName, None, line, False, True)
#         file.close()


def toEPS(outputDir, metricsList: List[SolutionMetrics], scenario):
    __checkFile__(outputDir)
    plt.rc('pgf', texsystem='pdflatex')
    outputNames = ["AssignedUsers", "relCapacity", "Efficiency"]
    vis = Visualization(metricsList)
    figSize = (3.24, 2.85)
    for index in range(3):
        fig, ax = plt.subplots(figsize=figSize, constrained_layout=True)
        if index == 0:
            vis.__assigned__(ax)
        elif index == 1:
            vis.__capacity__(ax, scenario)
        else:
            vis.__efficiency__(ax)

        output = outputDir+outputNames[index]
        plt.savefig(output+".eps")


def __fixTex__(fileDir, vis):
    with open(fileDir, 'r+') as file:
        lines = []
        islabeled = False
        for line in file:
            if line.startswith("yticklabels"):
                islabeled = True
            if line.startswith("legend style="):
                lines.append("legend style={legend columns=-1, fill opacity=0.8, font=\\tiny},\n")
            elif line.startswith("xticklabel style = {"):
                lines.append("xticklabel style = {rotate={"+str(vis.rotation)+"},font=\\scriptsize},\n")
                lines.append("yticklabel style = {font=\\scriptsize},\n")
            elif line.startswith("\\end{tikzpicture}"):
                lines.append(line)
                break
            else:
                lines.append(line)

        if not islabeled:
            ticks = ",".join([str(v) for v in vis.yticks])
            labels = ",".join([str(v) for v in vis.ylabels])
            text = "ytick={" + ticks + "}, \n" + "yticklabels={" + labels + "}, \n"
            lines.insert(15, text)


        # Fix legend markers:
        lines.insert(3, "\\pgfplotsset{\n"
                        "/pgfplots/ybar legend/.style={\n"
                        " /pgfplots/legend image code/.code={\n"
                        " \\draw [##1,/tikz/.cd,bar width=5pt,yshift=-0.2em,bar shift=0pt]\n"
                        " plot coordinates {(0cm,0.6em)};}, }, }")

        file.seek(0)
        for line in lines:
            file.write(line)
        file.close()
