from PyQt6.QtCore import QObject, QRunnable, pyqtSignal, pyqtSlot
import time
import sched

from interface import DCSupply
from util import Params, ControlSignals
from gui import MainWindow


class ControlRunner(QRunnable):
    def __init__(self, addr : str, gui : MainWindow, params : Params):
        super().__init__(self)
        self.signals = ControlSignals()

        self.addr = addr
        self.params = params
        self.supply = DCSupply(self.addr)

    @pyqtSlot
    def run(self):
        print('Control thread starting.')
        self.exec() # run event loop

    def connect(self):
        self.signals.connecting.emit()
        self.supply.connect()
        self.signals.connected.emit()

    def disconnect(self):
        self.signals.disconnecting.emit()
        self.supply.disconnect()
        self.signals.disconnected.emit()

    def start(self):
        self.signals.starting.emit()
        self.supply.enable()
        # TODO start sample thread
        self.signals.started.emit()

    def stop(self):
        self.signals.stopping.emit()
        self.supply.disable()
        # TODO stop sample thread
        self.signals.stopped.emit()

    

class SampleRunner():
    def __init__(self, supply : DCSupply):
        super().__init__(self)

        self.supply = supply