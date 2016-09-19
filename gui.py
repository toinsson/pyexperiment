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
            if self.state != 'recording': self.transition()


    def on_touch_down(self, touch):
        if self.state == 'recording':
            self.touch.append(touch)
            self.transition()


    def transition(self):
        print 'transition'
        self.next_state()
        self.ids['label_text'].text_ = self.state

    def add_target(self):
        width, height = self.size
        x, y, = rnd()*width, rnd()*height
        self.add_widget(Target(x,y))


class GuiApp(App):


    def build(self):

        ## GUI
        myGui = MyGui()

        ## STATE MACHINE
        states = [
            'init',
            'ready',
            tr.State('recording', on_enter=self.add_target),
            tr.State('finish', on_enter=self.on_state_finish),
            tr.State('send', on_enter=self.on_state_send),
            'done'
        ]

        machine = tr.Machine(model=myGui, states=states, initial='init')
        machine.add_ordered_transitions()

        self.machine = machine

        return myGui


    def on_state_finish(self, *args):
        for touch in self.root.touch: print touch.time_start, touch.time_end
        self.root.touch = []

        self.transition()


    def on_state_send(self):
        print 'send'


    def transition(self):
        print 'transition ', self.machine.model.state
        self.machine.model.next_state()
        self.root.ids['label_text'].text_ = self.machine.model.state


    def add_target(self):
        self.machine.model.add_target()


if __name__ == '__main__':
    GuiApp().run()
