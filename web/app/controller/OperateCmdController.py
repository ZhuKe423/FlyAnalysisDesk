#!/usr/bin/env python3
#coding:utf-8

import time
from bottle import static_file, request, TEMPLATE_PATH, template
from util.RedisHandler import RedisHandler


class OperateCmdController(object):
    def __init__(self):
        self.r = RedisHandler()

    def change_datetime(self):
        timeArray = time.strptime(request.query['datetime'], "%Y-%m-%d %H:%M:%S")
        value = time.mktime(timeArray)
        cmds = {
            "changeTime": value,
            "timestamp": time.time()
        }
        self.r.set('FrontCmd', cmds)

    def update_play_speed(self):
        speed = int(request.query['playSpeed'])
        cmds = {
            "playSpeed": speed,
            "timestamp": time.time()
        }
        self.r.set('FrontCmd', cmds)

    def update_stop_state(self):
        stop = bool(int(request.query['stop']))
        cmds = {
            "stop": stop,
            "timestamp": time.time()
        }
        self.r.set('FrontCmd', cmds)


OperateCmd = ["Cmd", OperateCmdController]


