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
    connectSig = pyqtSignal()
    disconnectSig = pyqtSignal()
    setParamsSig = pyqtSignal(Params)
    startSig = pyqtSignal()
    stopSig = pyqtSignal()

class SampleSignals(QObject):
    newDataSig = pyqtSignal(tuple) # (time, V, I, P, T)

class ControlSignals(QObject):
    newDataSig = pyqtSignal(tuple) # (time, E, J, P, T)

    connectingSig = pyqtSignal()
    connectedSig = pyqtSignal()

    disconnectingSig = pyqtSignal()
    disconnectedSig = pyqtSignal()

    settingParamsSig = pyqtSignal()
    setParamsDoneSig = pyqtSignal()

    startingSig = pyqtSignal()
    startedSig = pyqtSignal()

    stoppingSig = pyqtSignal()
    stoppedSig = pyqtSignal()
