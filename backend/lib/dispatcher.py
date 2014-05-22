##
## dispatcher.py
##

##
# Includes
#
# Threading
import threading

class Dispatcher(object):
	def __init__(self, targets=None, nonBlocking=True):
		if not targets or targets is None:
			self._targets = []
		else:
			self._targets = targets
		self._nonBlocking = nonBlocking
	def __iadd__(self, target):
		self._targets.append(target)
		return self
	def __isub__(self, target):
		self._targets.remove(target)
		return self
	def __len__(self):
		return len(self._targets)
	def isNonBlocking(self):
		return self._nonBlocking
	nonBlocking = property(isNonBlocking)
	def __call__(self, *listArgs, **kwArgs):
		def invokeTargets():
			for target in self._targets:
				target(*listArgs, **kwArgs)
		if self.nonBlocking:
			threading.Timer(0, invokeTargets).start()
		else:
			invokeTargets()
