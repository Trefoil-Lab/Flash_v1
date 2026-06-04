from dataclasses import dataclass
from PyQt6.QtCore import QObject, QRunnable, pyqtSignal, pyqtSlot

@dataclass
class Params:
    e_field: float
    curr_density: float
    temperature: float | None
    diameter: float
    height: float
    sample_interval: float

class GuiSignals(QObject):
    connect = pyqtSignal()
    disconnect = pyqtSignal()
    setParams = pyqtSignal(Params)
    start = pyqtSignal()
    stop = pyqtSignal()

class SampleSignals(QObject):
    newData = pyqtSignal(tuple) # (time, V, I, P, T)

class ControlSignals(QObject):
    newData = pyqtSignal(tuple) # (time, E, J, P, T)

    connecting = pyqtSignal()
    connected = pyqtSignal()

    disconnecting = pyqtSignal()
    disconnected = pyqtSignal()

    settingParams = pyqtSignal()
    setParamsDone = pyqtSignal()

    starting = pyqtSignal()
    started = pyqtSignal()

    stopping = pyqtSignal()
    stopped = pyqtSignal()
