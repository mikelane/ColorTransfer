#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
An adapter for the SQLite3 database so that the ShowerThoughtBot class can
make pythonic calls rather than database calls.
"""

__author__ = 'Mike Lane (http://www.github.com/mikelane/'
__copyright__ = 'Copyright (c) 2015 Mike Lane'
__license__ = 'GPLv3'

from dbmanager import DBManager


class DBAdapter:
    def __init__(self, file):
        self.file = file
        self.create_database()

    def create_database(self):
        with DBManager(self.file) as c:
            c.execute('''
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY,
  username TEXT UNIQUE,
  password TEXT,
  source_image TEXT,
  target_image TEXT,
  result_image TEXT
  );
'''
                      )

    def user_exists(self, username):
        with DBManager(self.file) as c:
            c.execute('''
SELECT username FROM users
WHERE username = ?
            ''',
                      (username,))
            if c.fetchone():
                return c.fetchone()[0]
            else:
                return None

    def register_user(self, username, password):
        with DBManager(self.file) as c:
            c.execute('''
INSERT INTO users (username, password) VALUES (?, ?)
            ''',
                      (username, password))
            # Verify the user made it into the database
            return self.user_exists(username)

    def login_user(self, username, password):
        with DBManager(self.file) as c:
            c.execute('''
select username from users
where username = ? and password = ?;
            ''',
                      (username, password))
            return c.fetchone()

    def remove_image(self, column, username):
        with DBManager(self.file) as c:
            c.execute('''
UPDATE users
SET {} = ?
WHERE username = ?'''.format(column),
                      ('', username))

    def store_image_fn(self, column, filename, username):
        with DBManager(self.file) as c:
            c.execute('''
UPDATE users
SET {} = ?
WHERE username = ?'''.format(column),
                      (filename, username))

    def get_image_fn(self, column, username):
        with DBManager(self.file) as c:
            c.execute('''
SELECT {} FROM users
WHERE username = ?;
            '''.format(column),
                      (username,))
            try:
                return c.fetchone()[0]
            except TypeError:
                return None
