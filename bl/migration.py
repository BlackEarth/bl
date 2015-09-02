
import os
from glob import glob
from bl.model import Model

class Migration(Model):
    relation = 'migrations'
    pk = ['id']

    @classmethod
    def create_id(M, filename):
        return os.path.basename(os.path.splitext(filename)[0])

    @classmethod
    def migrate(M, db, migrations_path=None, log=print):
        "update the database with unapplied migrations"
        migrations_path = migrations_path or db.config.Database.migrations
        try:
            # will throw an error if this is the first migration -- migrations table doesn't yet exist.
            migrations_ids = [r.id for r in M(db).select()]
        except:
            migrations_ids = []
        fns = [fn for fn 
                in glob(os.path.join(migrations_path, "*.*")) 
                if M.create_id(fn) not in migrations_ids]
        log("[%s]" % log.timestamp(), "Migrate Database: %d migrations" % len(fns))
        for fn in fns:
            id = M.create_id(fn)
            ext = os.path.splitext(fn)[1]
            if id in migrations_ids: 
                continue
            else:
                f = open(fn, 'r'); script = f.read(); f.close()
                description = script.split("\n")[0].strip('-#/*; ') # first line is the description
                log(' ', id+ext, ':', description)
                cursor = db.cursor()
                if ext=='.sql':                                     # script is a SQL script, db.execute it
                    db.execute(script, cursor=cursor)
                else:                                               # script is system script, subprocess it
                    subprocess.check_output(script, {'db': db})
                migration = M(db, id=id, description=description)
                migration.insert(cursor=cursor)
                cursor.connection.commit()
                cursor.close()