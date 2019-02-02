import glob, logging, os
import bl.rglob
from .file import File

log = logging.getLogger(__name__)


class Folder(File):
    def __truediv__(self, other):
        """enable the use of / as an operator to build paths"""
        fn = '/'.join([self.fn, str(other)])
        if os.path.isfile(fn):
            return File(fn=fn)
        else:
            return Folder(fn=fn)

    def glob(self, pattern, folders=True):
        results = [
            file
            for file in [File(r) for r in glob.glob(str(Folder(self / pattern)))]
            if folders is True or not file.isdir
        ]
        for i in range(len(results)):
            if results[i].isdir:
                results[i] = Folder(results[i])
        return results

    def rglob(self, pattern, **kwargs):
        return [
            Folder(r) if os.path.isdir(r) else File(r)
            for r in bl.rglob.rglob(self.fn, pattern, **kwargs)
        ]
