from PyQt5 import QtCore, QtGui, QtWidgets
from rmlsa.graph import Topology, loadGraph
from rmlsa.spectrum_assignment import AlgNames, SlidingFit, FirstFit, ParcelFit
from rmlsa.tools import Order, Priority, RouteAlgorithms, RouteMetric, LinkUsage


class NetGUI(QtWidgets.QMainWindow):

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)

        # Datos para simular n veces:
        self.mSimulationsCount = 1
        self.currentSimulationNumber = 0
        self.mPaintAvailable = True
        self.resultsToExport = []
        self.assignedCount = 0
        self.mCBF = 0
        self.freePorcentage = 0
        self.numberOfFreeFSUs = self.numberOfFragmentedFSUs = 0
        self.usedFSUs = 0
        self.maxPathsCache = 1
        self.header_title_List = []

        self.graph = None

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setWindowModality(QtCore.Qt.NonModal)
        MainWindow.resize(1799, 1001)

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # ***********************************************************************************************
        #                                   ROUTES GROUPBOX
        # ***********************************************************************************************
        self.routesGroupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.routesGroupBox.setGeometry(QtCore.QRect(60, 30, 411, 220))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.routesGroupBox.setFont(font)
        self.routesGroupBox.setObjectName("routesGroupBox")

        self.formLayoutWidget = QtWidgets.QWidget(self.routesGroupBox)
        self.formLayoutWidget.setGeometry(QtCore.QRect(9, 9, 401, 201))
        self.formLayoutWidget.setObjectName("formLayoutWidget")

        self.routesFormLayout = QtWidgets.QFormLayout(self.formLayoutWidget)
        self.routesFormLayout.setContentsMargins(30, 20, 10, 10)
        self.routesFormLayout.setHorizontalSpacing(50)
        self.routesFormLayout.setObjectName("routesFormLayout")

        self.methodlabel = QtWidgets.QLabel(self.formLayoutWidget)
        self.methodlabel.setSizeIncrement(QtCore.QSize(0, 0))
        self.methodlabel.setBaseSize(QtCore.QSize(0, 0))
        self.methodlabel.setObjectName("methodlabel")
        self.routesFormLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.methodlabel)

        self.methodComboBox = QtWidgets.QComboBox(self.formLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.methodComboBox.setSizePolicy(sizePolicy)
        self.methodComboBox.setMinimumSize(QtCore.QSize(150, 0))
        self.methodComboBox.setObjectName("methodComboBox")
        for key in RouteAlgorithms:
            self.methodComboBox.addItem(key)
        self.routesFormLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.methodComboBox)
        self.methodComboBox.currentTextChanged['QString'].connect(self.on_MethodComboBoxValueChanged)

        self.usageLabel = QtWidgets.QLabel(self.formLayoutWidget)
        self.usageLabel.setObjectName("usageLabel")
        self.routesFormLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.usageLabel)

        self.usageFormLayout = QtWidgets.QFormLayout()
        self.usageFormLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.usageFormLayout.setHorizontalSpacing(20)
        self.usageFormLayout.setObjectName("usageFormLayout")

        self.usersUsageRadioButton = QtWidgets.QRadioButton(self.formLayoutWidget)
        self.usersUsageRadioButton.setChecked(True)
        self.usersUsageRadioButton.setDisabled(True)
        self.usersUsageRadioButton.setObjectName("usersUsageRadioButton")
        self.usageFormLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.usersUsageRadioButton)

        self.demandUsageRadioButtom = QtWidgets.QRadioButton(self.formLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHeightForWidth(self.demandUsageRadioButtom.sizePolicy().hasHeightForWidth())
        self.demandUsageRadioButtom.setSizePolicy(sizePolicy)
        self.demandUsageRadioButtom.setChecked(False)
        self.demandUsageRadioButtom.setDisabled(True)
        self.demandUsageRadioButtom.setObjectName("demandUsageRadioButtom")
        self.usageFormLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.demandUsageRadioButtom)
        self.routesFormLayout.setLayout(1, QtWidgets.QFormLayout.FieldRole, self.usageFormLayout)

        self.metricLabel = QtWidgets.QLabel(self.formLayoutWidget)
        self.metricLabel.setObjectName("metricLabel")
        self.routesFormLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.metricLabel)

        self.metricComboBox = QtWidgets.QComboBox(self.formLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.metricComboBox.setSizePolicy(sizePolicy)
        self.metricComboBox.setMinimumSize(QtCore.QSize(150, 0))
        self.metricComboBox.setObjectName("metricComboBox")
        for key in RouteMetric:
            self.metricComboBox.addItem(key)
        self.routesFormLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.metricComboBox)

        self.kspLabel = QtWidgets.QLabel(self.formLayoutWidget)
        self.kspLabel.setObjectName("kspLabel")
        self.routesFormLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.kspLabel)

        self.kspSpinBox = QtWidgets.QSpinBox(self.formLayoutWidget)
        self.kspSpinBox.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.kspSpinBox.setSizePolicy(sizePolicy)
        self.kspSpinBox.setMinimumSize(QtCore.QSize(80, 0))
        self.kspSpinBox.setMinimum(1)
        self.kspSpinBox.setMaximum(1)
        self.kspSpinBox.setObjectName("kspSpinBox")
        self.routesFormLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.kspSpinBox)

        self.scaleLabel = QtWidgets.QLabel(self.formLayoutWidget)
        self.scaleLabel.setObjectName("scaleLabel")
        self.routesFormLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.scaleLabel)

        self.scaleSpinBox = QtWidgets.QDoubleSpinBox(self.formLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.scaleSpinBox.setSizePolicy(sizePolicy)
        self.scaleSpinBox.setMinimumSize(QtCore.QSize(80, 0))
        self.scaleSpinBox.setMinimum(0.1)
        self.scaleSpinBox.setMaximum(2.0)
        self.scaleSpinBox.setSingleStep(0.1)
        self.scaleSpinBox.setStepType(QtWidgets.QAbstractSpinBox.DefaultStepType)
        self.scaleSpinBox.setProperty("value", 1.0)
        self.scaleSpinBox.setObjectName("scaleSpinBox")
        self.routesFormLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.scaleSpinBox)

        self.spectAssignmentGroupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.spectAssignmentGroupBox.setGeometry(QtCore.QRect(480, 30, 411, 220))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.spectAssignmentGroupBox.setFont(font)
        self.spectAssignmentGroupBox.setObjectName("spectAssignmentGroupBox")

        self.formLayoutWidget_2 = QtWidgets.QWidget(self.spectAssignmentGroupBox)
        self.formLayoutWidget_2.setGeometry(QtCore.QRect(10, 10, 401, 201))
        self.formLayoutWidget_2.setObjectName("formLayoutWidget_2")

        self.spectAssignmentFormLayout = QtWidgets.QFormLayout(self.formLayoutWidget_2)
        self.spectAssignmentFormLayout.setContentsMargins(30, 20, 10, 10)
        self.spectAssignmentFormLayout.setHorizontalSpacing(50)
        self.spectAssignmentFormLayout.setObjectName("spectAssignmentFormLayout")

        self.algorithmLabel = QtWidgets.QLabel(self.formLayoutWidget_2)
        self.algorithmLabel.setObjectName("algorithmLabel")
        self.spectAssignmentFormLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.algorithmLabel)

        self.algorithmComboBox = QtWidgets.QComboBox(self.formLayoutWidget_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.algorithmComboBox.setSizePolicy(sizePolicy)
        self.algorithmComboBox.setMinimumSize(QtCore.QSize(150, 0))
        self.algorithmComboBox.setObjectName("algorithmComboBox")
        for key in AlgNames:
            self.algorithmComboBox.addItem(key)
        self.spectAssignmentFormLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.algorithmComboBox)

        self.priorityLabel = QtWidgets.QLabel(self.formLayoutWidget_2)
        self.priorityLabel.setObjectName("priorityLabel")
        self.spectAssignmentFormLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.priorityLabel)

        self.priorityComboBox = QtWidgets.QComboBox(self.formLayoutWidget_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.priorityComboBox.setSizePolicy(sizePolicy)
        self.priorityComboBox.setMinimumSize(QtCore.QSize(150, 0))
        self.priorityComboBox.setObjectName("priorityComboBox")
        for key in Priority:
            self.priorityComboBox.addItem(key)
        self.spectAssignmentFormLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.priorityComboBox)

        self.demandsLabel = QtWidgets.QLabel(self.formLayoutWidget_2)
        self.demandsLabel.setObjectName("demandsLabel")
        self.spectAssignmentFormLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.demandsLabel)

        self.demandsComboBox = QtWidgets.QComboBox(self.formLayoutWidget_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.demandsComboBox.setSizePolicy(sizePolicy)
        self.demandsComboBox.setMinimumSize(QtCore.QSize(150, 0))
        self.demandsComboBox.setObjectName("demandsComboBox")
        for key in Order:
            self.demandsComboBox.addItem(key)
        self.spectAssignmentFormLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.demandsComboBox)

        self.stepsLabel = QtWidgets.QLabel(self.formLayoutWidget_2)
        self.stepsLabel.setObjectName("stepsLabel")
        self.spectAssignmentFormLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.stepsLabel)

        self.stepsComboBox = QtWidgets.QComboBox(self.formLayoutWidget_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.stepsComboBox.setSizePolicy(sizePolicy)
        self.stepsComboBox.setMinimumSize(QtCore.QSize(150, 0))
        self.stepsComboBox.setObjectName("stepsComboBox")
        for key in Order:
            self.stepsComboBox.addItem(key)
        self.spectAssignmentFormLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.stepsComboBox)

        self.simsGroupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.simsGroupBox.setGeometry(QtCore.QRect(900, 30, 411, 220))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.simsGroupBox.setFont(font)
        self.simsGroupBox.setObjectName("simsGroupBox")

        self.formLayoutWidget_3 = QtWidgets.QWidget(self.simsGroupBox)
        self.formLayoutWidget_3.setGeometry(QtCore.QRect(9, 10, 401, 201))
        self.formLayoutWidget_3.setObjectName("formLayoutWidget_3")

        self.simsFormLayout = QtWidgets.QFormLayout(self.formLayoutWidget_3)
        self.simsFormLayout.setContentsMargins(30, 20, 10, 10)
        self.simsFormLayout.setHorizontalSpacing(50)
        self.simsFormLayout.setObjectName("simsFormLayout")

        self.simulationsLabel = QtWidgets.QLabel(self.formLayoutWidget_3)
        self.simulationsLabel.setObjectName("simulationsLabel")
        self.simsFormLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.simulationsLabel)

        self.simulationSpinBox = QtWidgets.QSpinBox(self.formLayoutWidget_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.simulationSpinBox.setSizePolicy(sizePolicy)
        self.simulationSpinBox.setMinimumSize(QtCore.QSize(80, 0))
        self.simulationSpinBox.setMinimum(1)
        self.simulationSpinBox.setMaximum(1000)
        self.simulationSpinBox.setObjectName("simulationSpinBox")
        self.simsFormLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.simulationSpinBox)

        self.seedLabel = QtWidgets.QLabel(self.formLayoutWidget_3)
        self.seedLabel.setObjectName("seedLabel")
        self.simsFormLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.seedLabel)

        self.seedSpinBox = QtWidgets.QSpinBox(self.formLayoutWidget_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.seedSpinBox.setSizePolicy(sizePolicy)
        self.seedSpinBox.setMinimumSize(QtCore.QSize(80, 0))
        self.seedSpinBox.setObjectName("seedSpinBox")
        self.simsFormLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.seedSpinBox)

        self.coresLabel = QtWidgets.QLabel(self.formLayoutWidget_3)
        self.coresLabel.setObjectName("coresLabel")
        self.simsFormLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.coresLabel)

        self.coresSpinBox = QtWidgets.QSpinBox(self.formLayoutWidget_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.coresSpinBox.setSizePolicy(sizePolicy)
        self.coresSpinBox.setMinimumSize(QtCore.QSize(80, 0))
        self.coresSpinBox.setMinimum(1)
        self.coresSpinBox.setMaximum(10)
        self.coresSpinBox.setObjectName("coresSpinBox")
        self.simsFormLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.coresSpinBox)

        self.fsusLabel = QtWidgets.QLabel(self.formLayoutWidget_3)
        self.fsusLabel.setObjectName("fsusLabel")
        self.simsFormLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.fsusLabel)

        self.fsusSpinBox = QtWidgets.QSpinBox(self.formLayoutWidget_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.fsusSpinBox.setSizePolicy(sizePolicy)
        self.fsusSpinBox.setMinimumSize(QtCore.QSize(80, 0))
        self.fsusSpinBox.setMinimum(320)
        self.fsusSpinBox.setMaximum(5000)
        self.fsusSpinBox.setObjectName("fsusSpinBox")
        self.simsFormLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.fsusSpinBox)

        self.resultsGroupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.resultsGroupBox.setGeometry(QtCore.QRect(1320, 30, 411, 221))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.resultsGroupBox.setFont(font)
        self.resultsGroupBox.setObjectName("resultsGroupBox")

        self.formLayoutWidget_4 = QtWidgets.QWidget(self.resultsGroupBox)
        self.formLayoutWidget_4.setGeometry(QtCore.QRect(9, 10, 401, 201))
        self.formLayoutWidget_4.setObjectName("formLayoutWidget_4")

        self.resultsFormLayout = QtWidgets.QFormLayout(self.formLayoutWidget_4)
        self.resultsFormLayout.setContentsMargins(30, 20, 10, 10)
        self.resultsFormLayout.setHorizontalSpacing(50)
        self.resultsFormLayout.setObjectName("resultsFormLayout")

        self.assignedLabel = QtWidgets.QLabel(self.formLayoutWidget_4)
        self.assignedLabel.setObjectName("assignedLabel")
        self.resultsFormLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.assignedLabel)

        self.assignedProgressBar = QtWidgets.QProgressBar(self.formLayoutWidget_4)
        self.assignedProgressBar.setProperty("value", 0)
        self.assignedProgressBar.setObjectName("assignedProgressBar")
        self.assignedProgressBar.setAlignment(QtCore.Qt.AlignCenter)
        self.resultsFormLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.assignedProgressBar)

        self.freeLabel = QtWidgets.QLabel(self.formLayoutWidget_4)
        self.freeLabel.setObjectName("freeLabel")
        self.resultsFormLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.freeLabel)

        self.freeProgressBar = QtWidgets.QProgressBar(self.formLayoutWidget_4)
        self.freeProgressBar.setProperty("value", 0)
        self.freeProgressBar.setObjectName("freeProgressBar")
        self.freeProgressBar.setAlignment(QtCore.Qt.AlignCenter)
        self.resultsFormLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.freeProgressBar)

        self.fragementedLabel = QtWidgets.QLabel(self.formLayoutWidget_4)
        self.fragementedLabel.setObjectName("fragementedLabel")
        self.resultsFormLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.fragementedLabel)

        self.fragmentedProgressBar = QtWidgets.QProgressBar(self.formLayoutWidget_4)
        self.fragmentedProgressBar.setProperty("value", 0)
        self.fragmentedProgressBar.setObjectName("fragmentedProgressBar")
        self.fragmentedProgressBar.setAlignment(QtCore.Qt.AlignCenter)
        self.resultsFormLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.fragmentedProgressBar)

        self.relCapacityLabel = QtWidgets.QLabel(self.formLayoutWidget_4)
        self.relCapacityLabel.setObjectName("relCapacityLabel")
        self.resultsFormLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.relCapacityLabel)

        self.relCapacityResultLabel = QtWidgets.QLabel(self.formLayoutWidget_4)
        self.relCapacityResultLabel.setObjectName("relCapacityResultLabel")
        self.resultsFormLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.relCapacityResultLabel)

        self.efficiencyLabel = QtWidgets.QLabel(self.formLayoutWidget_4)
        self.efficiencyLabel.setObjectName("efficiencyLabel")
        self.resultsFormLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.efficiencyLabel)

        self.efficiencyResultlabel = QtWidgets.QLabel(self.formLayoutWidget_4)
        self.efficiencyResultlabel.setObjectName("efficiencyResultlabel")
        self.resultsFormLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.efficiencyResultlabel)

        self.separatorLine = QtWidgets.QFrame(self.centralwidget)
        self.separatorLine.setGeometry(QtCore.QRect(60, 280, 1671, 16))
        self.separatorLine.setFrameShape(QtWidgets.QFrame.HLine)
        self.separatorLine.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.separatorLine.setObjectName("separatorLine")

        self.runButtom = QtWidgets.QPushButton(self.centralwidget)
        self.runButtom.setGeometry(QtCore.QRect(640, 273, 93, 28))
        self.runButtom.clicked.connect(self.on_startButtomClick)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.runButtom.setFont(font)
        self.runButtom.setObjectName("runButtom")

        self.assignationResultTableWidget = QtWidgets.QTableWidget(self.centralwidget)
        self.assignationResultTableWidget.setGeometry(QtCore.QRect(60, 340, 1251, 581))
        self.assignationResultTableWidget.setRowCount(320)
        self.assignationResultTableWidget.setColumnCount(42)
        self.assignationResultTableWidget.setObjectName("assignationResultTableWidget")
        self.assignationResultTableWidget.horizontalHeader().setDefaultSectionSize(55)

        MainWindow.setCentralWidget(self.centralwidget)

        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1799, 26))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        MainWindow.setMenuBar(self.menubar)

        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.actionLoad = QtWidgets.QAction(MainWindow)
        self.actionLoad.triggered['bool'].connect(self.loadTopology)
        self.actionLoad.setObjectName("actionLoad")
        self.actionSave = QtWidgets.QAction(MainWindow)
        self.actionSave.setObjectName("actionSave")
        self.menuFile.addAction(self.actionLoad)
        self.menuFile.addAction(self.actionSave)
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "RMLSA"))
        self.routesGroupBox.setTitle(_translate("MainWindow", "Routes:"))
        self.methodlabel.setText(_translate("MainWindow", "Method:"))
        self.usageLabel.setText(_translate("MainWindow", "Usage:"))
        self.usersUsageRadioButton.setText(_translate("MainWindow", "Users"))
        self.demandUsageRadioButtom.setText(_translate("MainWindow", "Demand"))
        self.metricLabel.setText(_translate("MainWindow", "Metric:"))
        self.kspLabel.setText(_translate("MainWindow", "KSP:"))
        self.scaleLabel.setText(_translate("MainWindow", "Scale:"))
        self.spectAssignmentGroupBox.setTitle(_translate("MainWindow", "Spectrum Assigment:"))
        self.algorithmLabel.setText(_translate("MainWindow", "Algorithm:"))
        self.priorityLabel.setText(_translate("MainWindow", "Priority:"))
        self.demandsLabel.setText(_translate("MainWindow", "Demands Order:"))
        self.stepsLabel.setText(_translate("MainWindow", "Steps Order:"))
        self.simsGroupBox.setTitle(_translate("MainWindow", "Simulation Params:"))
        self.simulationsLabel.setText(_translate("MainWindow", "Simulations:"))
        self.seedLabel.setText(_translate("MainWindow", "Seed:"))
        self.coresLabel.setText(_translate("MainWindow", "Cores:"))
        self.fsusLabel.setText(_translate("MainWindow", "FSUs:"))
        self.resultsGroupBox.setTitle(_translate("MainWindow", "Results:"))
        self.assignedLabel.setText(_translate("MainWindow", "Assigned Users:"))
        self.freeLabel.setText(_translate("MainWindow", "Free FSUs:"))
        self.fragementedLabel.setText(_translate("MainWindow", "Fragmented FSUs:"))
        self.relCapacityLabel.setText(_translate("MainWindow", "Rel. Capacity:"))
        self.relCapacityResultLabel.setText(_translate("MainWindow", "0"))
        self.efficiencyLabel.setText(_translate("MainWindow", "Efficiency:"))
        self.efficiencyResultlabel.setText(_translate("MainWindow", "0"))
        self.runButtom.setText(_translate("MainWindow", "Run"))
        self.menuFile.setTitle(_translate("MainWindow", "Topology"))
        self.actionLoad.setText(_translate("MainWindow", "Load"))
        self.actionSave.setText(_translate("MainWindow", "Save"))

    def updateTableHeaders(self, links: list = None, fsus=None):
        if fsus is not None:
            self.assignationResultTableWidget.setRowCount(self.fsusSpinBox.value())

        if links is not None:
            self.assignationResultTableWidget.setColumnCount(len(links))
            self.header_title_List = \
                ["{0}-{1}".format(link[0], link[1]) for link in links]

            for index in range(0, len(links)):
                item = QtWidgets.QTableWidgetItem()
                item.setText(self.header_title_List[index])
                self.assignationResultTableWidget.setHorizontalHeaderItem(index, item)

            # for ht in range(0, len(self.header_title_List)):
            #     item = self.assignationResultTableWidget.horizontalHeaderItem(ht)
            #     item.setText(self.header_title_List[ht])

    def loadTopology(self):
        fileAddress = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', filter="Image files (*.txt *.top)")
        if fileAddress[0] is not "":
            address = fileAddress[0]
            self.graph = loadGraph(address)
            self.updateTableHeaders(self.graph.edges(), self.fsusSpinBox.value())
            self.kspSpinBox.setMaximum(self.graph.getNodesCount()-1)

    # ----------- Sección de manejadores de eventos: ------------- #
    def on_MethodComboBoxValueChanged(self):
        if self.methodComboBox.currentText() == "Dijkstra":
            self.usersUsageRadioButton.setDisabled(True)
            self.demandUsageRadioButtom.setDisabled(True)
        else:
            self.usersUsageRadioButton.setDisabled(False)
            self.demandUsageRadioButtom.setDisabled(False)

    def on_fsusSpinBoxChanged(self, value):
        self.assignationResultTableWidget.setRowCount(value)

    def onkspSpinBoxChange(self, e):
        if self.kspSpinBox.isEnabled():
            self.maxPathsCache = e

    def on_startButtomClick(self):
        if self.graph is None:
            msg = QtWidgets.QMessageBox()
            msg.setWindowTitle("Error")
            msg.setIcon(QtWidgets.QMessageBox.Critical)
            msg.setText("You must insert a graph")
            msg.exec_()
        else:
            from rmlsa.metrics import SolutionMetrics, toTex, toEPS
            from rmlsa.metrics import SolutionManager as slm
            from GUI.TablePaint import Paint  # Aquí evita el circular import
            import os

            # method = RouteAlgorithms[self.methodComboBox.currentText()]
            # usageMetric = list(LinkUsage.values())[int(self.demandUsageRadioButtom.isChecked())]
            # routeMetric = RouteMetric[self.metricComboBox.currentText()]
            # scale = self.scaleSpinBox.value()
            # cores = self.coresSpinBox.value()
            # alPaths = self.kspSpinBox.value()
            # demandsOrder = self.demandsComboBox.currentText()
            # priority = self.priorityComboBox.currentText()
            # self.mSimulationsCount = self.simulationSpinBox.value()
            # maxFSUs = self.fsusSpinBox.value()
            # stepsOrder = self.stepsComboBox.currentText()
            # algorithm = self.algorithmComboBox.currentText()
            # seed = self.seedSpinBox.value()

            # -------------- ESTO ES PARA Cada TOPOLOGIA---------------------- #
            # baseAddrs = './Topologias/'
            # for fileTXT in os.listdir(baseAddrs):
            #     # if fileTXT == "NSFNet.txt":
            #     #     continue
            #     print("\n")
            #     print(fileTXT)
            #     address = baseAddrs + fileTXT
            #     self.graph = loadGraph(address)
            #     self.updateTableHeaders(self.graph.edges(), self.fsusSpinBox.value())
            #     self.kspSpinBox.setMaximum(self.graph.getNodesCount() - 1)

            # -------------- ESTO ES PARA 100 SIMULACIONES en la lopologia seleccionada---------------------- #
            self.mSimulationsCount = 1
            alPaths = self.kspSpinBox.value()
            cores = 1
            priority = self.priorityComboBox.currentText()
            method = RouteAlgorithms[self.methodComboBox.currentText()]
            usageMetric = list(LinkUsage.values())[int(self.demandUsageRadioButtom.isChecked())]
            routeMetric = RouteMetric[self.metricComboBox.currentText()]
            scale = self.scaleSpinBox.value()

            maxFSUsList = [320, 10000]
            for scenario in range(len(maxFSUsList)):
                if scenario == 0:
                    print("Scenario1")

                else:
                    print("Scenario2")
                    continue

                metricsList = []
                # for strategy in [0, 1, 2, 3, 4, 5]:
                for strategy in [0]:
                    trafficOrderList = ["DESCENDING", "AS_IS", "DESCENDING", "AS_IS", "DESCENDING", "AS_IS"]

                    methodList = ["FIRST_FIT", "FIRST_FIT",
                                  "SLIDING_FIT", "SLIDING_FIT",
                                  "PARCEL_FIT", "PARCEL_FIT"
                                  ]

                    demandsOrder = trafficOrderList[strategy]
                    stepsOrder = trafficOrderList[-(strategy+1)]
                    algorithm = methodList[strategy]
                    maxFSUs = maxFSUsList[scenario]
                    seed = self.simulationSpinBox.value()


                    graph: Topology = self.graph.build(method, usageMetric, routeMetric,
                                                       alPaths, scale, seed, cores, maxFSUs)

                    if algorithm == AlgNames["FIRST_FIT"]:
                        alg = FirstFit(graph, [demandsOrder, stepsOrder], priority)
                    elif algorithm == AlgNames["PARCEL_FIT"]:
                        alg = ParcelFit(graph, [demandsOrder, stepsOrder], priority)
                    else: # algorithm == AlgNames["SLIDING_FIT"]:
                        alg = SlidingFit(graph, [demandsOrder, stepsOrder], priority)

                    solutionMetrics = SolutionMetrics(alg.abbr)

                    print("\n")
                    print("**********************************************************")
                    print("\t\t\t\t" + alg.abbr)
                    print("**********************************************************")
                    for simIndex in range(0, self.mSimulationsCount):
                        print(simIndex, end=",")
                        self.assignationResultTableWidget.clearContents()
                        self.updateTableHeaders(graph.edges(), maxFSUs)
                        solutionMetrics += alg.resolve()
                        if simIndex != self.mSimulationsCount-1:
                            graph.init(seed + simIndex)
                            alg.setTopology(graph)

                    Paint(alg.graph, self)
                    solutionMetrics /= self.mSimulationsCount
                    metricsList.append(solutionMetrics)

                    outputDir = "./Sim(Test)/"+graph.name+"/"
                    # if maxFSUsList[0] == 320:

                    if maxFSUs == 320:
                        outputDir = outputDir + "Scenario1/"
                    else:
                        outputDir = outputDir + "Scenario2/"

                    fragmented = solutionMetrics.fragmented()
                    assigned = solutionMetrics.assigned()
                    free = solutionMetrics.free()
                    efficiency = solutionMetrics.efficiency()
                    relCapacity = solutionMetrics.relative()

                    userCount = len(graph.getUsers())
                    totalFSUs = graph.getCoresCount() * graph.getLinksCount() * graph.getFSUsCount()

                    self.fragmentedProgressBar.setFormat('%.02f' % fragmented)
                    self.fragmentedProgressBar.setProperty("value", 100 * fragmented / totalFSUs)
                    self.freeProgressBar.setFormat('%.02f' % free)
                    self.freeProgressBar.setProperty("value", 100 * free / totalFSUs)
                    self.assignedProgressBar.setFormat('%.02f' % assigned)
                    self.assignedProgressBar.setProperty("value", 100 * assigned / userCount)
                    self.relCapacityResultLabel.setText(str(relCapacity) + " FSUs")
                    self.efficiencyResultlabel.setText(str(efficiency) + " %")

                toTex(outputDir, metricsList, scenario+1)
                # toEPS(outputDir, metricsList, scenario+1)
                slm.toPkl(outputDir, metricsList)
