"""
A simple relational database interface that stays out of your way.
Designed to be small, fast, and transparent. Integrates with user-defined record classes.

* Record:     base class for user-defined Record classes (inherits from bl.dict.Dict)
* RecordSet:  set of Records (inherits from list)
* Database :  a database connection
                (init with a standard DB-API 2.0 connection string)

---------------------------------------------------------------------------
                                            Memory:  Footprint:
# > python                                  4656 K   4656 K (Python 3.4.3 osx)
# >>> from bl.database import Database   5460 K    804 K (YMMV)
---------------------------------------------------------------------------
Sample session: 
>>> d = Database()      # in-memory sqlite3 database
>>> d.execute("create table table1 (name varchar primary key, email varchar not null unique)")
>>> d.execute("insert into table1 (name, email) values ('sah', 'sah@blackearthgroup.com')")
>>> records = d.select("select * from table1")
>>> records[0].name
'sah'
>>> d.connection.close()
>>>
"""

import datetime, imp, re, time
from bl.dict import Dict

class Database(Dict):
    """a database connection object."""

    def __init__(self, connection_string=None, dba=None, tries=3, dbconfig=None, debug=False, **args):
        Dict.__init__(self, 
            connection_string=connection_string or (dbconfig and dbconfig.connection_string) or '', 
            dba=dba or imp.load_module('sqlite3', *imp.find_module('sqlite3')), 
            dbconfig=dbconfig, 
            DEBUG=debug or (dbconfig and dbconfig.debug) or None,
            **args)
        if self.dba is None:
            import sqlite3 as dba
        elif type(self.dba) in (str, bytes):
            self.dba = imp.load_module(imp.find_module(dba), fm[0], fm[1], fm[2])
        if self.dba.__name__ == 'psycopg2':
            # make psycopg2 always return unicode strings
            try:
                dba.extensions.register_type(dba.extensions.UNICODE)
                dba.extensions.register_type(dba.extensions.UNICODEARRAY)                    
            except:
                # if that didn't work for some reason, then just go with the default setup.
                pass
            
        # try reaching the db "tries" times, with increasing wait times, before raising an exception.
        for i in range(tries):
            try: 
                if self.connection_string != None:
                    self.connection = self.dba.connect(self.connection_string)
                else:
                    self.connection = self.dba.connect(**args)
                break
            except: 
                if i==list(range(tries))[-1]:       # last try failed
                    raise
                else:                               # wait a bit
                    time.sleep(2*i)
        if self.dba.__name__ == 'sqlite3':
            self.execute("pragma foreign_keys = ON")

    def __repr__(self):
        return "Database(dba=%s, connection_string='%s')" % (self.dba.__name__, self.connection_string)

    def cursor(self):
        """get a cursor for fine-grained transaction control."""
        cursor = self.connection.cursor()
        return cursor

    def execute(self, sql, vals=None, cursor=None):
        """execute SQL transaction, commit it, and return nothing. If a cursor is specified, work within that transaction."""
        try:
            c = cursor or self.connection.cursor()
            if vals in [None, (), [], {}]:
                c.execute(sql)
            else:
                c.execute(sql, vals)
            if cursor is None:
                self.commit()
        except:
            self.rollback()
            raise

    def commit(self):
        """commit the changes on the current connection."""
        self.connection.commit()

    def rollback(self):
        """rollback the changes on the current connection, aborting the transaction."""
        self.connection.rollback()

    def select(self, sql, vals=None, Record=None, RecordSet=None, cursor=None):
        """select from db and return the full result set.
        Required Arguments:
            sql: the SQL query as a string
        Optional/Named Arguments
            vals: any bound variables
            Record: the class (itself) that the resulting records should be
        """
        if self.DEBUG == True: print("==SELECT:==\n", sql)
        c = cursor or self.cursor()
        self.execute(sql, vals=vals, cursor=c)

        if Record is None:
            from .record import Record
        if RecordSet is None:
            from .recordset import RecordSet

        # get a list of attribute names from the cursor.description
        attr_list = list()
        for r in c.description:
            attr_list.append(r[0])

        records = RecordSet()                   # Populate a RecordSet (list) with the all resulting
        results = c.fetchall()
        for result in results:
            record = Record(self)               # whatever the record class is, include another instance
            for i in range(len(attr_list)):     # make each attribute dict-able by name
                record[attr_list[i]] = result[i]
            records.append(record)                 # append the instance to the RecordSet

        if cursor is None:
            c.close()   # closing the cursor without committing rolls back the transaction.
        return records

    def select_one(self, sql, vals=None, Record=None, cursor=None):
        """select one record from db
        Required Arguments:
            sql: the SQL query as a string
        Optional/Named Arguments:
            vals: any bound variables
            Record: the class (itself) that the resulting records should be
        """
        c = cursor or self.cursor()
        self.execute(sql, vals, cursor=c)

        if Record is None:
            from .record import Record

        # get a list of attribute names from the cursor.description
        attr_list = list()
        for r in c.description:
            attr_list.append(r[0])
        result = c.fetchone()
        if result is None:
            record = None
        else:
            record = Record(self)
            for i in range(len(attr_list)):
                record[attr_list[i]] = result[i]
        if cursor is None:
            c.close()
        return record

    def quote(self, attr):
        """returns the given attribute in a form that is insertable in the insert() and update() methods."""
        t = type(attr)
        if t == type(None): return 'NULL'
        elif t == datetime.datetime:    # datetime -- put it in quotes
            return "'%s'" % str(attr)
        elif t == str:
            return self._quote_str(attr)
        elif t in [dict, Dict]:
            return "$$%s$$" % attr
        else:                           # boolean or number -- no quoting needed
            return str(attr).lower()

    def _quote_str(self, attr):
        """quote the attr string in a manner fitting the Database server, if known."""
        sn = self.servername().lower()
        if 'sqlserver' in sn or 'sqlite' in sn:
            # quote for sqlserver and sqlite: double '' to escape
            attr = "'" + re.sub("'", "''", attr) + "'"
        elif 'postgres' in sn:
            if type(attr) == str:
                attr = "$$%s$$" % attr
        else:
            if type(attr) == str:
                attr = "'%s'" % attr
            else:
                attr = "'%s'" % str(attr, 'UTF-8')
        return attr

    def servername(self):
        """return a string that describes the database server being used"""
        if 'psycopg' in self.dba.__name__: 
            return 'postgresql'
        elif 'sqlite' in self.dba.__name__: 
            return 'sqlite'
        elif self.dbconfig is not None and self.dbconfig.server is not None:
            return self.dbconfig.server
        elif 'adodbapi' in str(self.connection): 
            return 'sqlserver'
        elif 'port=5432' in str(self.connection): 
            return 'postgresql'
        elif 'port=3306' in str(self.connection): 
            return 'mysql'
        else: 
            return ''
        
    def table_exists(self, table_name):
        sn = self.servername().lower()
        if 'sqlite' in sn:
            return self.select_one(
                "select * from sqlite_master where name=? and type='table' limit 1", (table_name,))
        elif 'mysql' in sn:
            return self.select_one(
                "show tables like %s", (table_name,))
        else:   
            # postgresql and sqlserver both use the sql standard here.
            return self.select_one(
                "select * from information_schema.tables where table_name=%s limit 1", (table_name,))

def doctests():
    """doctests for the bl.db module
    >>> d = Database()
    >>> d.execute("create table table1 (name varchar primary key, email varchar not null unique);")
    >>> d.execute("insert into table1 (name, email) values ('sah', 'sah@tyndale.com')")
    >>> d.execute("insert into table1 (name, email) values ('sah', 'harrison@tbc.net')")
    Traceback (most recent call last):
      ...
    sqlite3.IntegrityError: UNIQUE constraint failed: table1.name
    """

if __name__ == "__main__":
    import doctest
    doctest.testmod()