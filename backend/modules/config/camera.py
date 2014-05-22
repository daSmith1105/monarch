##
## camera.py
##

##
# Includes
#
# System
import os, commands, threading
# Logging
from lib.messaging import stdMsg, dbgMsg, errMsg, setDebugging
# Cache
from lib.cache import Cache
# Camera Object
import db.camera


class Camera:

	def __init__(self):
		libCache = Cache()

		# Properties
		self._dbCameraList = libCache.get('dbCameraList')
		self._dbServerList = libCache.get('dbServerList')

	def _freezeCamera(self, oCamera):
		""" Flatten camera object to associative array. """

		try:
			rgsCamera = {}
			rgsCamera['bSerial'] = oCamera.getSerial()
			if rgsCamera['bSerial'] is None: rgsCamera['bSerial'] = 0
			rgsCamera['bCamera'] = oCamera.getCamera()
			if rgsCamera['bCamera'] is None: rgsCamera['bCamera'] = 0
			rgsCamera['bTimestamp'] = oCamera.getTimestamp()
			if rgsCamera['bTimestamp'] is None: rgsCamera['bTimestamp'] = 0
			rgsCamera['fSkip'] = oCamera.checkHasSkip()
			if rgsCamera['fSkip'] is None: rgsCamera['fSkip'] = False

			return rgsCamera

		except Exception, e:
			raise Exception, 'error freezing camera [%s]' % e

	def _thawCamera(self, rgsCamera):
		""" Create camera object from associative array. """

		try:
			oCamera = db.camera.CameraEntry()
			oCamera.setSerial(rgsCamera['bSerial'])
			oCamera.setCamera(rgsCamera['bCamera'])
			oCamera.setTimestamp(rgsCamera['bTimestamp'])
			oCamera.setSkip(rgsCamera['fSkip'])

			return oCamera

		except Exception, e:
			raise Exception, 'error thawing camera [%s]' % e

	def getAllCameras(self):
		""" Get all registered cameras """

		try:
			rgoResult = []
			rgoCamera = self._dbCameraList.getList()
			for oCamera in rgoCamera:
				# Filter out non-maintenance and test servers
				oServer = self._dbServerList.getServer( bSerial=oCamera.getSerial() )
				if oServer is None or \
				   oServer.getMaintenance() == 'no' or \
				   oServer.getPreferred() == 'test': continue

				rgsCamera = self._freezeCamera( oCamera )
				# Get Server Name for this camera
				rgsCamera[ 'sServer' ] = oServer.getName()
				rgoResult.append( rgsCamera )

			return rgoResult

		except Exception, e:
			errMsg('error getting camera list [%s]' % e)
			raise Exception, 'error getting camera list'

	def getCamera(self, bSerial, bCamera):
		""" Get camera object by Serial """

		try:
			oCamera = self._dbCameraList.getCamera(bSerial, bCamera)
			if oCamera is None:
				return {}

			oServer = self._dbServerList.getServer( bSerial=bSerial )
			rgsCamera = self._freezeCamera( oCamera )
			rgsCamera[ 'sServer' ] = ''
			if oServer is not None:
				rgsCamera[ 'sServer' ] = oServer.getName()

			return rgsCamera

		except Exception, e:
			errMsg('error getting camera by Serial [%s]' % e)
			raise Exception, 'error getting camera by Serial'

	def setCamera( self, rgsCamera ):
		""" Set camera in database. """

		try:
			oCamera = self._thawCamera( rgsCamera )
			self._dbCameraList.setCamera( oCamera )

			return True

		except Exception, e:
			errMsg( 'error setting camera [%s]' % e )
			raise Exception, 'error setting camera'

	def delCamera( self, rgsCamera ):
		""" Delete camera from database. """

		try:
			oCamera = self._thawCamera( rgsCamera )
			return self._dbCameraList.delCamera( oCamera )

		except Exception, e:
			errMsg( 'error deleting camera [%s]' % e )
			raise Exception, 'error deleting camera'
