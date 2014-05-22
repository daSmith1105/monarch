# xmlrpclibt.py

##
## xmlrpclib with timeout options
##

import xmlrpclib, httplib, threading, sys, socket

fTest = False
def setTest(f):
	global fTest
	fTest = f

# Copied from xmlrpclib
class _Method:
	def __init__( self, send, name ):
		self.__send = send
		self.__name = name
	def __getattr__( self, name ):
		return _Method( self.__send, "%s.%s" % ( self.__name, name ) )
	def __call__( self, *args, **kwargs ):
		return self.__send( self.__name, *args, **kwargs )

class InterruptableThread( threading.Thread ):
	def __init__( self, oFunc, *args, **kwargs ):
		threading.Thread.__init__( self )
		self._oFunc = oFunc
		self._args = args
		self._kwargs = kwargs
		self.oResult = None
		self.oError = None

	def run( self ):
		try:
			self.oResult = self._oFunc( *self._args, **self._kwargs )
		except Exception, e:
			self.oError = sys.exc_info()[ 0 ]

class Server:

	def __init__( self, url, *args, **kwargs ):

		self._bTimeout = kwargs.get( 'timeout', None )
		if 'timeout' in kwargs:
			del kwargs[ 'timeout' ]
		if self._bTimeout is None:
			self._bTimeout = 60

		oTransport = TimeoutTransport()
		oTransport.timeout = self._bTimeout
		kwargs[ 'transport' ] = oTransport

		if not fTest:
			self._oServer = xmlrpclib.Server( url, *args, **kwargs )
			return

		# Used for unittest stub
		import xmlrpclibt_stub
		self._oServer = xmlrpclibt_stub.Server(url, *args, **kwargs)

	def __request( self, methodname, *args, **kwargs ):
		oFunc = getattr( self._oServer, methodname )
		oThread = InterruptableThread( oFunc, *args, **kwargs )
		oThread.start()
		oThread.join( self._bTimeout )
		if oThread.isAlive():
			raise socket.error, ( 10060, 'The operation timed out.' )
		if oThread.oError:
			raise oThread.oError, ( 10060, 'The operation timed out.' )
		return oThread.oResult

	def __getattr__( self, name ):
		return _Method( self.__request, name )

class TimeoutTransport(xmlrpclib.Transport):

	def make_connection(self, host):
		conn = TimeoutHTTP(host)
		conn.set_timeout(self.timeout)
		return conn

class TimeoutHTTPConnection(httplib.HTTPConnection):

	def connect(self):
		httplib.HTTPConnection.connect(self)
		self.sock.settimeout(self.timeout)

class TimeoutHTTP(httplib.HTTP):
	_connection_class = TimeoutHTTPConnection

	def set_timeout(self, timeout):
		self._conn.timeout = timeout
