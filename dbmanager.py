#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
A super convenient method of managing the database connection when paired
with python's context feature. https://www.python.org/dev/peps/pep-0343/
"""

__author__ = 'Mike Lane (http://www.github.com/mikelane/'
__copyright__ = 'Copyright (c) 2015 Mike Lane'
__license__ = 'GPLv3'

import sqlite3


class DBManager:
    """Manage the opening and closing of the sqlite3 database. Use python3
    contexts ("with" syntax) to automatically open the database, create the
    cursor and then commit the changes and close the database.
    """
    def __init__(self, file):
        self.file = file
        self.conn = None
        self.cursor = None

    def __enter__(self):
        self.conn = sqlite3.connect(self.file, check_same_thread=True)
        # Define and return the cursor to the context
        self.cursor = self.conn.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.commit()
        self.conn.close()
