#!/usr/bin/env python3
#coding:utf-8

from bottle import static_file, request, TEMPLATE_PATH, template
from util.RedisHandler import RedisHandler
from web.base.models import new_db_handler


class RadarController(object):
    def __init__(self):
        self.r = RedisHandler()
        self.db = new_db_handler()

    def get(self):
        radars = self.r.get_dict_list('Radar')
        return {'data': radars}

    def get_plane_radar(self):
        callsign = request.query['airplane']
        start = int(request.query['start'])
        end = int(request.query['end'])
        sql = "select RDID,callsign,X,Y,longitude,latitude,C_altitude,A_altitude,speed,heading,utctime,rise,"
        sql += "CTL,Wake from radar where callsign = '%s' and utctime > %d and utctime < %d order by utctime asc;" % (
            callsign, start, end)
        print(sql)
        radars = self.db.find_by_sql(sql)
        return {'data': radars}


Radar = ['Radar', RadarController]
