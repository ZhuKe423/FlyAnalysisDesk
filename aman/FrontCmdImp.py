#!/usr/bin/env python3
#coding:utf-8

import time
from aman.data_define import gl, new_redis_handler
from util.Timer import TimerHandler
from aman.AirPlaneModel import AirPlaneHandler
from aman.RadarModel import RadarHandler
from aman.FlyPlanModel import FlyPlanHandler


class FrontCmdImplement(object):
    def __init__(self):
        self.r = new_redis_handler()
        TimerHandler.new_timer(2, self.get_cmd_loop)
        self.last_cmd_time = 0

    def get_cmd_loop(self):
        cmds = self.r.get("FrontCmd")
        if cmds is not None and len(cmds) > 0:
            print("Cmd Timer : get_cmd_loop: {}".format(cmds))
            if cmds['timestamp'] != self.last_cmd_time:
                self.last_cmd_time = cmds['timestamp']
                for key, value in cmds.items():
                    if key == 'playSpeed':
                        gl.set_value("playSpeed", value)
                    elif key == 'stop':
                        print("FrontCmd-Stop: {}".format(value))
                        gl.set_value("stop", value)
                        #AirPlaneHandler.stop_play(value)
                        #RadarHandler.stop_play(value)
                        #FlyPlanHandler.stop_play(value)
                    elif key == 'changeTime':
                        AirPlaneHandler.stop_play(True)
                        RadarHandler.stop_play(True)
                        FlyPlanHandler.stop_play(True)
                        time.sleep(5)
                        AirPlaneHandler.release_all()
                        RadarHandler.release_all()
                        FlyPlanHandler.release_all()
                        self.r.delete_all()
                        gl.set_value('currentTime', value)
                        RadarHandler.update_current_time(value)
                        FlyPlanHandler.update_current_time(value)
                        AirPlaneHandler.stop_play(False)
                        RadarHandler.stop_play(False)
                        FlyPlanHandler.stop_play(False)
                    elif key == 'timestamp':
                        print("command timestamp :%d" % value)
                    else:
                        print("invalid command %s !!" % key)

    def start(self):
        pass


FrontCmder = FrontCmdImplement()

