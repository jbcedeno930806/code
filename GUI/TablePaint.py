from rmlsa.graph import Topology
from GUI.NetSimGUI import NetGUI
from PyQt5 import QtCore, QtGui, QtWidgets
import numpy as np
from rmlsa.tools import pairwise


# Definiendo colores para el pintado de la Tabla
class Color(object):

    DARK_RED = QtGui.QColor(190, 0, 0)
    RED = QtGui.QColor(255, 0, 0)

    ORANGE = QtGui.QColor(255, 85, 0)
    LIGHT_ORNAGE = QtGui.QColor(255, 170, 0)
    SKIN_ORANGE = QtGui.QColor(255, 170, 127)

    DARK_GREEN = QtGui.QColor(0, 85, 0)
    GREEN = QtGui.QColor(0, 175, 0)
    LIGHT_GREEN = QtGui.QColor(0, 255, 0)

    YELLOW = QtGui.QColor(255, 255, 0)
    LIGHT_YELLOW = QtGui.QColor(255, 255, 127)

    PINK = QtGui.QColor(255, 0, 127)
    LIGHT_PINK = QtGui.QColor(255, 85, 127)

    LIGHT_BLUE = QtGui.QColor(85, 0, 255)
    SEA_BLUE = QtGui.QColor(85, 85, 255)
    BLUE = QtGui.QColor(0, 0, 180)
    DARK_BLUE = QtGui.QColor(0, 0, 255)
    SKY_BLUE = QtGui.QColor(170, 170, 255)

    COLORS = [DARK_RED, RED, ORANGE, LIGHT_ORNAGE, SKIN_ORANGE, DARK_GREEN, GREEN, LIGHT_GREEN, YELLOW, LIGHT_YELLOW,
              PINK, LIGHT_PINK, LIGHT_BLUE, SEA_BLUE, BLUE, DARK_BLUE, SKY_BLUE]


def Paint(graph: Topology, ui: NetGUI):

    for user in graph.getUsers():
        userState = user.getState()
        source = user.source
        destination = user.destination
        isAssigned = userState["isAssigned"]
        demand = userState["demand"]
        sIndex = userState["sIndex"]
        route = userState["selectedRoute"]

        # For later use:
        core = userState["core"]

        brush = QtGui.QBrush()
        brush.setStyle(QtCore.Qt.SolidPattern)

        color = Color.COLORS[np.random.randint(0, len(Color.COLORS))]
        brush.setColor(color)


        if isAssigned:
            for (u, v) in pairwise(route):
                data = str(u) + "-" + str(v)
                for ht in range(0, len(ui.header_title_List)):
                    if ui.header_title_List[ht] == data:
                        for index in range(sIndex, sIndex+demand):
                            item = QtWidgets.QTableWidgetItem()
                            showItemText = str.format("{0}-{1}", source, destination)
                            item.setText(showItemText)
                            item.setTextAlignment(QtCore.Qt.AlignCenter)
                            item.setBackground(brush)
                            ui.assignationResultTableWidget.setItem(index, ht, item)
