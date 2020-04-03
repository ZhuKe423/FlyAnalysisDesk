#!/usr/bin/env python3
#coding:utf-8

#from bottle import static_file, request, TEMPLATE_PATH, template
from util.database import MysqlConn
from web.base.models import new_db_handler


class MapController(object):
    def __init__(self):
        self.db = new_db_handler()

    def get_fix_point(self):
        sql = "select poncode,longV,latV from fixpoint where longV < 111.373095 and longV > 96.241318 "
        sql += "and latV < 33.426475 and latV > 27.625114;"
        print(sql)
        points = self.db.find_by_sql(sql)
        return {'data': points}

    def get_star_point(self):
        sql = "select POINTS from sidstar;"
        points = self.db.find_by_sql(sql)
        stars = []
        for point in points:
            if point not in stars:
                stars.append(point['POINTS'])
        return {'data': stars}

    def get_star_info(self):
        sql = "select STARNAME,POINTS from sidstarinfo;"
        star_routes = self.db.find_by_sql(sql)
        return {'data': star_routes}


Map = ['Map', MapController]
