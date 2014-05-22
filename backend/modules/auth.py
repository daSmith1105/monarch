##
## auth.py
##

##
# Includes
#
# Logging
from lib.messaging import stdMsg, dbgMsg, errMsg
# Internal
import lib.cache
# LDAP Auth
import ldap

USE_LDAP   = True
CACHE_LDAP = True

class Auth:

	def __init__(self):
		""" Initialize Auth Modules """

		libCache = lib.cache.Cache()
		self._dbUserList = libCache.get('dbUserList')
		self._dbSessionList = libCache.get('dbSessionList')
		self._dbAccessList = libCache.get('dbAccessList')
		self._dbRightList = libCache.get('dbRightList')

		self._libUtil = libCache.get('libUtil')

	def _authUserLdap( self, sUser, sPass ):
		""" Authenticate user against LDAP database. """

		try:
			sDN = 'uid=%s,ou=People,dc=dividia,dc=net' % sUser

			self._oLdapServer = ldap.initialize( "ldap://dtechpdc.dividia.net" )
			self._oLdapServer.protocol_version = ldap.VERSION3
			self._oLdapServer.simple_bind_s( sDN, sPass )
			self._oLdapServer.unbind_s()

			return True

		except Exception, e:
			dbgMsg( 'error authenticating against ldap [%s]' % e )
			return False

	def _authUserInternal(self, oUser, sPass):
		try:
			(fSuccess, sHash) = self._libUtil.hashPassword(sPass)
			if not fSuccess:
				return False

			if oUser.getPassword() == sHash:
				return True
			return False

		except Exception, e:
			errMsg('error while authenticating user [%s]' % e)
			return False

	def loginUser(self, sName, sPass, fForce=False):
		""" Validate user and create new session object """

		try:
			oUser = None
			# Auth against LDAP
			if USE_LDAP:
				if not self._authUserLdap( sName, sPass ):
					self._libUtil.logMsg( 'login failed [%s] [noauth]' % sName )
					stdMsg( 'login failed user-[%s] reason-[noauth]' % sName )
					return 'noauth'

				# Get User
				oUser = self._dbUserList.getUser( sName=sName )
				if oUser is None:
					if not CACHE_LDAP:
						# User not found
						stdMsg( 'login succeeded for user-[%s], but caching disabled ... denied' % sName )
						return 'noauth'

					try:
						# User is missing, but we need to Cache from Ldap lookup
						oUser = self._dbUserList.addUser( sName, sPass, '%s LDAP import' % sName, 20 )
						# Create default access entry
						self._dbAccessList.addEntry( oUser.getID(), [ self._dbRightList.getValueByName( 'access' ) ] )
						stdMsg( 'new user cached on system from ldap [%s]' % sName )

					except Exception, e:
						errMsg( 'error caching user from ldap [%s]' % e )
						return 'noauth'

			# Auth against internal DB only
			else:
				# Get User
				oUser = self._dbUserList.getUser(sName=sName)
				if oUser is None:
					# User not found
					return 'noauth'

				# Auth User
				if not self._authUserInternal(oUser, sPass):
					self._libUtil.logMsg('login failed [%s] [noauth]' % sName)
					stdMsg('login failed user-[%s] reason-[noauth]' % sName)
					return 'noauth'

			# Get ACL
			oAccessEntry = self._dbAccessList.getEntry(oUser.getID())
			if oAccessEntry is None and oUser.getType() != 0:
				# No rights to this server
				return 'noauth'

			bAccessValue = self._dbRightList.getValueByName('access')

			# Make sure this user has "access" rights to this system
			if oUser.getType() != 0 and not bAccessValue in oAccessEntry.getRights():
				self._libUtil.logMsg('login failed [%s] [noaccess]' % sName)
				stdMsg('login failed user-[%s] reason-[noaccess]' % sName)
				return 'noauth'

			# Authenticated and has access
			# So, see if we already have a session
			if not fForce and self._dbSessionList.checkExists(bUserID=oUser.getID()):
				#self._libUtil.logMsg('login failed user-[%s] reason-[exists]' % sName)
				stdMsg('login failed user-[%s] reason-[exists] force-[%s]' % (sName, fForce))
				return 'exists'

			oSession = self._dbSessionList.addUser(oUser.getID())

			self._libUtil.logMsg('login succeeded user-[%s] session-[%s] force-[%s]' % (sName, oSession.getSession(), fForce))
			stdMsg('login succeeded user-[%s] session-[%s] force-[%s]' % (sName, oSession.getSession(), fForce))

			return oSession.getSession()

		except Exception, e:
			errMsg('error while attempting to login user [%s]' % e)
			raise Exception, "System error while logging in."

	def logoutUser(self, sSessID):
		""" Logout this user session """

		try:
			oSession = self._dbSessionList.getSession(sSessID=sSessID)
			if oSession is None:
				# Session does not exist
				return False

			sName = self._dbUserList.getUser(bID=oSession.getUser()).getName()
			fStatus = self._dbSessionList.delUser(oSession.getUser())

			if fStatus:
				self._libUtil.logMsg('logout succeeded [%s]' % sName)
				stdMsg('logout succeeded [%s]' % sName)
			else:
				self._libUtil.logMsg('logout failed [%s]' % sName)
				stdMsg('logout failed [%s]' % sName)
			return fStatus

		except Exception, e:
			self._libUtil.logMsg('logout failed [%s]' % sName)
			errMsg('error while attempting to logout user [%s]' % e)
			raise Exception, "System error while logging out."

	def checkExists(self, sSessID):
		""" Check if session has authenticated. """

		try:
			if self._dbSessionList.checkExists(sSessID=sSessID):
				return True
			return False

		except Exception, e:
			errMsg('error while checking if session is valid [%s]' % e)
			raise Exception, "System error while checking session."
