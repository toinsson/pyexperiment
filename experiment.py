"""
Experiment.
"""

import sys

import pkg_resources

# from kivy.core import audio
# bip = audio.SoundLoader.load('../utils/start.wav')
# bop = audio.SoundLoader.load('../utils/stop.wav')

# from sys import path
# path.insert(1,'/home/antoine/Documents/owndev/sqlexperiment')
# import experimentlog

import comm

def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")


class Experiment(object):
    """
    """
    def __init__(self, logFilename, ntp_sync=False):
        super(Experiment, self).__init__()

        self.logFilename = logFilename
        # self.l = experimentlog.ExperimentLog(logFilename, ntp_sync=False)

    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_value, traceback):
        # self.l.close()
        pass

    def attach_feedback(self, feedback):
        self.feedback = feedback

    def attach_sensors(self, sensors):
        self.sensors = sensors

    def start_sensors(self):
        for sensor in self.sensors:
            sensor.start()


    def blocking_repetition(self, condition, numberSecs=10, validation=False):
        """Will block until numberFrame are captured through Recorder.
        """

        if not (condition == 'nocondition'):
            self.l.enter(condition, session = condition)

        session_id = str(self.l.session_id)
        numberFrame = numberSecs*30

        bip.play()
        rec = comm.Recorder(session_id, numberFrame, self.sensors)
        rec.run()
        bop.play()

        if validation:
            ok = query_yes_no('ok?')
        else: ok = True

        if not (condition == 'nocondition'):
            self.l.leave(valid=ok)

    def blocking_repetition_with_target(self, target, numberSecs=10):
        """Will block until numberFrame are captured through Recorder.
        Adds a target on game in (x,y) position before recording.
        """
        (x,y) = target
        self.l.enter(data={'target':(x,y)})

        session_id = str(self.l.session_id)
        numberFrame = numberSecs*30

        # create hdf5 group
        self.create_group(session_id, numberFrame)

        rec = Recorder(self.l, self.d[session_id], numberFrame,
            self.dataqueue, self.statequeue)

        # add target
        msg = {'msgType':'add_xy', 'args':(x,y)}
        self.gameclient.send_pyobj(msg)

        rec.run()
        self.l.leave()
        ## store in hdf5 file



    def non_blocking_repetition_with_random_target(self, condition, validation=False):

        # if not (condition == 'nocondition'):
        #     self.l.enter(condition, session = condition)

        # session_id = str(self.l.session_id)

        # self.start()

        # if not (condition == 'nocondition'):
        #     self.l.leave(valid=ok)

        pass



    def start():
        from numpy.random import random as rnd
        x, y, = rnd(2)

        comm.State.send('start')

        rec.run_until()

