#!/usr/bin/env python3
#coding:utf-8

from threading import Timer


class RepeatingTimer(Timer):
    def run(self):
        while not self.finished.is_set():
            self.function(*self.args, **self.kwargs)
            self.finished.wait(self.interval)


class MultiTimerHandler(object):
    def __init__(self):
        self.timerPool = []
        self.timerCount = 0

    def new_timer(self, interval, func, *args, **kwargs):
        self.timerPool.append(RepeatingTimer(interval, func, *args, **kwargs))
        self.timerCount += 1

    def start_all(self):
        for timer in self.timerPool:
            timer.start()

    def cancel_all(self):
        for timer in self.timerPool:
            timer.cancel()


TimerHandler = MultiTimerHandler()

