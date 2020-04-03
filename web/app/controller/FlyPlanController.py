#!/usr/bin/env python3
#coding:utf-8

from bottle import static_file, request, TEMPLATE_PATH, template
from util.RedisHandler import RedisHandler
from web.base.models import new_db_handler


class FlyPlanController(object):
    def __init__(self):
        self.r = RedisHandler()
        self.db = new_db_handler()

    def get_plane_flyplan(self):
        arcid = request.query['airplane']
        start = float(request.query['current'])
        sql = "select ARCID,timestamp,ETA,ADA_ATA,ATIME,RWY,ARWY,STAR,ROUTE,RTEPTS,SECTOR,TTLEET"
        sql += " from flyplan where timestamp > %d and ATIME > 0 and ARCID = '%s';" % (start, arcid)
        fly_plans = self.db.find_by_sql(sql)
        return {'data': fly_plans[0]}


FlyPlan = ['FlyPlan', FlyPlanController]

