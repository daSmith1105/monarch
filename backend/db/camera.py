##
## camera.py
##

##
# Includes
#
# System
import time, threading, copy
# Logging
from lib.messaging import dbgMsg
# Cache (Object store)
import lib.cache


class CameraEntry:
	"""
	Camera Object represents a failed camera for a DVS in our system.
	"""

	def __init__( self, bSerial=None, bCamera=None, bTimestamp=None, fSkip=False ):
		""" Setup Camera Object """

		self._bSerial = bSerial
		self._bCamera = bCamera
		self._bTimestamp = bTimestamp
		self._fSkip = False
		if fSkip:
			self._fSkip = True

	def getSerial( self ):
		""" Return Serial associated with this camera. """
		return self._bSerial

	def setSerial( self, bSerial ):
		""" Set new Serial for camera object. """
		self._bSerial = bSerial

	def getCamera( self ):
		""" Return Camera ID. """
		return self._bCamera

	def setCamera( self, bCamera ):
		""" Set new camera ID. """
		self._bCamera = bCamera

	def getTimestamp( self ):
		""" Return the last time this camera checked in. """
		return self._bTimestamp

	def setTimestamp( self, bTimestamp ):
		""" Set new timestamp for camera. """
		self._bTimestamp = None
		if bTimestamp != 0:
			self._bTimestamp = bTimestamp

	def checkHasSkip( self ):
		""" Return Skip status for camera Y, N, P. """
		return self._fSkip

	def setSkip( self, fSkip ):
		""" Set new Skip flag. """
		self._fSkip = False
		if fSkip:
			self._fSkip = True


class CameraList:
	"""
	Camera module takes care of all failed camera activities for systems on maintenance.
	 - Track new failed camera
	 - Ignore Failed camera
	 - Erase cameras that are back online
	"""

	def __init__( self ):
		""" Initialize Camera module """

		libCache = lib.cache.Cache()
		self._libDB = libCache.get( 'libDB' )
		self._oLock = threading.RLock()

	def size( self ):
		""" Return the number of cameras we have loaded. """

		return len( self.getList() )

	def getList( self ):
		""" Return list copy of our cameras. """

		try:
			self._oLock.acquire()

			try:
				# Clear in case of reload
				rgoCamera = []

				rgoResult = self._libDB.query(
					'SELECT bSerial, bCamera, UNIX_TIMESTAMP(dTimestamp), fSkip ' + \
					'FROM Camera ' + \
					'ORDER BY bSerial, bCamera'
				)

				for oRow in rgoResult:
					rgoCamera.append(
						CameraEntry(
							oRow[0],
							oRow[1],
							oRow[2],
							oRow[3]
						)
					)

				return copy.copy( rgoCamera )

			except Exception, e:
				raise Exception, 'error getting camera list [%s]' % e

		finally:
			self._oLock.release()

	def getCamera( self, bSerial, bCamera ):
		""" Return camera object. """

		try:
			self._oLock.acquire()

			try:
				rgoResult = self._libDB.query(
					'SELECT bSerial, bCamera, UNIX_TIMESTAMP(dTimestamp), fSkip ' + \
					'FROM Camera ' + \
					'WHERE bSerial=%s AND bCamera=%s',
					bSerial,
					bCamera
				)

				if len( rgoResult ) == 0:
					# Nothing found
					return None

				oRow = rgoResult[ 0 ]
				oCameraEntry = CameraEntry(
					oRow[0],
					oRow[1],
					oRow[2],
					oRow[3]
				)

				return copy.copy( oCameraEntry )

			except Exception, e:
				raise Exception, 'error getting camera [%s]' % e

		finally:
			self._oLock.release()

	def setCamera( self, oCamera ):
		""" Update our Camera Object. """

		try:
			self._oLock.acquire()

			try:
				oCameraEntry = self.getCamera( oCamera.getSerial(), oCamera.getCamera() )
				if oCameraEntry is None:
					raise Exception, 'not found'

				self._libDB.query( 'UPDATE Camera SET dTimestamp=FROM_UNIXTIME(%s), fSkip=%s WHERE bSerial=%s AND bCamera=%s',
					oCamera.getTimestamp(),
					oCamera.checkHasSkip(),
					oCamera.getSerial(),
					oCamera.getCamera()
				)

				#dbgMsg( 'updated camera serial-[%d]' % oCamera.getSerial() )

			except Exception, e:
				raise Exception, 'error updating camera [%s]' % e

		finally:
			self._oLock.release()

	def addCamera( self, bSerial, bCamera ):
		""" Create new camera entry. """

		try:
			self._oLock.acquire()

			try:
				# Camera does not exist, so add new failed camera
				self._libDB.query( 'INSERT INTO Camera (bSerial,bCamera,dTimestamp) VALUES (%s,%s,NOW())',
					bSerial,
					bCamera
				)

				oCameraEntry = CameraEntry()
				oCameraEntry.setSerial( bSerial )
				oCameraEntry.setCamera( bCamera )
				oCameraEntry.setTimestamp( time.time() )
				oCameraEntry.setSkip( False )

				dbgMsg( 'added camera serial-[%d]' % bSerial )

				return copy.copy( oCameraEntry )

			except Exception, e:
				raise Exception, 'error while attempting to add camera object [%s]' % e

		finally:
			self._oLock.release()

	def delCamera( self, oCamera ):
		""" Remove camera by id """

		try:
			self._oLock.acquire()

			try:
				oCameraEntry = self.getCamera( oCamera.getSerial(), oCamera.getCamera() )
				if oCameraEntry is None:
					dbgMsg( 'delete camera serial-[%d] camera-[%d] failed' % ( oCamera.getSerial(), oCamera.getCamera() ) )
					return False

				self._libDB.query( 'DELETE FROM Camera WHERE bSerial=%s AND bCamera=%s', oCamera.getSerial(), oCamera.getCamera() )

				dbgMsg( 'deleted camera serial-[%d] camera-[%d]' % ( oCamera.getSerial(), oCamera.getCamera() ) )
				return True

			except Exception, e:
				raise Exception, 'error while attempting to delete camera object [%s]' % e

		finally:
			self._oLock.release()
