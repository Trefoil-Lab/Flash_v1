from PyQt6.QtCore import QObject, QRunnable, QEventLoop, pyqtSignal, pyqtSlot
import time
import sched
import random
import math
from threading import Thread, Lock, Event
from dataclasses import fields

from interface import DCSupply
from util import Params, ControlSignals, SampleSignals, GuiSignals, Status
from eurotherm2400 import Eurotherm2400


class ControlRunner(QRunnable):
    def __init__(
        self,
        supply_addr : str,
        eurotherm_port : str,
        eurotherm_addr : int,
        gui_signals : GuiSignals,
        params : Params
    ):
        super().__init__()
        self.signals = ControlSignals()

        self.addr = supply_addr
        self.params = params

        self.status = Status(False, False) # for gui synchronization
        self.status_lock = Lock()

        self.supply = DCSupply(self.addr)
        self.supply_lock = Lock()

        self.eurotherm = Eurotherm2400(eurotherm_port, eurotherm_addr)
        self.eurotherm_lock = Lock()

        # set up sampling thread
        self.sample_stop_event = Event()
        self.sample_signal = SampleSignals()
        self.sample_thread = SampleRunner(self.supply, self.supply_lock, self.sample_signal,
                                          self.params.sample_interval, self.sample_stop_event)

        # set up listeners for events from GUI
        gui_signals.exitSig.connect(self.exit)
        gui_signals.connectSig.connect(self.connect)
        gui_signals.disconnectSig.connect(self.disconnect)
        gui_signals.setParamsSig.connect(self.setParams)
        gui_signals.startSig.connect(self.start)
        gui_signals.stopSig.connect(self.stop)
        
        # set up listener for newData event from sample collector
        self.sample_thread.sample_signal.newDataSig.connect(self.receiveData)

    #@pyqtSlot
    def run(self):
        print('Control thread starting.')
        self.eventloop = QEventLoop()
        self.eventloop.exec() # run event loop

    ######################
    # GUI event handlers #
    ######################

    def exit(self):
        self.eventloop.exit()

    def connect(self):
        self.signals.connectingSig.emit()
        with self.supply_lock:
            self.supply.connect()

            # sync parameters with actual state
            # TODO double check scale factor
            # area = 0.25 * math.pi * self.params.diameter * self.params.diameter
            # self.params.curr_density = self.supply.getI() / area
            # self.params.e_field = self.supply.getV() / self.params.height
        with self.status_lock:
            self.status.connected = True
        self.signals.connectedSig.emit()

    def disconnect(self):
        self.signals.disconnectingSig.emit()
        with self.supply_lock:
            self.supply.disconnect()
        self.status.connected = False
        self.signals.disconnectedSig.emit()

    def setParams(self, new_params : Params):
        self.signals.settingParamsSig.emit()

        # TODO what if we aren't connected?
        if new_params == self.params: # only update if we need to
            self.signals.setParamsDoneSig.emit()
            return
        
        # do we need to update voltage?
        if new_params.e_field != self.params.e_field or new_params.height != self.params.height:
            with self.supply_lock:
                # TODO check scale factor (cm)
                self.supply.setV(new_params.e_field * new_params.height)
        
        # do we need to update current?
        if new_params.curr_density != self.params.curr_density or new_params.diameter != self.params.diameter:
            area = 0.25 * math.pi * new_params.diameter * new_params.diameter
            with self.supply_lock:
                self.supply.setI(new_params.curr_density * area)

        # do we need to update temperature?
        if new_params.temperature != self.params.temperature:
            with self.eurotherm_lock:
                self.eurotherm.target_setpoint = new_params.temperature

        # do we need to update sample interval?
        if new_params.sample_interval != self.params.sample_interval:
            self.sample_thread.interval = new_params.sample_interval
        
        self.params = new_params
        self.signals.setParamsDoneSig.emit()

    def start(self):
        self.signals.startingSig.emit()
        with self.supply_lock:
            self.supply.enable()

        self.sample_stop_event.clear()
        self.sample_thread.start() # start sample thread
        
        with self.status_lock:
            self.status.running = True
        self.signals.startedSig.emit()

    def stop(self):
        self.signals.stoppingSig.emit()
        
        if self.status.running:
            self.sample_stop_event.set() # tell sampling to stop

            with self.supply_lock:
                self.supply.disable()
            
            self.sample_thread.join() # wait for sample thread to stop

            with self.status_lock:
                self.status.running = False
        self.signals.stoppedSig.emit()
    
    ##########################
    # sample signal handlers #
    ##########################

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
        
        self.signals.newDataSig.emit(out_data)

class SampleRunner(Thread):
    def __init__(self,
        supply : DCSupply,
        supply_lock : Lock,
        eurotherm : Eurotherm2400,
        eurotherm_lock : Lock,
        sample_signal : SampleSignals,
        interval : float,
        stop_event : Event
    ):
        super().__init__()

        self.interval = interval
        self.supply = supply
        self.supply_lock = supply_lock
        self.eurotherm = eurotherm
        self.eurotherm_lock = eurotherm_lock
        self.sample_signal = sample_signal
        self.stop_event = stop_event


    def run(self):
        sc = sched.scheduler(time.perf_counter, time.sleep)

        start_time = time.perf_counter()
        data = (0,0,0,0) # (time, V, I, P, T)

        def sample(sc : sched.scheduler, target_time : float):
            with self.supply_lock:
                with self.eurotherm_lock:
                    data = (0, # time
                            self.supply.measV(), # voltage 
                            self.supply.measI(), # current
                            self.supply.measP(), # power
                            self.eurotherm.process_value # temperature
                        )
            data[0] = time.perf_counter - start_time
            self.sample_signal.newDataSig.emit(data)

            # check event to see if we should continue
            if not self.stop_event.is_set():
                # schedule next sample
                next_time = target_time + self.interval
                sc.enterabs(next_time, 1, sample, argument=(sc, next_time))

        # schedule first sample
        next_time = start_time + self.interval
        sc.enterabs(next_time, 1, sample, argument=(sc, next_time))