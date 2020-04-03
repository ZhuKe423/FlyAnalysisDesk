#!/usr/bin/env python3
#coding:utf-8

# 导入pymysql模块
import pymysql

# 连接database

import threading

MYSQL_HOST = 'localhost'
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'mczk@423'
MYSQL_PORT = 3306
DATABASE = 'aman_1'
lock = threading.Lock()


class MysqlConn:
    def __init__(self, host=MYSQL_HOST, username=MYSQL_USER, password=MYSQL_PASSWORD, port=MYSQL_PORT,
                 database=DATABASE):
        """
        mysql 初始化
        :param host:
        :param username:
        :param password:
        :param port:
        """
        try:
            self.db = pymysql.Connection(host=host, user=username, password=password,
                                         database=database, port=port)
            self.cursor = self.db.cursor(cursor=pymysql.cursors.DictCursor)  # TODO 最主要的一行。。。
        except pymysql.MySQLError as e:
            print(e.args)

    def create_table(self, table, fieldsAttr):
        '''
        :param table:
        :param fieldsAttr: [{name:xxx, type='INT', auto_increment:true, pri_key: true, notnull: true, unique: true}]
        :return:
        '''
        #print(fieldsAttr)
        fields = ''
        key = ''
        for field in fieldsAttr:
            fields = '%s %s %s' % (fields, field['name'], field['type'])
            fields = fields + (' ' + 'auto_increment' if field['auto_increment'] is True else '')
            fields = fields + (' ' + 'PRIMARY KEY' if field['pri_key'] is True else '')
            fields = fields + (' ' + 'NOT NULL' if field['notnull'] is True else '')
            fields = fields + (' ' + 'UNIQUE' if field['unique'] is True else '')
            fields = fields + ','
            #key = key + ('' if 'key' not in field else " KEY '%s' ('%s')," % (field['key'], field['name']))
        sql = "CREATE TABLE IF NOT EXISTS `%s`(%s)ENGINE=InnoDB DEFAULT CHARSET=utf8;" % (table, fields[:-1])
        print(sql)
        try:
            self.cursor.execute(sql)
            self.db.commit()
        except pymysql.MySQLError as e:
            print(e.args)
            #self.db.rollback()
            return

    def debug(self, table, data):
        print("table : %s" % table)

    def insert(self, table, data):
        keys = ', '.join(data.keys())
        values = ', '.join(['%s'] * len(data))
        sql = 'insert into %s (%s) values (%s)' % (table, keys, values)
        try:
            self.cursor.execute(sql, tuple(data.values()))
            self.db.commit()
        except pymysql.MySQLError as e:
            print(e.args)
            self.db.rollback()

    def insert_many(self, table, data):
        if isinstance(data, list) or isinstance(data, tuple):
            keys = str(tuple(data[0].keys())).replace('(', '').replace(')', '').replace("'", '')
            sql = 'insert into %s (%s) value' % (table, keys) + ' (' + '%s, ' * (len(data[0].keys()) - 1) + '%s);'
            values = [tuple(d.values()) for d in data]
            #print(values)
            if lock.acquire():
                try:
                    self.cursor.executemany(sql, values)
                    self.db.commit()
                except pymysql.MySQLError as e:
                    print(e.args)
                    self.db.rollback()
                finally:
                    lock.release()

    def find_key_val(self, table, key_val):
        sql = None
        if isinstance(key_val, str):
            sql = 'SELECT * FROM `%s` WHERE %s ;' % (table, key_val)
        elif isinstance(key_val, dict):
            sql_where = ''
            for item in key_val.items():
                row_str = str(item[0]) + '="' + str(item[1]) + '" and '
                sql_where += row_str
            sql_where = sql_where[:-4]
            sql = 'SELECT * FROM `%s` WHERE %s ;' % (table, sql_where)
            #print(sql)
        if sql:
            try:
                self.cursor.execute(sql)
                data = self.cursor.fetchall()
                if len(data) > 0:
                    return data
                return None
            except pymysql.MySQLError as e:
                print(e.args)
        return None

    def find_by_sql(self, sql):
        if sql:
            try:
                self.cursor.execute(sql)
                data = self.cursor.fetchall()
                if len(data) > 0:
                    return data
                return None
            except pymysql.MySQLError as e:
                print(e.args)
        return None

    def del_by_sql(self, sql):
        if sql:
            try:
                self.cursor.execute(sql)
                self.db.commit()
                return True
            except pymysql.MySQLError as e:
                print(e.args)
                self.db.rollback()
        return None

    def update_by_sql(self, sql):
        if sql:
            try:
                self.cursor.execute(sql)
                self.db.commit()
                return True
            except pymysql.MySQLError as e:
                print(e.args)
                self.db.rollback()
        return None

    def close(self):
        try:
            self.cursor.close()
        except:
            pass
        try:
            self.db.close()
        except:
            pass


#mysqlHandler = MysqlConn()

if __name__ == '__main__':
    fields = [
            {'name': 'id', 'type': 'INT', 'auto_increment': True, 'pri_key': True, 'notnull': False, 'unique': False},
            {'name': 'callsign', 'type': 'CHAR(10)', 'auto_increment':False, 'pri_key': False, 'notnull': True, 'unique': False}
        ]
    mysqlHandler.create_table('zk_test', fields)
    #result = mc.find_by_sql('select * from tst;')
    #print(result)

