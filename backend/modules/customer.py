##
## customer.py
##

##
# Includes
#
# Logging
from lib.messaging import stdMsg, dbgMsg, errMsg
# Internal
import lib.cache


class Customer:

	def __init__(self):
		""" Initialize Customer Modules """

		libCache = lib.cache.Cache()

		self._libDB = libCache.get( 'libDB' )
		self._oLock = threading.RLock()

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
