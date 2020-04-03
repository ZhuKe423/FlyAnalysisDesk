#!/usr/bin/env python3
#coding:utf-8

import threading
from aman.FlyPlanModel import FlyPlanHandler
from aman.RadarModel import RadarHandler
from util.MultiThreadHandler import ThreadHandler
from aman.data_define import gl
from util.Timer import TimerHandler

AirPlanes = {}


class AirPlaneModel:
    def __init__(self, call_sign):
        self.callSign = call_sign
        self.radar = None
        self.plan = None

    def set_radar_model(self, radar):
        self.radar = radar

    def set_plan_model(self, flyplan):
        self.plan = flyplan

    def is_arrived(self):
        if self.plan is None:
            return False

        if self.plan.arrived_time() == 0:
            return False
        elif self.plan.arrived_time() + 20 < gl.get_value("currentTime"):
            return True
        else:
            return False

    def is_outdate(self):
        if self.radar is None:
            return False
        elif abs(self.radar.get_current_time() - gl.get_value("currentTime")) > 60*60:
            return True
        else:
            return False

    def release(self):
        RadarHandler.release_one(self.callSign)
        FlyPlanHandler.release_one(self.callSign)


class AirPlaneManager:
    def __init__(self):
        self.event_tick = threading.Event()
        self.new_plane_queue = gl.get_value('queueForAirPlane')
        print(gl.get_value('queueForAirPlane'))
        self.thread_for_new_plane = ThreadHandler.create_task('JoinNewAirPlane', self.new_air_plane,
                                                              self.new_plane_queue, None, )
        TimerHandler.new_timer(2, self.update_resource_loop)
        self.is_stop = False

    def update_resource_loop(self):
        self.filter_arrived_planes()

    def filter_arrived_planes(self):
        print("AirPlane Timer Ticked!!")
        if self.is_stop:
            return

        for plane in list(AirPlanes.keys()):
            if AirPlanes[plane].is_arrived() or AirPlanes[plane].is_outdate():
                AirPlanes[plane].release()
                del AirPlanes[plane]

    def new_air_plane(self, task, item, out_queue):
        print("out:: {}: processing {}".format(task.get_name(), item))
        if self.is_stop:
            return
        if item['AirPlane'] not in AirPlanes:
            AirPlanes[item['AirPlane']] = AirPlaneModel(item['AirPlane'])

        if item['classType'] is not None:
            if item['classType'] == 'FlyPlan':
                AirPlanes[item['AirPlane']].set_plan_model(FlyPlanHandler.get_one(item['AirPlane']))
            else:
                AirPlanes[item['AirPlane']].set_radar_model(RadarHandler.get_one(item['AirPlane']))

    def stop_play(self, stop):
        self.is_stop = stop

    def release_all(self):
        global AirPlanes
        AirPlanes = {}


AirPlaneHandler = AirPlaneManager()


