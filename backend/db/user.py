##
## user.py
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

class UserEntry:

	def __init__( self, bID=None, sName=None, sDescription=None, sPassword=None, bType=None ):
		""" Initialize new UserEntry object.  Password should already be hashed here. """

		self._bID = bID
		self._sName = sName
		self._sDescription = sDescription
		self._sPassword = sPassword
		self._bType = bType

		libCache = lib.cache.Cache()
		self._libUtil = libCache.get( 'libUtil' )

	def getID( self ):
		return self._bID

	def setID( self, bID ):
		self._bID = bID

	def getName( self ):
		return self._sName

	def setName( self, sName ):
		self._sName = sName

	def getDescription( self ):
		return self._sDescription

	def setDescription( self, sDescription ):
		self._sDescription = sDescription

	def getPassword( self ):
		return self._sPassword

	def setPassword( self, sPass, fHash=True ):
		sHash = sPass
		if fHash:
			(fStatus, sHash) = self._libUtil.hashPassword( sPass )
			if not fStatus:
				raise Exception, 'error setting password'
		self._sPassword = sHash

	def getType( self ):
		return self._bType

	def setType( self, bType ):
		self._bType = bType


class UserList:

	def __init__( self ):
		libCache = lib.cache.Cache()
		self._libDB = libCache.get( 'libDB' )
		self._libUtil = libCache.get( 'libUtil' )
		self._oLock = threading.RLock()

	def size( self ):
		""" Return the number of users we have loaded. """

		return len( self.getList() )

	def getList( self ):
		""" Return list copy of all users. """

		try:
			self._oLock.acquire()

			try:
				rgoUser = []

				rgoResult = self._libDB.query( 'SELECT bID, sName, sDescription, sPassword, bType FROM User ORDER BY bID' )

				for oRow in rgoResult:
					rgoUser.append(
						UserEntry(
							oRow[0],
							oRow[1],
							oRow[2],
							oRow[3],
							oRow[4]
						)
					)

				return copy.copy( rgoUser )

			except Exception, e:
				raise Exception, 'error loading user list from database [%s]' % e

		finally:
			self._oLock.release()

	def getUser( self, bID=None, sName=None ):
		""" Find User by ID or Name. """

		try:
			self._oLock.acquire()

			try:
				sQuery = 'SELECT bID, sName, sDescription, sPassword, bType FROM User WHERE '

				rgoResult = ()
				if bID is not None:
					sQuery += 'bID=%s'
					rgoResult = self._libDB.query( sQuery, bID )

				elif sName is not None:
					sQuery += 'sName=%s'
					rgoResult = self._libDB.query( sQuery, sName )

				if len( rgoResult ) == 0:
					return None

				oRow = rgoResult[ 0 ]
				oUserEntry = UserEntry(
					oRow[0],
					oRow[1],
					oRow[2],
					oRow[3],
					oRow[4]
				)

				return copy.copy( oUserEntry )

			except Exception, e:
				raise Exception, 'error getting user [%s]' % e

		finally:
			self._oLock.release()

	def setUser( self, oUser ):
		""" Update our User Object. """

		try:
			self._oLock.acquire()

			try:
				oUserEntry = self.getUser( bID=oUser.getID() )
				if oUserEntry is not None:
					if oUser.getPassword() is None:
						self._libDB.query( 'UPDATE User SET sName=%s, sDescription=%s, bType=%s WHERE bID=%s',
							oUser.getName(),
							oUser.getDescription(),
							oUser.getType(),
							oUser.getID()
						)

					else:
						self._libDB.query('UPDATE User SET sName=%s, sDescription=%s, sPassword=%s, bType=%s WHERE bID=%s',
							oUser.getName(),
							oUser.getDescription(),
							oUser.getPassword(),
							oUser.getType(),
							oUser.getID()
						)

					dbgMsg( 'updated user name-[%s]' % oUser.getName() )
					return

				# User does not exist, so add them
				# This is used by controller syncing
				self._libDB.query( 'INSERT INTO User (bID,sName,sPassword,sDescription,bType) VALUES (%s,%s,%s,%s,%s)',
					oUser.getID(),
					oUser.getName(),
					oUser.getPassword(),
					oUser.getDescription(),
					oUser.getType()
				)
				dbgMsg( 'added user name-[%s]' % oUser.getName() )

			except Exception, e:
				raise Exception, 'error updating user [%s]' % e

		finally:
			self._oLock.release()

	def addUser( self, sName, sPass, sDescription, bType ):
		""" Add new User to system. """

		try:
			self._oLock.acquire()

			try:
				self._libDB.query( 'INSERT INTO User (sName,sPassword,sDescription,bType) VALUES (%s,PASSWORD(%s),%s,%s)',
					sName,
					sPass,
					sDescription,
					bType
				)

				oUserEntry = self.getUser( sName=sName )
				if oUserEntry is None:
					dbgMsg( 'adding user name-[%s] failed' % sName )
					return None

				dbgMsg( 'added user name-[%s]' % sName )
				return copy.copy( oUserEntry )

			except Exception, e:
				raise Exception, 'error adding user [%s]' % e

		finally:
			self._oLock.release()

	def delUser( self, oUser ):
		""" Delete this User. """

		try:
			self._oLock.acquire()

			try:
				oUserEntry = self.getUser( bID=oUser.getID() )
				if oUserEntry is None:
					dbgMsg( 'delete user name-[%s] failed' % oUser.getName() )
					return False

				self._libDB.query( 'DELETE FROM User WHERE bID=%s', oUser.getID() )

				dbgMsg( 'deleted user name-[%s]' % oUser.getName() )
				return True

			except Exception, e:
				raise Exception, 'error deleting user [%s]' % e

		finally:
			self._oLock.release()
