'''
Game wack-a-mole like for data collection. It will spawn a new target each time 
the current one is acquired at a random (x,y) position on the screen. It grants
access to live touch data via a 0mq server.
'''
import sys
import argparse


print 'NAME:   ', __name__

################################################################################
# this allow to highjack kivy's argument parser
################################################################################
if __name__ == '__main__':

    print 'Hell'


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
    parser.add_argument('--recurrent', help='add random target',
        required=False, action='store_true')
    parser.add_argument('--keep', help='keep the traces on display',
        required=False, action='store_true')
    parser.add_argument('--bgimg', help='background image to display',
        required=False, default='')
    parser.add_argument('--port', help='communition port, default 5557',
        required=False, default='5557')

    args = parser.parse_args(argv)
    print args

__version__ = '1.0'

import numpy as np
from numpy.random import random as rnd
import ipdb, pdb

import kivy
kivy.require('1.0.6')

from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.graphics import Ellipse, Color, Rectangle, Point, GraphicException
from kivy.properties import BooleanProperty, StringProperty, NumericProperty
from kivy.graphics import Line
from kivy.uix.widget import Widget
from kivy.clock import Clock


class Target(Widget):
    """Circle target of absolute position (x,y) and radius r that pops in a 
    floatLayout. The collision function is redefined to trigger on the canvas
    and not on the total widget size.
    """
    def __init__(self, x=0, y=0, r=50, **kwargs):
        super(Target, self).__init__(**kwargs)
        with self.canvas:
            self.centered_circle = Line(circle = (x, y, 50), width = 2)

        self.cx = x
        self.cy = y
        self.r  = r

    def collide_point(self, x,y):
        return np.linalg.norm([x-self.cx, y-self.cy]) < self.r

class CrossTarget(Widget):
    """Cross target of absolute position (x,y) and width w that pops in a 
    floatLayout. The collision function is redefined to trigger on the canvas
    and not on the total widget size.
    """
    def __init__(self, x=0, y=0, r=30, **kwargs):
        super(CrossTarget, self).__init__(**kwargs)

        with self.canvas:
            # Color(1,0,1)
            Line(points = [x-r,y,x+r,y], width = 2)
            Line(points = [x,y-r,x,y+r], width = 2)
            # Color(1,1,1)

        self.cx = x
        self.cy = y
        self.r  = r

    def collide_point(self, x,y):
        return np.linalg.norm([x-self.cx, y-self.cy]) < self.r


# class FullImage(Image):
#     """Can be used to place a background to the TouchTracer app.
#     """
#     source = StringProperty(args.bgimg)
#     allow_stretch = BooleanProperty(True)


class Touchtracer(FloatLayout):
    """Simple floatLayout that can add targets to its layout and removes them 
    when a collision is detected between the touch point and any target 
    position.
    """
    target_reached = NumericProperty(0)
    background = StringProperty()

    def __init__(self, pub=None, background='', **kwargs):
        super(Touchtracer, self).__init__(**kwargs)
        self.pub = pub
        self.background = background

    def add_random_target(self):
        """
        """
        width, height = self.size
        x, y, = rnd()*width, rnd()*height
        self.add_widget(Target(x,y))

    def add_target(self, dt):
        self.target_reached += 1
        width, height = self.size
        x, y, = rnd()*width, rnd()*height
        self.add_widget(CrossTarget(x,y))

    def add_xy_target(self, x, y):
        """
        """
        width, height = self.size
        x, y = x*width, y*height
        self.add_widget(CrossTarget(x,y))

    def on_key_down(self, *args, **kwargs):
        print args

    def on_keyboard(self, key, scancode, codepoint, modifier):
        print key


    def on_touch_down(self, touch):
        if self.pub is not None:  ## send normalised touch position
            data = str((str(touch.uid), touch.sx, touch.sy))
            self.pub.send_topic("state", 'down ' + str(touch.uid))
            self.pub.send_topic("data", data)

        for child in self.children:
            if child.collide_point(touch.x, touch.y):
                self.remove_widget(child)

                if self.pub is not None:
                    self.pub.send_topic("state", 'target')
                # self.add_target(0)

        pointsize = 5
        ud = touch.ud
        ud['group'] = g = str(touch.uid)

        self.canvas.remove_group(ud['group'])
        with self.canvas:
            Color(0,0,0)
            ud['lines'] = Point(points=(touch.x, touch.y),
                                pointsize=pointsize, group=g)
        return True

    def on_touch_move(self, touch):
        if self.pub is not None:  ## send normalised touch position
            data = str((str(touch.uid), touch.sx, touch.sy))
            self.pub.send_topic("data", data)

        pointsize = 5

        ud = touch.ud
        ud['group'] = g = str(touch.uid)
        self.canvas.remove_group(ud['group'])
        with self.canvas:
            ud['lines'] = Point(points=(touch.x, touch.y),
                                pointsize=pointsize, group=g)

        for child in self.children:
            if child.collide_point(touch.x, touch.y):
                self.remove_widget(child)
                # self.add_target(0)

    def on_touch_up(self, touch):
        if self.pub is not None:  ## send normalised touch position
            self.pub.send_topic("state", 'up ' + str(touch.uid))

        ud = touch.ud
        self.canvas.remove_group(ud['group'])

from kivy.core.window import Window

class TouchtracerApp(App):

    def __init__(self, publish=False, recurrent=False, background='', **kwargs):
        super(TouchtracerApp, self).__init__(**kwargs)
        self.publish = publish
        self.recurrent = recurrent
        self.background = background

        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        print keycode

        if keycode[1] == 'escape': self.stop()

        return True

    def _keyboard_closed(self):
        print 'close keyboard'
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None


    def build(self):

        if self.publish:
            from .. import clientserver as cs

            self.pub = cs.SimplePublisher(port = "5558")
            self.touchtracer = Touchtracer(pub = self.pub, background=self.background)

            cmd_dict = {
            'runAndDie' : self.stop,
            'add' : self.touchtracer.add_random_target,
            'add_xy' : self.touchtracer.add_xy_target,
            }
            self.cmdServer = cs.ThreadedServer(cmd_dict, port='5557')

        else:
            self.touchtracer = Touchtracer(background=self.background)

        ## add random target every 0.5 seconds
        if self.recurrent:
            Clock.schedule_interval(self.touchtracer.add_target, 0.7)

        return self.touchtracer


    def on_stop(self):

        # import ipdb; ipdb.set_trace()

        if self.publish:

            if self.cmdServer.is_alive() and not self.cmdServer.request_alive:
                self.cmdServer.stop()

            # self.pub.send_topic(b'kill', '')
            self.pub.close()

        if self.recurrent:
            print self.touchtracer.target_reached

        return True

if __name__ == '__main__':
    TouchtracerApp(publish=args.publish, 
                recurrent=args.recurrent,
                background=args.bgimg,
                ).run()