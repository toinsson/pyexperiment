
import pyrealsense as pyrs
pyrs.start()

import datetime
import scipy.misc

class CameraCalibration(Sensor):
    def __init__(self, dataStore, pattern, length=100):

        ## this is a trick to disable the recording later on
        self.calibDone = False
        self.cnt = -1

        self.dataStore = dataStore
        self.pattern = pattern
        self.length = length

        def _datetime_now():
            datetime_format = "%Y-%m-%d_%H:%M:%S:%f"
            return datetime.datetime.now().strftime(datetime_format)

        self.capture_function = {
            'd' : pyrs.get_depth,
            'c' : pyrs.get_colour,
            'v' : pyrs.get_pointcloud,
            't' : _datetime_now,
            }


    def _prepare_nframes(self, session, length):

        dataMap = {
        'c' : ((480, 640, 3), 'u1'),    # colour map
        'd' : ((480, 640), 'i2'),       # depth map
        't': ((), 'S26'),               # sample time
        }

        self.dataStore.create_group(session)
        datagrp = self.dataStore[session]
        datagrp.attrs.create('length', length)

        for k,v in dataMap.items():
            datagrp.create_dataset(k, (length,)+v[0], dtype=v[1])


    def start(self):

        pattern = scipy.misc.imread(self.pattern)
        self.dataStore.create_dataset('pattern', data=pattern)

        self._prepare_nframes('calib/before', self.length)
        rec = RecordSensors('calib/before', self.length, [self])
        rec.run()


    def prepare_nframes(self, session, length): pass


    def record_frame(self, session, frame):
        if self.calibDone == False:

            self.cnt += 1
            if self.cnt < self.length:

                for key in 'cdt':
                    self.dataStore[session][key][frame] = self.capture_function[key]()
            else:
                calibDone = True


class Camera(Sensor):
    def __init__(self, types, dataStore):

        self.types = types
        self.dataStore = dataStore

        def _datetime_now():
            datetime_format = "%Y-%m-%d_%H:%M:%S:%f"
            return datetime.datetime.now().strftime(datetime_format)

        self.capture_function = {
            'd' : pyrs.get_depth,
            'c' : pyrs.get_colour,
            'v' : pyrs.get_pointcloud,
            't' : _datetime_now,
            }

    def start(self): pass


    def prepare_nframes(self, session, length):
        dataMap = {
        'd' : ((480, 640), 'i2'),       # depth map
        't': ((), 'S26'),               # sample time
        }

        self.dataStore.create_group(session)
        datagrp = self.dataStore[session]
        datagrp.attrs.create('length', length)

        for k,v in dataMap.items():
            datagrp.create_dataset(k, (length,)+v[0], dtype=v[1])


    def record_frame(self, session, frame):
        for key in self.types:
            self.dataStore[session][key][frame] = self.capture_function[key]()
