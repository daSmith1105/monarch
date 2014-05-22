##
## ticket.py
##

##
# Includes
#
# General
import commands, re, os
# Logging
from lib.messaging import stdMsg, dbgMsg, errMsg
# Internal
import lib.cache


BASE = '/usr/share/monarch-backend/'


class Ticket:

	def __init__(self):
		""" Initialize Ticket Modules """

		libCache = lib.cache.Cache()
		self._libDBbug = libCache.get( 'libDBbug' )
		self._dbServerList = libCache.get( 'dbServerList' )

		# Offline debug mode
		# This is useful if running monarch codebase on test server (not webhost)
		self._fOfflineDebug = False
		if os.access( '/rda/devel', os.F_OK ):
			self._fOfflineDebug = True

	def _openBug( self, sType, bSerial, sCompany, sName, sSummary='', sDesc='' ):
		""" Open new bug in bugzilla.  """

		try:
			dbgMsg( 'Opening Bug serial-[%d] company-[%s] name-[%s]' % \
				( bSerial, sCompany, sName ) )

			if self._fOfflineDebug:
				dbgMsg( 'Skipping since we are in offline debug mode' )
				return True

			sFileIn = ''
			sFileOut = ''
			sAssignee = ''
			sSum = ''
			sDescription = ''
			if sType == "Ticket":
				sFileIn = BASE + 'templates/dvs.bug'
				sFileOut = '/tmp/dvs-%d.bug' % bSerial
				sAssignee = 'bugzilla@dividia.net'
				sSum = sSummary
				sDescription = sDesc

			elif sType == "On-Site Maintenance":
				sFileIn = BASE + 'templates/onsite-maintenance.bug'
				sFileOut = '/tmp/onsite-maintenance.bug'
				sAssignee = 'bugzilla@dividia.net'

			else:
				raise Exception, 'unknown bug type [%s]' % sType

			# Sanitize input for perl replacements
			sCompany = sCompany.replace( '"', "_" )
			sName = sName.replace( '"', "_" )
			sAssignee = sAssignee.replace( '"', "_" )
			sSum = sSum.replace( '"', "_" )
			sDescription = sDescription.replace( '"', "_" )

			os.system( 'cp %s %s' % ( sFileIn, sFileOut ) )
			os.system( "perl -pi -e \"s/\@\@SERIAL\@\@/%03d/g\" %s" % ( bSerial, sFileOut ) )
			os.system( "perl -pi -e \"s/\@\@COMPANY\@\@/%s/g\" %s" % ( re.escape( sCompany ), sFileOut ) )
			os.system( "perl -pi -e \"s/\@\@NAME\@\@/%s/g\" %s" % ( re.escape( sName ), sFileOut ) )
			os.system( "perl -pi -e \"s/\@\@ASSIGNEE\@\@/%s/g\" %s" % ( re.escape( sAssignee ), sFileOut ) )
			os.system( "perl -pi -e \"s/\@\@SUMMARY\@\@/%s/g\" %s" % ( re.escape( sSum ), sFileOut ) )
			os.system( "perl -pi -e \"s/\@\@DESCRIPTION\@\@/%s/g\" %s" % ( re.escape( sDescription ), sFileOut ) )

			os.system( "perl -pi -e \"s/@/\\\\\\@/g\" %s" % sFileOut )

			sResult = commands.getoutput( '/usr/local/bin/bz_webservice_demo.pl --uri http://tickets.dividia.net/xmlrpc.cgi --rememberlogin --login bugzilla --password \'dt!8734\' --create %s 2>/dev/null' % sFileOut )
			os.unlink( sFileOut )

			try:
				oMatch = re.search( ".*id: ([0-9]+).*", sResult, re.MULTILINE )
				if not oMatch:
					return False

				bBug = 0
				try:
					bBug = int( oMatch.group( 1 ) )
				except ValueError, e:
					return False

			except:
				return False

			return True

		except Exception, e:
			errMsg( 'error opening new bug in bugzilla' )
			errMsg( e )
			return False

	def openTicket( self, bSerial, sSummary, sDesc ):
		""" Open a new Ticket in Bugzilla for this Serial """

		try:
			oServer = self._dbServerList.getServer( bSerial=bSerial )
			if oServer is None:
				dbgMsg( 'unknown serial [%d]' % bSerial )
				return False

			return self._openBug( 'Ticket', bSerial, oServer.getCompany(), oServer.getName(), sSummary, sDesc )

		except Exception, e:
			errMsg( 'error while opening ticket for serial [%d]' % bSerial )
			errMsg( e )
			raise Exception, "System error while opening ticket."

	def openMaintTicket( self, bSerial ):
		""" Manually open a new maintenance ticket for this serial. """

		try:
			oServer = self._dbServerList.getServer( bSerial=bSerial )
			if oServer is None:
				dbgMsg( 'unknown serial [%d]' % bSerial )
				return False

			return self._openBug( 'On-Site Maintenance', bSerial, oServer.getCompany(), oServer.getName() )

		except Exception, e:
			errMsg( 'error while opening maint ticket for serial [%d]' % bSerial )
			errMsg( e )
			raise Exception, "System error while opening maint ticket."

	def getTickets( self, bSerial ):
		""" Return a list of the 5 most recent open tickets for this serial """

		try:
			# Get most recent 5 tickets for this serial
			sQuery = "SELECT B.bug_id, P.realname, B.bug_status, B.short_desc, UNIX_TIMESTAMP( B.lastdiffed ) " + \
				"FROM bugs B, components C, profiles P " + \
				"WHERE " + \
					"( B.component_id = C.id AND B.assigned_to = P.userid ) AND " + \
					"( C.name = 'Fort Worth' OR C.name = 'Odessa' OR C.name = 'Contractor' ) AND " + \
					"B.version = " + str( bSerial ) + " " + \
				"ORDER BY B.bug_id DESC LIMIT 5"

			rgoResult = self._libDBbug.query( sQuery )

			if rgoResult is None:
				return []

			return rgoResult

		except Exception, e:
			errMsg( 'error while getting open tickets for serial [%d]' % bSerial )
			errMsg( e )
			raise Exception, "System error while getting tickets."
