##
## cache.py
##

##
# Includes
#
# Threading
import threading, commands
# Application Modules
from lib.messaging import stdMsg, dbgMsg, errMsg, setDebugging
# Database Handle
from lib.dbutil import DBUtil

class Cache:
	""" Cache object used to store application objects """

	# storage for the instance reference
	__instance = None

	def __init__(self):
		""" Create Singleton instance of our Cache object """

		# Check whether we already have an instance
		if Cache.__instance is None:
			# Create and remember instance
			Cache.__instance = Cache.__impl()

		# Store instance reference as the only member in the handle
		self.__dict__['_Cache__instance'] = Cache.__instance

	def __getattr__(self, attr):
		""" Delegate access to implementation """
		return getattr(self.__instance, attr)

	def __setattr__(self, attr, value):
		""" Delegate access to implementation """
		return setattr(self.__instance, attr, value)

	class __impl:
		""" Implementation of our Cache object """

		def __init__(self):
			# Object Store
			self._rgoStore = {}

			# Setup Global
			rgsGlobal = {}
			self._rgoStore['rgsGlobal'] = rgsGlobal

			# Setup Database Handle
			libDB = DBUtil(sHost='localhost', sUser='root', sPass='lynn1094', sDB='monarch')
			self._rgoStore['libDB'] = libDB
			libDBbug = DBUtil(sHost='localhost', sUser='root', sPass='lynn1094', sDB='bugs')
			self._rgoStore['libDBbug'] = libDBbug

		def get(self, sName):
			""" Return object from our store. """

			if not self._rgoStore.has_key(sName):
				return None
			else:
				return self._rgoStore[sName]

		def set(self, sName, oValue):
			""" Set object in our store.  If oValue is None, then erase. """

			if oValue is None:
				if self._rgoStore.has_key(sName):
					del self._rgoStore[sName]
			else:
				self._rgoStore[sName] = oValue
