import time
import subprocess

from .. import clientserver as cs

class Feedback(object):
    def __init__(self, local=True):

        game_cmd = ['python', '-m', 'pyexperiment.gui', '--publish']

        if local:
            server = 'localhost'
            p = subprocess.Popen(game_cmd)
        else:
            ## to the MS surface for launching game
            server = '10.0.0.2'
            port = '5556'
            self.winclient = cs.LPClient(server, port)

            msg = cs.Message(msgType='command', command=game_cmd)
            self.winclient.send_pyobj(msg.msg)

        ## to game server for commands - add/stop/...
        port = '5557'
        self.gameclient = cs.LPClient(server, port)
        self.statesub = cs.StateSubscriber('5558')


        ## could send a ping to gameclient...
        time.sleep(1)


    def send(self, message):
        msg = {'msgType' : message}
        self.gameclient.send_pyobj(msg)

    def wait_for_end(self):

        print 'start wait'
        res = self.statesub.wait()
        print 'end wait'

        return res