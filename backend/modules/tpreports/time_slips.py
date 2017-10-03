#!/usr/bin/python

import sys
import pymssql
import time
import locale
from datetime import date

DB_HOST = 'tigerpaw'
DB_USER = 'sa'
DB_PASS = 'Y3R]=68RF4'
DB_NAME = 'TigerPaw'

OVERTIME_LIMIT = float( 40 )
OVERTIME_MULTIPLIER = float( 1.5 )

class App:

	_oDB = None
	_oCursor = None

	def __init__( self ):
		self._oDB = pymssql.connect( DB_HOST, DB_USER, DB_PASS, DB_NAME )
		self._oCursor = self._oDB.cursor( as_dict=True )

	def finish( self ):

		self._oDB.close()

	def _getAdjustedTime( self, oRow ):

		# Deduct time and round to nearest quarter hour
		bHours = oRow[ 'LogHours' ] - oRow[ 'DeductHours' ]
		bMinutes = ( oRow[ 'LogMinutes' ] - oRow[ 'DeductMinutes' ] ) / 60.0
		if bMinutes <= 0:
			bMinutes = 0
		elif bMinutes > 0 and bMinutes <= .25:
			bMinutes = .25
		elif bMinutes > .25 and bMinutes <= .5:
			bMinutes = .5
		elif bMinutes > .5 and bMinutes <= .75:
			bMinutes = .75
		else:
			bMinutes = 1

		return bHours + bMinutes

	def _getSundayOrdinal( self, dDay ):

		b = dDay.toordinal()
		bWeekSunday = b - b % 7 # Sunday

		return bWeekSunday

	def prepHeader( self, fHTML, rgsBody, sName, sRunFrom, sRunTo ):

		if fHTML:
			# Prepend Report Name
			rgsBody.append( '<html><body>' )
			rgsBody.append( '<table>' )
			rgsBody.append( '<tr><td>Report Name:</td><td>&nbsp;%s</td></tr>' % sName )

			# Prepend our report run dates to email
			rgsBody.append( '<tr><td>Start Date:</td><td>&nbsp;%s</td></tr>' % sRunFrom )
			rgsBody.append( '<tr><td>End   Date:</td><td>&nbsp;%s</td></tr>' % sRunTo )
			rgsBody.append( '</table>' )

		else:
			# Prepend Report Name
			rgsBody.append( 'Report Name: %s' % sName )

			# Prepend our report run dates to email
			rgsBody.append( 'Start Date: %s' % sRunFrom )
			rgsBody.append( 'End   Date: %s' % sRunTo )

		return rgsBody

	def prepFooter( self, fHTML, rgsBody ):

		if fHTML:
			rgsBody.append( '<p>This report was generated at %s from TigerPaw.</p></body></html>' % time.asctime() )

		else:
			rgsBody.append( '\nThis report was generated at %s from TigerPaw.' % time.asctime() )

		return rgsBody

	def getUnacceptedTimeSlips( self, sRunFrom, sRunTo ):

		self._oCursor.execute( """
			SELECT R.RepName, L.LogHours, L.LogMinutes, L.DeductHours, L.DeductMinutes, L.StartDateTime, L.EndDateTime
			FROM tblTimeSlips L, tblReps R
			WHERE
				L.Tech=R.RepNumber AND
				L.AcceptanceStatus<>1 AND
				L.StartDateTime>=%s AND
				L.EndDateTime<=%s
			ORDER BY L.StartDateTime, R.RepName
		""", ( sRunFrom, sRunTo ) )

	def _wrapUnacceptedTitle( self, fHTML, rgsBody ):

		if fHTML:
			rgsBody.append( '<h2>Unaccepted Time Slips</h2>' )
			rgsBody.append( '<table>' )
			rgsBody.append( '<tr><th>Date</th><th>Tech</th><th>Time</th></tr>' )

		else:
			rgsBody.append( '\nUnaccepted Time Slips\n-----------------------' )
			rgsBody.append( '\n%-12s%-17s%s\n' % (
				'Date', 'Tech', 'Time' ) )

		return rgsBody

	def _wrapUnacceptedItem( self, fHTML, rgsBody, oRow ):

		if fHTML:
			rgsBody.append( '<tr><td>%s</td><td>%s</td><td>%.2f</td></tr>' % (
				oRow[ 'StartDateTime' ].strftime( '%m/%d/%Y' ),
				oRow[ 'RepName' ],
				self._getAdjustedTime( oRow )
			) )

		else:
			rgsBody.append( '%-12s%-17s%.2f' % (
				oRow[ 'StartDateTime' ].strftime( '%m/%d/%Y' ),
				oRow[ 'RepName' ],
				self._getAdjustedTime( oRow )
			) )

		return rgsBody

	def _wrapUnacceptedFooter( self, fHTML, rgsBody ):

		if fHTML:
			rgsBody.append( '</table>' )

		else:
			rgsBody.append( '\n' )

		return rgsBody

	def prepUnacceptedTimeSlips( self, fHTML, rgsBody ):

		oRow = self._oCursor.fetchone()

		if not oRow: return rgsBody

		rgsBody = self._wrapUnacceptedTitle( fHTML, rgsBody )

		while oRow:
			rgsBody = self._wrapUnacceptedItem( fHTML, rgsBody, oRow )

			oRow = self._oCursor.fetchone()

		rgsBody = self._wrapUnacceptedFooter( fHTML, rgsBody )

		return rgsBody

	def getAcceptedTimeSlipsByRep( self, sRunFrom, sRunTo ):

		self._oCursor.execute( """
			SELECT R.RepName, L.LogHours, L.LogMinutes, L.DeductHours, L.DeductMinutes, L.StartDateTime, L.EndDateTime, L.LogComment, I.LaborCost
			FROM tblTimeSlips AS L, tblReps AS R, tblRepsInfo I
			WHERE
				L.Tech=R.RepNumber AND
				R.RepNumber=I.FKRepNumber AND
				L.AcceptanceStatus=1 AND
				L.StartDateTime>=%s AND
				L.StartDateTime<=%s
			ORDER BY R.RepName, L.LogComment, L.StartDateTime
		""", ( sRunFrom, sRunTo ) )

	def _wrapTitle( self, fHTML, rgsBody ):

		if fHTML:
			rgsBody.append( '<h2>TimeSlip By Rep</h2>' )

		else:
			rgsBody.append( '\nTimeSlip By Rep\n' )

		return rgsBody

	def _wrapRepTitle( self, fHTML, rgsBody, sRep ):

		if fHTML:
			rgsBody.append( '<h3>%s</h3>' % sRep )

		else:
			rgsBody.append( '\n%s\n' % sRep )

		return rgsBody

	def _wrapRepHeader( self, fHTML, rgsBody ):

		if fHTML:
			rgsBody.append( '<table>' )
			rgsBody.append( '<tr><th>Date</th><th>Time</th><th>Rate</th><th>Amount</th></tr>' )

		else:
			rgsBody.append( '%-12s%-8s%-6s%s' % (
				'Date', 'Time', 'Rate', 'Amount' ) )

		return rgsBody

	def _wrapRepItem( self, fHTML, rgsBody, oRow, bHours, bRate, bSubTotal ):

		if fHTML:
			rgsBody.append( '<tr><td>%s</td><td align="right">%.2f</td><td align="right">%0.2f</td><td align="right">%0.2f</td></tr>' % (
				oRow[ 'StartDateTime' ].strftime( '%m/%d/%Y' ),
				bHours,
				bRate,
				bSubTotal
			) )

		else:
			rgsBody.append( '%-12s%5.2f%6.2f%8.2f' % (
				oRow[ 'StartDateTime' ].strftime( '%m/%d/%Y' ),
				bHours,
				bRate,
				bSubTotal
			) )

		return rgsBody

	def _wrapTotalLine( self, fHTML, rgsBody, bTotal ):

		if fHTML:
			rgsBody.append( '<tr><td colspan="3" align="right"><strong><em>%s</em></strong></td><td align="right"><strong>%0s</strong></td></tr>' % (
				'Total', locale.format( '%.2f', float( bTotal ), grouping=True ) ) )
			rgsBody.append( '</table>' )

		else:
			rgsBody.append( '%7s  %s\n' % (
				'Total', locale.format( '%.2f', float( bTotal ), grouping=True ) ) )

		return rgsBody

	def _wrapWeekLine( self, fHTML, rgsBody, bWeek ):

		if fHTML:
			rgsBody.append( '<tr><td align="left"><strong><em>%s</em></strong></td><td colspan="3" align="left"><strong>%d</strong></td></tr>' % (
				'Week', bWeek ) )

		else:
			rgsBody.append( '%7s  %s\n' % (
				'Week', bWeek ) )

		return rgsBody

	def prepTimeSlipsByRep( self, fHTML, rgsBody ):

		oRow = self._oCursor.fetchone()

		if not oRow: return rgsBody

		rgsBody = self._wrapTitle( fHTML, rgsBody )
		sRep = ''						# Current Rep
		bTotalAmount = 0.0	# Total dollar amount per tech based on rate and hours
		bTotalHours = 0.0		# Track total hours per week for overtime
		bWeekSunday = 0			# Used to determine when we need to roll over for overtime
		bWeek = 1						# Week number

		while oRow:

			# If this is a contractor account, then pull contractor name from Comment
			sRepCheck = oRow[ 'RepName' ]
			if oRow[ 'RepName' ] == 'John Doe':
				s = oRow[ 'LogComment' ].split( ' - ' )[ 0 ]
				if s != '':
					sRepCheck = s

			bRate = float( oRow[ 'LaborCost' ] )

			if sRep != sRepCheck:
				if sRep != '':
					rgsBody = self._wrapTotalLine( fHTML, rgsBody, bTotalAmount )

				sRep = sRepCheck
				bTotalAmount = 0.0
				bTotalHours = 0.0
				bWeekSunday = self._getSundayOrdinal( oRow[ 'StartDateTime' ] )
				bWeek = 1

				rgsBody = self._wrapRepTitle( fHTML, rgsBody, sRep )

				rgsBody = self._wrapRepHeader( fHTML, rgsBody )
				rgsBody = self._wrapWeekLine( fHTML, rgsBody, bWeek )

			# Do we need to reset our overtime accumulator?
			if bWeekSunday != self._getSundayOrdinal( oRow[ 'StartDateTime' ] ):
				bWeekSunday = self._getSundayOrdinal( oRow[ 'StartDateTime' ] )
				bTotalHours = 0.0
				bWeek += 1
				rgsBody = self._wrapWeekLine( fHTML, rgsBody, bWeek )

			bHours = self._getAdjustedTime( oRow )

			# Figure overtime rate if needed
			if bTotalHours > OVERTIME_LIMIT:
				bRate = bRate * OVERTIME_MULTIPLIER
			elif bTotalHours + bHours > OVERTIME_LIMIT:
				# Handle lower tier split item here
				bHours = OVERTIME_LIMIT - bTotalHours
				bSubTotalAmount = bHours * bRate
				rgsBody = self._wrapRepItem( fHTML, rgsBody, oRow, bHours, bRate, bSubTotalAmount )
				bTotalAmount += bSubTotalAmount
				# Remainder
				bHours = bTotalHours + self._getAdjustedTime( oRow ) - OVERTIME_LIMIT
				bRate = bRate * OVERTIME_MULTIPLIER

			bSubTotalAmount = bHours * bRate
			bTotalAmount += bSubTotalAmount
			bTotalHours += self._getAdjustedTime( oRow )

			rgsBody = self._wrapRepItem( fHTML, rgsBody, oRow, bHours, bRate, bSubTotalAmount )

			oRow = self._oCursor.fetchone()

		if sRep != '':
			rgsBody = self._wrapTotalLine( fHTML, rgsBody, bTotalAmount )

		return rgsBody

	def run( self, sRunFrom, sRunTo, fHTML=True ):

		sReport = 'Tech Time Slips'
		rgsBody = []

		self = App()

		rgsBody = self.prepHeader( fHTML, rgsBody, sReport, sRunFrom, sRunTo )

		# Unaccepted Time Logs
		self.getUnacceptedTimeSlips( sRunFrom, sRunTo )
		rgsBody = self.prepUnacceptedTimeSlips( fHTML, rgsBody )

		# TimeSlips
		self.getAcceptedTimeSlipsByRep( sRunFrom, sRunTo )
		rgsBody = self.prepTimeSlipsByRep( fHTML, rgsBody )

		rgsBody = self.prepFooter( fHTML, rgsBody )

		self.finish()

		return( "\n".join( rgsBody ) )

def main( argv ):

	sRunFrom = '2017-10-01'
	sRunTo = '2017-10-07'

	oApp = App()
	print oApp.run( sRunFrom, sRunTo, False )

	return 0

if __name__ == '__main__':
	sys.exit( main( sys.argv ) )
