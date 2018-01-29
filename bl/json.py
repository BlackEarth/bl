
import os, json
from bl.file import File

class JSON(File):
	
	def __init__(self, fn=None, data=None):
		super().__init__(fn=fn, data=data)
		if self.data is None and os.path.exists(self.fn):
			self.data = self.read()
		if self.data is not None:
			self.data = json.loads(self.data)

	def write(self, fn=None, data=None, indent=2):
		fn = fn or self.fn
		data = data or json.dumps(self.data, indent=indent)
		super().write(fn=fn, data=data.encode('utf-8'))
