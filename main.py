import sys
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
)
from PyQt6 import QtGui
import pyqtgraph as pg
import numpy as np
import interface
from MainWindow import Ui_MainWindow

WINDOW_TITLE = 'flash-v1'

E_FIELD_COLOR_STR = '#00FFFF'
CURRENT_DENSITY_COLOR_STR = '#FF0000'
POWER_DENSITY_COLOR_STR = '#FFFF00'
TEMPERATURE_COLOR_STR = '#00FF00'


def main():
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec()

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, *args, obj=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)

        ###############################
        # custom initialization below #
        ###############################

        self.setWindowTitle(WINDOW_TITLE)

        # connect buttons
        self.applyButton.clicked.connect(self.applyPress)
        self.connectionButton.clicked.connect(self.connectionTogglePress)
        self.startButton.clicked.connect(self.startPress)
        self.endButton.clicked.connect(self.endPress)
        self.loadPresetButton.clicked.connect(self.loadPresetPress)
        self.storePresetButton.clicked.connect(self.storePresetPress)

        # set parameter label colors
        self.eFieldLabel.setStyleSheet(f'QLabel {{color: {E_FIELD_COLOR_STR}}}')
        self.currentDensityLabel.setStyleSheet(f'QLabel {{color: {CURRENT_DENSITY_COLOR_STR}}}')

        # graph 1
        self.graph1 = pg.PlotWidget()
        self.graph1.setSizePolicy(self.graphPlaceholder1.sizePolicy())
        self.graph1.setMinimumSize(self.graphPlaceholder1.minimumSize())
        self.graph1.setObjectName('graph1')
        self.GraphBox.replaceWidget(self.graphPlaceholder1, self.graph1)
        self.graphPlaceholder1.hide()

        # graph 2
        self.graph2 = pg.PlotWidget()
        self.graph2.setSizePolicy(self.graphPlaceholder2.sizePolicy())
        self.graph2.setMinimumSize(self.graphPlaceholder2.minimumSize())
        self.graph2.setObjectName('graph2')
        self.GraphBox.replaceWidget(self.graphPlaceholder2, self.graph2)
        self.graphPlaceholder2.hide()

        # plot test data

        time = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        J = np.random.rand(len(time))
        P = np.random.rand(len(time))
        T = np.random.rand(len(time))
        E = np.random.rand(len(time))

        self.graph1.plot(time, E, pen=pg.mkPen(color=E_FIELD_COLOR_STR))
        self.graph1.plot(time, J, pen=pg.mkPen(color=CURRENT_DENSITY_COLOR_STR))
        self.graph2.plot(time, P, pen=pg.mkPen(color=POWER_DENSITY_COLOR_STR))
        self.graph2.plot(time, T, pen=pg.mkPen(color=TEMPERATURE_COLOR_STR))

        self.graph1.setLabel('left', 'E-field', color=E_FIELD_COLOR_STR)
        self.graph1.setLabel('right', 'Current Density', color=CURRENT_DENSITY_COLOR_STR)

        self.graph2.setLabel('left', 'Power Density', color=POWER_DENSITY_COLOR_STR)
        self.graph2.setLabel('right', 'Temperature', color=TEMPERATURE_COLOR_STR)

        self.graph1.setBackground(background=None)
        self.graph2.setBackground(background=None)

    def applyPress(self):
        pass

    def connectionTogglePress(self):
        pass

    def startPress(self):
        pass

    def endPress(self):
        pass

    def loadPresetPress(self):
        pass

    def storePresetPress(self):
        pass

if __name__ == "__main__":
    main()
