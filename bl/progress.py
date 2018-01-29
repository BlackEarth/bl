
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
		# self.current_times stores start times for current stack processes.
		self.current_times = Dict()
		self.init_key = self.stack_key

	def start(self, key=None):
		"""initialize process timing for the current stack"""
		key = key or self.stack_key
		self.current_times[key] = time()

	def runtime(self, key):
		if self.data.get(key) is not None:
			return sum(self.data[key]) / len(self.data[key])

	def runtimes(self):
		r = Dict()
		for key in self.data.keys():
			r[key] = self.runtime(key)
		return r

	def report(self, fraction=None, runtimes=None):
		"""report the total progress for the current stack, optionally given the local fraction completed.
		fraction=None: if given, used as the fraction of the local method so far completed.
		runtimes=None: if given, used as the expected runtimes for the current stack.
		"""
		r = Dict()
		local_key = self.stack_key
		runtimes = runtimes or self.runtimes()
		for key in self.stack_keys:
			if self.current_times.get(key) is None: 
				self.start(key=key)
			runtime = runtimes.get(key) or self.runtime(key)
			if key == local_key and fraction is not None:
				r[key] = fraction
			elif runtime is not None:
				r[key] = (time() - self.current_times[key]) / runtime
			else:
				r[key] = 0.00
		return r

	def finish(self, runtimes=None):
		"""record the current stack process as finished"""
		self.report(fraction=1.0, runtimes=runtimes)
		key = self.stack_key
		if self.data.get(key) is None:
			self.data[key] = []
		start_time = self.current_times.get(key) or time()
		self.data[key].append(time() - start_time)

	def __delete__(self):
		"""save progress stats"""
		if self.fn is not None:
			self.write()
		super().__delete__()

	@property
	def stack_keys(self):
		l = self.stack_key.split(',')
		return [','.join(l[:i]) for i in range(1, len(l)+1)]

	@property
	def stack_key(self):
		return ','.join(list(reversed([
			t.filename+':'+t.function for t in 
			[inspect.getframeinfo(i.frame) for i in inspect.stack()]
			if os.path.abspath(t.filename) != os.path.abspath(__file__)	# omit locations in this file
			and t.function != '<module>'
			and 'runpy.py' not in t.filename
		])))

