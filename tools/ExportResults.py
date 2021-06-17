import numpy as np
from typing import List
import methods.FirstFit as ff
import os
from decimal import Decimal
from rmlsa.graph import Topology


class BarPlot(object):
    def __init__(self):
        object.__init__(self)

    NEW_BAR = "NEW_BAR"
    OLD_BAR = "OLD_BAR"


class ExportResults(object):
    def __init__(self, resultsToExport: List[ff.FirstFitResults], simCount,
                 fragmentedCount, freeCount, assigned_prom, FSUsCount, totalFSUs, graph: Topology):
        object.__init__(self)
        self.projectDir = os.getcwd()
        self.resultsToExport = resultsToExport
        self.simCount = simCount
        self.fragmentedCount = fragmentedCount
        self.freeCount = freeCount
        self.assigned_prom = assigned_prom
        self.results = []
        self.FSUsCount = FSUsCount
        self.discriminateResults()
        self.totalFSUs = totalFSUs
        self.capacityUsed = 0
        self.graph = graph
        self.numUser = graph.getNodesCount()*(graph.getNodesCount()-1)

    def discriminateResults(self):
        from rmlsa.components import DemandsGenerator
        for modulation in DemandsGenerator.modulationList:
            r = []
            for result in self.resultsToExport:
                if result.hasCapacity and result.modulation == modulation:
                    r.append(result)

            self.results.append(r)

    def export(self, barType: BarPlot):
        tableName = ["assignedUsers", "relCapacity", "Efficiency", "BW"]
        # if barType == BarPlot.OLD_BAR:
        for x in [7, 8, 9, 10]:
        # for x in [10]:
            columnsCount = x
            name = tableName[x-7]
            relativeTable1Dir = "\\Simulaciones\\"+name+".txt"
            resultsDir = self.projectDir + relativeTable1Dir

            allText, last_method = self.readFile(resultsDir)
            if x == 7:
                allText = self.resolveDataTable1(allText, last_method, columnsCount)
            elif x == 8:
                allText = self.resolveDataTable2(allText, last_method, columnsCount)
            elif x == 9:
                allText = self.resolveDataTable3(allText, last_method)
            else:
                self.resolveDataTable4(resultsDir)
                continue

            if x != 9:
                self.writeFile(resultsDir, allText, last_method, columnsCount)
            else:
                self.writeFile(resultsDir, allText, last_method, 1)

        # else:
        #     for x in [1, 2]:
        #         relativeTable1Dir = "\\Simulaciones\\table"+str(x+3)+".txt"
        #         resultsDir = self.projectDir + relativeTable1Dir
        #         if x == 1:
        #             columnsCount = 6
        #             allText, last_method = self.readFile(resultsDir)
        #             allText = self.fillTable1(allText, last_method, columnsCount)
        #         else:
        #             columnsCount = 6
        #             allText, last_method = self.readFile(resultsDir)
        #             allText = self.fillTable2(allText, last_method, columnsCount)
        #
        #     self.writeFile(resultsDir, allText, last_method, columnsCount)


    def readFile(self, resultsDir):

        allText = []
        try:
            file = open(resultsDir, "r")
            for line in file:
                allText.append(line[0:len(line) - 1])
            file.close()
            firstLine = allText[0]
            firstLine = firstLine[::-1]
            pos2 = firstLine.find(",")
            pos1 = firstLine.find("(", pos2)
            last_method = int(firstLine[pos2 + 1:pos1][::-1])

        except:
            last_method = 0

        return allText, last_method

    def writeFile(self, resultsDir, allText, last_method, columnsCount):
        if last_method == 0:
            simbolicLine = "symbolic x coords={1}\n"
            allText.append(simbolicLine)
        else:
            simbolicLine = allText[columnsCount]
            simbolicLine = simbolicLine[0:len(simbolicLine)-1] + ", " + str(last_method + 1) + "}\n"
            allText[columnsCount] = simbolicLine

        try:
            f = open(resultsDir, "w")
            f.writelines(allText)
            f.close()
        except:
            pass

    # Assigned + unassigned users:
    def resolveDataTable1(self, allText, last_method, columnsCount):

        for col in range(0, columnsCount):
            if col == 6:
                data = 0
                for res in self.results:
                    data += len(res)
                data = np.round(float(Decimal(str(self.numUser))-Decimal(str(data/self.simCount))), 2)  # Usuarios no Asignados
            else:
                data = np.round(len(self.results[col])/self.simCount, 2) # Usuarios Asignados acorde a su modulación

            text = str.format(" ({0},{1})", last_method+1, data)
            if last_method == 0:
                beginText = "\\addplot+ [ybar] coordinates {" + text + "};\n"
                allText.append(beginText)

            else:
                lineText = allText[col]
                allText[col] = lineText[0:len(lineText)-2]+text+lineText[len(lineText)-2:len(lineText)]+"\n"
        return allText

    # Total Network Capacity:
    def resolveDataTable2(self, allText, last_method, columnsCount):

        for col in range(0, columnsCount):
            data = 0
            if col == 6:
                data = self.fragmentedCount
            elif col == 7:
                data = self.freeCount
            else:
                for i in self.results[col]:
                    data += i.traffic*len(i.linksOfPath)
            if col != 7:
                data = np.round(data / self.simCount, 2)
                self.capacityUsed = float(Decimal(str(self.capacityUsed)) + Decimal(str(data)))  # Capcidad relativa
            else:
                data = float(Decimal(str(self.totalFSUs)) - Decimal(str(self.capacityUsed)))  # Capcidad disponible

            text = str.format(" ({0},{1})", last_method + 1, data)
            if last_method == 0:
                beginText = "\\addplot+ [ybar] coordinates {" + text + "};\n"
                allText.append(beginText)

            else:
                lineText = allText[col]
                allText[col] = lineText[0:len(lineText) - 2] + text + lineText[len(lineText) - 2:len(lineText)] + "\n"
        return allText

    # Efficiency:
    def resolveDataTable3(self, allText, last_method):

        data = np.round(100 - 100*self.fragmentedCount/(self.simCount*self.capacityUsed), 2)
        text = str.format(" ({0},{1})", last_method + 1, data)
        if last_method == 0:
            beginText = "\\addplot+ [ybar] coordinates {" + text + "};\n"
            allText.append(beginText)
        else:
            lineText = allText[0]
            allText[0] = lineText[0:len(lineText) - 2] + text + lineText[len(lineText) - 2:len(lineText)] + "\n"
        return allText

    def resolveDataTable4(self, resultsDir):
        BW = 0
        BWlist = [10,40,100,400,1000]
        from rmlsa.components import DemandsGenerator
        for modIndex in range(len(DemandsGenerator.modulationList)):
            for i in self.results[modIndex]:


                rowPerModulation: np.ndarray = DemandsGenerator.table_BitRate_vs_Distance[modIndex]
                finalIndex = np.where(rowPerModulation == i.traffic)
                z: int = finalIndex[0][0]
                BW += BWlist[z]

        BW = np.round(BW/float(self.simCount), 2)
        allText = []
        try:
            file = open(resultsDir, "r")
            for line in file:
                allText.append(line)
            file.close()

        except:
            pass

        text = str(BW)
        allText.append(text + "\n")

        try:
            f = open(resultsDir, "w")
            f.writelines(allText)
            f.close()
        except:
            pass


    # def __exportTable2__(self):
    #     columnsCount = 8
    #     relativeTable1Dir = "\Simulaciones\\table2.txt"
    #     resultsDir = self.projectDir + relativeTable1Dir
    #
    #     allText = []
    #
    #     try:
    #         file = open(resultsDir, "r")
    #         for line in file:
    #             allText.append(line[0:len(line) - 1])
    #         file.close()
    #         firstLine = allText[0]
    #         firstLine = firstLine[::-1]
    #         pos2 = firstLine.find(",")
    #         pos1 = firstLine.find("(", pos2)
    #         last_method = int(firstLine[pos2 + 1:pos1][::-1])
    #
    #     except:
    #         last_method = 0
    #
    #
    #
    #     if last_method == 0:
    #         simbolicLine = "symbolic x coords={1}\n"
    #         allText.append(simbolicLine)
    #     else:
    #         simbolicLine = allText[columnsCount]
    #         simbolicLine = simbolicLine[0:len(simbolicLine)-1] + ", " + str(last_method + 1) + "}"
    #         allText[columnsCount] = simbolicLine
    #
    #     try:
    #         f = open(resultsDir, "w")
    #         f.writelines(allText)
    #         f.close()
    #     except:
    #         pass

    # %%%%%%%%%%%%%%%%%%%%%%%%  Para la tabla: NEW_BAR  %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


    def fillTable1(self, allText, lastMethod, columnsCount):
        for col in range(0, columnsCount):
            if col == 1:
                data = np.round(self.fragmentedCount*100/(self.simCount*self.totalFSUs), 1)  # -->> VERIFICAR
            else:
                data = np.round(self.assigned_prom, 0)

            text = str.format(" ({0},{1})", lastMethod+1, data)
            if lastMethod == 0:
                beginText = "\\addplot coordinates {" + text + "};\n"
                allText.append(beginText)
            else:
                lineText = allText[col]
                allText[col] = lineText[0:len(lineText)-2]+text+lineText[len(lineText)-2:len(lineText)]+"\n"
        return allText

    def fillTable2(self, allText, lastMethod, columnsCount):

        capacity = np.round((self.totalFSUs * self.simCount - self.freeCount) / self.simCount, 0)

        for col in range(0, columnsCount):
            data = 0
            if col == 5:
                data = self.fragmentedCount
            else:
                for i in self.results[col]:
                    data += i.traffic*len(i.linksOfPath)
            data = np.round(data / (self.simCount), 0)
            text = str.format(" ({0},{1})", lastMethod + 1, data)
            if lastMethod == 0:
                beginText = "\\addplot+ [ybar] coordinates {" + text + "};\n"
                allText.append(beginText)

            else:
                lineText = allText[col]
                allText[col] = lineText[0:len(lineText) - 2] + text + lineText[len(lineText) - 2:len(lineText)] + "\n"
        return allText


        # data1 = 1
        # for col in range(0, columnsCount):
        #     if col == 1:
        #         data = np.round(self.fragmentedCount*100/(self.simCount*data1), 1)  # -->> VERIFICAR
        #     else:
        #         data1 = np.round((self.totalFSUs*self.simCount - self.freeCount)/self.simCount, 0)
        #         data = data1
        #
        #
        #     text = str.format(" ({0},{1})", lastMethod+1, data)
        #     if lastMethod == 0:
        #         beginText = "\\addplot coordinates {" + text + "};\n"
        #         allText.append(beginText)
        #     else:
        #         lineText = allText[col]
        #         allText[col] = lineText[0:len(lineText)-2]+text+lineText[len(lineText)-2:len(lineText)]+"\n"
        # return allText