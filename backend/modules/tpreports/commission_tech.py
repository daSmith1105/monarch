#!/usr/bin/python

import sys
import pymssql
import time

DB_HOST = 'tigerpaw'
DB_USER = 'sa'
DB_PASS = 'Y3R]=68RF4'
DB_NAME = 'TigerPaw'

TECH_COMM = {}
TECH_COMM[ 'Default' ] = {}
TECH_COMM[ 'Default' ][ 'Solo' ] = .20
TECH_COMM[ 'Default' ][ 'Split' ] = .15

RATE_INSTALL = 120
RATE_SERVICE = 75


class App:

	_oDB = None
	_oCursor = None

	def __init__( self ):
		self._oDB = pymssql.connect( DB_HOST, DB_USER, DB_PASS, DB_NAME )
		self._oCursor = self._oDB.cursor( as_dict=True )

	def finish( self ):

		self._oDB.close()


	def prepHeaderHTML( self, rgsBody, sName, sRunFrom, sRunTo ):

		# Prepend Report Name
		rgsBody.append( '<html><body>' )
		rgsBody.append( '<table>' )
		rgsBody.append( '<tr><td>Report Name:</td><td>&nbsp;%s</td></tr>' % sName )

		# Prepend our report run dates to email
		rgsBody.append( '<tr><td>Start Date:</td><td>&nbsp;%s</td></tr>' % sRunFrom )
		rgsBody.append( '<tr><td>End   Date:</td><td>&nbsp;%s</td></tr>' % sRunTo )
		rgsBody.append( '</table>' )

		return rgsBody

	def prepHeaderPlain( self, rgsBody, sName, sRunFrom, sRunTo ):

		# Prepend Report Name
		rgsBody.append( 'Report Name: %s' % sName )

		# Prepend our report run dates to email
		rgsBody.append( 'Start Date: %s' % sRunFrom )
		rgsBody.append( 'End   Date: %s' % sRunTo )

		return rgsBody

	def prepFooterHTML( self, rgsBody ):

		rgsBody.append( '<p>This report was generated at %s from TigerPaw.</p></body></html>' % time.asctime() )

		return rgsBody

	def prepFooterPlain( self, rgsBody ):

		rgsBody.append( '\nThis report was generated at %s from TigerPaw.' % time.asctime() )

		return rgsBody

	def getUnacceptedTimeLogs( self, sRunFrom, sRunTo ):

		self._oCursor.execute( """
			SELECT L.SONumber, R.RepName, A.AccountName, L.TimeLogReason, L.LogHours, L.LogMinutes, L.StartDateTime, L.EndDateTime
			FROM tblSOLogs L, tblReps R, tblAccounts A
			WHERE
				L.Tech=R.RepNumber AND
				L.AccountNumber=A.AccountNumber AND
				L.AcceptanceStatus=0 AND
				L.StartDateTime>=%s AND
				L.EndDateTime<=%s
			ORDER BY L.StartDateTime, L.SONumber, A.AccountName, R.RepName
		""", ( sRunFrom, sRunTo ) )

	def prepUnacceptedTimeLogsHTML( self, rgsBody ):

		oRow = self._oCursor.fetchone()

		if not oRow: return rgsBody

		rgsBody.append( '<h2>Unaccepted Time Logs</h2>' )
		rgsBody.append( '<table>' )
		rgsBody.append( '<tr><th>Date</th><th>SO</th><th>Account</th><th>Type</th><th>Tech</th><th>Time</th></tr>' )

		while oRow:
			rgsBody.append( '<tr><td>%s</td><td>%d</td><td>%s</td><td>%s</td><td>%s</td><td>%.2f</td></tr>' % (
				oRow[ 'StartDateTime' ].strftime( '%m/%d/%Y' ),
				oRow[ 'SONumber' ],
				oRow[ 'AccountName' ],
				oRow[ 'TimeLogReason' ],
				oRow[ 'RepName' ],
				oRow[ 'LogHours' ] + oRow[ 'LogMinutes' ] / 60.0
			) )

			oRow = self._oCursor.fetchone()

		rgsBody.append( '</table>' )

		return rgsBody

	def prepUnacceptedTimeLogsPlain( self, rgsBody ):

		oRow = self._oCursor.fetchone()

		if not oRow: return rgsBody

		rgsBody.append( '\nUnaccepted Time Logs\n-----------------------' )
		rgsBody.append( '\n%-12s%-7s%-30s%-9s%-17s%s\n' % (
			'Date', 'SO', 'Account', 'Type', 'Tech', 'Time' ) )

		while oRow:
			rgsBody.append( '%-12s%-7d%-30s%-9s%-17s%.2f' % (
				oRow[ 'StartDateTime' ].strftime( '%m/%d/%Y' ),
				oRow[ 'SONumber' ],
				oRow[ 'AccountName' ][ 0:28 ],
				oRow[ 'TimeLogReason' ],
				oRow[ 'RepName' ],
				oRow[ 'LogHours' ] + oRow[ 'LogMinutes' ] / 60.0
			) )

			oRow = self._oCursor.fetchone()

		rgsBody.append( '\n' )

		return rgsBody

	def getAcceptedTimeLogsByRep( self, sRunFrom, sRunTo ):

		self._oCursor.execute( """
			SELECT L.SONumber, R.RepName, A.AccountName, L.TimeLogReason, L.LogHours, L.LogMinutes, L.StartDateTime, L.EndDateTime,
				( SELECT COUNT( DISTINCT Q.Tech ) FROM tblSOLogs AS Q WHERE L.SONumber=Q.SONumber ) AS Count, L.LogComment
			FROM tblSOLogs AS L, tblReps AS R, tblAccounts AS A
			WHERE
				L.Tech=R.RepNumber AND
				L.AccountNumber=A.AccountNumber AND
				L.AcceptanceStatus=1 AND
				L.StartDateTime>=%s AND
				L.StartDateTime<=%s
			ORDER BY R.RepName, L.StartDateTime, A.AccountName
		""", ( sRunFrom, sRunTo ) )

	def prepCommissionByRepHTML( self, rgsBody ):

		oRow = self._oCursor.fetchone()

		if not oRow: return rgsBody

		rgsBody.append( '<h2>Commission By Rep</h2>' )
		sRep = ''
		bTotal = 0.0

		while oRow:

			if sRep != oRow[ 'RepName' ]:
				if sRep != '':
					rgsBody.append( '<tr><td colspan="7" align="right"><strong><em>%s</em></strong></td><td align="right"><strong>%0.2f</strong></td></tr>' % (
						'Total', bTotal ) )
					rgsBody.append( '</table>' )

				sRep = oRow[ 'RepName' ]
				bTotal = 0.0

				rgsBody.append( '<h3>%s</h3>' % sRep )

				rgsBody.append( '<table>' )
				rgsBody.append( '<tr><th>Date</th><th>SO</th><th>Account</th><th>Type</th><th>Time</th><th>Rate</th><th>Comm</th><th>Amount</th></tr>' )

			# If this is a contractor account, then pull contractor name from Comment
			sAccountName = oRow[ 'AccountName' ]
			if oRow[ 'RepName' ] == 'John Doe':
				rgs = oRow[ 'LogComment' ].split( ' - ' )
				if len( rgs ) > 1:
					sAccountName = '%s - %s' % ( rgs[ 0 ], sAccountName )

			bCommSolo = TECH_COMM[ 'Default' ][ 'Solo' ]
			bCommSplit = TECH_COMM[ 'Default' ][ 'Split' ]
			if sRep in TECH_COMM.keys():
				bCommSolo = TECH_COMM[ sRep ][ 'Solo' ]
				bCommSplit = TECH_COMM[ sRep ][ 'Split' ]

			bComm = bCommSolo
			sSplit = 'Solo'
			if oRow[ 'Count' ] > 1:
				sSplit = 'Split'
				bComm = bCommSplit

			bRate = RATE_SERVICE
			if oRow[ 'TimeLogReason' ] == 'Install':
				bRate = RATE_INSTALL

			bHours = oRow[ 'LogHours' ] + oRow[ 'LogMinutes' ] / 60.0
			bSubTotal = bHours * bRate * bComm
			bTotal += bSubTotal

			rgsBody.append( '<tr><td>%s</td><td>%d</td><td>%s</td><td>%s</td><td align="right">%.2f</td><td align="right">%d</td><td align="right">%d%%</td><td align="right">%0.2f</td></tr>' % (
				oRow[ 'StartDateTime' ].strftime( '%m/%d/%Y' ),
				oRow[ 'SONumber' ],
				sAccountName,
				'%s %s' % ( oRow[ 'TimeLogReason' ], sSplit ),
				bHours,
				bRate,
				int( bComm * 100 ),
				bSubTotal
			) )

			oRow = self._oCursor.fetchone()

		if sRep != '':
			rgsBody.append( '<tr><td colspan="7" align="right"><strong><em>%s</em></strong></td><td align="right"><strong>%0.2f</strong></td></tr>' % (
				'Total', bTotal ) )
			rgsBody.append( '</table>' )

		return rgsBody

	def prepCommissionByRepPlain( self, rgsBody ):

		oRow = self._oCursor.fetchone()

		if not oRow: return rgsBody

		rgsBody.append( '\nCommission By Rep\n' )
		sRep = ''
		bTotal = 0.0

		while oRow:

			if sRep != oRow[ 'RepName' ]:
				if sRep != '':
					rgsBody.append( '%7s  %0.2f\n' % (
						'Total', bTotal ) )

				sRep = oRow[ 'RepName' ]
				bTotal = 0.0

				rgsBody.append( '\n%s\n' % sRep )

				rgsBody.append( '%-12s%-7s%-30s%-15s%-8s%-6s%-6s%s' % (
					'Date', 'SO', 'Account', 'Type', 'Time', 'Rate', 'Comm', 'Amount' ) )

			# If this is a contractor account, then pull contractor name from Comment
			sAccountName = oRow[ 'AccountName' ][ 0:28 ]
			if oRow[ 'RepName' ] == 'John Doe':
				rgs = oRow[ 'LogComment' ].split( ' - ' )
				if len( rgs ) > 1:
					sAccountName = '%s - %s' % ( rgs[ 0 ], sAccountName )

			bCommSolo = TECH_COMM[ 'Default' ][ 'Solo' ]
			bCommSplit = TECH_COMM[ 'Default' ][ 'Split' ]
			if sRep in TECH_COMM.keys():
				bCommSolo = TECH_COMM[ sRep ][ 'Solo' ]
				bCommSplit = TECH_COMM[ sRep ][ 'Split' ]

			bComm = bCommSolo
			sSplit = 'Solo'
			if oRow[ 'Count' ] > 1:
				sSplit = 'Split'
				bComm = bCommSplit

			bRate = RATE_SERVICE
			if oRow[ 'TimeLogReason' ] == 'Install':
				bRate = RATE_INSTALL

			bHours = oRow[ 'LogHours' ] + oRow[ 'LogMinutes' ] / 60.0
			bSubTotal = bHours * bRate * bComm
			bTotal += bSubTotal

			rgsBody.append( '%-12s%-7d%-30s%-15s%5.2f%6d%6d%%%8.2f' % (
				oRow[ 'StartDateTime' ].strftime( '%m/%d/%Y' ),
				oRow[ 'SONumber' ],
				sAccountName,
				'%s %s' % ( oRow[ 'TimeLogReason' ], sSplit ),
				bHours,
				bRate,
				int( bComm * 100 ),
				bSubTotal
			) )

			oRow = self._oCursor.fetchone()

		if sRep != '':
			rgsBody.append( '%7s  %0.2f\n' % (
				'Total', bTotal ) )

		rgsBody.append( '\n' )

		return rgsBody


	def run( self, sRunFrom, sRunTo, fHTML=True ):

		sReport = 'Tech Commission'
		rgsBody = []

		self = App()

		if fHTML:
			rgsBody = self.prepHeaderHTML( rgsBody, sReport, sRunFrom, sRunTo )

			# Unaccepted Time Logs
			self.getUnacceptedTimeLogs( sRunFrom, sRunTo )
			rgsBody = self.prepUnacceptedTimeLogsHTML( rgsBody )

			# Commission
			self.getAcceptedTimeLogsByRep( sRunFrom, sRunTo )
			rgsBody = self.prepCommissionByRepHTML( rgsBody )

			rgsBody = self.prepFooterHTML( rgsBody )

		else:
			rgsBody = self.prepHeaderPlain( rgsBody, sReport, sRunFrom, sRunTo )

			# Unaccepted Time Logs
			self.getUnacceptedTimeLogs( sRunFrom, sRunTo )
			rgsBody = self.prepUnacceptedTimeLogsPlain( rgsBody )

			# Commission
			self.getAcceptedTimeLogsByRep( sRunFrom, sRunTo )
			rgsBody = self.prepCommissionByRepPlain( rgsBody )

			rgsBody = self.prepFooterPlain( rgsBody )

		self.finish()

		return( "\n".join( rgsBody ) )

def main( argv ):

	sRunFrom = '2016-01-31'
	sRunTo = '2016-02-13'

	oApp = App()
	print oApp.run( sRunFrom, sRunTo, False )

	return 0

if __name__ == '__main__':
	sys.exit( main( sys.argv ) )
