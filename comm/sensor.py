"""
Defines an abstract class for sensors and an associated recorder.
"""

import abc
class Sensor():
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def start(self, frame):
        pass

    @abc.abstractmethod
    def prepare_nframes(self, frame):
        pass

    @abc.abstractmethod
    def record_frame(self, frame):
        pass

import sched
import time

class Recorder(object):
    def __init__(self, session, numberFrame, sensors):
        super(Recorder, self).__init__()

        self.fps = 1./30
        self.cnt = -1
        self.s = sched.scheduler(time.time, time.sleep)

        self.session = session
        self.numberFrame = numberFrame

        self.sensors = sensors

        for sensor in self.sensors:
            sensor.prepare_nframes(session, numberFrame)

    def record_frame(self):
        # import ipdb; ipdb.set_trace()

        self.cnt += 1
        if (self.cnt < self.numberFrame):
            self.s.enter(self.fps, 1, self.record_frame, ())
        else:
            return

        for sensor in self.sensors:
            sensor.record_frame(self.session, self.cnt)

    def run(self):
        self.s.enter(0, 1, self.record_frame, ())
        self.s.run()

