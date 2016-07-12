# dvslog.py
#
# Tony Mendolia
#
# Changelog:
#
# 2009-09-29    Created
#

# Includes
#
# System
import threading, copy
# Logging
from lib.messaging import dbgMsg

# Cache (Object store)
import lib.cache

# Log Event Object
class DVSLogEntry:
	""" 
	DVSLogEntry represents a DVS "dial-out" event
	"""

	def __init__(self, bID=None, bSerial=None, bEventID=None, sData=None, sTimeStamp=None ):
		libCache = lib.cache.Cache()
		self._libUtil = libCache.get('libUtil')

		# Stuff we store in the Database        
		self._bID = bID                   # DVSLogEntry ID Number (For ease in DB operations)
		self._bSerial = bSerial           # Serial number of the DVS
		self._bEventID = bEventID         # Event ID
		self._sData = sData               # Data in Event Message
		self._sTimeStamp = None           # When did we last see this error  

	def getID(self):
		return self._bID

	def setID(self, bID):
		self._bID = bID

	def getSerial(self):
		return self._bSerial

	def setSerial(self, bID):
		self._bID = bSerial

	def getEventID(self):
		return self._bEventID

	def setEventID(self, bEventID):
		self._bEventID = bEventID

	def getData(self):
		return self._sData

	def setData(self, sData):
		self._sData = sData

	def getTimeStamp(self):
		return self._sTimeStamp

	def setTimeStamp(self, sTimeStamp):
		self._sTimeStamp = sTimeStamp



# List of DVSLogEntry Objects and subsequent operations
class DVSLogList:

	def __init__(self):
		self._oLock = threading.RLock()
		libCache = lib.cache.Cache()
		self._libDB = libCache.get('libDB')
		self._libUtil = libCache.get('libUtil')

	def size(self):
		""" Return the number of DVSLogEntrys we have loaded. """
		return len(self._oDVSLogEntries)   

	def getList(self, sTimestamp=None):

		try:
			self._oLock.acquire()

			try:
				# Clear in case of reload
				self._oDVSLogEntries = []

				sQuery = 'SELECT bID, bSerial, bEventID, sData, UNIX_TIMESTAMP(dTimeStamp) FROM DVSLog'
				if sTimestamp is not None:
					sQuery += ' WHERE dTimeStamp>"%s"' % sTimestamp
				sQuery += ' ORDER BY bID'
				rgoResult = self._libDB.query( sQuery )

				if rgoResult is not None:
					for oRow in rgoResult:
						self._oDVSLogEntries.append(
							DVSLogEntry(
								oRow[0],
								oRow[1],
								oRow[2],
								oRow[3],
								oRow[4]
							)
						)

				""" Return list copy of our DVSLogEntry List. """
				return copy.copy(self._oDVSLogEntries)

			except Exception, e:
				raise Exception, 'error loading DVSLogEntry list from database [%s]' % e

		finally:
			self._oLock.release()

	def addDVSLogEntry(self, bSerial, bEventID, sData, sTimeStamp):
		""" Add new DVSLogEntry to the DVSLogEntry List. """

		try:
			self._oLock.acquire()

			try:
				self._libDB.query('INSERT INTO DVSLog (bSerial, bEventID, sData, dTimeStamp) VALUES (%s,%s,%s,FROM_UNIXTIME(%s))',
					bSerial,
					bEventID,
					sData,
					sTimeStamp
				)

				rgoResult = self._libDB.query('SELECT bID FROM DVSLog ORDER BY bID LIMIT 1')

				bID = rgoResult[0][0]

				oDVSLogEntry = self.getDVSLogEntry( bID )
				dbgMsg('added DVSLogEntry id-[%s]' % bID)

				return oDVSLogEntry

			except Exception, e:
				raise Exception, 'error adding DVSLogEntry [%s]' % e

		finally:
			self._oLock.release()

	def delDVSLogEntry(self, oDVSLogEntry):
		""" Delete this DVSLogEntry. """

		try:
			self._oLock.acquire()

			try:

				oDVSLogEntry = self.getDVSLogEntry( bID = oDVSLogEntry.getID )

				if oDVSLogEntry is None:
					dbgMsg( 'delete DVSLogEntry ID-[%d] failed' % oDVSLogEntry.getID() )
					return False

				self._libDB.query('DELETE FROM DVSLog WHERE bID=%s', oDVSLogEntry.getID())

				dbgMsg('delete DVSLogEntry id-[%s]' % oDVSLogEntry.getID())
				return False

			except Exception, e:
				raise Exception, 'error deleting DVSLogEntry [%s]' % e

		finally:
			self._oLock.release()

	def getDVSLogEntry(self, bID=None):
		""" Find a DVSLogEntry by ID """

		try:
			self._oLock.acquire()

			try:
				rgoResult = ()

				sQuery = 'SELECT bID, bSerial, bEventID, sData, UNIX_TIMESTAMP(dTimeStamp) FROM DVSLog WHERE '

				if bID is not None:
					sQuery += 'bID=%s'
				rgoResult = self._libDB.query( sQuery, bID )

				if len ( rgoResult ) == 0:
					# No Results
					return None

				oRow = rgoResult[ 0 ]
				oDVSLogEntry = DVSLogEntry(oRow[0],oRow[1],oRow[2],oRow[3],oRow[4])

				return copy.copy( oDVSLogEntry )

			except Exception, e:
				raise Exception, 'error getting DVSLogEntry [%s]' % e

		finally:
			self._oLock.release()

	def setDVSLogEntry(self, oDVSLogEntry):
		""" Update the DVSLogEntry Object """

		try:
			self._oLock.acquire()

			try:
				oDVSLogEntry = self.getDVSLogEntry( bID=oDVSLogEntry.getID() )
				if oDVSLogEntry is not None:
					self._libDB.query('UPDATE DVSLog SET bSerial=%s, bEventID=%s, sData=%s, sTimeStamp=FROM_UNIXTIME(%s) WHERE bID=%s',
						oDVSLogEntry.getSerial(),
						oDVSLogEntry.getEventID(),
						oDVSLogEntry.getData(),
						oDVSLogEntry.getTimeStamp()
					)

					dbgMsg('updated DVSLogEntry-[%d]' % oDVSLogEntry.getID())
					return

			except Exception, e:
				raise Exception, 'error updating DVSLogEntry [%s]' % e

		finally:
			self._oLock.release()
