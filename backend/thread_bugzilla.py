# thread_bugzilla.py

##
# Includes
#
# System
import threading, time, re, os
# Logging
from lib.messaging import stdMsg, dbgMsg, errMsg
# Library
import lib.cache


BASE = '/usr/share/monarch-backend/'

DVS_OFFLINE_LIMIT = 86400          # 24 hours (secs) ( 24 * 60 * 60 )
CAMERA_FAIL_LIMIT = 86400          # 24 hours (secs) ( 24 * 60 * 60 )
MAINT_REMINDER_LIMIT = 15552000    # 6 months (secs) ( 6 * 30 * 24 * 60 * 60 )

PURGE_DVS_LOG = 30                 # Days

class ThreadBugzilla( threading.Thread ):

	def __init__( self, sName ):
		threading.Thread.__init__( self, name=sName )

		self._sName = sName
		self._fRunning = False             # Are we actually running?
		self._fStop = False                # Stop requested by parent
		self._oLock = threading.RLock()

		self._libDBbug = None
		self._libDB = None
		self._dbServerList = None
		self._dbCameraList = None
		self._dbMisc = None
		self._dbDVSLogList = None

		# Offline debug mode
		# This is useful if running monarch codebase on test server (not webhost)
		self._fOfflineDebug = False
		if os.access( '/rda/devel', os.F_OK ):
			dbgMsg( 'Found /rda/devel repo, so running in offline debug mode' )
			dbgMsg( 'Skipping emails and opening tickets in Bugzilla' )
			self._fOfflineDebug = True

		# Make sure we have credentials setup for bugzilla
		try:
			if not self._fOfflineDebug:
				if not os.access( '/root/.netrc', os.F_OK ):
					# Attempt to make a new one
					oFile = open( '/root/.netrc', 'w' )
					oFile.write( 'machine "http://tickets.dividia.net/"\n' )
					oFile.write( 'login bugzilla\n' )
					oFile.write( 'password dt!8734\n' )
					oFile.close()
				if not os.access( '/usr/local/bin/bz_webservice_demo.pl', os.F_OK ):
					errMsg( 'bz_webserice_demo.pl utility is not installed, tickets will not get opened.' )

		except Exception, e:
			errMsg( 'Bugzilla credential file is missing and we could not create it, tickets will not get opened.' )
			errMsg( e )

	def _postInit( self ):
		# Grab other modules we might use from cache
		libCache = lib.cache.Cache()
		self._libDBbug = libCache.get( 'libDBbug' )
		self._libDB = libCache.get( 'libDB' )
		self._dbServerList = libCache.get( 'dbServerList' )
		self._dbCameraList = libCache.get( 'dbCameraList' )
		self._dbMisc = libCache.get( 'dbMisc' )
		self._dbDVSLogList = libCache.get( 'dbDVSLogList' )

	def run( self ):
		try:
			self._fRunning = True

			# sleep a bit and let everything initialize first
			time.sleep( 10 )
			self._postInit()

			fFirst = True
			while not self._fStop:

				# Only run at the top of the hour
				bSleep = 0
				if fFirst:
					fFirst = False
				else:
					bSleep = self._getTimeUntilNextHour()
					dbgMsg( 'sleeping for [%d] seconds' % bSleep )
				while not self._fStop and bSleep > 0:
					time.sleep( 5 )
					bSleep -= 5
				if self._fStop: break
				dbgMsg( 'processing bugzilla tickets' )

				# Offline Servers
				self._processOfflineServers()

				# Camera Failed
				self._processFailedCameras()

				# Maintenance Reminders
				# Check all servers set to "install" for maintenance
				# If they are beyond 6 month, open a new ticket for sales
				self._processInstallMaintenance()

				# Weekly Check
				# (TXI, Rosa's, etc)
				self._processWeeklyChecks()

				# On-Site Maintenance
				# Open Monthly/Quarterly/Bi-Annual On-site Tickets
				# 06/24/2014 Temprarily Disable Opening these.
				# I'm trying a new process where I have all maintenance events pre-laoded on calendar.
				#self._processOnsiteMaintTickets()

				# Resolved Reminder
				# Send a reminder email on tickets marked as RESOLVED but not FIXED
				self._sendResolvedReminderEmail()

				# Install Date Reminder
				# Send a reminder email on Serials that have been installed, but
				# nobody input an install date in the database
				self._sendMissingInstallReminderEmail()

				# Maintenance Billing Reminder
				# Send an email to double check that all customers that are paying
				# for maintenance are marked correctly in Monarch and visa versa
				self._sendMaintBillingReminderEmail()

				# DVS Log Events
				# Open Tickets for certain DVS Log events
				self._processDVSLog()

			self._fRunning = False

		except Exception, e:
			self._fRunning = False
			errMsg( 'encountered an error [%s], terminating' % e )

	def stop( self ):
		self._fStop = True

	def checkIsRunning( self ):
		return self._fRunning

	def _getTimeUntilNextHour( self ):
		""" Return the number of seconds to sleep until the next hour. """

		bNow = int( time.time() )
		oTime = time.localtime()
		bLastHour = int( time.mktime( (
			oTime.tm_year,
			oTime.tm_mon,
			oTime.tm_mday,
			oTime.tm_hour,
			0,
			0,
			oTime.tm_wday,
			oTime.tm_yday,
			oTime.tm_isdst
		) ) )

		return bLastHour + 3600 - bNow

	def _getNextRunTime( self, bTimestamp, bOffset ):
		""" Figure out a next run time with a monthly offset. """

		if bTimestamp is None: bTimestamp = 0

		oTime = time.localtime( bTimestamp )
		bYear = oTime.tm_year
		bMonth = oTime.tm_mon
		while bOffset > 0:
			bMonth += 1
			if bMonth > 12:
				bYear += 1
				bMonth = 1
			bOffset -= 1

		bNextRun = int( time.mktime( (
			bYear,
			bMonth,
			oTime.tm_mday,
			oTime.tm_hour,
			oTime.tm_min,
			oTime.tm_sec,
			oTime.tm_wday,
			oTime.tm_yday,
			oTime.tm_isdst
		) ) )

		return bNextRun

	def _sendEmail( self, *args ):
		""" Send email.  """

		try:
			sType = args[ 0 ]
			dbgMsg( 'Sending Email [%s]' % \
				( sType ) )

			if self._fOfflineDebug:
				dbgMsg( 'Skipping since we are in offline debug mode' )
				return True

			sFileIn = ''
			sFileOut = ''
			sTo = ''
			sSubject = ''
			sBugs = ''
			sServerList = ''
			if sType == "Internet Down":
				sFileIn = BASE + 'templates/internet-down.eml'
				sFileOut = '/tmp/internet-down.eml'
				sTo = 'support@dividia.net'
				sSubject = 'bugzilla-offline - Internet down?'

			elif sType == "Resolved Reminder":
				sFileIn = BASE + 'templates/resolved-reminder.eml'
				sFileOut = '/tmp/resolved-reminder.eml'
				sTo = args[ 1 ]
				sSubject = 'Bugzilla Reminder Email'
				sBugs = args[ 2 ]

			elif sType == "Install Reminder":
				sFileIn = BASE + 'templates/install-reminder.eml'
				sFileOut = '/tmp/install-reminder.eml'
				sTo = args[ 1 ]
				sSubject = 'Missing Installation Date Reminder Email'
				sServerList = args[ 2 ]

			elif sType == "Maint Billing Reminder":
				sFileIn = BASE + 'templates/maint-billing-reminder.eml'
				sFileOut = '/tmp/maint-billing-reminder.eml'
				sTo = args[ 1 ]
				sSubject = 'Maintenance Billing Reminder Email'
				sServerList = args[ 2 ]

			else:
				raise Exception, 'unknown email type [%s]' % sType

			# Sanitize input for perl replacement
			sTo = sTo.replace( '"', "_" )
			sSubject = sSubject.replace( '"', "_" )
			sBugs = sBugs.replace( '"', "_" )
			sServerList = sServerList.replace( '"', "_" )

			os.system( 'cp %s %s' % ( sFileIn, sFileOut ) )
			os.system( "perl -pi -e \"s/\@\@TO\@\@/%s/g\" %s" % ( re.escape( sTo ), sFileOut ) )
			os.system( "perl -pi -e \"s/\@\@SUBJECT\@\@/%s/g\" %s" % ( re.escape( sSubject ), sFileOut ) )
			if sBugs != '':
				os.system( "perl -pi -e \"s/\@\@BUGS\@\@/%s/g\" %s" % ( re.escape( sBugs ), sFileOut ) )
			if sServerList != '':
				os.system( "perl -pi -e \"s/\@\@SERVERLIST\@\@/%s/g\" %s" % ( re.escape( sServerList ), sFileOut ) )

			#bStatus = os.system( 'cat %s | /bin/mail -s "%s" %s 1>/dev/null 2>/dev/null' % ( sFileOut, sSubject, re.escape( sTo ) ) )
			bStatus = os.system( 'cat %s | /usr/sbin/sendmail -t 1>/dev/null 2>/dev/null' % sFileOut )
			os.unlink( sFileOut )

			if not os.WIFEXITED( bStatus ):
				return False

			if os.WEXITSTATUS( bStatus ) != 0:
				return False

			return True

		except Exception, e:
			errMsg( 'error sending email' )
			errMsg( e )
			return False

	def _openBug( self, sType, bSerial, sCompany, sName, bCamera=None, sSummary=None, sDescription=None ):
		""" Open new bug in bugzilla.  """

		try:
			time.sleep( 5 )

			if bCamera is None:
				dbgMsg( 'Opening Bug [%s] serial-[%d] company-[%s] name-[%s]' % \
					( sType, bSerial, sCompany, sName ) )
			else:
				dbgMsg( 'Opening Bug [%s] serial-[%d] company-[%s] name-[%s] camera-[%d]' % \
					( sType, bSerial, sCompany, sName, bCamera ) )

			if self._fOfflineDebug:
				dbgMsg( 'Skipping since we are in offline debug mode' )
				return True

			sFileIn = ''
			sFileOut = ''
			sAssignee = ''
			if sType == "Offline":
				sFileIn = BASE + 'templates/dvs-offline.bug'
				sFileOut = '/tmp/dvs-offline.bug'
				sAssignee = 'mlaplante@dividia.net'

			elif sType == "Camera Down":
				sFileIn = BASE + 'templates/camera-down.bug'
				sFileOut = '/tmp/camera-down.bug'
				sAssignee = 'mlaplante@dividia.net'

			elif sType == "Maintenance Reminder":
				sFileIn = BASE + 'templates/maintenance-reminder.bug'
				sFileOut = '/tmp/maintenance-reminder.bug'
				sAssignee = 'mlaplante@dividia.net'

			elif sType == "Weekly Check":
				sFileIn = BASE + 'templates/weekly-check.bug'
				sFileOut = '/tmp/weekly-check.bug'
				sAssignee = 'mlaplante@dividia.net'

			elif sType == "On-Site Maintenance":
				sFileIn = BASE + 'templates/onsite-maintenance.bug'
				sFileOut = '/tmp/onsite-maintenance.bug'
				sAssignee = 'bugzilla@dividia.net'

			elif sType == "DVS Log":
				sFileIn = BASE + 'templates/dvs-log.bug'
				sFileOut = '/tmp/dvs-log.bug'
				sAssignee = 'bugzilla@dividia.net'

			else:
				raise Exception, 'unknown bug type [%s]' % sType

			# Sanitize input for perl replacements
			sCompany = sCompany.replace( '"', "_" )
			sName = sName.replace( '"', "_" )
			sAssignee = sAssignee.replace( '"', "_" )

			os.system( 'cp %s %s' % ( sFileIn, sFileOut ) )
			os.system( "perl -pi -e \"s/\@\@SERIAL\@\@/%03d/g\" %s" % ( bSerial, sFileOut ) )
			os.system( "perl -pi -e \"s/\@\@COMPANY\@\@/%s/g\" %s" % ( re.escape( sCompany ), sFileOut ) )
			os.system( "perl -pi -e \"s/\@\@NAME\@\@/%s/g\" %s" % ( re.escape( sName ), sFileOut ) )
			os.system( "perl -pi -e \"s/\@\@ASSIGNEE\@\@/%s/g\" %s" % ( re.escape( sAssignee ), sFileOut ) )
			if bCamera is not None:
				os.system( "perl -pi -e \"s/\@\@CAMERA\@\@/%03d/g\" %s" % ( bCamera, sFileOut ) )
			if sSummary is not None:
				os.system( "perl -pi -e \"s/\@\@SUMMARY\@\@/%s/g\" %s" % ( sSummary, sFileOut ) )
			if sDescription is not None:
				os.system( "perl -pi -e \"s/\@\@DESCRIPTION\@\@/%s/g\" %s" % ( sDescription, sFileOut ) )

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

	def _getBugzillaSerials( self, sQuery ):
		"""
		Return a list of Serial numbers that already have
		tickets opened that match sQuery in Bugzilla.
		"""

		try:
			rgbSerial = []
			rgoResult = self._libDBbug.query( sQuery )

			if rgoResult is None:
				return rgbSerial

			for oRow in rgoResult:
				try:
					rgbSerial.append( int( oRow[ 0 ] ) )
				except ValueError, e:
					errMsg( 'error converting serial to int [%s]' % oRow[ 0 ] )

			return rgbSerial

		except Exception, e:
			errMsg( 'error getting opened bugs in bugzilla (serial)' )
			errMsg( e )

	def _getBugzillaSerialsAndCameras( self, sQuery ):
		"""
		Return a list of Serial/Camera numbers that already have
		tickets opened that match sQuery in Bugzilla.
		sQuery should return a version and short_desc to parse
		for the camera number.
		"""

		try:
			rgoSerial = []
			rgoResult = self._libDBbug.query( sQuery )

			if rgoResult is None:
				return rgoSerial

			for oRow in rgoResult:
				try:
					bSerial = int( oRow[ 0 ] )
					rgs = oRow[ 1 ].split( ' - ' )
					bCamera = int( rgs[ 2 ] )
					rgoSerial.append( [ bSerial, bCamera ] )
				except Exception, e:
					errMsg( 'error converting serial/camera [%s]-[%s]' % ( oRow[ 0 ], oRow[ 1 ] ) )

			return rgoSerial

		except Exception, e:
			errMsg( 'error getting opened bugs in bugzilla (serial and camera)' )
			errMsg( e )

	def _processOfflineServers( self ):
		"""
		Open a ticket for any server that has been offline more
		than 1 day.  If we are going to open more than 30 tickets
		at a time, then send a warning email and delay since this
		means our Internet may be down.
		"""

		try:
			dbgMsg( 'processing offline servers' )

			oMatchTest = re.compile( '.*test.*' )           # Regex to skip any "test" systems
			rgoServer = []                                  # Array to hold Servers we want to open tickets for

			# Get Serials from Bugzilla that already have tickets open
			sQuery = "SELECT version FROM bugs WHERE " + \
				"product_id=7 AND " + \
				"short_desc LIKE 'Offline - %' AND " + \
				"((bug_status<>'RESOLVED') OR (bug_status='RESOLVED' AND (resolution='REMIND' OR resolution='LATER')))"
			rgbSerial = self._getBugzillaSerials( sQuery )

			bNow = int( time.time() )
			for oServer in self._dbServerList.getList():
				if oServer.checkHasSkip():
					continue
				if oMatchTest.match( oServer.getCategories() ):
					continue
				if oServer.getMaintenance() == 'no':
					continue
				if oServer.getTimestamp() is not None and ( bNow - oServer.getTimestamp() ) <= DVS_OFFLINE_LIMIT:
					continue

				# Make sure we do not already have a ticket open
				if oServer.getSerial() in rgbSerial: continue

				# Delay opening ticket here, just save it for later.
				# This way we can check if we have more than 10 systems
				# reporting down at a time to send an alert email instead
				rgoServer.append( oServer )

			# Internet down?
			if len( rgoServer ) > 30:
				self._sendEmail( "Internet Down" )
				rgoServer = []

			bCount = 0
			for oServer in rgoServer:
				if self._openBug(
					"Offline",
					oServer.getSerial(),
					oServer.getCompany(),
					oServer.getName()
				):
					bCount += 1

			dbgMsg( 'opened [%d] offline server tickets' % bCount )

		except Exception, e:
			errMsg( 'error occurred while processing offline server tickets' )
			errMsg( e )

	def _processFailedCameras( self ):
		"""
		Open a ticket for any camera that has been marked failed more
		than 1 day.
		"""

		try:
			dbgMsg( 'processing camera failure tickets' )

			oMatchTest = re.compile( '.*test.*' )           # Regex to skip any "test" systems

			# Get Serials from Bugzilla that already have tickets open
			sQuery = "SELECT version, short_desc FROM bugs WHERE " + \
				"product_id=7 AND " + \
				"short_desc LIKE 'Camera Down - %' AND " + \
				"((bug_status<>'RESOLVED') OR (bug_status='RESOLVED' AND (resolution='REMIND' OR resolution='LATER' OR resolution='WONTFIX')))"
			rgoSerial = self._getBugzillaSerialsAndCameras( sQuery )

			bCount = 0
			bNow = int( time.time() )
			for oCamera in self._dbCameraList.getList():
				oServer = self._dbServerList.getServer( bSerial=oCamera.getSerial() )

				if oServer is None:
					continue
				if oCamera.checkHasSkip():
					continue
				if oMatchTest.match( oServer.getCategories() ):
					continue
				if oServer.getMaintenance() == 'no':
					continue
				if oCamera.getTimestamp() is not None and ( bNow - oCamera.getTimestamp() ) <= CAMERA_FAIL_LIMIT:
					continue

				# Make sure we do not already have a ticket open
				bSerial = oServer.getSerial()
				bCamera = oCamera.getCamera()
				fFound = False
				for o in rgoSerial:
					if bSerial == o[ 0 ] and bCamera == o[ 1 ]:
						fFound = True
						break
				if fFound:
					continue

				if self._openBug(
					"Camera Down",
					oServer.getSerial(),
					oServer.getCompany(),
					oServer.getName(),
					bCamera=oCamera.getCamera()
				):
					bCount += 1

			dbgMsg( 'opened [%d] camera failure tickets' % bCount )

		except Exception, e:
			errMsg( 'error occurred while processing camera failure tickets' )
			errMsg( e )

	def _processDVSLog( self ):
		"""
		Open certain tickets automatically for DVS Log Events.
		"""

		try:
			dbgMsg( 'processing dvs log tickets' )

			oMatchTest = re.compile( '.*test.*' )           # Regex to skip any "test" systems

			# Process all events since our last run
			bCount = 0
			sLastRun = self._dbMisc.get( 'bugzilla', 'dvs-log-last' )
			for oLog in self._dbDVSLogList.getList( sLastRun ):

				# Kernel Oops
				if oLog.getEventID() == 20000:
					sTitle = 'Kernel Oops'

				# System Load
				elif oLog.getEventID() == 21000:
					# See if our load is too high
					try:
						rgb = oLog.getData()[ 6: ].split( ',' )
						if float( rgb[ 2 ] ) > 2.0:
							sTitle = 'System Load'
						else:
							continue # Skip
					except:
						continue

				# Capture Card Error
				elif oLog.getEventID() == 41000:
					sTitle = 'Capture Card Error'

				# Disk Report
				elif oLog.getEventID() >= 51000 and oLog.getEventID() <= 51100:
					sTitle = 'Disk Report'

				# Camera Record Issue
				elif oLog.getEventID() == 61000:
					sTitle = 'Camera Record Issue'

				# VMD
				elif oLog.getEventID() == 62000:
					sTitle = 'VMD Issue'

				# DB Issue
				elif oLog.getEventID() == 65000:
					sTitle = 'DB Issue'

				# Skip
				else:
					continue

				# Make sure we do not already have a ticket open
				sQuery = "SELECT version FROM bugs WHERE " + \
					"version='" + oLog.getSerial() + "' AND " + \
					"short_desc LIKE 'DVS Log - % - " + sTitle + "' AND " + \
					"((bug_status<>'RESOLVED') OR (bug_status='RESOLVED' AND (resolution='REMIND' OR resolution='LATER' OR resolution='WONTFIX')))"
				oResult = self._libDBbug.query( sQuery )
				if oResult is not None and len( oResult ) > 0:
					# Already open
					continue

				# See if we should skip anything for this serial
				oServer = self._dbServerList.getServer( bSerial=oLog.getSerial() )
				if oServer is None:
					continue # server does not exist?
				if oServer.checkHasSkip():
					continue
				if oMatchTest.match( oServer.getCategories() ):
					continue
				if oServer.getMaintenance() == 'no':
					continue

				if self._openBug(
					"DVS Log",
					oServer.getSerial(),
					oServer.getCompany(),
					oServer.getName(),
					sSummary=sTitle,
					sDescrption=oLog.getData()
				):
					bCount += 1

			# Save our last run time
			self._dbMisc.set( 'bugzilla', 'dvs-log-last', time.strftime( '%Y-%m-%d %H:%M:%S' ) )

			dbgMsg( 'opened [%d] dvslog tickets' % bCount )

			# Purge old log entries
			self._libDB.query( 'DELETE FROM DVSLog WHERE dTimeStamp < DATE_SUB( NOW(), INTERVAL ' + str( PURGE_DVS_LOG ) + ' DAY )' )

		except Exception, e:
			errMsg( 'error occurred while processing dvs log tickets' )
			errMsg( e )

	def _processInstallMaintenance( self ):
		"""
		Check all servers that have maintenance set to "install".
		If greater than 6 months from install date, send sales a
		reminder email.
		"""

		try:
			dbgMsg( 'processing install maintenance reminders' )

			oMatchTest = re.compile( '.*test.*' )           # Regex to skip any "test" systems

			# Get Serials from Bugzilla that already have tickets open
			sQuery = "SELECT version FROM bugs WHERE " + \
				"product_id=7 AND " + \
				"short_desc LIKE 'Maintenance - %' AND " + \
				"((bug_status<>'RESOLVED') OR (bug_status='RESOLVED' AND (resolution='REMIND' OR resolution='LATER' OR resolution='WONTFIX')))"
			rgbSerial = self._getBugzillaSerials( sQuery )

			bCount = 0
			bNow = int( time.time() )
			for oServer in self._dbServerList.getList():
				# See if maintenance plan == "install" and
				# system has been installed more than 6 months ago
				if oServer.getInstall() is None:
					continue
				if oServer.getMaintenance() != 'install' or \
				   ( bNow - oServer.getInstall() ) <= MAINT_REMINDER_LIMIT:
					continue
				if oServer.checkHasSkip():
					continue
				if oMatchTest.match( oServer.getCategories() ):
					continue

				# Make sure we do not already have a ticket open
				if oServer.getSerial() in rgbSerial: continue

				if self._openBug(
					"Maintenance Reminder",
					oServer.getSerial(),
					oServer.getCompany(),
					oServer.getName()
				):
					bCount += 1

			dbgMsg( 'opened [%d] maintenance reminder tickets' % bCount )

		except Exception, e:
			errMsg( 'error occurred while processing install maintenance reminders' )
			errMsg( e )

	def _processWeeklyChecks( self ):
		"""
		Certain maintenance plans include our techs looks at the
		cameras once a week.  This should automatically open tickets
		for those systems to help us track if the techs are looking
		at this information.  Also, if they notice a bad camera (focus)
		they should contact to see if we should go onsite.
		Included in plan2, plan3, plan4, and plan5.
		"""

		try:
			# Only run this check if it is Monday
			rgoTime = time.localtime()
			if rgoTime.tm_wday != 0: return

			dbgMsg( 'processing weekly maintenance checks' )

			# List of plans that support weekly checks
			rgsPlans = [ 'plan2', 'plan3', 'plan4', 'plan5' ]

			# Get Serials from Bugzilla that already have tickets open
			sQuery = "SELECT version FROM bugs WHERE " + \
				"product_id=7 AND " + \
				"short_desc LIKE 'Weekly Check - %' AND " + \
				"((bug_status<>'RESOLVED') OR (bug_status='RESOLVED' AND (resolution='REMIND' OR resolution='LATER' OR resolution='WONTFIX')))"
			rgbSerialOpen = self._getBugzillaSerials( sQuery )
			# Get Serials from Bugzilla that have tickets opened/closed for today
			sQuery = "SELECT version FROM bugs WHERE " + \
				"product_id=7 AND " + \
				"short_desc LIKE 'Weekly Check - %' AND " + \
				"DATE(delta_ts)='" + time.strftime( '%Y-%m-%d' ) + "'"
			rgbSerialToday = self._getBugzillaSerials( sQuery )

			bCount = 0
			for oServer in self._dbServerList.getList():
				# See if maintenance plan includes weekly checks
				if not oServer.getMaintenance() in rgsPlans: continue

				# Is there an existing ticket open for this server already?
				if oServer.getSerial() in rgbSerialOpen: continue

				# Was there a ticket opened for this location already today?
				# It may be closed, but just skip since we already logged it
				if oServer.getSerial() in rgbSerialToday: continue

				if self._openBug(
					"Weekly Check",
					oServer.getSerial(),
					oServer.getCompany(),
					oServer.getName()
				):
					bCount += 1

			dbgMsg( 'opened [%d] weekly maintenance check tickets' % bCount )

		except Exception, e:
			errMsg( 'error occurred while processing weekly maintenance check tickets' )
			errMsg( e )

	def _processOnsiteMaintTickets( self ):
		"""
		Certain maintenance plans include on-site cleaning billed
		separately.  This would include cleaning the cameras, inside
		the DVR, etc.
		Included in plan3, plan4, and plan5.
		"""

		try:
			dbgMsg( 'processing on-site maintenance tickets' )

			# List of plans that support weekly checks
			rgsPlans = [ 'plan3', 'plan4', 'plan5' ]

			# Get Serials from Bugzilla that already have tickets open
			sQuery = "SELECT version FROM bugs WHERE " + \
				"product_id=7 AND " + \
				"short_desc LIKE 'On-Site Maintenance - %' AND " + \
				"((bug_status<>'RESOLVED') OR (bug_status='RESOLVED' AND (resolution='REMIND' OR resolution='LATER' OR resolution='WONTFIX')))"
			rgbSerial = self._getBugzillaSerials( sQuery )

			bCount = 0
			bNow = int( time.time() )
			for oServer in self._dbServerList.getList():
				# See if maintenance plan includes weekly checks
				sPlan = oServer.getMaintenance()
				if not sPlan in rgsPlans: continue

				# Is there an existing ticket open for this server already?
				if oServer.getSerial() in rgbSerial: continue

				# See if we are beyond our check date based on plan
				bNextRun = 0
				if sPlan == 'plan3':
					# Monthly Visit
					bNextRun = self._getNextRunTime( oServer.getMaintenanceOnsite(), 1 )
					if bNextRun > bNow:
						continue

				elif sPlan == 'plan4':
					# Quarterly Visit
					bNextRun = self._getNextRunTime( oServer.getMaintenanceOnsite(), 3 )
					if bNextRun > bNow:
						continue

				elif sPlan == 'plan5':
					# Bi-Annual Visit
					bNextRun = self._getNextRunTime( oServer.getMaintenanceOnsite(), 6 )
					if bNextRun > bNow:
						continue

				# We made it, let's open some tickets
				if not self._openBug(
					"On-Site Maintenance",
					oServer.getSerial(),
					oServer.getCompany(),
					oServer.getName()
				):
					dbgMsg( 'could not open bug, skip updating date' )
					continue
				bCount += 1

				# Now, update our date for this server object
				try:
					self._oLock.acquire()
					try:
						oServer.setMaintenanceOnsite( bNow )
						self._dbServerList.setServer( oServer )
					except Exception, e:
						errMsg( 'error saving new on-site maintenance date to server object' )
						errMsg( e )
				finally:
					self._oLock.release()

			dbgMsg( 'opened [%d] on-site maintenance tickets' % bCount )

		except Exception, e:
			errMsg( 'error occurred while processing on-site maintenance tickets' )
			errMsg( e )

	def _sendResolvedReminderEmail( self ):
		"""
		Send an email to the bug assignee for any emails that are marked as
		RESOLVED, but the resolution is REMIND, LATER, or WONTFIX.
		This email should be send every Monday morning.
		"""

		try:
			# Only send emails if it is Monday and we haven't already sent them
			rgoTime = time.localtime()
			if rgoTime.tm_wday != 0: return
			bLastRun = 0
			try:
				sLastRun = self._dbMisc.get( 'bugzilla', 'resolved-reminder-last' )
				if sLastRun != '0':
					bLastRun = int( time.mktime( time.strptime( sLastRun, '%Y-%m-%d' ) ) )
			except:
				errMsg( 'error parsing resolved-reminder-last run time' )
			bNow = int( time.time() )
			if bNow - bLastRun < 86400: # Already ran within last 24 hours
				return

			dbgMsg( 'sending any resolved reminder emails' )

			# Get bugs that need reminding
			rgoBug = self._libDBbug.query(
				"SELECT bug_id, login_name, short_desc " + \
				"FROM " + \
					"bugs INNER JOIN profiles ON userid = assigned_to " + \
					"INNER JOIN products ON id = product_id " + \
				"WHERE " + \
					"products.name='Support' AND " + \
					"bug_status='RESOLVED' AND " + \
						"(resolution='REMIND' OR resolution='LATER') " + \
				"ORDER BY login_name, bug_id"
			)

			# Cycle through bugs and build buglist to email user
			bCount = 0
			sEmailCurr = ''
			sBugList = ''
			for oBug in rgoBug + [ [ 0, 'last', 'last' ] ]:
				bBug   = oBug[ 0 ]
				sEmail = oBug[ 1 ]
				sDesc  = oBug[ 2 ]

				if sEmailCurr != '' and sEmailCurr != sEmail:
					# Send email
					self._sendEmail( "Resolved Reminder", sEmailCurr, sBugList )
					sBugList = ''
					bCount += 1

				sEmailCurr = sEmail

				sBugList += '<tr><td><a href="http://tickets.dividia.net/show_bug.cgi?id=%d">%d</a></td><td>%s</td></tr>\n' % \
					( bBug, bBug, sDesc )

			dbgMsg( 'sent [%d] resolved reminder emails' % bCount )

			# Save our last run time
			self._dbMisc.set( 'bugzilla', 'resolved-reminder-last', time.strftime( '%Y-%m-%d' ) )

		except Exception, e:
			errMsg( 'error occurred while sending resolved reminder email' )
			errMsg( e )

	def _sendMissingInstallReminderEmail( self ):
		"""
		Send an email for any serials that have been installed, but
		are missing an Install date in the database.
		Skip "test" systems.
		"""

		try:
			# Only send emails if it is Monday and we haven't already sent them
			rgoTime = time.localtime()
			if rgoTime.tm_wday != 0: return
			bLastRun = 0
			try:
				sLastRun = self._dbMisc.get( 'bugzilla', 'install-reminder-last' )
				if sLastRun != '0':
					bLastRun = int( time.mktime( time.strptime( sLastRun, '%Y-%m-%d' ) ) )
			except:
				errMsg( 'error parsing install-reminder-last run time' )
			bNow = int( time.time() )
			if bNow - bLastRun < 86400: # Already ran within last 24 hours
				return

			dbgMsg( 'sending any missing install date reminder emails' )

			oMatchTest = re.compile( '.*test.*' )           # Regex to skip any "test" systems

			bCount = 0
			sServerList = ''
			for oServer in self._dbServerList.getList():
				if oServer.getMaintenance() != 'install':
					continue
				if oServer.getInstall() is not None:
					continue
				if oMatchTest.match( oServer.getCategories() ):
					continue

				bCount += 1
				sServerList += '<tr><td>%d</td><td>%s</td><td>%s</td></tr>' % \
					( oServer.getSerial(), oServer.getCompany(), oServer.getName() )

			if bCount > 0:
				self._sendEmail( "Install Reminder", 'mlaplante@dividia.net', sServerList )
				dbgMsg( 'sent reminder email on [%d] serials that were missing install dates' % bCount )

			# Save our last run time
			self._dbMisc.set( 'bugzilla', 'install-reminder-last', time.strftime( '%Y-%m-%d' ) )

		except Exception, e:
			errMsg( 'error occurred while sending missing install date reminder email' )
			errMsg( e )

	def _sendMaintBillingReminderEmail( self ):
		"""
		Send an email to accounting to verify that all paying maint customers are
		marked correctly in Monarch.  Additionally, this will allow a check that any
		customers that are not paying will be removed.
		This email should be send every 1st day of the month.
		"""

		try:
			# Only send emails if it is the 1st and we haven't already sent them
			rgoTime = time.localtime()
			if rgoTime.tm_mday != 1: return
			bLastRun = 0
			try:
				sLastRun = self._dbMisc.get( 'bugzilla', 'maint-reminder-last' )
				if sLastRun != '0':
					bLastRun = int( time.mktime( time.strptime( sLastRun, '%Y-%m-%d' ) ) )
			except:
				errMsg( 'error parsing maint-reminder-last run time' )
			bNow = int( time.time() )
			if bNow - bLastRun < 86400: # Already ran within last 24 hours
				return

			dbgMsg( 'sending maint billing reminder email' )

			bCount = 0
			sServerList = ''
			for oServer in self._dbServerList.getList():
				if oServer.getMaintenance() == 'no' or \
				   oServer.getMaintenance() == 'free' or \
				   oServer.getMaintenance() == 'install':
					continue

				bCount += 1
				sServerList += '<tr><td>%d</td><td>%s</td><td>%s</td><td>%s</td></tr>' % \
					( oServer.getSerial(), oServer.getCompany(), oServer.getName(), oServer.getMaintenance() )

			if bCount > 0:
				self._sendEmail( "Maint Billing Reminder", 'accounting@dividia.net', sServerList )
				dbgMsg( 'sent maintenance billing reminder email on [%d] serials that have a valid maintenance plan' % bCount )

			# Save our last run time
			self._dbMisc.set( 'bugzilla', 'maint-reminder-last', time.strftime( '%Y-%m-%d' ) )

		except Exception, e:
			errMsg( 'error occurred while sending maint billing reminder email' )
			errMsg( e )
