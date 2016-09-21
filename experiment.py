import transitions as tr


from numpy.random import random as rnd





## STATE MACHINE

states = [
    'init',
    'send_start',
    'get_data',
    'log',
]



# states_msg = {
#     'init':'',                                  ## wait for master message
#     'ready':'',                                 ## wait for keyboard space press
#     'recording':'press space to start',         ## wait for touch events
#     'finish':'touch',                           ## wait for keyboard space press
#     'send':'press space to stop',               ## send data and reboot
# }

transitions = [
    {'trigger': 'receive_master_msg',   'source': 'init',       'dest': 'ready',
    'before':'save_target'},
    {'trigger': 'on_spacebar',          'source': 'ready',      'dest': 'recording'},
    {'trigger': 'on_touch_up_',         'source': 'recording',  'dest': 'finish'},
    {'trigger': 'on_spacebar',          'source': 'finish',     'dest': 'send'},
    {'trigger': 'reboot',               'source': 'send',       'dest': 'init', },
]

# myGui = MyGui(states=states, transitions=transitions)



class Experiment(object):
    """docstring for Experiment"""
    def __init__(self, feedback=None):
        super(Experiment, self).__init__()
        self.feedback = feedback


    def repetition(self):

        ## send start
        msg = {'msgType':'add_target', 'args':{'x':rnd(), 'y':rnd()}}
        self.feedback.send(msg)

        ## wait for 
        res = self.feedback.wait_for_end()
        # pass

        print 'received msg: ', res
