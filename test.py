#!/usr/bin/env python3
#coding:utf-8

import json
import time
from util.database import MysqlConn

db = MysqlConn(host="132.232.7.110", username='root', password='Admin123!', port=3306, database='AMAN_DOG')

last_epts = []


def check_rtepts(rtepts):
    global last_epts
    cur_rtepts = []
    index = 0
    is_same = True
    for item in rtepts:
        cur_rtepts.append(item['PTID'])
        if len(last_epts) > index and last_epts[index] != item['PTID']:
            is_same = False
            # print(last_epts[index]+" -- "+item['PTID'])
        index += 1
    if is_same is False:
        print("last_rtepts: {}".format(cur_rtepts))
        print("cur_rtepts:  {}".format(cur_rtepts))

    last_epts = cur_rtepts


def get_flyplan(plane, start, end):
    sql = "select * from flyplan where arcid ='%s' and timestamp>%d and timestamp<=%d;" % (plane, start, end)
    flyplans = db.find_by_sql(sql)
    for fp in flyplans:
        print('FPID: %d  -TimeStamp: %d  -ETA: %s' % (fp['FPID'], fp['timestamp'], fp['ETA']))
        check_rtepts(json.loads(fp['RTEPTS']))


last_a_lat = 0
def check_a_lat(radar):
    global last_a_lat
    str = ''
    a = radar['A_altitude']
    if last_a_lat!=0 and last_a_lat != a:
        str += ("A_altitude is changed: %d -> %d" %(last_a_lat, a))
    last_a_lat = a
    return str


def get_radar(plane, start, end):
    sql = "select * from radar where callsign ='%s' and utctime>%d and utctime<=%d;" % (plane, start, end)
    radars = db.find_by_sql(sql)
    for radar in radars:
        str = check_a_lat(radar)
        if str != '':
            print("RDID: %d, utctime: %d" %(radar['RDID'], radar['utctime']))
            print(str)
            print("---------------------------------------------")


def get_fp_conflict():
    sql = "select * from fp_conflict;"
    conflicts = db.find_by_sql(sql)


if __name__ == "__main__":
    #get_flyplan("CES2252", 1574743860, 1574747460)
    #get_radar("CES2252", 1574743860, 1574747460)

    get_flyplan("CSC8698", 1574743860, 1574747460)

