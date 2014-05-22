##
## acl.py
##

##
# Includes
#
# System
import threading, copy
# Logging
from lib.messaging import dbgMsg
# Cache (Object store)
import lib.cache

class AccessEntry:

	def __init__( self, bUser=0, rgbRight=[] ):
		libCache = lib.cache.Cache()
		self._libDB = libCache.get( 'libDB' )

		self._bUser = bUser
		self._rgbRight = rgbRight

	def getUser( self ):
		return self._bUser

	def setUser( self, bUser ):
		self._bUser = bUser

	def getRights( self ):
		return self._rgbRight

	def setRights( self, rgbRight ):
		self._rgbRight = rgbRight


class AccessList:

	def __init__( self ):
		libCache = lib.cache.Cache()
		self._libDB = libCache.get( 'libDB' )
		self._oLock = threading.RLock()

	def size( self ):
		""" How many ACL entries did we load? """

		return len( self.getList() )

	def getList( self ):
		""" Return a list copy of all entries. """

		try:
			self._oLock.acquire()

			try:
				rgoEntry = []

				rgoResult = self._libDB.query( 'SELECT bUserID, bRight FROM ACL ORDER BY bUserID' )

				for oRow in rgoResult:
					bUser    = oRow[ 0 ]
					bRight   = oRow[ 1 ]

					rgbRight = []
					for b in [ 1, 2, 4, 8, 16, 32, 64, 128, 256 ]:
						if bRight & b:
							rgbRight.append( b )

					rgoEntry.append(
						AccessEntry(
							bUser,
							rgbRight
						)
					)

				return copy.copy( rgoEntry )

			except Exception, e:
				raise Exception, 'error getting acl list [%s]' % e

		finally:
			self._oLock.release()

	def getEntry( self, bUser ):
		""" Find Access Entry for this server and user combination. """

		try:
			self._oLock.acquire()

			try:
				rgoResult = self._libDB.query( 'SELECT bUserID, bRight FROM ACL WHERE bUserID=%s', bUser )

				if len( rgoResult ) == 0:
					return None

				oRow = rgoResult[ 0 ]
				bUser    = oRow[ 0 ]
				bRight   = oRow[ 1 ]

				rgbRight = []
				for b in [ 1, 2, 4, 8, 16, 32, 64, 128, 256 ]:
					if bRight & b:
						rgbRight.append( b )

				oEntry = AccessEntry(
					bUser,
					rgbRight
				)

				return copy.copy( oEntry )

			except Exception, e:
				raise Exception, 'error while getting entry [%s]' % e

		finally:
			self._oLock.release()

	def setEntry( self, oEntry ):
		""" Update our Entry for this server and user. """

		try:
			self._oLock.acquire()

			try:
				bRight = 0
				for b in oEntry.getRights():
					bRight |= b

				oAccessEntry = self.getEntry( oEntry.getUser() )
				if oAccessEntry is not None:
					self._libDB.query( 'UPDATE ACL SET bRight=%s WHERE bUserID=%s',
						bRight, oEntry.getUser() )

					dbgMsg( 'updated acl user-[%d]' % ( oEntry.getUser() ) )
					return

				self._libDB.query( 'INSERT INTO ACL (bUserID,bRight) VALUES (%s,%s)',
					oEntry.getUser(), bRight )

				dbgMsg( 'added acl user-[%d]' % ( oEntry.getUser() ) )

			except Exception, e:
				raise Exception, 'error while setting entry [%s]' % e

		finally:
			self._oLock.release()

	def addEntry( self, bUser, rgbRight ):
		""" Add new Entry for this user and add to database. """

		try:
			oEntry = AccessEntry( bUser, rgbRight )
			self.setEntry( oEntry )
			dbgMsg( 'added acl user-[%d]' % ( oEntry.getUser() ) )
			return copy.copy( oEntry )

		except Exception, e:
			raise Exception, 'error while adding entry [%s]' % e

	def delEntry( self, oEntry ):
		""" Delete this entry from our list and database. """

		try:
			self._oLock.acquire()

			try:
				oAccessEntry = self.getEntry( oEntry.getUser() )
				if oAccessEntry is None:
					dbgMsg( 'delete acl user-[%d] failed' % ( oEntry.getUser() ) )
					return False

				self._libDB.query( 'DELETE FROM ACL WHERE bUserID=%s', oEntry.getUser() )

				dbgMsg( 'deleted acl user-[%d]' % ( oEntry.getUser() ) )
				return True

			except Exception, e:
				raise Exception, 'error while deleting entry [%s]' % e

		finally:
			self._oLock.release()
