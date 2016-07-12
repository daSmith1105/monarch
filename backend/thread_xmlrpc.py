# thread_xmlrpc.py

##
# Includes
#
# Threading
import os, sys, threading
sys.path.append( 'lib/jsonrpclib' )
# XMLRPC Server
import SocketServer, socket, select
from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
# JSON-RPC Server
from jsonrpclib.SimpleJSONRPCServer import SimpleJSONRPCServer, SimpleJSONRPCRequestHandler
# Logging
from lib.messaging import stdMsg, dbgMsg, errMsg
import fcntl

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
import modules.customer
import modules.tigerpaw


SERVER_PORT = 9000
SERVER_PORT_JSON = 9001
MAGIC = 'dtech'

# Experimental JSON-RPC Support
ENABLE_JSON = True

class ThreadXmlRpc(threading.Thread):

	def __init__(self, sName, rgoThread):
		threading.Thread.__init__(self, name=sName)

		self.sName = sName
		self.fRunning = False     # Are we actually running?
		self.fStop = False        # Stop requested by parent
		self.oServerXML = None
		self.oServerJSON = None

		self.rgoThread = rgoThread

		self.initCache()

	def run(self):
		try:
			self.fRunning = True

			self.oServerXML = XmlRpcServer('', SERVER_PORT, self)
			if ENABLE_JSON:
				self.oServerJSON = JsonRpcServer('', SERVER_PORT_JSON, self)

			# Make sure our children do not inherit our socket
			# Found at http://mail.python.org/pipermail/python-list/2007-July/621680.html
			if sys.modules.has_key( 'fcntl' ):
				bFlags = fcntl.fcntl( self.oServerXML.fileno(), fcntl.F_GETFD )
				fcntl.fcntl( self.oServerXML.fileno(), fcntl.F_SETFD, bFlags | fcntl.FD_CLOEXEC )
				if ENABLE_JSON:
					bFlags = fcntl.fcntl( self.oServerJSON.fileno(), fcntl.F_GETFD )
					fcntl.fcntl( self.oServerJSON.fileno(), fcntl.F_SETFD, bFlags | fcntl.FD_CLOEXEC )

			while not self.fStop:
				rgbSocket = [ self.oServerXML.socket ]
				if ENABLE_JSON:
					rgbSocket.append( self.oServerJSON.socket )
				rgbRead, rgbWrite, rgbErr = select.select( rgbSocket, [], [], 5 )
				if len( rgbRead ) > 0:
					if self.oServerXML.socket in rgbRead:
						self.oServerXML.handle_request()
					elif self.oServerJSON is not None and self.oServerJSON.socket in rgbRead:
						self.oServerJSON.handle_request()

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
		""" Called after a SIGHUP to reload config from db. """

		stdMsg( 'reloading configuration' )
		libCache = lib.cache.Cache()
		libCache.get('dbPriceList')._load()

		# Reload crash report skip list
		libCache.get( 'modCrash' )._getSkipList()

	def initCache(self):
		# Initialize cache (watch dependencies here)
		libCache = lib.cache.Cache()
		libCache.set('dbAccessList', db.acl.AccessList())
		libCache.set('dbRightList', db.rights.RightList())
		libCache.set('dbSessionList', db.session.SessionList())
		libCache.set('dbServerList', db.server.ServerList())
		libCache.set('dbCameraList', db.camera.CameraList())
		libCache.set('dbPriceList', db.pricelist.PriceList())
		libCache.set('dbDVSLogList',db.dvslog.DVSLogList())
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
		libCache.set('modCustomer', modules.customer.Customer())
		libCache.set('modTigerpaw', modules.tigerpaw.Tigerpaw())

		# Hook up Process Control Handlers
		#libCache.get('modUtil')._controlProcess += self.rgoThread['ProcessControl'].controlProcess

		dbgMsg('loaded cache objects')

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

		elif sModule == 'modKey' and ( sMethod == 'getKey' or sMethod == 'getKeyV2' ):
			return True
		
		elif sModule == 'modDvslog':
			return True

		elif sModule == 'modCrash':
			return True

		elif sModule == 'modCustomer':
			if sMethod == 'verifySession':
				return True

		return False

	def _checkPrivate(self, sModule, sMethod):
		""" See if this is a private function not exported as a public api. """

		#if sModule == 'modConfigGeneral':
		#	if sMethod == 'addFeature' or \
		#		 sMethod == 'delFeature':
		#		return True

		return False

	def _checkMagic( self, sModule, sMethod ):
		""" See if this is a function protected by magic session. """

		if sModule == 'modCustomer':
			if sMethod == 'getSyncHash' or \
				 sMethod == 'setSyncData':
				return True

		return False

	def _dispatch(self, sRequest, rgoParam, sRemoteIP):
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

				elif sSessID == MAGIC and self._checkMagic( sModule, sMethod ):
					pass

				# Okay, just check the session
				elif not libCache.get('dbSessionList').checkExists(sSessID=sSessID):
					return (True, 'noauth')

			# Inject Remote IP into UpdateIP call
			if sModule == 'modStats' and ( sMethod == 'updateIP' or sMethod == 'newserver' ):
				rgoParam = list( rgoParam )
				rgoParam.insert( 1, sRemoteIP )
				rgoParam = tuple( rgoParam )

			# Alright, let's call it
			oFunc = getattr(oModule, sMethod)

			# Skip logging these functions since they are chatty
			rgsSkipLog = [
				'stats.updateIP',
				'stats.cameraFail',
				'stats.isAlive'
			]

		except AttributeError, e:
			errMsg( e )
			# Oops it wasn't found, throw an error
			sMsg = 'method "%s" is not supported' % sRequest
			stdMsg(sMsg)
			return (False, 'method "%s" is not supported' % sRequest)
		except Exception, e:
			errMsg('uncaught exception [%s]' % e)
			return (False, e[0])
		else:
			try:
				if sRequest not in rgsSkipLog:
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
				if sRequest not in rgsSkipLog:
					dbgMsg('%s returning' % sRequest)

