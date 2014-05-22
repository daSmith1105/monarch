# thread_xmlrpc.py

##
# Includes
#
# Threading
import threading
# XMLRPC Server
import SocketServer, SimpleXMLRPCServer, threading, socket, select
# Logging
from lib.messaging import stdMsg, dbgMsg, errMsg

# Library
import lib.cache
import lib.util
# DB Models
import db.acl
import db.rights
import db.session
import db.user
import db.server
import db.camera
import db.pricelist
import db.misc
import db.dvslog

# Config
import modules.config.user
import modules.config.server
import modules.config.camera
import modules.config.pricelist
# Standard
import modules.auth
import modules.stats
import modules.key
import modules.dvslog
import modules.crash
import modules.ticket


SERVER_PORT = 9000


class ThreadXmlRpc(threading.Thread):

	def __init__(self, sName, rgoThread):
		threading.Thread.__init__(self, name=sName)

		self.sName = sName
		self.fRunning = False     # Are we actually running?
		self.fStop = False        # Stop requested by parent
		self.oServer = None

		self.rgoThread = rgoThread

	def run(self):
		try:
			self.fRunning = True

			self.oServer = XmlRpcServer('', SERVER_PORT, self.rgoThread)
			while not self.fStop:
				rgbRead, rgbWrite, rgbErr = select.select( [ self.oServer.socket ], [], [], 5 )
				if len( rgbRead ) > 0:
					self.oServer.handle_request()

			self.fRunning = False

		except Exception, e:
			self.fRunning = False
			errMsg('%s encountered an error [%s]' % (self.sName, e))
			stdMsg('%s terminating' % self.sName)

	def stop(self):
		self.fStop = True

	def checkIsRunning(self):
		return self.fRunning

	def reloadConfig(self):
		self.oServer.reloadConfig()


class XmlRpcDispatch(SimpleXMLRPCServer.SimpleXMLRPCRequestHandler):

	def is_rpc_path_valid(self):
		return True

	def _parseRequest(self, sRequest):
		
		""" Parse XmlRpc request into valid class mapping. """

		# Parse request into a valid subclass
		rgsToks = sRequest.split('.')
		sMethod = rgsToks[-1]
		sModule = 'mod'
		for s in rgsToks[0:-1]:
			sModule += s.capitalize()

		return (sModule, sMethod)

	def _getSession(self, rgoParam):
		""" Peel session off parameter list. """

		sSessID = rgoParam[0]
		rgoParam = rgoParam[1:]

		return (sSessID, rgoParam)

	def _checkEverybody(self, sModule, sMethod):
		""" Certain functions can be called by everybody, see if this is one of them. """

		if sModule == 'modAuth':
			if sMethod == 'loginUser' or \
			   sMethod == 'logoutUser' or \
			   sMethod == 'checkExists':
				return True

		elif sModule == 'modStats':
			return True

		elif sModule == 'modKey' and sMethod == 'getKey':
			return True
		
		elif sModule == 'modDvslog':
			return True

		elif sModule == 'modCrash':
			return True

		return False

	def _checkPrivate(self, sModule, sMethod):
		""" See if this is a private function not exported as a public api. """

		#if sModule == 'modConfigGeneral':
		#	if sMethod == 'addFeature' or \
		#		 sMethod == 'delFeature':
		#		return True

		return False

	def _getRemoteIP( self ):
		""" Find IP of remote client. """

		if self.headers.has_key( 'x-forwarded-for' ) and \
		   self.headers[ 'x-forwarded-for' ] != '':
			return self.headers[ 'x-forwarded-for' ].split( ',' )[ 0 ]

		return self.client_address[ 0 ]

	def _dispatch(self, sRequest, rgoParam):
		# Okay, let's check our subclasses
		try:
			libCache = lib.cache.Cache()

			# Parse Request
			sModule, sMethod = self._parseRequest(sRequest)
			oModule = libCache.get(sModule)
			if oModule is None:
				raise AttributeError

			# Make sure this method isn't private
			if sMethod[0:1] == '_':
				stdMsg('cannot call private method "%s"' % sRequest)
				raise Exception, 'cannot call private method "%s"' % sRequest

			# If this is not a function that can be called by Everyone, check session and proceed
			if not self._checkEverybody(sModule, sMethod):
				# Discard any attempt to proceed further without a session or magic
				if len(rgoParam) == 0:
					return (True, 'noauth')
				sSessID, rgoParam = self._getSession(rgoParam)

				if self._checkPrivate(sModule, sMethod):
					return (True, 'noauth')

				# Okay, just check the session
				elif not libCache.get('dbSessionList').checkExists(sSessID=sSessID):
					return (True, 'noauth')

			# Inject Remote IP into UpdateIP call
			if sModule == 'modStats' and ( sMethod == 'updateIP' or sMethod == 'newserver' ):
				rgoParam = list( rgoParam )
				rgoParam.insert( 1, self._getRemoteIP() )
				rgoParam = tuple( rgoParam )

			# Alright, let's call it
			oFunc = getattr(oModule, sMethod)

		except AttributeError, e:
			# Oops it wasn't found, throw an error
			sMsg = 'method "%s" is not supported' % sRequest
			stdMsg(sMsg)
			return (False, 'method "%s" is not supported' % sRequest)
		except Exception, e:
			errMsg('uncaught exception [%s]' % e)
			return (False, e[0])
		else:
			try:
				dbgMsg('%s called' % sRequest)
				try:
					oResult = oFunc(*rgoParam)
					if sModule == 'modStats':
						return oResult
					return (True, oResult)
				except Exception, e:
					if sModule == 'modStats':
						return e[0]
					return (False, e[0])
			finally:
				dbgMsg('%s returning' % sRequest)


