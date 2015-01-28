##
## key.py
##

##
# Includes
#
# General
import commands, subprocess
# Logging
from lib.messaging import stdMsg, dbgMsg, errMsg
# Internal
import lib.cache


class Key:

	def __init__(self):
		""" Initialize Key Modules """

		libCache = lib.cache.Cache()
		self._dbServerList = libCache.get('dbServerList')

		self._libUtil = libCache.get('libUtil')

	def _getSerial( self, bSeed ):
		""" Parse seed and find Serial. """

		return ( bSeed >> 8 ) & 0xFFF

	def _setSerial( self, bSeed, bSerial ):
		""" Set serial in seed. """

		return ( bSerial << 8 ) | bSeed;

	def _getVersion( self, bSeed ):
		""" Parse seed and find Version. """

		bMinor = bSeed & 0xF
		bMajor = ( bSeed >> 4 ) & 0xF

		return '%X.%X' % ( bMajor, bMinor )

	def _setVersion( self, bSeed, sVersion ):
		""" Set version in seed. """

		try:
			rgs = sVersion.split( '.' )
			bMajor = int( rgs[ 0 ] )
			bMinor = int( rgs[ 1 ] )
		except:
			raise Exception, 'could not convert version for seed'

		bSeed |= bMinor
		bSeed |= bMajor << 4
		return bSeed

	def _getNumcam( self, bSeed ):
		""" Parse seed and find Numcam. """

		return ( ( bSeed >> 20 ) & 0xF ) + 1

	def _setNumcam( self, bSeed, bNumcam ):
		""" Set numcam in seed. """

		return ( ( bNumcam - 1 ) << 20 ) | bSeed;

	def _getMac( self, bSeed ):
		""" Parse seed and find Mac. """

		bMac = ( bSeed >> 24 ) & 0xFF
		return '%02X' % bMac

	def _setMac( self, bSeed, sMac ):
		""" Set mac in seed. """

		return ( int( sMac, 16 ) << 24 ) | bSeed;

	def _getPosLock( self, bSeed ):
		""" Parse seed and find Mac. """

		return ( bSeed & 0xFF )

	def _setPosLock( self, bSeed, bPosLock ):
		""" Set pos in seed. """
		
		if bPosLock > 255: bPosLock = 255
		if bPosLock < 0: bPosLock = 0
		bSeed &= 0xFFFFFF00
		bSeed |= bPosLock
		return bSeed
	
	def decomposeSeed( self, bSeed ):
		""" Decompose seed into Serial, Version, Numcam, and Mac. """

		try:
			bSeed = long( bSeed )
			
			# This is a copy of the functions in product-key/ck-common.c
			# They are rewritten here to save on shelling out with each
			# rda-backend that checks in.
			bSerial = self._getSerial( bSeed )
			sVersion = self._getVersion( bSeed )
			bNumcam = self._getNumcam( bSeed )
			sMac = self._getMac( bSeed )

			return ( bSerial, sVersion, bNumcam, sMac )

		except Exception, e:
			errMsg( 'error while decomposing key' )
			raise

	def decomposeSeedPos( self, bSeed ):
		""" Decompose POS seed into Serial, POS Lock, and Mac. """

		try:
			bSeed = long( bSeed )
			
			# This is a copy of the functions in product-key/ck-common.c
			# They are rewritten here to save on shelling out with each
			# rda-backend that checks in.
			bSerial = self._getSerial( bSeed )
			#sVersion = self._getVersion( bSeed )
			#bNumcam = self._getNumcam( bSeed )
			#Jake Add something here
			bPosLock = self._getPosLock(bSeed)
			sMac = self._getMac( bSeed )

			return ( bSerial, bPosLock, sMac )

		except Exception, e:
			errMsg( 'error while decomposing key' )
			raise
		
	def makeKey( self, bSerial, sVersion, bNumcam, sMac ):
		""" Make new product key based on seed. """

		bSeed = 0
		bSeed = self._setSerial( bSeed, bSerial )
		bSeed = self._setVersion( bSeed, sVersion )
		bSeed = self._setNumcam( bSeed, bNumcam )
		bSeed = self._setMac( bSeed, sMac )

		sKey = commands.getoutput( '/usr/local/bin/make-key -s %s' % bSeed )
		if len( sKey ) != 24:
			raise Exception, 'make-key did not return a valid key [%s]' % sKey

		return sKey

	def makeKeyPos( self, bSerial, bPosLock, sMac ):
		""" Make new product key based on seed. """

		bSeed = 0
		bSeed = self._setSerial( bSeed, bSerial )
		bSeed = self._setPosLock( bSeed, bPosLock )
		bSeed = self._setMac( bSeed, sMac )

		sPosKey = commands.getoutput( '/usr/local/bin/make-key -s %s -p %s' % (bSeed, bPosLock) )
		if len( sPosKey ) != 24:
			raise Exception, 'make-key did not return a valid key [%s]' % sPosKey

		return sPosKey

	def getKeyDVS( self, bSeed ):
		""" Decompose Seed and check credentials.  If they match, then return Product Key. """

		try:
			bSeed = long( bSeed )
			
			( bSerial, sVersion, bNumcam, sMac ) = self.decomposeSeed( bSeed )

			# Skip reporting on devel serials
			if bSerial >= 4000:
				return ( False, 'Unknown Server' )

			dbgMsg( 'getting key for seed-[%d] serial-[%d] version-[%s] numcam-[%d] mac-[%s]' % ( bSeed, bSerial, sVersion, bNumcam, sMac ) )

			# Make sure this server exists
			oServer = self._dbServerList.getServer( bSerial=bSerial )
			if oServer is None:
				dbgMsg( 'server [%d] does not exists?' % bSerial )
				return ( False, 'Unknown Server' )

			# If Numcam and/or Mac are blank for this Server object
			# then we will allow this system to auto-key this time
			if oServer.getNumcam() == 0:
				dbgMsg( 'automatically setting numcam [%d] from seed' % bNumcam )
				oServer.setNumcam( bNumcam )
				oServer.setKey( '' )
			if oServer.getMac() == '':
				dbgMsg( 'automatically setting mac [%s] from seed' % sMac )
				oServer.setMac( sMac )
				oServer.setKey( '' )

			# Now, check all key items
			if sVersion != oServer.getVersion():
				dbgMsg( 'key check failed [version mismatch] [%s != %s]' % ( sVersion, oServer.getVersion() ) )
				return ( False, 'version mismatch' )

			if bNumcam != oServer.getNumcam():
				dbgMsg( 'key check failed [numcam mismatch] [%d != %d]' % ( bNumcam, oServer.getNumcam() ) )
				return ( False, 'numcam mismatch' )

			if sMac != oServer.getMac():
				dbgMsg( 'key check failed [mac mismatch] [%s != %s]' % ( sMac, oServer.getMac() ) )
				return ( False, 'mac mismatch' )

			# We passed!  Make new key if we do not have one
			if oServer.getKey() == '':
				sKey = self.makeKey( bSerial, sVersion, bNumcam, sMac )
				dbgMsg( 'making new key serial-[%d] key-[%s]' % ( bSerial, sKey ) )
				oServer.setKey( sKey )

			# Save server information back to database in case we changed something
			self._dbServerList.setServer( oServer )

			dbgMsg( 'serial-[%d] has valid key' % bSerial )
			return ( True, oServer.getKey() )

		except Exception, e:
			errMsg( 'error while getting product key' )
			errMsg( e )
			raise Exception, "System error during keying process."

	def getKeyPos( self, bSeed ):
		""" Decompose Seed and check credentials.  If they match, then return Product Key. """

		try:
			bSeed = long( bSeed )
			
			( bSerial, bPosLock, sMac ) = self.decomposeSeedPos( bSeed )
			dbgMsg( 'getting pos key for seed-[%s] serial-[%d] bPos-[%d] mac-[%s]' % ( bSeed, bSerial, bPosLock, sMac ) )

			# Make sure this server exists
			oServer = self._dbServerList.getServer( bSerial=bSerial )
			if oServer is None:
				dbgMsg( 'server [%d] does not exists?' % bSerial )
				return ( False, 'Unknown Server' )

			# If Mac are blank for this Server object
			# then we will allow this system to auto-key this time
			if oServer.getMac() == '':
				dbgMsg( 'automatically setting mac [%s] from seed' % sMac )
				oServer.setMac( sMac )
				oServer.setPosKey( '' )

			# Now, check all key items
			#if bPosLock != oServer.getPosLock():
			#	dbgMsg( 'key check failed [Pos mismatch] [%d != %d]' % ( bPosLock, oServer.getPosLock() ) )
			#	return ( False, 'Pos mismatch' )

			if sMac != oServer.getMac():
				dbgMsg( 'key check failed [mac mismatch] [%s != %s]' % ( sMac, oServer.getMac() ) )
				return ( False, 'mac mismatch' )

			# We passed!  Make new key if we do not have one
			if oServer.getPosKey() == '':
				sKey = self.makeKeyPos( bSerial, oServer.getPosLock(), sMac )
				dbgMsg( 'making new pos key serial-[%d] key-[%s]' % ( bSerial, sKey ) )
				oServer.setPosKey( sKey )

			# Save server information back to database in case we changed something
			self._dbServerList.setServer( oServer )

			dbgMsg( 'serial-[%d] has valid pos key' % bSerial )
			return ( True, oServer.getPosKey() )

		except Exception, e:
			errMsg( 'error while getting pos key' )
			errMsg( e )
			raise Exception, "System error during pos keying process."
		
	def isPosSeed(self,bSeed):
		bSeed = long( bSeed )
		if self._getNumcam(bSeed) == 1:
			return True	
		return False
		
	def getKey( self, sSeed ):
		""" Decompose Seed and check credentials.  If they match, then return Product Key. """

		try:
			bSeed = long( sSeed )
			
			if self.isPosSeed( bSeed ):
				return self.getKeyPos( bSeed )
			
			return self.getKeyDVS( bSeed )

		except Exception, e:
			errMsg( 'error while getting product key' )
			errMsg( e )
			raise Exception, "System error during keying process."

	def _getNewFeatures( self, sFeatures ):
		""" Get feature and pos type list. """

		try:
			rgsFeature = []
			rgsPosType = []

			for s in sFeatures.split( ',' ):
				if s == 'jws':
					rgsFeature.append( 'pos' )
					rgsPosType.append( 'jws_apex' )
				if s == 'lpr':
					rgsFeature.append( 'lpr' )
					rgsPosType.append( 'license_plate_recognition' )
				if s == 'valve' or s == 'scale':
					rgsFeature.append( 'jws_anti_theft' )
				if s == 'pos':
					for sPos in [ 'aloha','subway','debug','retail_pro','polewatcher','verifone','micros','drb','restaurant_manager','cap_retail','focus_pos','positouch','hme_zoom_drive_timer','tanklogix','ecrs' ]:
						rgsPosType.append( sPos )

				return ( ",".join( rgsFeature ), ",".join( rgsPosType ) )

		except:
			return ( '', '' )

	def getKeyV2( self, sSeed, bSerial=0, bNumcam=0, sFeatures='', bPosLock=0, sVersion='' ):
		""" New Product Key """

		try:
			# Skip reporting on devel serials
			if bSerial >= 4000:
				return ( False, 'Unknown Server' )

			dbgMsg( 'getting key v2 for seed-[%s]' % sSeed )

			# See if this seed is already assigned
			oServer = self._dbServerList.getServer( sSeed=sSeed )
			if oServer is not None:
				return oServer.getKey()

			# Did not find seed assigned, see if our Serial Hint is available
			oServer = self._dbServerList.getServer( bSerial=bSerial )
			if oServer is not None:
				if oServer.getSeed() == '':
					# Serial is unlocked, so assign seed and create new key with hints
					try:
						( sFeatures, sPosTypes ) = self._getNewFeatures( sFeatures )
						if oServer.getFeatures() != '':
							sFeatures = oServer.getFeatures()
						if oServer.getPosTypes() != '':
							sPosTypes = oServer.getPosTypes()
						if oServer.getNumcam() == 0:
							oServer.setNumcam( bNumcam )
						sKey = self.makeKeyV2(
							sSeed,
							bSerial,
							oServer.getVersion(),
							oServer.getNumcam(),
							bPosLock,
							oServer.getLprLock(),
							sFeatures,
							sPosTypes
						)
						oServer.setSeed( sSeed )
						oServer.setKey( sKey )
						oServer.setFeatures( sFeatures )
						oServer.setPosTypes( sPosTypes )
						oServer.setPosLock( bPosLock )
						self._dbServerList.setServer( oServer )
						return ( True, oServer.getKey() )

					except Exception, e:
						errMsg( 'error creating new key' )
						errMsg( e )
						return ( False, 'Cannot make new key' )

				else:
					return ( False, 'Seed already assigned for serial.' )

			return ( False, 'Unknown Server' )

		except Exception, e:
			errMsg( 'error while getting product key V2' )
			errMsg( e )
			raise Exception, "System error during keying process."

	def makeKeyV2( self, sSeed, bSerial, sVersion, bNumcam, bPosLock, bLprLock, sFeatures, sPosTypes ):
		""" Make new product key based on seed. """

		rgs = [
			'/usr/local/bin/make-key',
			'-s', sSeed,
			'-n', str( bNumcam ),
			'-p', str( bPosLock ),
			'-L', str( bLprLock ),
			'-S', str( bSerial ),
			'-V', sVersion,
			'-F', sFeatures,
			'-P', sPosTypes
		]
		#dbgMsg( 'Making key with command [%s]' % " ".join( rgs ) )

		oCMD = subprocess.Popen(
			rgs,
			stdin=subprocess.PIPE,
			stdout=subprocess.PIPE,
			stderr=subprocess.STDOUT,
			shell=False,
			close_fds=True
		)
		sOutput = oCMD.communicate()[ 0 ]
		bStatus = oCMD.returncode

		#dbgMsg( 'make-key return value [%d]' % bStatus )
		#dbgMsg( 'make-key return output [%s]' % sOutput )

		if bStatus != 1:
			raise Exception( 'make-key returned bad exit status' )

		rgsOutput = sOutput.strip().split( '\n' )
		sKey = rgsOutput[ -1 ].strip()

		if len( sKey ) != 39:
			raise Exception( 'make-key did not return a valid key [%s]' % sKey )

		return sKey
