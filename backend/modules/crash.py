##
## crash.py
##

##
# Includes
#
# General
import os, time, re
# Logging
from lib.messaging import stdMsg, dbgMsg, errMsg
# Internal
import lib.cache

BASE = '/usr/share/monarch-backend/'
IMPORT_FILE = BASE + 'crash-skip.lst'

class Crash:
		
	def __init__( self ):
		""" Initialize Crash Module """

		libCache = lib.cache.Cache()
		self._dbServerList = libCache.get( 'dbServerList' )

		# Offline debug mode
		# This is useful if running monarch codebase on test server (not webhost)
		self._fOfflineDebug = False
		if os.access( '/rda/devel', os.F_OK ):
			self._fOfflineDebug = True

		# Exception skiplist regex cache
		self._rgoSkip = []

	def _getSkipList( self ):
		""" Read exception skip list from file. """

		try:
			# Clear cache
			self._rgoSkip = []

			if not os.access( IMPORT_FILE, 'r' ):
				return

			# Slurp the file Yummy!
			oFile = open( IMPORT_FILE, 'r' )
			rgsLine = oFile.readlines()
			oFile.close()

			# Build regex cache
			for sLine in rgsLine:
				# Skip blank lines and comments
				if not sLine.strip() or sLine.startswith( '#' ): continue

				self._rgoSkip.append( re.compile( sLine.strip() ) )

		except Exception, e:
			errMsg( 'error reading skip list' )
			errMsg( e )

	def _checkSkipList( self, fLocal, sTraceback ):
		""" See if we should skip this crash report. """

		try:
			# Do not skip any local dview crashes
			if fLocal is None or fLocal: return False

			# Loop through skip list cache
			for oSearch in self._rgoSkip:
				if oSearch.search( sTraceback ) is not None:
					return True

			# Default to not skip
			return False

		except Exception, e:
			errMsg( 'error checking skip list' )
			errMsg( e )
			return False

	def _openBug( self, bSerial, sCompany, sName, fLocal, sUser, sTraceback ):
		""" Open new bug in bugzilla.  """

		try:
			sType = 'Crash Report'

			dbgMsg( 'Opening Bug [%s] serial-[%d] company-[%s] name-[%s]' % \
				( sType, bSerial, sCompany, sName ) )

			if self._fOfflineDebug:
				dbgMsg( 'Skipping since we are in offline debug mode' )
				return True

			sFileIn = BASE + 'templates/dvs-crash.bug'
			sFileOut = '/tmp/dvs-crash.bug'
			sAssignee = 'rayers@dividia.net'

			# Sanitize input for perl replacements
			sCompany = sCompany.replace( '"', "_" )
			sName = sName.replace( '"', "_" )
			sAssignee = sAssignee.replace( '"', "_" )

			os.system( 'cp %s %s' % ( sFileIn, sFileOut ) )
			os.system( "perl -pi -e \"s/\@\@SERIAL\@\@/%03d/g\" %s" % ( bSerial, sFileOut ) )
			os.system( "perl -pi -e \"s/\@\@COMPANY\@\@/%s/g\" %s" % ( re.escape( sCompany ), sFileOut ) )
			os.system( "perl -pi -e \"s/\@\@NAME\@\@/%s/g\" %s" % ( re.escape( sName ), sFileOut ) )
			os.system( "perl -pi -e \"s/\@\@LOCAL\@\@/%s/g\" %s" % ( re.escape( fLocal ), sFileOut ) )
			os.system( "perl -pi -e \"s/\@\@USER\@\@/%s/g\" %s" % ( re.escape( sUser ), sFileOut ) )
			os.system( "perl -pi -e \"s/\@\@ASSIGNEE\@\@/%s/g\" %s" % ( re.escape( sAssignee ), sFileOut ) )
			os.system( "perl -pi -e \"s/\@\@TRACEBACK\@\@/%s/g\" %s" % ( sTraceback, sFileOut ) )

			os.system( "perl -pi -e \"s/@/\\\\\\@/g\" %s" % sFileOut )

			bStatus = os.system( '/usr/local/bin/bz_webservice_demo.pl --uri http://tickets.dividia.net/xmlrpc.cgi --rememberlogin --login bugzilla --password \'dt!8734\' --create %s 2>/dev/null' % sFileOut )
			os.unlink( sFileOut )

			if not os.WIFEXITED( bStatus ):
				return False

			if os.WEXITSTATUS( bStatus ) != 0:
				return False

			return True

		except Exception, e:
			errMsg( 'error opening new bug in bugzilla' )
			errMsg( e )
			return False

	def addCrash( self, bSerial=None, sTraceback='', fLocal=None, sUser='' ):
		""" Add new crash log for dvs """

		try:
			try:
				bSerial = int( bSerial )
			except ValueError:
				return False

			# Verify the Serial is known
			oServer = self._dbServerList.getServer( bSerial=bSerial )
			if oServer is None:
				return False

			# Bail if we want to skip this bug
			if self._checkSkipList( fLocal, sTraceback ):
				return False

			self._openBug(
				bSerial,
				oServer.getCompany(),
				oServer.getName(),
				fLocal,
				sUser,
				sTraceback
			)

			return True

		except Exception, e:
			errMsg( 'error adding crash' )
			errMsg( e )
			return False
