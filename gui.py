import sys
import argparse

if __name__ == '__main__':
    argv = sys.argv[1:]
    sys.argv = sys.argv[:1]
    if "--" in argv:
        index = argv.index("--")
        kivy_args = argv[index+1:]
        argv = argv[:index]

        sys.argv.extend(kivy_args)

    desc = ''.join(['Touch tracer app. Can send data via socket.'])
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument('--publish', help='publish touch/cmd data',
        required=False, action='store_true')
    args = parser.parse_args(argv)

import time

import kivy
from kivy.lang import Builder
from kivy.app import App
from kivy.properties import NumericProperty
from kivy.graphics import Line
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget

from numpy.random import random as rnd
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
            # Color(1,0,1)
            Line(points = [cx-r,cy,cx+r,cy], width = 2)
            Line(points = [cx,cy-r,cx,cy+r], width = 2)
            # Color(1,1,1)

        self.cx = cx
        self.cy = cy
        self.r  = r

    def collide_point(self, x,y):
        return np.linalg.norm([x-self.cx, y-self.cy]) < self.r



class MyGui(FloatLayout):
    def __init__(self, *args, **kwargs):
        super(MyGui, self).__init__(*args, **kwargs)
        self.touch = []

        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)


    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None


    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] == 'spacebar':
            self.on_spacebar()

            if self.state not in ['init', 'recording']: self.transition()



    def on_spacebar(self):
        print 'spacebar'
        # pass

    def on_touch_down(self, touch):
        if self.state == 'recording':
            self.touch.append(touch)
            self.transition()


    def on_touch_up(self, touch):
        for child in self.children:
            if isinstance(child, CrossTarget) or isinstance(child, Target):
                self.remove_widget(child)


    def transition(self):
        print 'transition'
        self.next_state()
        self.ids['label_text'].text_ = self.state


    def add_target(self):
        width, height = self.size
        x, y, = rnd()*width, rnd()*height
        self.add_widget(CrossTarget(x,y))


class GuiApp(App):

    def __init__(self, publish=False, **kwargs):
        super(GuiApp, self).__init__(**kwargs)
        self.publish = publish


    def build(self):

        ## GUI
        myGui = MyGui()

        ## STATE MACHINE
        states = [
            'init',
            'ready',
            tr.State('recording', on_enter=self.add_target),
            tr.State('finish', on_enter=self.on_state_finish),
            tr.State('send', on_exit=self.on_state_send),
            # 'done'
        ]

        machine = tr.Machine(model=myGui, states=states, initial='init', auto_transitions=False)
        machine.add_ordered_transitions()
        machine.add_transition('on_spacebar', 'ready', 'recording')


        if False:
            from transitions.extensions import GraphMachine
            gm = GraphMachine(model=myGui, states=states, initial='init', auto_transitions=False)
            gm.add_ordered_transitions()
            gm.add_transition('on_spacebar', 'ready', 'recording')
            gm.graph.draw('my_state_diagram.png', prog='dot')


        self.machine = machine

        ## COMMUNICATION
        if self.publish:
            from . import clientserver as cs
            self.pub = cs.SimplePublisher(port = "5558")

            cmd_dict = {
            'add_target' : self.transition,
            }

            self.cmdServer = cs.ThreadedServer(cmd_dict, port='5557')

        return myGui


    def on_state_finish(self, *args):
        self.to_send = self.root.touch[:]
        self.root.touch = []

        self.transition()


    def on_state_send(self):
        for touch in self.to_send: print touch.time_start, touch.time_end

        print 'send: ', self.to_send
        if self.publish:
            self.pub.send_topic('changestate', self.to_send)

    def transition(self):
        state = str(self.machine.model.state)
        self.machine.model.next_state()
        self.root.ids['label_text'].text_ = self.machine.model.state
        print state, ' -> ', self.machine.model.state


    def add_target(self):
        # self.transition()
        self.machine.model.add_target()


    def on_stop(self):
        if self.publish:

            if self.cmdServer.is_alive() and not self.cmdServer.request_alive:
                self.cmdServer.stop()

            self.pub.close()

        return True



if __name__ == '__main__':
    GuiApp(publish=args.publish).run()
