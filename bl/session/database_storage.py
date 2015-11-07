
DEBUG = False

import json

from bl.session import Session, SessionStorage

class DatabaseStorage(SessionStorage):
    """Database storage of sessions.
        init with a DB-API 2.0 db connection.

    Example Session (uses an in-memory sqlite database for storage)
    >>> from bl.database import Database
    >>> db = Database()                             
    >>> db.execute('''create table sessions (id varchar primary key, data text)''')
    >>> st = DatabaseStorage(db.connection)
    >>> s = Session(st, name='sah')
    >>> s
    {'name': 'sah'}
    >>> s.save()
    >>> s1 = Session.load(st, s.id)
    >>> s1
    {'name': 'sah'}
    >>> s2 = Session.load(st, 'nonexistentid')
    >>> s2
    {}
    >>> s2.id == 'nonexistentid'
    False
    >>> st.delete(s.id)
    >>> s3 = Session.load(st, s.id)
    >>> s3 == {} and s3.id != s.id and s3.id != None
    True
    >>> db.execute("drop table sessions")
    """

    def __init__(self, dbconn, table='sessions', idfield='id', datafield='data', **args):
        self.dbconn = dbconn
        self.table = table
        self.idfield = idfield
        self.datafield = datafield

    def load(self, sessionid=None):
        c = self.dbconn.cursor()
        c.execute("select %s from %s where %s='%s' limit 1" % (self.datafield, self.table, self.idfield, sessionid))
        res = c.fetchone()
        c.close()
        if res:
            sdata = json.loads(res[0])
            s = Session(self)
            s.update(**sdata)
            s.id = sessionid
            return s
        else:
            return Session(self)

    def save(self, session):
        sdata = json.dumps(session)
        c = self.dbconn.cursor()
        try:
            c.execute("delete from %s where %s='%s'" % (self.table, self.idfield, session.id))
            c.execute("insert into %s (%s, %s) values ('%s', '%s')" % (self.table, self.idfield, self.datafield, session.id, sdata))
            self.dbconn.commit()
        except:
            self.dbconn.rollback()
            raise
        c.close()

    def delete(self, sessionid):
        c = self.dbconn.cursor()
        try:
            c.execute("delete from %s where %s='%s'" % (self.table, self.idfield, sessionid))
            self.dbconn.commit()
        except:
            self.dbconn.rollback()
            raise
        c.close()


if __name__ == "__main__":
    import doctest
    doctest.testmod()
