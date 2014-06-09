##
## util.py
##

##
# Includes
#
# General
import time
# Hashing with controller code
import pickle
# Logging
from messaging import stdMsg, dbgMsg, errMsg, setDebugging
# Cache
from lib.cache import Cache


class Util:
	def __init__(self):
		# Initialize variables
		libCache = Cache()
		self._libDB = libCache.get('libDB')
		self._dbUserList = libCache.get('dbUserList')

	def checkTimeout(self, sTime, bTimeout):
		# check timestamp timestr against current time and timeout
		# return True if we have not timed out yet
		try:
			bYear     = int(sTime[0:4])
			bMonth    = int(sTime[4:6])
			bDay      = int(sTime[6:8])
			bHour     = int(sTime[8:10])
			bMinute   = int(sTime[10:12])
			bSecond   = int(sTime[12:14])
			bDaylight = time.localtime()[8]

			bThen = int(time.mktime((bYear, bMonth, bDay, bHour, bMinute, bSecond, 0, 0, bDaylight)))
			bNow = int(time.time())
			bTimeout = int(bTimeout) * 60

			if bNow - bThen > bTimeout:
				return False

			return True

		except Exception, e:
			errMsg('cannot convert time [%s] to int [%s]' % (sTime, e))
			return False

	def hashPassword(self, sPass):
		try:
			# Call underlying password func for mysql
			rgoResult = self._libDB.query('SELECT PASSWORD(%s)', sPass)
			if len( rgoResult ) != 0:
				return (True, rgoResult[0][0])
			return (False, '')

		except Exception, e:
			errMsg('cannot get password hash from mysql [%s] [%s]' % (sPass, e))
			return (False, '')

	def hashObject(self, o):
		try:
			# return an md5 hash of the object serialized as a string
			try:
				import hashlib
				m = hashlib.md5()
			except ImportError:
				import md5
				m = md5.new()

			m = md5.new()
			m.update(pickle.dumps(o))
			return m.hexdigest()

		except Exception, e:
			errMsg('cannot hash object [%s]' % e)
			return ''

	def logMsg(self, sMsg, sUser=''):
		""" Log msg into database. """

		try:
			bUserID = 0
			if sUser != '':
				bUserID = self._dbUserList.getUser(sName=sUser).getID()

			sTimestamp = time.strftime('%Y%m%d%H%M%S')
			self._libDB.query('INSERT INTO log (timestamp,user_id,message) VALUES (%s,%s,%s)', sTimestamp, bUserID, sMsg)

			return True

		except Exception, e:
			errMsg('error logging message [%s]' % e)
			raise Exception, 'System error while trying to log message.'
