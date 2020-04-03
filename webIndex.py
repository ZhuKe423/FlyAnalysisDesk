#!/usr/bin/env python3
#coding:utf-8

import os
import inspect
from bottle import route, run, default_app, static_file, response, request, TEMPLATE_PATH
from web.base.dispatcher import Dispatcher
from web.base.controllers import Controllers
from util.Timer import TimerHandler
from web.base.models import create_a_idle_timer

def module_path(local_function):
    '''
    returns the module path without the use of __file__.  Requires a function defined
    locally in the module.
    from http://stackoverflow.com/questions/729583/getting-file-path-of-imported-module
    '''
    return os.path.abspath(inspect.getsourcefile(local_function))


@route('/static/images/<filename:re:.*\.png>')
def send_image(filename):
    return static_file(filename, root='./web/static/images', mimetype='image/png')


@route('/static/js/<filename:path>')
def send_static(filename):
    print(filename)
    return static_file(filename, root='./web/static/js')


@route('/')
def main():
    response.set_cookie('AmanSim', '123', secret=None)
    return static_file("index.html", root='./web/static/html')


@route('/test/<case>')
def test(case):
    return static_file("test.html", root='./web/static/html')


@route('/draft/<case>')
def draft(case):
    response.set_cookie('AmanSim', '123', secret=None)
    if case == '1':
        return static_file("draft.html", root='./web/static/html')
    if case == '2':
        return static_file("plane_eta_same.html", root='./web/static/html')


@route('/app/<controller>/<action>', method='GET')
def process_apps(controller, action):
    return Dispatcher.dispatch(controller, action)


if __name__ == "__main__":
    # Interactive mode
    Dispatcher.register_ctrl_list(Controllers)
    TEMPLATE_PATH.append('./web/static/views')

    run(host='localhost', port=9001)


else:
    # Mod WSGI launch
    # os.chdir(os.path.dirname(__file__))
    Dispatcher.register_ctrl_list(Controllers)
    os.chdir(os.path.dirname(module_path(main)))
    application = default_app()

