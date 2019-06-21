#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import mysql.connector

class Supertrack():
    
    def __init__(self):
        
        self.user = 'supertrack'
        self.password = 'supertrack2013'
        self.host = '10.200.129.100'
        self.port = 3306

    def connect_to_sql(self):
        """Connects to sql"""
        self.con = mysql.connector.connect(user=self.user, 
                                           password=self.password,
                                           host=self.host,
                                           port=self.port,
                                           db="")
    def close_connetion(self):
        """Close connection to sql"""
        self.con.close()
        self.con = None
    
    def get_df_from_qry(self, qry):
        
        df = pd.DataFrame()
        self.connect_to_sql()
        try:
            df = pd.read_sql(qry, con=self.con)
        finally:
            self.close_connetion()
            return df
            