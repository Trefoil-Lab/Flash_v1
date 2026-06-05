import sys
from PyQt6.QtCore import QSize, Qt, QThreadPool
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
from util import GuiSignals
from control import ControlRunner

DC_SOURCE_ADDR = "USB0::0x3121::0x1004::615E25116::INSTR"

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

        # set up control thread
        self.signals = GuiSignals()
        self.threadpool = QThreadPool()
        self.control_thread = ControlRunner(DC_SOURCE_ADDR, self, None)
        
        # set up control signal listeners
        self.control_thread.signals.newDataSig.connect(self.receiveData)
        self.control_thread.signals.connectingSig.connect(self.connecting)
        self.control_thread.signals.connectedSig.connect(self.connected)
        self.control_thread.signals.disconnectingSig.connect(self.disconnecting)
        self.control_thread.signals.disconnectedSig.connect(self.disconnected)
        self.control_thread.signals.settingParamsSig.connect(self.settingParams)
        self.control_thread.signals.setParamsDoneSig.connect(self.setParamsDone)
        self.control_thread.signals.startingSig.connect(self.starting)
        self.control_thread.signals.startedSig.connect(self.started)
        self.control_thread.signals.stoppingSig.connect(self.stopping)
        self.control_thread.signals.stoppedSig.connect(self.stopped)

        # start control thread
        self.threadpool.start(self.control_thread)

        # connect buttons
        self.applyButton.clicked.connect(self.applyPress)
        self.connectionButton.clicked.connect(self.connectionTogglePress)
        self.startButton.clicked.connect(self.startPress)
        self.stopButton.clicked.connect(self.stopPress)
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

    #########################
    # button press handlers #
    #########################

    def applyPress(self):
        pass

    def connectionTogglePress(self):
        pass

    def startPress(self):
        pass

    def stopPress(self):
        pass

    def loadPresetPress(self):
        pass

    def storePresetPress(self):
        pass

    ###########################
    # control signal handlers #
    ###########################

    def receiveData(self, data : tuple[float]):
        pass

    def connecting(self):
        pass

    def connected(self):
        pass

    def disconnecting(self):
        pass

    def disconnected(self):
        pass

    def settingParams(self):
        pass

    def setParamsDone(self):
        pass

    def starting(self):
        pass

    def started(self):
        pass

    def stopping(self):
        pass

    def stopped(self):
        pass

if __name__ == "__main__":
    main()
