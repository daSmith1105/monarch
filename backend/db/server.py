##
## server.py
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


class ServerEntry:
	"""
	Server Object represents a registered server in our system.
	"""

	_bTimeDiffMax = 36000

	def __init__( self, bSerial=None, sCompany='Test', sName='Test', sCategories='test', sPreferred='test', sIP='127.0.0.1', sRemoteIP='127.0.0.1', sLocalIP='127.0.0.1', bPort=80, bSshPort=22, sHostname='', bTimestamp=None, bInstall=None, sMaintenance='install', bMaintenanceOnsite=None, fSkip=False, fSick=False, bController=0, sOS='', sVersionInstalled='', sVersion='3.0', bNumcam=0, sMac='', sKey='', sPosKey='', bPosLock=0, sKill='', fEnterprise=False, fAuth=False, sSeed='', sFeatures='' ):
		""" Setup Server Object for a certain server """

		self._bSerial = bSerial
		self._sCompany = sCompany
		self._sName = sName
		self._sCategories = sCategories
		self._sPreferred = sPreferred
		self._sIP = sIP
		self._sRemoteIP = sRemoteIP
		self._sLocalIP = sLocalIP
		self._bPort = bPort
		self._bSshPort = bSshPort
		self._sHostname = sHostname
		self._bTimestamp = bTimestamp
		self._bInstall = bInstall
		self._sMaintenance = sMaintenance
		self._bMaintenanceOnsite = bMaintenanceOnsite
		self._fSkip = False
		if fSkip:
			self._fSkip = True
		self._fSick = False
		if fSick:
			self._fSick = True
		self._bController = bController
		self._sOS = sOS
		self._sVersionInstalled = sVersionInstalled
		self._sVersion = sVersion
		self._bNumcam = bNumcam
		self._sMac = sMac
		self._sKey = sKey
		self._sPosKey = sPosKey
		self._bPosLock = bPosLock
		self._sKill = sKill
		self._fEnterprise = False
		if fEnterprise:
			self._fEnterprise = True
		self._fAuth = False
		if fAuth:
			self._fAuth = True
		self._sSeed = sSeed
		self._sFeatures = sFeatures

	def getSerial( self ):
		""" Return Serial associated with this server. """
		return self._bSerial

	def setSerial( self, bSerial ):
		""" Set new Serial for server object. """
		try:
			self._bSerial = int( bSerial )
		except ValueError, e:
			pass

	def getCompany( self ):
		""" Return Server Company. """
		return self._sCompany

	def setCompany( self, sCompany ):
		""" Set new Company for server. """
		self._sCompany = sCompany

	def getName( self ):
		""" Return Server Name. """
		return self._sName

	def setName( self, sName ):
		""" Set new Name for server. """
		self._sName = sName

	def getCategories( self ):
		""" Return Server Categories. """
		return self._sCategories

	def setCategories( self, sCategories ):
		""" Set new Categories for server. """
		self._sCategories = sCategories

	def getPreferred( self ):
		""" Return Server Preferred. """
		return self._sPreferred

	def checkHasCategory( self, sCategory ):
		""" Does this Server have this category? """
		try:
			rgs = self._sCategories.split( ',' )
			if sCategory in rgs:
				return True
			return False
		except:
			return False

	def setPreferred( self, sPreferred ):
		""" Set new Preferred for server. """
		self._sPreferred = sPreferred

	def getIP( self ):
		""" Return Server IP. """
		return self._sIP

	def setIP( self, sIP ):
		""" Set new IP address for server. """
		self._sIP = sIP

	def getRemoteIP( self ):
		""" Return Server Remote IP. """
		return self._sRemoteIP

	def setRemoteIP( self, sRemoteIP ):
		""" Set new Remote IP address for server. """
		self._sRemoteIP = sRemoteIP

	def getLocalIP( self ):
		""" Return Server Local IP. """
		return self._sLocalIP

	def setLocalIP( self, sLocalIP ):
		""" Set new LocalIP address for server. """
		self._sLocalIP = sLocalIP

	def getPort( self ):
		""" Return Server Port. """
		return self._bPort

	def setPort( self, bPort ):
		""" Set new port for server. """
		try:
			self._bPort = int( bPort )
		except:
			pass

	def getSshPort( self ):
		""" Return Server Ssh Port. """
		return self._bSshPort

	def setSshPort( self, bSshPort ):
		""" Set new ssh port for server. """
		try:
			self._bSshPort = int( bSshPort )
		except:
			pass

	def getHostname( self ):
		""" Return hostname for serial. """
		return self._sHostname

	def setHostname( self, sHostname ):
		""" Set hostname for serial. """
		self._sHostname = sHostname

	def getTimestamp( self ):
		""" Return the last time this server checked in. """
		return self._bTimestamp

	def setTimestamp( self, bTimestamp ):
		""" Set new timestamp for server. """
		self._bTimestamp = None
		if bTimestamp != 0:
			self._bTimestamp = bTimestamp

	def checkIsAlive( self ):
		""" Make sure our timestamp is relatively fresh. """
		if self._bTimestamp is None:
			return False
		return self._bTimeDiffMax > int( time.time() ) - self._bTimestamp

	def getInstall( self ):
		""" Return the last time this server checked in. """
		return self._bInstall

	def setInstall( self, bInstall ):
		""" Set new timestamp for server. """
		self._bInstall = None
		if bInstall != 0:
			self._bInstall = bInstall

	def getMaintenance( self ):
		""" Return maintenance plan for server. """
		return self._sMaintenance

	def setMaintenance( self, sMaintenance ):
		""" Set new local flag. """
		self._sMaintenance = sMaintenance

	def getMaintenanceOnsite( self ):
		""" Return the last time we opened an on-site maintenance ticket. """
		return self._bMaintenanceOnsite

	def setMaintenanceOnsite( self, bMaintenanceOnsite ):
		""" Set new timestamp for on-site maintenance ticket. """
		self._bMaintenanceOnsite = None
		if bMaintenanceOnsite != 0:
			self._bMaintenanceOnsite = bMaintenanceOnsite

	def checkHasSkip( self ):
		""" Return True if this server is local to our network. """
		return self._fSkip

	def setHasSkip( self, fSkip ):
		""" Set new local flag. """
		self._fSkip = False
		if fSkip:
			self._fSkip = True

	def checkIsSick( self ):
		""" Return True if this server has a misconfigured firewall. """
		return self._fSick

	def setIsSick( self, fSick ):
		""" Set new sick flag if this server has a misconfigured firewall. """
		self._fSick = False
		if fSick:
			self._fSick = True

	def getController( self ):
		""" Return the Controller Serial for server. """
		return self._bController

	def setController( self, bController ):
		""" Set new Controller Serial for server. """
		self._bController = bController

	def getOS( self ):
		""" Return OS for server. """
		return self._sOS

	def setOS( self, sOS ):
		""" Set new OS. """
		self._sOS = sOS

	def getVersionInstalled( self ):
		""" Return DVS Product VersionInstalled for server. """
		return self._sVersionInstalled

	def setVersionInstalled( self, sVersionInstalled ):
		""" Set new product VersionInstalled. """
		self._sVersionInstalled = sVersionInstalled

	def getVersion( self ):
		""" Return DVS Product Version for server. """
		return self._sVersion

	def setVersion( self, sVersion ):
		""" Set new product Version. """
		self._sVersion = sVersion

	def getNumcam( self ):
		""" Return the number of cameras supported for this server. """
		return self._bNumcam

	def setNumcam( self, bNumcam ):
		""" Set the number of cameras supported for this server. """
		try:
			self._bNumcam = int( bNumcam )
		except:
			pass

	def getMac( self ):
		""" Return the partial mac address of the first NIC on this server. """
		return self._sMac

	def setMac( self, sMac ):
		""" Set the partial mac address of the first NIC on this server. """
		self._sMac = sMac

	def getKey( self ):
		""" Return product key registered for this server. """
		return self._sKey

	def setKey( self, sKey ):
		""" Set product key registered for this server. """
		self._sKey = sKey
		
	def getPosKey( self ):
		""" Return product key registered for this server. """
		return self._sPosKey

	def setPosKey( self, sKey ):
		""" Set product key registered for this server. """
		self._sPosKey = sKey
		
	def getPosLock( self ):
		""" Return product key registered for this server. """
		return self._bPosLock

	def setPosLock( self, bPosLock ):
		""" Set product key registered for this server. """
		self._bPosLock = bPosLock

	def getKill( self ):
		""" Return kill status for this server if we are killing their DVS. """
		return self._sKill

	def setKill( self, sKill ):
		""" Set kill status string for this server if we intend to kill their DVS. """
		self._sKill = sKill

	def checkHasEnterprise( self ):
		""" Return True if this server is licensed for Enterprise Viewer. """
		return self._fEnterprise

	def setEnterprise( self, fEnterprise ):
		""" Set new enterprise flag. """
		self._fEnterprise = False
		if fEnterprise:
			self._fEnterprise = True

	def checkHasAuth( self ):
		""" Return True if this server is allowed to sync Auth credentials with us. """
		return self._fAuth

	def setAuth( self, fAuth ):
		""" Set new flag to allow Auth credentials syncing. """
		self._fAuth = False
		if fAuth:
			self._fAuth = True

	def getSeed( self ):
		""" Return Seed for server. """
		return self._sSeed

	def setSeed( self, sSeed ):
		""" Set new Seed. """
		self._sSeed = sSeed

	def getFeatures( self ):
		""" Return Features for server. """
		return self._sFeatures

	def setFeatures( self, sFeatures ):
		""" Set new Features. """
		self._sFeatures = sFeatures


