
import json, os, shutil, tempfile
from bl.file import File
from bl.dict import Dict

class JSON(File):

    def __init__(self, fn=None, data=None, **args):
        File.__init__(self, fn=fn, **args)
        if data is not None:
            self.data = json.loads(self.read())

    def read(self):
        return File.read(self, mode='r')

    def write(self, fn=None, data=None, indent=None, **args):
        File.write(self, 
            fn=fn or self.fn, 
            data=json.dumps(data or self.data, indent=indent).encode('utf-8'), 
            **args)
        
