import matplotlib.pyplot as plt
import os
from rmlsa.metrics import __checkFile__
import tikzplotlib

baseDir = "../Sim(R+SA)/"
scenNames = ["Scenario2"]
# metricLabels = ["assignedUsers", "unassignedFSUs", "unassignedFSU_per_ciento", "fragmentedFSUs", "fragmented_per_ciento", "relativeCapacity", "efficiency"]
metricLabels = ["efficiency"]
sortingCriterion = ["-DB", "-DL"]
saStrategies = ["FF", "SF", "PF"]


# notStrategies = ["DB-", "Mx-"]


for sorting in sortingCriterion:
    strategiesNames = []
    metricsValues = {}
    topNames = []
    values = []

    for topology in os.listdir(baseDir):
        if topology == "USNet":  # or topology == ""
            continue
        topNames.append(topology)

        for metricLabel in metricLabels:
            for scenFolder in os.listdir(baseDir + topology + "/"):
                if scenFolder == scenNames[0]:
                    fileName = baseDir + topology + "/" + scenFolder + "/" + "metricsCoef.csv"
                    with open(fileName, 'r') as file:
                        lines = [line.replace(",", ".").replace("\n", "").split(";") for line in file]

                        columIndex = lines[0].index(metricLabel)
                        if not strategiesNames:
                            strategiesNames = []
                            # for sa in saStrategies:
                            #     strategiesNames.extend([line[0] for line in lines if not line[0].startswith("Strategies")
                            #                             if sorting in line[0] if sa in line[0]])

                            strategiesNames = ([line[0] for line in lines if not line[0].startswith("Strategies")
                                               if sorting in line[0]])

                        # values = []
                        # for sa in saStrategies:
                        #     value = [float(line[columIndex]) for idx, line in enumerate(lines) if idx != 0
                        #              if sorting in line[0] if sa in line[0]]
                        #     values.extend(value)

                        values = [float(line[columIndex]) for idx, line in enumerate(lines) if idx != 0
                                  if sorting in line[0]]



                        if metricLabel not in metricsValues:
                            metricsValues[metricLabel] = [values.copy()]
                        else:
                            metricsValues[metricLabel].append(values.copy())


    for s in scenNames:
        if s == "Scenario1":
            pass
        for metric in metricsValues.keys():
            plt.figure(constrained_layout=True)
            strategiesIndexes = [x for x in range(len(strategiesNames))]
            for topIndex in range(len(topNames)):
                y = metricsValues[metric][topIndex]
                label = topNames[topIndex]
                plt.plot(strategiesIndexes, y, label=label)

            plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=len(strategiesNames), fontsize="small")
            plt.grid()
            plt.ylabel(metric)

            __checkFile__("./FigsSA_Tesis/" + s + "/", None)
            tikzplotlib.save("./FigsSA_Tesis/" + s + "/" + metric +sorting + ".tex", axis_width="8.25cm", axis_height="7.5cm")
            plt.show()
