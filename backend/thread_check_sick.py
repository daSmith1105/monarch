# thread_check_sick.py

##
# Includes
#
# System
import threading, time, re, os, socket
# Logging
from lib.messaging import stdMsg, dbgMsg, errMsg
# Library
import lib.cache
import lib.xmlrpclibt


CHECK_LIMIT = 86400                       # 24 hours (secs) ( 24 * 60 * 60 )
RECHECK_LIMIT = 3600                      #  1 hour  (secs) (      60 * 60 )
REMOVE_CATEGORY_LIMIT = 2*365*24*60*60    #  2 years (secs)


class ThreadCheckSick( threading.Thread ):

	def __init__( self, sName ):
		threading.Thread.__init__( self, name=sName )

		self._sName = sName
		self._fRunning = False             # Are we actually running?
		self._fStop = False                # Stop requested by parent
		self._oLock = threading.RLock()

		self._dbServerList = None
		self._dbMisc = None

	def _postInit( self ):
		# Grab other modules we might use from cache
		libCache = lib.cache.Cache()
		self._dbServerList = libCache.get( 'dbServerList' )
		self._dbMisc = libCache.get( 'dbMisc' )

	def run( self ):
		try:
			self._fRunning = True

			# sleep a bit and let everything initialize first
			time.sleep( 10 )
			self._postInit()

			# Load last check times from DB
			bLastCheckSick = self._loadLastTime( 'sick' )
			bLastCheckAll = self._loadLastTime( 'all' )

			fHaveSick = self._haveSick()

			while not self._fStop:

				# Calculate our next run time
				bNow = int( time.time() )
				bSleep = CHECK_LIMIT - ( bNow - bLastCheckAll )
				if fHaveSick:
					bSleep = RECHECK_LIMIT - ( bNow - bLastCheckSick )
				if bSleep > 0:
					dbgMsg( 'sleeping for [%d] seconds' % bSleep )
				while not self._fStop and bSleep > 0:
					time.sleep( 5 )
					bSleep -= 5
				if self._fStop: break

				bNow = int( time.time() )
				if bNow - bLastCheckAll >= CHECK_LIMIT:
					self._checkAll()
					bLastCheckSick = self._saveLastTime( 'sick' )
					bLastCheckAll = self._saveLastTime( 'all' )
					# Remove DVR's from video.dividia.net that are dead
					self._removeDeadDVRs()

				bNow = int( time.time() )
				if bNow - bLastCheckSick >= RECHECK_LIMIT:
					self._checkSick()
					bLastCheckSick = self._saveLastTime( 'sick' )

				fHaveSick = self._haveSick()

			self._fRunning = False

		except Exception, e:
			self._fRunning = False
			errMsg( 'encountered an error [%s], terminating' % e )

	def stop( self ):
		self._fStop = True

	def checkIsRunning( self ):
		return self._fRunning

	def _haveSick( self ):
		""" Return true if any Serial's were in sick state """

		for oServer in self._dbServerList.getList():
			if oServer.checkIsSick():
				return True
		return False

	def _checkAll( self ):
		""" Check if we can access all DVR's """

		dbgMsg( 'checking all dvrs for misconfigured firewalls (sick)' )
		self._check( self._dbServerList.getList() )

	def _checkSick( self ):
		""" Check if we can access any DVR's that were previously sick. """

		rgoServer = []
		for oServer in self._dbServerList.getList():
			if oServer.checkIsSick():
				rgoServer.append( oServer )

		dbgMsg( 'rechecking sick dvrs for misconfigured firewalls (sick)' )
		self._check( rgoServer )

	def _check( self, rgoServer ):

		try:
			for oServer in rgoServer:
				if self._fStop: return
				if not oServer.checkIsAlive(): continue

				fSick = False
				try:
					sServer = 'http://' + oServer.getIP()
					if oServer.getPort() != 80:
						sServer += ':' + str( oServer.getPort() )
					sServer += '/RDA/'
					oXmlRpc = lib.xmlrpclibt.Server( url=sServer, timeout=5 )
					oResult = oXmlRpc.info.isAlive()

				except socket.error, (errno, errstr):
					dbgMsg( 'serial [%d] is sick' % oServer.getSerial() )
					fSick = True

				except Exception, e:
					dbgMsg( 'serial [%d] is sick' % oServer.getSerial() )
					fSick = True

				self._updateSick( oServer, fSick )

		except Exception, e:
			errMsg( 'error occurred while checking sick servers' )
			errMsg( e )

	def _updateSick( self, oServer, fSick ):
		""" Update sick flag if it is different """

		if oServer.checkIsSick() != fSick:
			# Now, update our date for this server object
			try:
				self._oLock.acquire()
				try:
					oServer.setIsSick( fSick )
					self._dbServerList.setServer( oServer )
				except Exception, e:
					errMsg( 'error saving new sick flag to server object' )
					errMsg( e )
			finally:
				self._oLock.release()

	def _removeDeadDVRs( self ):
		""" Remove video link on video.dividia.net on DVR's that are dead. """

		try:
			dbgMsg( 'removing dead dvrs from video.dividia.net link page' )
			for oServer in self._dbServerList.getList():
				if not oServer.checkHasCategory( 'video' ): continue
				if oServer.getInstall() is None: continue

				bNow = int( time.time() )
				if oServer.getTimestamp() is None or bNow - oServer.getTimestamp() > REMOVE_CATEGORY_LIMIT:

					# Remove this DVR from video.dividia.net page
					try:
						self._oLock.acquire()
						try:
							rgs = []
							for s in oServer.getCategories().split( ',' ):
								if s == 'video': continue
								rgs.append( s )
							oServer.setCategories( ','.join( rgs ) )
							self._dbServerList.setServer( oServer )
						except Exception, e:
							errMsg( 'error saving new categories to server object' )
							errMsg( e )
					finally:
						self._oLock.release()

		except Exception, e:
			errMsg( 'error occurred while updating video.dividia.net page' )
			errMsg( e )

	def _loadLastTime( self, sWhich ):
		""" Load last check time from database """

		# Load last check sick time from DB
		bLast = int( time.time() )
		try:
			sLast = self._dbMisc.get( 'checksick', sWhich )
			dbgMsg( 'loading last check %s time [%s]' % ( sWhich, sLast ) )
			if sLast != '0':
				bLast = int( time.mktime( time.strptime( sLast, '%Y-%m-%d %H:%M:%S' ) ) )
		except:
			errMsg( 'error parsing last check %s time' % sWhich )
		return bLast

	def _saveLastTime( self, sWhich ):
		""" Save last check time to database """

		bNow = int( time.time() )
		try:
			# Save our last run time
			self._dbMisc.set( 'checksick', sWhich, time.strftime( '%Y-%m-%d %H:%M:%S' ) )
		except:
			errMsg( 'error saving last check %s time' % sWhich )
		return bNow
