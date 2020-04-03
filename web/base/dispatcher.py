#!/usr/bin/env python3
#coding:utf-8

from bottle import static_file, request, TEMPLATE_PATH, template


class DispatchHandler:
    def __init__(self):
        self.controllers = {}

    def register_controller(self, node, controller):
        self.controllers[node] = controller

    def register_ctrl_list(self, controllers):
        for item in controllers:
            self.register_controller(item[0], item[1])

    def dispatch(self, controller, action):
        print("dispatch: %s->%s" % (controller, action))
        if controller in self.controllers:
            ctrl = self.controllers[controller]()
            act = getattr(ctrl, action, None)
            if act is not None:
                return act()
            else:
                print("error : doesn't has this action %!!!" % action)
                return "error : doesn't has this action %!!!" % action
        else:
            print("error : doesn't has this application!!!")
            return "error : doesn't has this application!!!"


Dispatcher = DispatchHandler()
