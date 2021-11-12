import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix
import time
import os
import pymongo
from datetime import datetime, timedelta

config = {
    'collection' : os.getenv('MONGO_COLLECTION'),
    'dbname' : os.getenv('MONGO_INITDB_DATABASE'),
    'user' : os.getenv('MONGO_INITDB_ROOT_USERNAME'),
    'pass' : os.getenv('MONGO_INITDB_ROOT_PASSWORD'),
    'host' : 'mongo',
    'width': int(os.getenv('HEATMAP_WIDTH')),
    'height': int(os.getenv('HEATMAP_HEIGHT'))
}

conn_str = f"mongodb://{config['user']}:{config['pass']}@{config['host']}:27017/{config['dbname']}"

class DataHolder:
    def __init__(self):
        self.config = config
        self.shape = (self.config['height'], self.config['width'])
        self.timed_data = None
        self.set_connection()
        self.last_time = (datetime.now() - timedelta(0, 60)).isoformat()
        self.update()
        # self.mask = Get from first document of database, or something
        while self.df.empty:
            self.update()

    def set_connection(self):
        self.conn = pymongo.MongoClient(conn_str)
        self.db = self.conn[self.config['dbname']]
        self.col = self.db[self.config['collection']]

    def read_df_from_query(self, query={}):
        cursor = self.col.find(query)
        return pd.DataFrame(list(cursor))

    def generate_csr(self, df):
        return csr_matrix((np.array(df['data']),
                           np.array(df['indices']),
                           np.array(df['indptr'])), shape=self.shape)

    def decode(self, csr):
        return (self.mask*100) + csr.toarray()
        
    def update(self):
        self.df = self.read_df_from_query({"date": {"$gte": self.last_time}})
        if not self.df.empty:
            self.df = self.df.set_index('date')
            self.last_time = self.df.iloc[-1].name

    def get_data_from_date(self, date, delta=1):
        low = (date - timedelta(0, delta)).isoformat()
        high = (date + timedelta(0, delta)).isoformat()
        _tmp = self.read_df_from_query({"date": {"$gte": low, "$lte": high}})
        if _tmp.empty:
            return np.zeros(self.shape), f'{date.isoformat()} NOT FOUND'
        _tmp = _tmp.set_index('date').iloc[-1]
        _tmp = generate_csr(_tmp)
        _tmp = decode(_tmp)
        return _tmp, date.isoformat()

    def get_data_from_date_bunch(self, date, delta=60):
        low = (date - timedelta(0, delta)).isoformat()
        high = (date + timedelta(0, delta)).isoformat()
        _tmp = self.read_df_from_query({"date": {"$gte": low, "$lte": high}})
        if not _tmp.empty:
            _tmp = _tmp.set_index('date')
        self.timed_data = _tmp.iloc[-10:]

    def get_last_data(self):
        _tmp = self.df.iloc[-1]
        _tmp = generate_csr(_tmp)
        _tmp = decode(_tmp)
        return _tmp
