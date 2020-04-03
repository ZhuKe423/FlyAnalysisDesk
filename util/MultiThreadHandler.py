#!/usr/bin/env python3
#coding:utf-8

import queue
import argparse
import threading
import time


class MultiThreadHandler(object):
    def __init__(self):
        self.thread_pool = []
        self.thread_count = 0

    def create_task(self, task_name, task_func, task_queue, result_queue=None, **kwargs):
        thread = {
            'name': task_name,
            'runing': False,
            'handler': _TaskHandler(task_name, task_queue, task_func, result_queue, **kwargs)
        }
        self.thread_pool.append(thread)
        self.thread_count += 1

    def run_all(self):
        for th in self.thread_pool:
            th['runing'] = True
            th['handler'].setDaemon(True)
            th['handler'].start()

    def thread_checker(self):
        while self._check_stop():
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                print('KeyboardInterruption')
                self.stop_all()
                break
        print('>>>all Done')

    def _check_stop(self):
        """检查线程池中所有线程是否全部运行完"""
        finish_num = 0
        for th in self.thread_pool:
            if not th['handler'].isAlive():
                finish_num += 1

        return False if finish_num == len(self.thread_pool) else True

    def stop_all(self):
        """掉用线程体stop方法，停止所有线程"""
        for th in self.thread_pool:
            th['handler'].stop()


class _TaskHandler(threading.Thread):
    def __init__(self, task_name, task_queue, task_handler, result_queue=None, **kwargs):
        threading.Thread.__init__(self)
        self.name = task_name
        self.task_queue = task_queue
        self.task_handler = task_handler
        self.result_queue = result_queue
        self.kwargs = kwargs
        self.is_running = False

    def get_name(self):
        return self.name

    def get_i_queue(self):
        return self.task_queue

    def get_o_queue(self):
        return self.result_queue

    def run(self):
        self.is_running = True
        while self.is_running:
            try:
                #print("%s: running!" % self.name)
                if self.task_queue is not None:
                    item = self.task_queue.get(True)  # block= False
                    self.task_handler(self, item, self.result_queue, **self.kwargs)
                    self.task_queue.task_done()  # 退出queue
                else:
                    self.task_handler(self, **self.kwargs)

            except queue.Empty as e:
                print("%s task has done!" % self.name)
                break
            except Exception as e:
                print("%s error _T:" % self.name, e)
                # time.sleep(1)

    def stop(self):
        self.is_running = False


ThreadHandler = MultiThreadHandler()


def out(task, item, o, **kwargs):  # 加载处理函数
    print("out:: {}: process {}".format(task.get_name(), item))
    if kwargs is not None and len(kwargs) > 0:
        print(kwargs)
    if task.get_o_queue() is not None:
        task.get_o_queue().put(item)


if __name__ == "__main__":
    name = "Thread#1-"
    name1 = "Thread#2-"
    name2 = "Thread#3-"
    queue1 = queue.Queue()
    queue2 = queue.Queue()
    queue3 = queue.Queue()
    queue4 = queue.Queue()

    ThreadHandler.create_task(name, out, queue1, queue2, b="testString")
    ThreadHandler.create_task(name1, out, queue2, queue3)
    ThreadHandler.create_task(name2, out, queue3, queue4)

    for i in range(20):
        queue1.put("_%d_" % i)
    ThreadHandler.run_all()

    while True:
        print("Final: %s" % queue4.get(True, timeout=300))
        queue4.task_done()
        if queue4.empty():
            break
    ThreadHandler.thread_checker()
    print("end")