class XmlRpcServer(SocketServer.ThreadingMixIn, SimpleXMLRPCServer.SimpleXMLRPCServer):
	def __init__(self, *args):
		SimpleXMLRPCServer.SimpleXMLRPCServer.__init__(self,addr=(args[0], args[1]), requestHandler=XmlRpcDispatch, logRequests=0)

		# Initialize cache (watch dependencies here)
		libCache = lib.cache.Cache()
		libCache.set('dbAccessList', db.acl.AccessList())
		libCache.set('dbRightList', db.rights.RightList())
		libCache.set('dbSessionList', db.session.SessionList())
		libCache.set('dbServerList', db.server.ServerList())
		libCache.set('dbCameraList', db.camera.CameraList())
		libCache.set('dbPriceList', db.pricelist.PriceList())
		libCache.set('dbDVSLogList',db.dvslog.DVSLogEntryList())
		libCache.set('dbMisc', db.misc.Misc())
		libCache.set('libUtil', lib.util.Util())
		libCache.set('dbUserList', db.user.UserList())
		libCache.set('modKey', modules.key.Key())
		libCache.set('modConfigUser', modules.config.user.User())
		libCache.set('modConfigServer', modules.config.server.Server())
		libCache.set('modConfigCamera', modules.config.camera.Camera())
		libCache.set('modConfigPricelist', modules.config.pricelist.PriceList())
		libCache.set('modAuth', modules.auth.Auth())
		libCache.set('modStats', modules.stats.Stats())
		libCache.set('modDvslog',modules.dvslog.DVSLog())
		libCache.set('modCrash',modules.crash.Crash())
		libCache.set('modTicket', modules.ticket.Ticket())

		# Hook up Process Control Handlers
		#libCache.get('modUtil')._controlProcess += self.rgoThread['ProcessControl'].controlProcess

		dbgMsg('loaded acl-[%d] right-[%d] session-[%d] server-[%d] user-[%d]' % \
			(
				libCache.get('dbAccessList').size(),
				libCache.get('dbRightList').size(),
				libCache.get('dbSessionList').size(),
				libCache.get('dbServerList').size(),
				libCache.get('dbUserList').size()
			)
		)

	def reloadConfig(self):
		""" Called after a SIGHUP to reload config from db. """

		stdMsg( 'reloading configuration' )
		libCache = lib.cache.Cache()
		libCache.get('dbPriceList')._load()
		libCache.get('dbDVSLogEntryList')._load()

		# Reload crash report skip list
		libCache.get( 'modCrash' )._getSkipList()

	def server_bind(self):
		# Make sure we can reuse this socket
		self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		SimpleXMLRPCServer.SimpleXMLRPCServer.server_bind(self)

	def handle_error(self, request, client_address):
		errMsg('Error communicating with client-[%s]' % client_address[0])
