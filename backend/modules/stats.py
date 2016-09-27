##
## stats.py
##

##
# Includes
#
# General
import os, time, threading
# Logging
from lib.messaging import stdMsg, dbgMsg, errMsg
# Internal
import lib.cache

class Stats:

	def __init__( self ):
		""" Initialize Stats Module """

		libCache = lib.cache.Cache()
		self._dbServerList = libCache.get( 'dbServerList' )
		self._dbCameraList = libCache.get( 'dbCameraList' )
		self._libDBbug = libCache.get( 'libDBbug' )
		self._oLock = threading.RLock()

		# Should we run in offline mode?
		self._fOffline = False
		if os.access( '/rda/devel', os.F_OK ):
			self._fOffline = True

	def iplist( self, sName, sPass, fForce=False ):
		""" List all servers """

		try:
			rgoResult = []
			for oServer in self._dbServerList.getList():
				rgoResult.append( [
					oServer.getSerial(),
					oServer.getIP(),
					oServer.getName()
				] )

			return rgoResult

		except Exception, e:
			errMsg('error while generating server ip list [%s]' % e)
			raise Exception, "System error while generating server ip list."

	def updateIP( self, bSerial, sIPLookup, sIP=None, bPort=None, bSerialController=0 ):
		""" Update IP address, Port, and Heartbeat for this Server """

		try:
			# Initialize default return value
			rgoResult = [ bSerial, sIP ]

			if sIP == 'None': sIP = None
			if bPort == 'None': bPort = None
			try:
				bSerial = int( bSerial )
			except ValueError:
				return rgoResult
			try:
				if bPort is not None:
					bPort = int( bPort )
			except ValueError:
				return rgoResult

			# Dynamically get ip address from request
			if sIP is None or sIP == 'None':
				sIP = sIPLookup
			rgoResult[ 1 ] = sIP

			# Find Server object
			oServer = self._dbServerList.getServer( bSerial=bSerial )
			if oServer is None:
				if bSerial < 4000:
					raise Exception, 'unknown serial [%s]' % bSerial
				else:
					# This is a devel system, don't log error
					return rgoResult

			# Append kill status if we intend to kill this DVS (pirate?)
			if oServer.getKill() != '':
				rgoResult.append( oServer.getKill() )

			# Determine Port
			if bPort is None or bPort == 'None':
				bPort = oServer.getPort()

			# Hack for old rda-clients
			rgs = sIP.split( ':' )
			if len( rgs ) > 1:
				bPort = int( rgs[ 1 ] )
				sIP = rgs[ 0 ]
				dbgMsg( 'old rda-client format detected ip-[%s] port-[%s]' % ( sIP, bPort ) )

			# Update return information
			rgoResult[ 1 ] = sIP
			if bPort != 80:
				rgoResult[ 1 ] = '%s:%s' % ( sIP, bPort )

			# Finally, save updates to server object
			oServer.setIP( sIP )
			oServer.setRemoteIP( sIPLookup )
			oServer.setPort( bPort )
			oServer.setController( bSerialController )
			oServer.setTimestamp( time.time() )
			self._dbServerList.setServer( oServer )

			#stdMsg( 'ip updated for serial-[%3s] ip-[%15s] remoteip-[%15s] port-[%4s] controller-[%3s]' % ( bSerial, sIP, sIPLookup, bPort, bSerialController ) )

			return rgoResult

		except Exception, e:
			errMsg('error updateing ip [%s]' % e)
			#raise Exception, "System error updating ip."
			return rgoResult

	def getIP( self, bSerial ):
		""" Retrieve IP address for Server by Serial. """

		try:
			oServer = self._dbServerList.getServer( bSerial=bSerial )
			if not oServer.checkIsAlive():
				return '127.0.0.1'

			sIP = oServer.getIP()
			if oServer.getPort() != 80:
				sIP = '%s:%s' % ( sIP, oServer.getPort() )

			return sIP

		except Exception, e:
			errMsg( 'error retrieving ip address [%s]' % e )
			raise Exception, "System error retrieving ip address."

	def newserver( self, bSerial, sIP, sName, sUrl, sVersion='2.5' ):
		""" Register new Server in our Database. """

		try:
			# Block all access to adding new servers unless they are within our network
			#rgsIP = sIP.split( '.' )
			#if not ( rgsIP[ 0 ] == '192' and rgsIP[ 1 ] == '168' and rgsIP[ 2 ] == '0' ):
			rgsDividia = [ '24.178.194.110', '75.93.27.4', '47.51.193.54' ]
			if sIP not in rgsDividia:
				dbgMsg( 'blocking newserver call from outside Dividia network [%s]' % sIP )
				return False

			bSerial = int( bSerial )

			# Block any >= 4000 serial since these are currently used as development systems and shouldn't be in the DB
			if bSerial >= 4000:
				dbgMsg( 'blocking newserver call for development serial >= 4000 [%s]' % sIP )
				return False

			oServer = self._dbServerList.getServer( bSerial=bSerial )
			if oServer is not None:
				dbgMsg( 'server [%s] already exists' % bSerial )
				return False

			oServer = self._dbServerList.addServer( bSerial )
			oServer.setName( sName )
			oServer.setCategories( sUrl )
			oServer.setPreferred( sUrl )
			oServer.setIP( '127.0.0.1' )
			oServer.setRemoteIP( '127.0.0.1' )
			oServer.setVersion( sVersion )
			self._dbServerList.setServer( oServer )

			try:
				self._oLock.acquire()

				try:
					# Add this serial to our Bugzilla installation for Support
					rgoResult = self._libDBbug.query( 'SELECT id FROM products WHERE name=%s', 'Support' )

					if rgoResult is not None:
						bProduct = int( rgoResult[ 0 ][ 0 ] )
						sSerial = '%03d' % bSerial
						# Loop here to make sure it gets added
						for ix in range( 0, 5 ):
							self._libDBbug.query( 'INSERT INTO versions (value, product_id) VALUES (%s, %s)', sSerial, bProduct )
							rgoResult = self._libDBbug.query( 'SELECT value FROM versions WHERE product_id=%s AND value=%s', bProduct, sSerial )
							if rgoResult is not None and len( rgoResult ) > 0:
								stdMsg( 'added new serial to Bugzilla [%s]' % sSerial )
								break

				except Exception, e:
					errMsg( 'error adding serial to Bugzilla' )
					errMsg( e )

			finally:
				self._oLock.release()

			stdMsg( 'new serial added to system serial-[%d] name-[%s] url-[%s] version-[%s]' % ( bSerial, sName, sUrl, sVersion ) )

			return True

		except Exception, e:
			errMsg( 'error registering new server [%s]' % e )
			raise Exception, "System error registering new server."

	def upgradedvs( self, bSerial, sOS, sVersion ):
		"""
		DEPRECATED
		Upgrade DVS repo to 3.0.
		This function is no longer used >=3.1.
		Instead rda-backend will communicate the OS and DVS version to
		us periodically like a heartbeat.  It will call setupRepo instead.

		Params are: bSerial, sOS {8.0,co4,co5}, sVersion {dvs-2.0,dvs-2.5,dvs-3.0}
		"""

		try:
			# Parse sVersion and send to setupRepo to check and update
			if not self.setupRepo( bSerial, sOS, sVersion.split( 'dvs-' )[ 1 ] ):
				raise Exception, 'could not upgrade dvs'

			stdMsg( 'serial updated serial-[%d] os-[%s] version-[%s]' % ( bSerial, sOS, sVersion ) )

			return True

		except Exception, e:
			errMsg( 'error upgrading DVS repo [%s]' % e )
			raise Exception, "System error upgrading DVS repo."

	def setupRepo( self, bSerial, sOS, sVersion ):
		"""
		If sVersion is eligible for changing repo?
		Yes - update YUM repo.
		No - skip update and return failure.
		"""

		try:
			# Find Server object
			oServer = self._dbServerList.getServer( bSerial=bSerial )
			if oServer is None:
				dbgMsg( 'unknown serial [%s]' % bSerial )
				return ( False, 'unknown serial' )

			# Store this OS/Version so we know what is already installed
			if oServer.getOS() != sOS or \
			   oServer.getVersionInstalled() != sVersion:
				oServer.setOS( sOS )
				oServer.setVersionInstalled( sVersion )
				self._dbServerList.setServer( oServer )

			# Verify Server is elibile for version repo
			sVersionRepo = ''
			try:
				rgs = sVersion.split( '.' )
				bMajor1 = int( rgs[ 0 ] )
				bMinor1 = int( rgs[ 1 ] )
				bDoubleMinor1 = 0
				if len( rgs ) > 2:
					bDoubleMinor1 = int( rgs[ 2 ] )

				rgs = oServer.getVersion().split( '.' )
				bMajor2 = int( rgs[ 0 ] )
				bMinor2 = int( rgs[ 1 ] )
				bDoubleMinor2 = 0
				if len( rgs ) > 2:
					bDoubleMinor2 = int( rgs[ 2 ] )

				if bMajor1 > bMajor2 or \
				     ( bMajor1 == bMajor2 and \
				       bMinor1 > bMinor2 ):
					dbgMsg( 'version not supported for serial-[%s]' % bSerial )
					return ( False, 'version not eligible' )

				# Auto Promotion
				# If Monarch has a newer version listed for keying, let's
				# see if we can auto-promote this system.  First we make
				# sure this new version/repo is supported on the installed
				# OS.  If not, just setup as the old repo.
				# Alpha/Beta dminor>=90 is handled separately
				if bDoubleMinor1 < 90 and ( bMajor2 > bMajor1 or bMinor2 > bMinor1 ):
					# First check if this is a 3.X upgrade, if so, lock out for RH8
					if bMajor2 >= 3 and sOS == '8.0':
						pass

					else:
						# Promote
						bMajor1 = bMajor2
						bMinor1 = bMinor2
						bDoubleMinor1 = bDoubleMinor2

				# Handle special case if this is an alpha/beta release
				# Check double minor >= 90
				# If yes, then bump our repo to the next minor version
				if bDoubleMinor1 >= 90:
					bMinor1 += 1
					bDoubleMinor1 = 0

				# This is murky.  Basically, normal repos are 3.0, 3.1, 3.2 ...
				# However, since we introduced 3.1.1, there is really a 3.1.1
				# Do we want to change this format for all going forward?
				# If so, then enable the below code block.  If not, then
				# just leave our 3.1.1 workaround in
				##if bDoubleMinor1 == 0:
				##	sVersionRepo = 'dvs-%d.%d' % ( bMajor1, bMinor1 )
				##else:
				##	sVersionRepo = 'dvs-%d.%d.%d' % ( bMajor1, bMinor1, bDoubleMinor1 )
				# Removing this code block since we merged our 3.1.1 tree with 3.1, so
				# We no longer need to handle this special case
				##if bMajor1 == 3 and bMinor1 == 1 and bDoubleMinor1 == 1:
				##	sVersionRepo = 'dvs-%d.%d.%d' % ( bMajor1, bMinor1, bDoubleMinor1 )
				##else:
				##	sVersionRepo = 'dvs-%d.%d' % ( bMajor1, bMinor1 )
				sVersionRepo = 'dvs-%d.%d' % ( bMajor1, bMinor1 )

			except Exception, e:
				dbgMsg( 'error verifying version' )
				dbgMsg( e )
				return ( False, 'error verifying version' )

			# Alright, they are eligible so attempt repo update
			if self._fOffline:
				dbgMsg( 'running in offline mode, skipping' )
				return ( True, '' )

			os.system( 'ssh webhost.dividia.net "/usr/local/bin/add_id.sh %s %s %s 1>/dev/null 2>/dev/null"' % ( bSerial, sOS, sVersionRepo ) )

			return ( True, '' )

		except Exception, e:
			errMsg( 'error setting up YUM repo.' )
			errMsg( e )
			raise Exception, "System error setting up YUM repo."

	def cameraFail( self, bSerial, rgbCamera, sStatus='' ):
		""" Server is notifying us that a camera is failed or restored. """

		try:
			try:
				bSerial = int( bSerial )
			except:
				return False

			if not isinstance( rgbCamera, list ):
				# Old style.  This should be removed after dvs-3.0 comes out and we have time to upgrade all systems.
				#dbgMsg( 'camera failure reported using old style' )

				bCamera = rgbCamera
				try:
					bCamera = int( bCamera )
				except:
					return False

				oCamera = self._dbCameraList.getCamera( bSerial, bCamera )
				if oCamera is None:
					if sStatus == 'fail':
						self._dbCameraList.addCamera( bSerial, bCamera )
						stdMsg( 'camera failed serial-[%d] camera-[%d]' % ( bSerial, bCamera ) )
					return True

				if oCamera is not None:
					if sStatus == 'restore':
						# Make sure it is not marked as permenantly failed
						if not oCamera.checkHasSkip():
							self._dbCameraList.delCamera( oCamera )
						stdMsg( 'camera restored serial-[%d] camera-[%d]' % ( bSerial, bCamera ) )
					return True

				return False

			else:
				# New style.  We are only receiving a camera array of failed cameras, all others are expected to be restored.
				#dbgMsg( 'camera failure reported using new style' )

				# Delete all cameras that were not sent to us since they have been restored
				for ixCam in range( 1, 17 ):
					if ixCam in rgbCamera: continue
					oCamera = self._dbCameraList.getCamera( bSerial, ixCam )
					if oCamera is None: continue
					if oCamera.checkHasSkip(): continue
					self._dbCameraList.delCamera( oCamera )
					stdMsg( 'camera restored serial-[%d] camera-[%d]' % ( bSerial, ixCam ) )

				# Now insert new failed cameras into database
				for bCamera in rgbCamera:
					oCamera = self._dbCameraList.getCamera( bSerial, bCamera )
					if oCamera is not None: continue
					self._dbCameraList.addCamera( bSerial, bCamera )
					stdMsg( 'camera failed serial-[%d] camera-[%d]' % ( bSerial, bCamera ) )

				return True

		except Exception, e:
			errMsg( 'error updating camera fail info [%s]' % e )
			raise Exception, "System error updating camera fail info."

	def isAlive( self, bSerial ):
		""" Let clients test whether they are alive by calling us. """

		try:
			return True

		except Exception, e:
			errMsg( 'error serving alive call [%s]' % e )
			raise Exception, "System error serving alive call."

	def lookupByCompanyCode( self, sCompanyCode ):
		""" Find the IP information by company code. """

		try:
			for oServer in self._dbServerList.getList():
				if not oServer.checkHasCategory( sCompanyCode ): continue
				if oServer.getController() != 0: continue
				result = oServer.getIP()
				if oServer.getPort() != 80:
					result += ":%d" % oServer.getPort()
				return (True,result)

			return (True,"")

		except Exception, e:
			errMsg( 'error looking up company code [%s]' % e )
			raise Exception, "System error looking up ip by company code."

	def _freezeServer(self, oServer):
		""" Flatten server object to associative array. """

		try:
			rgsServer = {}
			rgsServer['bSerial'] = oServer.getSerial()
			if rgsServer['bSerial'] is None: rgsServer['bSerial'] = 0
			rgsServer['sCompany'] = oServer.getCompany()
			if rgsServer['sCompany'] is None: rgsServer['sCompany'] = ''
			rgsServer['sName'] = oServer.getName()
			if rgsServer['sName'] is None: rgsServer['sName'] = ''
			rgsServer['sIP'] = oServer.getIP()
			if rgsServer['sIP'] is None: rgsServer['sIP'] = '000.000.000.000'
			#rgsServer['sRemoteIP'] = oServer.getRemoteIP()
			#if rgsServer['sRemoteIP'] is None: rgsServer['sRemoteIP'] = '000.000.000.000'
			rgsServer['sLocalIP'] = oServer.getLocalIP()
			if rgsServer['sLocalIP'] is None: rgsServer['sLocalIP'] = '000.000.000.000'
			rgsServer['bPort'] = oServer.getPort()
			if rgsServer['bPort'] is None: rgsServer['bPort'] = 80

			return rgsServer

		except Exception, e:
			raise Exception, 'error freezing server [%s]' % e

	def autocompleteServer( self, sSearch ):
		""" Find list of server names starting with search string. """

		try:
			result = []

			for oServer in self._dbServerList.getList( sSearch=sSearch ):
				if oServer.getName() == sSearch or oServer.checkHasCategory( sSearch ):
					# Matches exactly, so include no matter what
					result.append( self._freezeServer( oServer ) )
					continue

				# Filter out any that don't have video as a tag (meaning customer has requested we not show them in our list of results)
				if not oServer.checkHasCategory( 'video' ): continue
				if oServer.getPreferred() in [ 'test', 'closed', 'inactive', 'lost' ]: continue

				result.append( self._freezeServer( oServer ) )

			return ( True, result )

		except Exception, e:
			errMsg( 'error looking up autocomplete list [%s]' % e )
			raise Exception, "System error looking up autocomplete list."
