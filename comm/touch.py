import subprocess
import Queue

from .. import clientserver as cs
from . import comm

class TouchStream(sensors.Sensor):
    def __init__(self, dataStore, local=True):
        self.dataStore = dataStore
        self.local = local

        self.state = []
        self.ntouch = 0

        ## to game publisher for data/state
        self.dataqueue = Queue.LifoQueue()
        port = '5558'
        self.datasub = cs.ThreadedSubscriber(server, port, 
            self.dataqueue, topic='data')

        self.statequeue = Queue.Queue()
        port = '5558'
        self.statesub = cs.ThreadedSubscriber(server, port, 
            self.statequeue, purge=False, topic='state')

    def start(self): pass

    def prepare_nframes(self, session, length): pass
        ## make sure the queue is emptied

    def record_frame(self, session, frame):
        ## touch data: "data (touchId, x, y)"
        try:
            queueData = self.dataqueue.get_nowait()
            dataType = queueData.split(" ")[0]
            tid,x,y = eval("".join(queueData.split(" ")[1:]))
        except Queue.Empty:
            tid,x,y = (-1,-1,-1)

        ## state data: "state (up/down, touchId)"
        try:
            stateData = self.statequeue.get_nowait()
            dataType = stateData.split(" ")[0]
            state = stateData.split(" ")[1:]

            if state[0] == 'down':
                self.state.append(state[1])
                self.ntouch += 1
            if state[0] == 'up':
                try:
                    self.state.remove(state[1])
                    self.ntouch -= 1
                except ValueError:
                    pass

        except Queue.Empty:
            pass

        if (frame % 100 == 0): print "{} {:.2f} {:.2f}".format(self.state, x,y)

        frameData = {"x":x, "y":y, "tid":tid, "fid":frame,
                     "state":str(self.state), "ntouch":self.ntouch}

        self.dataStore.log("touch", data=frameData)
