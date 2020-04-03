#!/usr/bin/env python3
#coding:utf-8

import queue
from util.Timer import TimerHandler
from util.MultiThreadHandler import ThreadHandler
from aman.RadarModel import RadarHandler
from aman.FlyPlanModel import FlyPlanHandler
from aman.AirPlaneModel import AirPlaneHandler
from aman.FrontCmdImp import FrontCmder
from aman.data_define import gl


def info_process(*args):
    for manager in args:
        if gl.get_value('stop') is False:
            if gl.get_value('currentTime') > 1577203181:
                AirPlaneHandler.stop_play(True)
                AirPlaneHandler.release_all()
                RadarHandler.release_all()
                FlyPlanHandler.release_all()
            gl.increase('currentTime', 4 * gl.get_value('playSpeed'))
        manager.tick_run()


def init_data():
    gl.set_value('currentTime', 1574783981)
    gl.set_value('currentDate', "20191126000000")


if __name__ == "__main__":
    init_data()
    RadarHandler.update_current_time(gl.get_value('currentTime'))
    FlyPlanHandler.update_current_time(gl.get_value('currentTime'))
    FrontCmder.start()
    #AirPlaneHandler.start()
    #(radar_handler, flyplan_handler)
    TimerHandler.new_timer(4, info_process, (RadarHandler, FlyPlanHandler,))
    ThreadHandler.run_all()
    TimerHandler.start_all()

    ThreadHandler.thread_checker()
    TimerHandler.cancel_all()
    print("Dog Aman is stopped!!")

