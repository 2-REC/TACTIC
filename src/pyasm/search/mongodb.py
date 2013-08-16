###########################################################
#
# Copyright (c) 2013, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#


__all__ = ['MongoDbConn', 'MongoDbImpl']

from pyasm.common import Environment, SetupException, Config, Container, TacticException

from database_impl import DatabaseImplException, DatabaseImpl

import bson

try:
    import pymongo
except ImportError, e:
    pass



class MongoDbConn(object):
    '''A wrapper class around a MongoDb connection to conform to the interface
    required by the Sql class'''


    def __init__(my, database_name):
        my.database_name = database_name

        my.client = pymongo.MongoClient()
        my.conn = my.client[database_name]


    def get_client(my):
        return my.client

    def get_collection(my, table):
        return my.conn[table]


    def cursor(my):
        return {}

    def connect(my):
        pass

    def commit(my):
        pass

    def rollback(my):
        pass

    def close(my):
        pass
        #my.client.disconnect()






class MongoDbImpl(DatabaseImpl):


    def get_columns(cls, db_resource, table):
        from pyasm.search import DbResource, DbContainer
        sql = DbContainer.get(db_resource)
        conn = sql.get_connection()
        collection = conn.get_collection(table)

        result = collection.find_one()
        if not result:
            return ['_id']
        else:
            columns = result.keys()
            columns.remove("_id")
            columns.insert(0, "_id")
            return columns


    def get_column_info(cls, db_resource, table, use_cache=True):

        #info_dict = {'data_type': data_type, 'nullable': is_nullable, 'size': size}

        columns = cls.get_columns(db_resource, table)
        info_dict = {}
        for column in columns:
            info_dict[column] = {}
        return info_dict


    def get_table_info(my, database):

        print "database: ", database

        from pyasm.search import DbResource, DbContainer
        sql = DbContainer.get(database)
        conn = sql.get_connection()
        collections = conn.collection_names()

        table_info = {}
        for collection in collections:
            table_info[collection] = {
            }

        return table_info


    def table_exists(my, db_resource, table):
        return True


    def has_savepoint(my):
        return False


    def has_sequences(my):
        return False



    def build_filters(cls, filters):
        # interpret the assmebled filter data
        nosql_filters = {}
        for filter in filters:
            column = filter.get("column")
            value = filter.get("value")
            op = filter.get("op")

            if column == "_id" and value not in [-1, '-1']:
                value = bson.ObjectId(value)

            if op == "=":
                nosql_filters[column] = value
            else:
                if op == "<":
                    mongo_op = "$lt"
                elif op == ">":
                    mongo_op = "$gt"
                elif not op:
                    pass
                else:
                    raise Exception("Filter operator [%s] is not supported" % op)
                if not op:
                    nosql_filters[column] = value
                else:
                    nosql_filters[column] = {mongo_op: value}

        return nosql_filters
    build_filters = classmethod(build_filters)



    def execute_query(my, sql, select):
        '''Takes a select object and operates
        
        NOTE: this requires a lot of internal knowledge of the Select object 
        '''
        conn = sql.get_connection()

        # select data
        table = select.tables[0]
        filters = select.raw_filters
        order_bys = select.order_bys

        collection = conn.get_collection(table)

        nosql_filters = my.build_filters(filters)
        cursor = collection.find(nosql_filters)

        select.cursor = cursor

        if order_bys:
            sort_list = []
            for order_by in order_bys:
                parts = order_by.split(" ")
                order_by = parts[0]
                if len(parts) == 2:
                    direction = parts[1]
                else:
                    direction = "asc"

                if direction == "desc":
                    sort_list.append( [order_by, -1] )
                else:
                    sort_list.append( [order_by, 1] )

                cursor.sort(sort_list)

        results = []
        for result in cursor:
            results.append(result)

        return results


    def execute_update(my, sql, update):
        conn = sql.get_connection()

        # select data
        table = update.table
        data = update.data
        filters = update.raw_filters

        collection = conn.get_collection(table)
        nosql_filters = my.build_filters(filters)
        item = collection.find_one(nosql_filters)


        result = collection.update( {'_id': item.get('_id')}, {'$set': data} )
        print "result: ", result

        err = result.get("err")
        if err:
            raise Exception(result)

        sql.last_row_id = item.get("_id")





    def execute_insert(my, sql, update):

        conn = sql.get_connection()

        # select data
        table = update.table
        data = update.data

        if data.get("_id") in ["-1", -1]:
            del(data['_id'])

        collection = conn.get_collection(table)

        object_id  = collection.insert(data)

        sql.last_row_id = object_id




