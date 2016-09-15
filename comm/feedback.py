import time
import subprocess

from .. import clientserver as cs

class Feedback(object):
    def __init__(self, local=True):

        game_cmd = ['python', '-m', 'pyexperiment.game.game', '--publish']

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


        time.sleep(5)

    def send(self):
        msg = {'msgType' : 'add'}
        self.gameclient.send_pyobj(msg)
