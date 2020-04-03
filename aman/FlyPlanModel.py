#!/usr/bin/env python3
#coding:utf-8

import queue
import threading
import time
from aman.data_define import new_db_handler, gl, new_redis_handler
from util.MultiThreadHandler import ThreadHandler

FlyPlans = {}


class AirPlaneFlyPlanModel:
    def __init__(self, call_sign):
        self.air_plane = call_sign
        self.current_fly_plan = {}
        self.arrived = 0
        print("AirPlaneFlyPlanModel New")
        gl.get_value("queueForAirPlane").put(
            {"AirPlane": self.air_plane,
             "classType": 'FlyPlan'})

    def update_plan(self, plan):
        #print(plan)
        if plan['ATIME'] is not None and plan['ATIME'] > 0:
            self.arrived = plan['ATIME']
        self.current_fly_plan = plan

    def get_current_plan(self):
        return self.current_fly_plan

    def arrived_time(self):
        return self.arrived

    def get_eta(self):
        return self.current_fly_plan['ETA']


class FlyPlanManager:
    def __init__(self):
        self.db = new_db_handler()
        self.flyplan_info_queue = queue.Queue(300)
        self.event_tick = threading.Event()
        self.thread_get_data = ThreadHandler.create_task('FlyPlanGetData', self.get_next_data_from_db, None, self.flyplan_info_queue)
        self.thread_process_pool = []
        self.redis_handlers = {"tickProcess": new_redis_handler()}
        self.is_stop = False
        for i in range(3):
            self.redis_handlers['FlyPlanProcessor#%d' % i] = new_redis_handler()
            self.thread_process_pool.append(
                ThreadHandler.create_task('FlyPlanProcessor#%d' % i, self.process_flyplan, self.flyplan_info_queue, None))
        self.current_time = 0

    def tick_run(self):
        #print("FlyPlanManager is ticked!!")
        self.event_tick.set()

    def get_next_data_from_db(self, task):
        #print("out:: {}: processing".format(task.get_name()))
        self.event_tick.wait()
        if self.is_stop is True:
            self.event_tick.clear()
            return
        timestamp = gl.get_value('currentTime')
        sql = "select ARCID,timestamp,ETA,ADA_ATA,ATIME,RWY,ARWY,STAR,ROUTE,RTEPTS,SECTOR,TTLEET"
        sql += " from flyplan where timestamp > %d and timestamp < %d;" % (self.current_time, timestamp)
        self.current_time = timestamp
        fly_plans = self.db.find_by_sql(sql)
        if fly_plans is not None and len(fly_plans) > 0:
            for plan in fly_plans:
                self.flyplan_info_queue.put(plan)
        self.event_tick.clear()

    def process_flyplan(self, task, item, out_queue):
        #print("out:: {}: process item".format(task.get_name()))
        if item['ARCID'] in FlyPlans:
            FlyPlans[item['ARCID']].update_plan(item)
        else:
            FlyPlans[item['ARCID']] = AirPlaneFlyPlanModel(item['ARCID'])
            FlyPlans[item['ARCID']].update_plan(item)
        self.redis_handlers[task.get_name()].set_one_dict_in_list('FlyPlan', 'ARCID', item)

    def update_current_time(self, timestamp):
        self.current_time = timestamp

    def get_airplane_number(self):
        return len(FlyPlans)

    def stop_play(self, stop):
        self.is_stop = stop

    def release_one(self, air_plane):
        self.redis_handlers["tickProcess"].del_on_dict_in_list('FlyPlan', 'ARCID', air_plane)
        if air_plane in FlyPlans:
            del FlyPlans[air_plane]

    def get_one(self, air_plane):
        return FlyPlans[air_plane]

    def release_all(self):
        global FlyPlans
        FlyPlans = {}


FlyPlanHandler = FlyPlanManager()


