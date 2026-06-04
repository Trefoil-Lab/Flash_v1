from PyQt6.QtCore import QObject, QRunnable, pyqtSignal, pyqtSlot
import time
import sched
import random
import math
from threading import Thread, Lock, Event

from interface import DCSupply
from util import Params, ControlSignals, SampleSignals, GuiSignals
from gui import MainWindow


class ControlRunner(QRunnable):
    def __init__(self, addr : str, gui : MainWindow, params : Params, data : list[tuple[float]], data_lock : Lock):
        super().__init__(self)
        self.signals = ControlSignals()

        self.addr = addr
        self.params = params

        self.supply_lock = Lock()
        self.supply = DCSupply(self.addr)

        # set up sampling thread
        self.sample_stop_event = Event()
        self.sample_signal = SampleSignals()
        self.sample_thread = SampleRunner(self.supply, self.supply_lock, self.sample_signal, 0.1, self.sample_stop_event)
        # TODO get rate from GUI for sampling

        # set up listeners for events from GUI
        # TODO
        
        # set up listener for newData event from sample collector
        # TODO

    @pyqtSlot
    def run(self):
        print('Control thread starting.')
        self.exec() # run event loop

    def connect(self):
        self.signals.connecting.emit()
        with self.supply_lock:
            self.supply.connect()
        self.signals.connected.emit()

    def disconnect(self):
        self.signals.disconnecting.emit()
        with self.supply_lock:
            self.supply.disconnect()
        self.signals.disconnected.emit()

    def start(self):
        self.signals.starting.emit()
        with self.supply_lock:
            self.supply.enable()
        # TODO start sample thread
        self.signals.started.emit()

    def stop(self):
        self.signals.stopping.emit()
        self.sample_stop_event.set() # tell sampling to stop
        with self.supply_lock:
            self.supply.disable()
        self.sample_thread.join() # wait for sample thread to stop
        self.signals.stopped.emit()
    
    def receiveData(self, inc_data : tuple[float]):
        area = 0.25 * math.pi * self.params.diameter * self.params.diameter
        # (time, V, I, P, T) -> (time, E, J, P, T)
        # TODO check scaling (because of cm)
        out_data = inc_data
        out_data[1] = inc_data[1] / self.params.height # e-field from voltage
        out_data[2] = inc_data[2] / area # current density from current
        out_data[3] = inc_data[3] / area # power density from power

        # TODO use queue to communicate between sampler and control thread to ensure reliability
        # TODO prepare for saving data
        
        self.signals.newData.emit(out_data)

class SampleRunner(Thread):
    def __init__(self, supply : DCSupply, supply_lock : Lock, sample_signal : SampleSignals, interval : float, stop_event : Event):
        super().__init__(self)

        self.interval = interval
        self.supply = supply
        self.supply_lock = supply_lock
        self.sample_signal = sample_signal
        self.stop_event = stop_event

    def run(self):
        sc = sched.scheduler(time.perf_counter, time.sleep)

        start_time = time.perf_counter()
        data = (0,0,0,0) # (time, V, I, P, T)

        def sample(sc : sched.scheduler, target_time : float):
            with self.supply_lock:
                data = (0, self.supply.measV(), self.supply.measI(), self.supply.measP(), random.random())
            data[0] = time.perf_counter - start_time
            self.sample_signal.newData.emit(data)

            # check event to see if we should continue
            if not self.stop_event.is_set():
                # schedule next sample
                next_time = target_time + self.interval
                sc.enterabs(next_time, 1, sample, argument=(sc, next_time))

        # schedule first sample
        next_time = start_time + self.interval
        sc.enterabs(next_time, 1, sample, argument=(sc, next_time))