## XML-RPC
class XmlRpcDispatch(SimpleXMLRPCRequestHandler):

	def is_rpc_path_valid(self):
		return True

	def _getRemoteIP( self ):
		""" Find IP of remote client. """

		try:
			if self.headers.has_key( 'x-forwarded-for' ) and \
				 self.headers[ 'x-forwarded-for' ] != '':
				return self.headers[ 'x-forwarded-for' ].split( ',' )[ 0 ]

			return self.client_address[ 0 ]

		except Exception, e:
			errMsg( 'error getting remote ip from client [%s]' % e )
			return ''

	def _dispatch(self, sRequest, rgoParam):
		return self.server.oParent._dispatch( sRequest, rgoParam, self._getRemoteIP() )

	def handle_error(self, request, client_address):
		errMsg('Error communicating with client-[%s]' % client_address[0])

class XmlRpcServer(SocketServer.ThreadingMixIn, SimpleXMLRPCServer):
	def __init__(self, *args):
		SimpleXMLRPCServer.__init__(self,addr=(args[0], args[1]), requestHandler=XmlRpcDispatch, logRequests=0)

		self.oParent = args[ 2 ]

		stdMsg( 'Started XML-RPC Server' )

	def server_bind(self):
		# Make sure we can reuse this socket
		self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		SimpleXMLRPCServer.server_bind(self)

## JSON-RPC
class JsonRpcDispatch(SimpleJSONRPCRequestHandler):

	def is_rpc_path_valid(self):
		return True

	def _getRemoteIP( self ):
		""" Find IP of remote client. """

		try:
			if self.headers.has_key( 'x-forwarded-for' ) and \
				 self.headers[ 'x-forwarded-for' ] != '':
				return self.headers[ 'x-forwarded-for' ].split( ',' )[ 0 ]

			return self.client_address[ 0 ]

		except Exception, e:
			errMsg( 'error getting remote ip from client [%s]' % e )
			return ''

	def _dispatch(self, sRequest, rgoParam):
		return self.server.oParent._dispatch( sRequest, rgoParam, self._getRemoteIP() )

	def handle_error(self, request, client_address):
		errMsg('Error communicating with client-[%s]' % client_address[0])

class JsonRpcServer(SocketServer.ThreadingMixIn, SimpleJSONRPCServer):
	def __init__(self, *args):
		SimpleJSONRPCServer.__init__(self,addr=(args[0], args[1]), requestHandler=JsonRpcDispatch, logRequests=0)

		self.oParent = args[ 2 ]

		stdMsg( 'Started JSON-RPC Server' )

	def server_bind(self):
		# Make sure we can reuse this socket
		self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		SimpleJSONRPCServer.server_bind(self)
