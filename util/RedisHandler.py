#!/usr/bin/env python3
#coding:utf-8

import redis
import json

HOST = 'localhost'
PORT = 6379
PASSWORD = '123456'
DBNUM = 5


class RedisHandler:
    def __init__(self, host=HOST, port=PORT, pwd=PASSWORD):
        self.pool = redis.ConnectionPool(host=host, port=port, db=5, password=pwd, decode_responses=True)
        self.r = redis.Redis(connection_pool=self.pool)

    def append_one_list(self, table, value):
        self.r.rpush(table, value)

    def get_list(self, table):
        return self.r.lrange(table, 0, -1)

    def set_dicts_list(self, table, dict_list, index_key):
        for item in dict_list:
            if index_key in item:
                key = "{}#{}".format(index_key, item[index_key])
                self.r.hset(table, key, json.dumps(item))
                # self.append_one_list("{}#List".format(table), key)
            else:
                print("One item didn't have the index_key")

    def set_one_dict_in_list(self, table, index_key, item):
        key = "{}#{}".format(index_key, item[index_key])
        self.r.hset(table, key, json.dumps(item))

    def del_on_dict_in_list(self, table, index_key, value):
        key = "{}#{}".format(index_key, value)
        print("del_on_dict_in_list： {}".format(key))
        self.r.hdel(table, key)

    def get_dict_list(self, table):
        content = self.r.hgetall(table)
        dict_list = []
        for key, value in content.items():
            dict_list.append(json.loads(value))
        return dict_list

    def get(self, table):
        value = self.r.get(table)
        if value is not None:
            return json.loads(value)
        else:
            return None

    def set(self, table, value):
        return self.r.set(table, json.dumps(value))

    def delete_all(self):
        return self.r.flushdb()


if __name__ == '__main__':
    r_h = RedisHandler()
    airplane = []
    for i in range(5):
        airplane.append({"callsign": "Plane_%d" % i, "X": 234324, "Y": 34534, "speed": i})
    r_h.set_dict_list('AirPlaneRadar', airplane, 'callsign')

    data = r_h.get_dict_list('AirPlaneRadar')
    print(data)

