#!/usr/bin/env python3
#coding:utf-8

import xlrd
import re
import numpy as np
from util.database import MysqlConn
from bottle import static_file, request, TEMPLATE_PATH, template


def DMS_2_D(d, m, s):
    return d + m / 60 + s / 60 / 60


def xy_2_gps(data):
    origin = {"latitude": DMS_2_D(30, 34, 42), "longitude": DMS_2_D(103, 56, 54)}
    ARC = 6371.393 * 1000
    longitude = origin['longitude'] + data['X'] / (
                (ARC * np.cos(np.deg2rad(origin['latitude'])) * 2 * np.pi) / 360)
    latitude = origin['latitude'] + data['Y'] / (ARC * 2 * np.pi / 360)
    data['longitude'] = float(longitude)
    data['latitude'] = float(latitude)
    return data


class DraftController(object):
    def __init__(self):
        self.conflict_case1 = MysqlConn(database="aman_conflict_case")

    def get_ces5405_radar(self):
        xl = xlrd.open_workbook('D:\华川信达\ArrivalManagement\沟通后的资料\data\9hours\CES5405_radar.xlsx')
        sheet = xl.sheet_by_index(0)
        rowNum = sheet.nrows
        print("rowNum:%d" % rowNum)
        index = 1
        data = []
        while True:
            if index >= rowNum:
                break
            row = sheet.row_values(index)
            tmpdata = {
                "dateTime": row[0],
                "longitude": row[4],
                "latitude": row[5],
                "C_lat": row[3],
                "speed": row[6]
            }
            data.append(tmpdata)
            index += 1
        return {'data': data}

    def get_CCA4402_radar(self):
        xl = xlrd.open_workbook('D:\华川信达\ArrivalManagement\沟通后的资料\data\9hours\CCA4402_radar.xlsx')
        sheet = xl.sheet_by_index(0)
        rowNum = sheet.nrows
        print("rowNum:%d" % rowNum)
        index = 1
        data = []
        while True:
            if index >= rowNum:
                break
            row = sheet.row_values(index)
            tmpdata = {
                "dateTime": row[0],
                "longitude": row[4],
                "latitude": row[5],
                "C_lat": row[3],
                "speed": row[6]
            }
            data.append(tmpdata)
            index += 1
        return {'data': data}

    def get_airplane_radar(self):
        airplane = request.query['airplane']
        sql = "select rid,i003_042,i003_090,i003_092,i003_200 from radar_conflict where i003_240 = '%s';" % airplane
        radars = self.conflict_case1.find_by_sql(sql)
        data = []
        for radar in radars:
            p = radar['i003_042'].split(',')
            print(p)
            x = p[0].split('=')[1]
            print("x={}".format(x))
            y = p[1].split('=')[1]
            print("y={}".format(y))
            c_al = re.findall('ch=(\d+)米', radar['i003_090'])
            print("c_al={}".format(c_al))
            a_al = re.findall('ch=(\d+)米', radar['i003_092'])
            print("a_al={}".format(a_al))
            speed = re.findall('=(\d+).', radar['i003_200'])
            print("speed={}".format(speed))
            tmp = {'X': int(x), 'Y': int(y),
                   'C_al': int(c_al[0]), 'A_al': int(a_al[0]), 'Speed': int(speed[0])}
            xy_2_gps(tmp)
            data.append(tmp)

        return {'data': data}


Draft = ['Draft', DraftController]


