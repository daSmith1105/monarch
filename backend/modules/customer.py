##
## customer.py
##

##
# Includes
#
import threading, copy, pickle
# Logging
from lib.messaging import stdMsg, dbgMsg, errMsg
# Internal
import lib.cache
import db.user
import db.server


class Customer:

	def __init__(self):
		""" Initialize Customer Modules """

		libCache = lib.cache.Cache()

		self._libDB = libCache.get( 'libDB' )
		self._dbServerList = libCache.get( 'dbServerList' )

		self._oLock = threading.RLock()

	def _freezeUser( self, o ):
		""" Flatten user object to associative array. """

		try:
			rgs = {}
			rgs['bID'] = o.getID()
			rgs['sName'] = o.getName()
			rgs['sDescription'] = o.getDescription()
			rgs['sPassword'] = o.getPassword()
			rgs['bType'] = o.getType()

			return rgs

		except Exception, e:
			raise Exception, 'error freezing user [%s]' % e

	def _thawUser( self, rgsUser ):
		""" Create user object from associative array. """

		try:
			oUser = db.user.UserEntry()
			oUser.setID( rgsUser['bID'] )
			oUser.setName( rgsUser['sName'] )
			oUser.setDescription( rgsUser['sDescription'] )
			if rgsUser['sPassword'] != '__notset__':
				# Password change
				oUser.setPassword( rgsUser['sPassword'], fHash=False )
			oUser.setType( rgsUser['bType'] )

			return oUser

		except Exception, e:
			raise Exception, 'error thawing user [%s]' % e

	def _expireSessions( self ):
		""" Expire stale sessions. """

		try:
			self._oLock.acquire()

			try:
				sQuery = 'DELETE FROM CustSession WHERE UNIX_TIMESTAMP( NOW() ) - UNIX_TIMESTAMP( dLastAccess ) > %s'
				rgoResult = self._libDB.query( sQuery, int( time.time() ) + 60 * 60 * 24 * 7 )

				return True

			except Exception, e:
				errMsg( 'Error expiring sessions [%s]' % e )
				return False

		finally:
			self._oLock.release()

	def verifySession( self, sSess ):
		""" Validate session and return authenticated username. """

		try:
			self._oLock.acquire()

			try:
				self._expireSessions()

				sQuery = 'SELECT U.sName FROM CustUser U, CustSession S WHERE ' + \
				         'U.bID = S.bUserID AND S.sSessID=%s'

				rgoResult = self._libDB.query( sQuery, sSess )

				if len( rgoResult ) == 0:
					return 'noauth'

				oRow = rgoResult[ 0 ]

				return oRow[ 0 ]

			except Exception, e:
				errMsg( 'error while attempting to verify session [%s]' % e )
				raise Exception, "System error while verifying session."

		finally:
			self._oLock.release()

	def _deleteUsers( self, bSerial ):
		""" Delete all users for a serial. """

		try:
			self._oLock.acquire()

			try:
				sQuery = 'DELETE FROM CustUser WHERE bSerial = %s'
				rgoResult = self._libDB.query( sQuery, bSerial )

				return True

			except Exception, e:
				errMsg( 'Error removing users for serial-[%s] [%s]' % ( bSerial, e ) )
				return False

		finally:
			self._oLock.release()

	def _addUser( self, bSerial, oUser ):
		""" Add a new user for this serial. """

		try:
			self._oLock.acquire()

			try:
				sQuery = 'INSERT INTO CustUser (bSerial,bID,sName,sPassword,sDescription,bType) VALUES (%s,%s,%s,%s,%s,%s)'
				self._libDB.query(
					sQuery,
					bSerial,
					oUser.getID(),
					oUser.getName(),
					oUser.getPassword(),
					oUser.getDescription(),
					oUser.getType()
				)

				return True

			except Exception, e:
				errMsg( 'Error adding user-[%d] for serial-[%s] [%s]' % ( oUser.getID(), bSerial, e ) )
				return False

		finally:
			self._oLock.release()

	def _getUsers( self, bSerial ):
		""" Return list copy of all users. """

		try:
			self._oLock.acquire()

			try:
				rgoUser = []

				rgoResult = self._libDB.query( 'SELECT bID, sName, sDescription, sPassword, bType FROM CustUser WHERE bSerial=%s ORDER BY sName', bSerial )

				for oRow in rgoResult:
					rgoUser.append(
						db.user.UserEntry(
							int( oRow[0] ),
							str( oRow[1] ),
							str( oRow[2] ),
							str( oRow[3] ),
							int( oRow[4] )
						)
					)

				return copy.copy( rgoUser )

			except Exception, e:
				raise Exception, 'error loading user list from database [%s]' % e

		finally:
			self._oLock.release()

	def _getSyncData( self, sType, bSerial ):
		""" Return a list of all users, servers, and acl to a member server. """

		try:
			rgs = []

			# User
			if sType == 'rgsUser':
				for oUser in self._getUsers( bSerial ):
					rgs.append( self._freezeUser( oUser ) )

			return rgs

		except Exception, e:
			errMsg( 'error while generating sync data for member server [%s]' % e )
			return []

	def getSyncHash( self, bSerial ):
		""" Return a binary has of our sync data.  Used to test if we should sync (data changed). """

		try:
			oServer = self._dbServerList.getServer( bSerial=bSerial )
			if oServer is None:
				dbgMsg( 'unknown serial' )
				return {}
			if not oServer.checkHasAuth():
				dbgMsg( 'auth not supported for this serial' )
				return {}

			rgsType = [ 'rgsUser' ]
			rgs = {}
			for sType in rgsType:
				rgsData = self._getSyncData( sType, bSerial )

				# return an md5 hash of the object serialized as a string
				try:
					import hashlib
					m = hashlib.md5()
				except ImportError:
					import md5
					m = md5.new()
				m.update( pickle.dumps( rgsData ) )
				rgs[ sType ] = m.hexdigest()

			return rgs

		except Exception, e:
			errMsg( 'error while getting sync hash user list for serial-[%s] [%s]' % ( bSerial, e ) )
			return {}

	def setSyncData( self, bSerial, rgsUserList ):
		""" Return a binary has of our sync data.  Used to test if we should sync (data changed). """

		try:
			oServer = self._dbServerList.getServer( bSerial=bSerial )
			if not oServer.checkHasAuth():
				raise Exception, 'auth not supported for this serial'

			dbgMsg( 'syncing user list with serial-[%s]' % bSerial )

			self._deleteUsers( bSerial )

			for rgsUser in rgsUserList:
				oUser = self._thawUser( rgsUser )
				self._addUser( bSerial, oUser )

			dbgMsg( 'finished syncing user list with serial-[%s]' % bSerial )

			return True

		except Exception, e:
			errMsg( 'error while syncing user list with serial-[%s] [%s]' % ( bSerial, e ) )
			return False
