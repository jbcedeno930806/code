import matplotlib.pyplot as plt
import os
from rmlsa.metrics import __checkFile__

baseDir = "../Sim(R+SA)/"
scenNames = ["Scenario2"]
metricLabels = ["relativeCapacity"]
sortingCriterion = ["-DB", "-DL"]
notStrategies = ["DB-", "Mx-"]
import tikzplotlib


for sorting in sortingCriterion:
    strategiesNames = []
    metricsValues = {}
    topNames = []
    for topology in os.listdir(baseDir):
        if topology == "USNet":  # or topology == ""
            continue
        topNames.append(topology)
        for scenFolder in os.listdir(baseDir + topology + "/"):
            if scenFolder == scenNames[0]:
                fileName = baseDir + topology + "/" + scenFolder + "/" + "metricsCoef.csv"
                with open(fileName, 'r') as file:
                    lines = [line.replace(",", ".").replace("\n", "").split(";") for line in file]
                    for metricLabel in metricLabels:
                        columIndex = lines[0].index(metricLabel)
                        if not strategiesNames:
                            strategiesNames = [line[0] for line in lines if not line[0].startswith("Strategies")
                                               if sorting in line[0]]

                        values = [float(line[columIndex]) for idx, line in enumerate(lines) if idx != 0
                                  if sorting in line[0]]
                        if metricLabel not in metricsValues:
                            metricsValues[metricLabel] = [values.copy()]
                        else:
                            metricsValues[metricLabel].append(values.copy())


    for s in scenNames:
        if s == "Scenario1":
            continue
        for metric in metricsValues.keys():
            plt.figure(constrained_layout=True)
            strategiesIndexes = [x for x in range(len(strategiesNames))]
            for topIndex in range(len(topNames)):
                data = metricsValues[metric][topIndex]
                ffValue = 0
                y = []
                for idv, v in enumerate(data):
                    # if idv == 0:
                    #     continue
                        # if v == 0:
                        #     ffValue = 1
                        # else:
                        #     ffValue = v
                    if idv == 0:
                        ffValue = v
                    elif idv >= 1:
                        diff = ffValue-v
                        percent = round(diff/ffValue*100, 2)
                        y.append(percent)

                label = topNames[topIndex]
                plt.plot(strategiesIndexes[1::], y, label=label)

            plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=len(strategiesNames), fontsize="small")
            plt.grid()
            plt.ylabel(metric+"-"+sorting)

            __checkFile__("./Figs1/" + s + "/", None)
            tikzplotlib.save("./Figs1/" + s + "/" + metric +sorting + ".tex", axis_width="8.25cm", axis_height="7.5cm")
            plt.show()
