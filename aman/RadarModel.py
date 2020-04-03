#!/usr/bin/env python3
#coding:utf-8

import queue
import threading
import time
from aman.data_define import new_db_handler, gl, new_redis_handler
from util.MultiThreadHandler import ThreadHandler

Radars = {}


class AirPlaneRadar:
    def __init__(self, call_sign):
        self.current = {}
        self.history = []
        self.air_plane = call_sign
        self.is_took = False
        gl.get_value("queueForAirPlane").put(
            {"AirPlane": self.air_plane,
             "classType": 'Radar'})

    def update_radar(self, radar):
        #print("Model Rec: {}".format(radar))
        #self.history.append(self.current)
        self.current = radar
        self.is_took = False

    def get_current_radar(self):
        self.is_took = True
        return self.current

    def get_current_time(self):
        return self.current['utctime']


class RadarManager:
    def __init__(self):
        self.db = new_db_handler()
        self.radar_info_queue = queue.Queue(500)
        self.event_tick = threading.Event()
        self.thread_get_data = ThreadHandler.create_task('RadarGetData', self.get_next_data_from_db, None, self.radar_info_queue)
        self.thread_process_pool = []
        self.redis_handlers = {"tickProcess": new_redis_handler()}
        self.is_stop = False
        for i in range(5):
            self.redis_handlers['RadarProcessor#%d' % i] = new_redis_handler()
            self.thread_process_pool.append(
                ThreadHandler.create_task('RadarProcessor#%d' % i, self.process_radar, self.radar_info_queue, None))
        self.current_time = 0

    def tick_run(self):
        #print("RadarManager is ticked!!")
        self.event_tick.set()

    def get_next_data_from_db(self, task):
        #print("out:: {}: processing".format(task.get_name()))
        self.event_tick.wait()
        if self.is_stop is True:
            self.event_tick.clear()
            return
        timestamp = gl.get_value('currentTime')
        sql = "select callsign,X,Y,longitude,latitude,C_altitude,A_altitude,speed,heading,utctime,rise,CTL,Wake"
        sql += " from radar where utctime > %d and utctime < %d;" % (self.current_time, timestamp)
        print(sql)
        self.current_time = timestamp
        radars = self.db.find_by_sql(sql)
        if radars is not None and len(radars) > 0:
            print(len(radars))
            for radar in radars:
                self.radar_info_queue.put(radar)
        self.event_tick.clear()

    def process_radar(self, task, item, out_queue):
        #print("out:: {}: process item".format(task.get_name()))
        if item['callsign'] in Radars:
            Radars[item['callsign']].update_radar(item)
        else:
            Radars[item['callsign']] = AirPlaneRadar(item['callsign'])
            Radars[item['callsign']].update_radar(item)
        self.redis_handlers[task.get_name()].set_one_dict_in_list('Radar', 'callsign', item)

    def update_current_time(self, timestamp):
        self.current_time = timestamp

    def get_current_time(self):
        return self.current_time

    def get_airplane_number(self):
        return len(Radars)

    def stop_play(self, stop):
        self.is_stop = stop

    def release_one(self, air_plane):
        print("Release_Radar of " + air_plane)
        self.redis_handlers["tickProcess"].del_on_dict_in_list('Radar', 'callsign', air_plane)
        if air_plane in Radars:
            del Radars[air_plane]

    def release_all(self):
        global Radars
        Radars = {}

    def get_one(self, air_plane):
        return Radars[air_plane]


RadarHandler = RadarManager()



