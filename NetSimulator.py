from PyQt5 import QtWidgets


# Entrada al programa
if __name__ == "__main__":
    import sys
    from GUI.NetSimGUI import NetGUI
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = NetGUI()
    ui.setupUi(MainWindow)
    MainWindow.showMaximized()
    sys.exit(app.exec_())