class ServerList:
	"""
	Server module takes care of all server relating activities.
	 - Create new servers
	 - Removing servers
	 - Server lookups
	"""

	def __init__( self ):
		""" Initialize Server module """

		libCache = lib.cache.Cache()
		self._libDB = libCache.get( 'libDB' )
		self._oLock = threading.RLock()

	def size( self ):
		""" Return the number of servers we have loaded. """

		return len( self.getList() )

	def getList( self ):
		""" Return list copy of our servers. """

		try:
			self._oLock.acquire()

			try:
				rgoServer = []

				rgoResult = self._libDB.query( 'SELECT bSerial, sCompany, sName, sCategories, sPreferred, sIP, sRemoteIP, sLocalIP, bPort, bSshPort, sHostname, UNIX_TIMESTAMP(dTimestamp), UNIX_TIMESTAMP(dInstall), sMaintenance, UNIX_TIMESTAMP(dMaintenanceOnsite), fSkip, fSick, bController, sOS, sVersionInstalled, sVersion, bNumcam, sMac, sKey, sKeyPos, bPos, sKill, fEnterprise, fAuth, sSeed, sFeatures FROM Server ORDER BY bSerial' )

				for oRow in rgoResult:
					rgoServer.append(
						ServerEntry(
							oRow[0],
							oRow[1],
							oRow[2],
							oRow[3],
							oRow[4],
							oRow[5],
							oRow[6],
							oRow[7],
							oRow[8],
							oRow[9],
							oRow[10],
							oRow[11],
							oRow[12],
							oRow[13],
							oRow[14],
							oRow[15],
							oRow[16],
							oRow[17],
							oRow[18],
							oRow[19],
							oRow[20],
							oRow[21],
							oRow[22],
							oRow[23],
							oRow[24],
							oRow[25],
							oRow[26],
							oRow[27],
							oRow[28],
							oRow[29],
							oRow[30]
						)
					)

				return copy.copy( rgoServer )

			except Exception, e:
				raise Exception, 'error getting server list [%s]' % e

		finally:
			self._oLock.release()

	def getServer( self, bSerial=None, sName=None ):
		""" Return server object. """

		try:
			self._oLock.acquire()

			try:
				rgoResult = ()

				sQuery = 'SELECT bSerial, sCompany, sName, sCategories, sPreferred, sIP, sRemoteIP, sLocalIP, bPort, bSshPort, sHostname, UNIX_TIMESTAMP(dTimestamp), UNIX_TIMESTAMP(dInstall), sMaintenance, UNIX_TIMESTAMP(dMaintenanceOnsite), fSkip, fSick, bController, sOS, sVersionInstalled, sVersion, bNumcam, sMac, sKey, sKeyPos, bPos, sKill, fEnterprise, fAuth, sSeed, sFeatures FROM Server WHERE '
				if bSerial is not None:
					sQuery += 'bSerial=%s'
					rgoResult = self._libDB.query( sQuery, bSerial )

				elif sName is not None:
					sQuery += 'sName=%s'
					rgoResult = self._libDB.query( sQuery, sName )

				if len( rgoResult ) == 0:
					# Nothing found
					return None

				oRow = rgoResult[ 0 ]
				oServerEntry = ServerEntry(
					oRow[0],
					oRow[1],
					oRow[2],
					oRow[3],
					oRow[4],
					oRow[5],
					oRow[6],
					oRow[7],
					oRow[8],
					oRow[9],
					oRow[10],
					oRow[11],
					oRow[12],
					oRow[13],
					oRow[14],
					oRow[15],
					oRow[16],
					oRow[17],
					oRow[18],
					oRow[19],
					oRow[20],
					oRow[21],
					oRow[22],
					oRow[23],
					oRow[24],
					oRow[25],
					oRow[26],
					oRow[27],
					oRow[28],
					oRow[29],
					oRow[30]
				)

				return copy.copy( oServerEntry )

			except Exception, e:
				raise Exception, 'error getting server [%s]' % e

		finally:
			self._oLock.release()

	def setServer( self, oServer ):
		""" Update our Server Object. """

		try:
			self._oLock.acquire()

			try:
				oServerEntry = self.getServer( bSerial=oServer.getSerial() )
				if oServerEntry is not None:
					self._libDB.query( 'UPDATE Server SET sCompany=%s, sName=%s, sCategories=%s, sPreferred=%s, sIP=%s, sRemoteIP=%s, sLocalIP=%s, bPort=%s, bSshPort=%s, sHostname=%s, dTimestamp=FROM_UNIXTIME(%s), dInstall=FROM_UNIXTIME(%s), sMaintenance=%s, dMaintenanceOnsite=FROM_UNIXTIME(%s), fSkip=%s, fSick=%s, bController=%s, sOS=%s, sVersionInstalled=%s, sVersion=%s, bNumcam=%s, sMac=%s, sKey=%s, sKeyPos=%s, bPos=%s, sKill=%s, fEnterprise=%s, fAuth=%s, sSeed=%s, sFeatures=%s WHERE bSerial=%s',
						oServer.getCompany(),
						oServer.getName(),
						oServer.getCategories(),
						oServer.getPreferred(),
						oServer.getIP(),
						oServer.getRemoteIP(),
						oServer.getLocalIP(),
						oServer.getPort(),
						oServer.getSshPort(),
						oServer.getHostname(),
						oServer.getTimestamp(),
						oServer.getInstall(),
						oServer.getMaintenance(),
						oServer.getMaintenanceOnsite(),
						oServer.checkHasSkip(),
						oServer.checkIsSick(),
						oServer.getController(),
						oServer.getOS(),
						oServer.getVersionInstalled(),
						oServer.getVersion(),
						oServer.getNumcam(),
						oServer.getMac(),
						oServer.getKey(),
						oServer.getPosKey(),
						oServer.getPosLock(),
						oServer.getKill(),
						oServer.checkHasEnterprise(),
						oServer.checkHasAuth(),
						oServer.getSeed(),
						oServer.getFeatures(),
						oServer.getSerial()
					)

					# Detect if we removed Auth flag and remove users from database
					if not oServer.checkHasAuth() and oServerEntry.checkHasAuth():
						self._libDB.query( 'DELETE FROM CustUser WHERE bSerial=%s', oServer.getSerial() )

					#dbgMsg( 'updated server serial-[%d]' % oServer.getSerial() )
					return

				# Server does not exist, so add them
				# This is used by controller syncing
				self._libDB.query( 'INSERT INTO Server (bSerial,sCompany,sName,sCategories,sPreferred,sIP,sRemoteIP,sLocalIP,bPort,bSshPort,sHostname,dTimestamp,dInstall,sMaintenance,dMaintenanceOnsite,fSkip,fSick,bController,sOS,sVersionInstalled,sVersion,bNumcam,sMac,sKey,sKeyPos,bPos,sKill,fEnterprise,fAuth,sSeed,sFeatures) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,FROM_UNIXTIME(%s),FROM_UNIXTIME(%s),%s,FROM_UNIXTIME(%s),%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
					oServer.getSerial(),
					oServer.getCompany(),
					oServer.getName(),
					oServer.getCategories(),
					oServer.getPreferred(),
					oServer.getIP(),
					oServer.getRemoteIP(),
					oServer.getLocalIP(),
					oServer.getPort(),
					oServer.getSshPort(),
					oServer.getHostname(),
					oServer.getTimestamp(),
					oServer.getInstall(),
					oServer.getMaintenance(),
					oServer.getMaintenanceOnsite(),
					oServer.checkHasSkip(),
					oServer.checkIsSick(),
					oServer.getController(),
					oServer.getOS(),
					oServer.getVersionInstalled(),
					oServer.getVersion(),
					oServer.getNumcam(),
					oServer.getMac(),
					oServer.getKey(),
					oServer.getPosKey(),
					oServer.getPosLock(),
					oServer.getKill(),
					oServer.checkHasEnterprise(),
					oServer.checkHasAuth(),
					oServer.getSeed(),
					oServer.getFeatures()
				)
				dbgMsg( 'added server serial-[%d]' % oServer.getSerial() )

			except Exception, e:
				raise Exception, 'error updating server [%s]' % e

		finally:
			self._oLock.release()

	def addServer( self, bSerial=None ):
		""" Create new server entry. """

		try:
			self._oLock.acquire()

			try:
				# Hacky auto increment 
				if bSerial is None:
					res = self._libDB.query( 'SELECT MAX(bSerial) FROM Server' )
					bSerial = int( res[0][0] ) + 1
				 
				self._libDB.query( 'INSERT INTO Server (bSerial) VALUES (%s)', bSerial )

				oServerEntry = self.getServer( bSerial=bSerial )

				dbgMsg( 'added server serial-[%d]' % bSerial )

				return oServerEntry

			except Exception, e:
				raise Exception, 'error while attempting to add server object [%s]' % e

		finally:
			self._oLock.release()

	def delServer( self, oServer ):
		""" Remove server by id """

		try:
			self._oLock.acquire()

			try:
				oServerEntry = self.getServer( bSerial=oServer.getSerial() )
				if oServerEntry is None:
					dbgMsg( 'delete server serial-[%d] failed' % oServer.getSerial() )
					return False

				self._libDB.query( 'DELETE FROM Server WHERE bSerial=%s', oServer.getSerial() )

				# Detect if we removed Auth flag and remove users from database
				if oServer.checkHasAuth():
					self._libDB.query( 'DELETE FROM CustUser WHERE bSerial=%s', oServer.getSerial() )

				dbgMsg( 'deleted server serial-[%d]' % oServer.getSerial() )
				return True

			except Exception, e:
				raise Exception, 'error while attempting to delete server object [%s]' % e

		finally:
			self._oLock.release()
