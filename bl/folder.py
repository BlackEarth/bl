
import glob, logging, os
from .file import File

log = logging.getLogger(__name__)

class Folder(File):
    
    def __truediv__(self, other):
        return Folder(fn='/'.join([self.fn, str(other)]))

    def glob(self, pattern):
        results = [File(r) for r in glob.glob(str(Folder(self / pattern)))]
        for i in range(len(results)):
            if results[i].isdir: results[i] = Folder(results[i])
        return results
