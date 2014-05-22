# thread_process_control.py

##
# Includes
#
# System
import threading, os, Queue, time, commands, re
# Logging
from lib.messaging import stdMsg, dbgMsg, errMsg
import lib.cache
import lib.dispatcher


PC_OPEN_TICKET          = 1


class ThreadProcessControl( threading.Thread ):

	def __init__( self, sName ):
		threading.Thread.__init__(self, name=sName)

		self._sName = sName
		self._fRunning = False          # Are we actually running?
		self._fStop = False             # Stop requested by parent
		self._q = Queue.Queue( 50 )     # Inter-thread Queue to handle function args

	def _postInit(self):
		# Grab other modules we might use from cache
		libCache = lib.cache.Cache()
		self._libDB = libCache.get('libDB')

	def run( self ):
		try:
			self._fRunning = True

			# sleep a bit and let everything initialize first
			time.sleep(10)
			self._postInit()

			while not self._fStop:
				try:
					rgoArg = self._q.get( True, 5 )

					try:
						bRequest = int( rgoArg[ 0 ] )
					except ValueError:
						raise Exception, 'invalid request [%s]' % bRequest

					if bRequest == PC_OPEN_TICKET:
						bArg1, bArg2, bArg3 = self._getArgs( bRequest, rgoArg[ 1: ] )
						self._openTicket( bArg1, bArg2, bArg3 )

					else:
						raise Exception, 'unknown request [%d]' % bRequest

				except Queue.Empty:
					pass

				except Exception, e:
					errMsg( 'error processing request [%s]' % e )

			self._fRunning = False

		except Exception, e:
			self._fRunning = False
			errMsg( 'encountered an error [%s], terminating' % e )

	def stop( self ):
		self._fStop = True

	def checkIsRunning( self ):
		return self._fRunning

	def controlProcess( self, *args ):
		""" Control Process identified by args. """
		try:
			self._q.put( args, True, 2 )
		except Queue.Full:
			errMsg( 'Process control queue is full, skipping' )

	def _getArgs( self, bRequest, rgoArg ):
		""" Parse argument list for request and return valid arguments. """

		try:
			if bRequest == PC_OPEN_TICKET:
				return int( rgoArg[ 0 ] ), int( rgoArg[ 1 ] ), int( rgoArg[ 2 ] )

		except Exception, e:
			raise Exception, 'wrong arguments for request type-[%d]' % bRequest

	def _openTicket( self, bArg1, bArg2, bArg3 ):
		""" Open ticket in Bugzilla. """

		try:
			pass

		except Exception, e:
			raise Exception, 'error while opening ticket [%s]' % e
