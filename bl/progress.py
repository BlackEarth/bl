
import inspect, os
from time import time
from bl.dict import Dict
from bl.json import JSON

class Progress(JSON):
	"""tabulate progress statistics for given processes, and report the progress of those processes"""
	
	def __init__(self, fn=None, data=None):
		# JSON.__init__() loads the stored progress data from the given .json file
		super().__init__(fn=fn, data=data)
		if self.data is None: self.data = Dict()
		# self.current stores start times for current stack processes.
		self.current = Dict()

	def start(self, key=None):
		"""initialize process timing for the current stack"""
		key = key or self.stack_key
		self.current[key] = time()

	def runtime(self, key):
		if self.data.get(key) is not None:
			return sum(self.data[key]) / len(self.data[key])

	def report(self, fraction=None):
		"""report the total progress for the current stack, optionally given the local fraction completed"""
		r = Dict()
		local_key = self.stack_key
		for key in self.stack_keys:
			if self.current.get(key) is None: 
				self.start(key=key)
			runtime = self.runtime(key)
			if key == local_key and fraction is not None:
				r[key] = "%.2f%%" % fraction
			elif runtime is not None:
				r[key] = "%.2f%%" % (100*(time() - self.current[key]) / runtime)
			else:
				r[key] = "%.2fs" % (time() - self.current[key])
		return r

	def finish(self):
		"""record the current stack process as finished"""
		key = self.stack_key
		if self.data.get(key) is None:
			self.data[key] = []
		start_time = self.current.get(key) or time()
		self.data[key].append(time() - start_time)

	def __delete__(self):
		"""save progress stats"""
		if self.fn is not None:
			self.write()
		super().__delete__()

	@property
	def stack_keys(self):
		l = self.stack_key.split(',')
		return list(reversed([','.join(l[:i]) for i in range(1, len(l)+1)]))

	@property
	def stack_key(self):
		return ','.join([
			t.filename+':'+t.function for t in 
			[inspect.getframeinfo(i.frame) for i in inspect.stack()]
			if os.path.abspath(t.filename) != os.path.abspath(__file__)	# omit locations in this file
		])

