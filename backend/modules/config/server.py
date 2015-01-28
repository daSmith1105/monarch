##
## server.py
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
# Server Object
import db.server


class Server:

	def __init__(self):
		libCache = Cache()

		# Properties
		self._dbServerList = libCache.get('dbServerList')
		self._modKey = libCache.get('modKey' )

	def _freezeServer(self, oServer):
		""" Flatten server object to associative array. """

		try:
			rgsServer = {}
			rgsServer['bSerial'] = oServer.getSerial()
			if rgsServer['bSerial'] is None: rgsServer['bSerial'] = 0
			rgsServer['bController'] = oServer.getController()
			if rgsServer['bController'] is None: rgsServer['bController'] = 0
			rgsServer['sCompany'] = oServer.getCompany()
			if rgsServer['sCompany'] is None: rgsServer['sCompany'] = ''
			rgsServer['sName'] = oServer.getName()
			if rgsServer['sName'] is None: rgsServer['sName'] = ''
			rgsServer['sCategories'] = oServer.getCategories()
			if rgsServer['sCategories'] is None: rgsServer['sCategories'] = ''
			rgsServer['sPreferred'] = oServer.getPreferred()
			if rgsServer['sPreferred'] is None: rgsServer['sPreferred'] = ''
			rgsServer['sIP'] = oServer.getIP()
			if rgsServer['sIP'] is None: rgsServer['sIP'] = '000.000.000.000'
			rgsServer['sRemoteIP'] = oServer.getRemoteIP()
			if rgsServer['sRemoteIP'] is None: rgsServer['sRemoteIP'] = '000.000.000.000'
			rgsServer['sLocalIP'] = oServer.getLocalIP()
			if rgsServer['sLocalIP'] is None: rgsServer['sLocalIP'] = '000.000.000.000'
			rgsServer['bPort'] = oServer.getPort()
			if rgsServer['bPort'] is None: rgsServer['bPort'] = 80
			rgsServer['bSshPort'] = oServer.getSshPort()
			if rgsServer['bSshPort'] is None: rgsServer['bSshPort'] = 80
			rgsServer['sHostname'] = oServer.getHostname()
			if rgsServer['sHostname'] is None: rgsServer['sHostname'] = ''
			rgsServer['bTimestamp'] = oServer.getTimestamp()
			if rgsServer['bTimestamp'] is None: rgsServer['bTimestamp'] = 0
			rgsServer['bInstall'] = oServer.getInstall()
			if rgsServer['bInstall'] is None: rgsServer['bInstall'] = 0
			rgsServer['sMaintenance'] = oServer.getMaintenance()
			if rgsServer['sMaintenance'] is None: rgsServer['sMaintenance'] = ''
			rgsServer['bMaintenanceOnsite'] = oServer.getMaintenanceOnsite()
			if rgsServer['bMaintenanceOnsite'] is None: rgsServer['bMaintenanceOnsite'] = 0
			rgsServer['fSkip'] = oServer.checkHasSkip()
			if rgsServer['fSkip'] is None: rgsServer['fSkip'] = False
			rgsServer['fSick'] = oServer.checkIsSick()
			if rgsServer['fSick'] is None: rgsServer['fSick'] = False
			rgsServer['sOS'] = oServer.getOS()
			if rgsServer['sOS'] is None: rgsServer['sOS'] = ''
			rgsServer['sVersionInstalled'] = oServer.getVersionInstalled()
			if rgsServer['sVersionInstalled'] is None: rgsServer['sVersionInstalled'] = ''
			rgsServer['sVersion'] = oServer.getVersion()
			if rgsServer['sVersion'] is None: rgsServer['sVersion'] = ''
			rgsServer['bNumcam'] = oServer.getNumcam()
			if rgsServer['bNumcam'] is None: rgsServer['bNumcam'] = 0
			rgsServer['sMac'] = oServer.getMac()
			if rgsServer['sMac'] is None: rgsServer['sMac'] = ''
			rgsServer['sKey'] = oServer.getKey()
			if rgsServer['sKey'] is None: rgsServer['sKey'] = ''
			rgsServer['sPosKey'] = oServer.getPosKey()
			if rgsServer['sPosKey'] is None: rgsServer['sPosKey'] = ''
			rgsServer['bPosLock'] = oServer.getPosLock()
			if rgsServer['bPosLock'] is None: rgsServer['bPosLock'] = 0
			rgsServer['sKill'] = oServer.getKill()
			if rgsServer['sKill'] is None: rgsServer['sKill'] = ''
			rgsServer['fEnterprise'] = oServer.checkHasEnterprise()
			if rgsServer['fEnterprise'] is None: rgsServer['fEnterprise'] = False
			rgsServer['fAuth'] = oServer.checkHasAuth()
			if rgsServer['fAuth'] is None: rgsServer['fAuth'] = False
			rgsServer['sSeed'] = oServer.getSeed()
			if rgsServer['sSeed'] is None: rgsServer['sSeed'] = ''
			rgsServer['sFeatures'] = oServer.getFeatures()
			if rgsServer['sFeatures'] is None: rgsServer['sFeatures'] = ''

			return rgsServer

		except Exception, e:
			raise Exception, 'error freezing server [%s]' % e

	def _thawServer(self, rgsServer):
		""" Create server object from associative array. """

		try:
			oServer = db.server.ServerEntry()
			oServer.setSerial(rgsServer['bSerial'])
			oServer.setController(rgsServer['bController'])
			oServer.setCompany(rgsServer['sCompany'])
			oServer.setName(rgsServer['sName'])
			oServer.setCategories(rgsServer['sCategories'])
			oServer.setPreferred(rgsServer['sPreferred'])
			oServer.setIP(rgsServer['sIP'])
			oServer.setRemoteIP(rgsServer['sRemoteIP'])
			oServer.setLocalIP(rgsServer['sLocalIP'])
			oServer.setPort(rgsServer['bPort'])
			oServer.setSshPort(rgsServer['bSshPort'])
			oServer.setHostname(rgsServer['sHostname'])
			oServer.setTimestamp(rgsServer['bTimestamp'])
			oServer.setInstall(rgsServer['bInstall'])
			oServer.setMaintenance(rgsServer['sMaintenance'])
			oServer.setMaintenanceOnsite(rgsServer['bMaintenanceOnsite'])
			oServer.setHasSkip(rgsServer['fSkip'])
			oServer.setIsSick(rgsServer['fSick'])
			oServer.setOS(rgsServer['sOS'])
			oServer.setVersionInstalled(rgsServer['sVersionInstalled'])
			oServer.setVersion(rgsServer['sVersion'])
			oServer.setNumcam(rgsServer['bNumcam'])
			oServer.setMac(rgsServer['sMac'])
			oServer.setKey(rgsServer['sKey'])
			oServer.setPosKey(rgsServer['sPosKey'])
			oServer.setPosLock(rgsServer['bPosLock'])
			oServer.setKill(rgsServer['sKill'])
			oServer.setEnterprise(rgsServer['fEnterprise'])
			oServer.setAuth(rgsServer['fAuth'])
			oServer.setSeed(rgsServer['sSeed'])
			oServer.setFeatures(rgsServer['sFeatures'])

			return oServer

		except Exception, e:
			raise Exception, 'error thawing server [%s]' % e

	def getAllServers(self):
		""" Get all registered servers """

		try:
			rgoResult = []
			rgoServer = self._dbServerList.getList()
			for oServer in rgoServer:
				rgoResult.append(self._freezeServer(oServer))

			return rgoResult

		except Exception, e:
			errMsg('error getting server list [%s]' % e)
			raise Exception, 'error getting server list'

	def getAllServersAlive(self):
		""" Get all registered servers that are alive (checking in) """

		try:
			rgoResult = []
			rgoServer = self._dbServerList.getList()
			for oServer in rgoServer:
				if oServer.checkIsAlive():
					rgoResult.append(self._freezeServer(oServer))

			return rgoResult

		except Exception, e:
			errMsg('error getting server list [%s]' % e)
			raise Exception, 'error getting server list'

	def getAllServersBySerial( self, rgbSerial ):
		""" Get all registered servers that are in this serial list. """

		try:
			# Workaround for javascript sending a dict instead of array
			if isinstance( rgbSerial, dict ):
				rgb = []
				for ix in rgbSerial:
					rgb.append( rgbSerial[ ix ] )
				rgbSerial = rgb

			rgoResult = []
			rgoServer = self._dbServerList.getList()
			for oServer in rgoServer:
				if oServer.getSerial() in rgbSerial:
					rgoResult.append( self._freezeServer( oServer ) )

			return rgoResult

		except Exception, e:
			errMsg( 'error getting server list [%s]' % e )
			raise Exception, 'error getting server list'

	def getAllServersByRange( self, bStart, bEnd ):
		""" Get all registered servers that are in this serial range. """

		try:
			rgoResult = []
			rgoServer = self._dbServerList.getList()
			for oServer in rgoServer:
				if oServer.getSerial() >= bStart and oServer.getSerial() <= bEnd:
					rgoResult.append( self._freezeServer( oServer ) )

			return rgoResult

		except Exception, e:
			errMsg( 'error getting server list [%s]' % e )
			raise Exception, 'error getting server list'

	def getServerBySerial(self, bSerial):
		""" Get server object by Serial """

		try:
			oServer = self._dbServerList.getServer(bSerial=bSerial)
			if oServer is None:
				return {}
			return self._freezeServer(oServer)

		except Exception, e:
			errMsg('error getting server by Serial [%s]' % e)
			raise Exception, 'error getting server by Serial'

	def getServerByName(self, sName):
		""" Set server object by Name """

		try:
			oServer = self._dbServerList.getServer(sName=sName)
			if oServer is None:
				return {}
			return self._freezeServer(oServer)

		except Exception, e:
			errMsg('error getting server by Name [%s]' % e)
			raise Exception, 'error getting server by Name'

	def setServer( self, rgsServer ):
		""" Set server in database. """

		try:
			oServerNew = self._thawServer( rgsServer )

			# See if we need to generate new Key
			oServer = self._dbServerList.getServer( bSerial=oServerNew.getSerial() )
			if oServer.getVersion() != oServerNew.getVersion() or \
			   oServer.getNumcam() != oServerNew.getNumcam() or \
			   oServer.getMac() != oServerNew.getMac():
				try:
					oServerNew.setKey( self._modKey.makeKey(
						oServerNew.getSerial(),
						oServerNew.getVersion(),
						oServerNew.getNumcam(),
						oServerNew.getMac()
					) )
				except Exception, e:
					oServerNew.setKey( '' )

			if oServer.getMac() != oServerNew.getMac() or \
			   oServer.getPosLock() != oServerNew.getPosLock():
				try:
					oServerNew.setPosKey( self._modKey.makeKeyPos(
						oServerNew.getSerial(),
						oServerNew.getPosLock(),
						oServerNew.getMac()
					) )
				except Exception, e:
					oServerNew.setPosKey( '' )
					oServerNew.setPosLock( 0 )
					
			self._dbServerList.setServer( oServerNew )

			return self._freezeServer( oServerNew )

		except Exception, e:
			errMsg( 'error setting server [%s]' % e )
			raise Exception, 'error setting server'

	def addServer( self, bSerial ):
		""" Set server in database. """

		try:
			oServer = self._dbServerList.addServer( bSerial )
			return self._freezeServer( oServer )

		except Exception, e:
			errMsg( 'error adding server [%s]' % e )
			raise Exception, 'error adding server'
