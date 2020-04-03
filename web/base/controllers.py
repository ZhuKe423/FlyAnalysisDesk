#!/usr/bin/env python3
#coding:utf-8

from web.app.controller.RaderController import Radar
from web.app.controller.MapController import Map
from web.app.controller.DraftController import Draft
from web.app.controller.OperateCmdController import OperateCmd
from web.app.controller.FlyPlanController import FlyPlan

Controllers = [Radar, Map, Draft, OperateCmd, FlyPlan]

