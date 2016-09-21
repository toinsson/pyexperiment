# import sys
# import argparse

# if __name__ == '__main__':
#     argv = sys.argv[1:]
#     sys.argv = sys.argv[:1]
#     if "--" in argv:
#         index = argv.index("--")
#         kivy_args = argv[index+1:]
#         argv = argv[:index]

#         sys.argv.extend(kivy_args)

#     desc = ''.join(['Touch tracer app. Can send data via socket.'])
#     parser = argparse.ArgumentParser(description=desc)

#     parser.add_argument('--publish', help='publish touch/cmd data',
#         required=False, action='store_true')
#     args = parser.parse_args(argv)

import time

import kivy
from kivy.lang import Builder
from kivy.app import App
from kivy.properties import NumericProperty, StringProperty
from kivy.graphics import Line, Color
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget

import numpy as np

import transitions as tr


class Target(Widget):
    """Circle target of absolute position (x,y) and radius r that pops in a 
    floatLayout. The collision function is redefined to trigger on the canvas
    and not on the total widget size.
    """
    # cx = NumericProperty()
    # cy = NumericProperty()

    def __init__(self, cx=0, cy=0, r=50, **kwargs):
        super(Target, self).__init__(**kwargs)

        with self.canvas:
            Line(circle = (cx, cy, 50), width = 2)

        self.cx = cx
        self.cy = cy
        self.r  = r

    def collide_point(self, x,y):
        return np.linalg.norm([x-self.cx, y-self.cy]) <= self.r


class CrossTarget(Widget):
    """Cross target of absolute position (x,y) and width w that pops in a 
    floatLayout. The collision function is redefined to trigger on the canvas
    and not on the total widget size.
    """
    def __init__(self, cx=0, cy=0, r=30, **kwargs):
        super(CrossTarget, self).__init__(**kwargs)

        with self.canvas:
            Color(1,0,1)
            Line(points = [cx-r,cy,cx+r,cy], width = 2)
            Line(points = [cx,cy-r,cx,cy+r], width = 2)

        self.cx = cx
        self.cy = cy
        self.r  = r

    def collide_point(self, x,y):
        return np.linalg.norm([x-self.cx, y-self.cy]) < self.r



class MyGui(FloatLayout, tr.Machine):

    state = StringProperty('default')

    def __init__(self, states, transitions, *args, **kwargs):
        super(MyGui, self).__init__(*args, **kwargs)

        tr.Machine.__init__(self, states=states, transitions=transitions, 
            initial='init', auto_transitions=False, ignore_invalid_triggers=True)
        self.add_ordered_transitions()


        self.touch = []
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)


    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None


    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] == 'spacebar':
            print 'spacebar ', self.state
            self.on_spacebar()


    def on_touch_down(self, touch):
        if self.state == 'recording': self.touch.append(touch)
    def on_touch_move(self, touch):
        if self.state == 'recording': self.touch.append(touch)
    def on_touch_up(self, touch):
        if self.state == 'recording': self.touch.append(touch)

        for child in self.children:
            if isinstance(child, CrossTarget) or isinstance(child, Target):
                self.remove_widget(child)

        self.on_touch_up_()


    def clean(self):
        self.touch = []

    def add_target(self):
        width, height = self.size
        x, y, = self.x*width, self.y*height
        self.add_widget(CrossTarget(x,y))


    def save_target(self, *args, **kwargs):
        self.x = kwargs['x']
        self.y = kwargs['y']


class GuiApp(App):

    def __init__(self, publish=False, **kwargs):
        super(GuiApp, self).__init__(**kwargs)
        self.publish = publish


    def build(self):

        ## STATE MACHINE && GUI
        states = [
            'init',
            'ready',
            tr.State('recording', on_enter='add_target'),
            'finish',
            tr.State('send', on_enter=self.send_feedback, on_exit='clean')
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

        myGui = MyGui(states=states, transitions=transitions)


        ## print state  machine
        if False:
            from transitions.extensions import GraphMachine
            gm = GraphMachine(model=myGui, states=states, initial='init', auto_transitions=False)
            gm.add_ordered_transitions()
            gm.add_transition('on_spacebar', 'ready', 'recording')
            gm.graph.draw('my_state_diagram.png', prog='dot')


        ## COMMUNICATION
        from . import clientserver as cs
        self.pub = cs.SimplePublisher(port = "5558")

        cmd_dict = {
        'add_target' : myGui.receive_master_msg,
        }

        self.cmdServer = cs.ThreadedServer(cmd_dict, port='5557')

        return myGui


    def send_feedback(self):
        self.pub.send_topic('changestate', self.root.touch)
        self.root.reboot()


    def on_stop(self):
        if self.cmdServer.is_alive() and not self.cmdServer.request_alive:
            self.cmdServer.stop()

        self.pub.close()

        return True


if __name__ == '__main__':
    GuiApp().run()
