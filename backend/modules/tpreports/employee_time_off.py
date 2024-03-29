#!/usr/bin/python

import sys
import pymssql
import time
from datetime import datetime

DB_HOST = 'tigerpaw'
DB_USER = 'sa'
DB_PASS = 'Y3R]=68RF4'
DB_NAME = 'TigerPaw'


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

	def getTimeOff( self, sRunFrom, sRunTo ):

		self._oCursor.execute( """
			SELECT
				R.RepName,
				T.Subject,
				T.TaskComment,
				T.WholeStart,
				T.WholeEnd,
				T.TaskCompletedIndicator
			FROM
				tblTasks T,
				tblReps R
			WHERE
				T.ScheduledForRepNumber = R.RepNumber AND 
				R.Inactive = 0 AND
				T.TaskAction = 'Time Off' AND
				( T.Subject LIKE '%Sick%' OR T.Subject LIKE '%Vacation%' OR T.Subject LIKE '%Company%' ) AND
				T.StartDate>=%s AND
				T.EndDate <=%s
			ORDER BY R.RepName, T.WholeStart
		""", ( sRunFrom, sRunTo ) )

	def prepTimeOffHTML( self, rgsBody ):

		oRow = self._oCursor.fetchone()

		if not oRow: return rgsBody

		rgsBody.append( '<h2>Time Off By Rep</h2>' )
		sRep = ''
		bSick = bVacation = bCompany = 0

		while oRow:

			if sRep != oRow[ 'RepName' ]:
				if sRep != '':
					rgsBody.append( '<tr><td colspan="5"><strong><em>%s</em></strong></td></tr>' % (
						'Sick-[%0.2f] Vacation-[%0.2f] Company-[%0.2f]' % ( bSick / 8.0, bVacation / 8.0, bCompany / 8.0 ) ) )
					rgsBody.append( '</table>' )

				sRep = oRow[ 'RepName' ]
				bSick = bVacation = bCompany = 0

				rgsBody.append( '<h3>%s</h3>' % sRep )

				rgsBody.append( '<table>' )
				rgsBody.append( '<tr><th>Date</th><th>Type</th><th>Comment</th><th>Duration</th><th>Completed</th></tr>' )

			# Looks like WholeStart is already a DateTime object
			#oStart = datetime.strptime( oRow[ 'WholeStart' ], '%Y-%m-%d %H:%M:%S.000' )
			#oEnd = datetime.strptime( oRow[ 'WholeEnd' ], '%Y-%m-%d %H:%M:%S.000' )
			oStart = oRow[ 'WholeStart' ]
			oEnd = oRow[ 'WholeEnd' ]

			sType = 'N/A'
			oTimeDelta = oEnd - oStart
			bHours = oTimeDelta.seconds / 3600

			# Normalize the hours
			if bHours == 9:
				bHours = 8
			if bHours > 2 and bHours <= 4:
				bHours = 4

			if oRow[ 'Subject' ].lower().startswith( 'sick' ):
				bSick += bHours
				sType = 'Sick'
			elif oRow[ 'Subject' ].lower().startswith( 'vacation' ):
				bVacation += bHours
				sType = 'Vacation'
			elif oRow[ 'Subject' ].lower().startswith( 'company' ):
				bCompany += bHours
				sType = 'Company'

			sComment = ''
			if oRow[ 'TaskComment' ] is not None and len( oRow[ 'TaskComment' ] ) > 0:
				sComment = oRow[ 'TaskComment' ].replace( '\r\n', ' ' )[ 0:28 ]
			# Remove default TP Comment like 'Ryan Ayers at Dividia'
			if sComment[0:10] == 'Ryan Ayers':
				sComment = ''

			rgsBody.append( '<tr><td>%s</td><td>%s</td><td>%s</td><td align="right">%s</td><td align="right">%d</td></tr>' % (
				oStart.strftime( '%m/%d/%Y' ),
				sType,
				sComment,
				'%sHR' % bHours,
				oRow[ 'TaskCompletedIndicator' ]
			) )

			oRow = self._oCursor.fetchone()

		if sRep != '':
			rgsBody.append( '<tr><td colspan="5"><strong><em>%s</em></strong></td></tr>' % (
				'Sick-[%0.2f] Vacation-[%0.2f] Company-[%0.2f]' % ( bSick / 8.0, bVacation / 8.0, bCompany / 8.0 ) ) )
			rgsBody.append( '</table>' )

		return rgsBody

	def prepTimeOffPlain( self, rgsBody ):

		oRow = self._oCursor.fetchone()

		if not oRow: return rgsBody

		rgsBody.append( '\nTime Off By Rep\n' )
		sRep = ''
		bSick = bVacation = bCompany = 0

		while oRow:

			if sRep != oRow[ 'RepName' ]:
				if sRep != '':
					rgsBody.append( '\n- Sick-[%0.2f] Vacation-[%0.2f] Company-[%0.2f]\n' % ( bSick / 8.0, bVacation / 8.0, bCompany / 8.0 ) )

				sRep = oRow[ 'RepName' ]
				bSick = bVacation = bCompany = 0

				rgsBody.append( '\n%s\n' % sRep )

				rgsBody.append( '%-12s%-10s%-30s%-12s%s' % (
					'Date', 'Type', 'Comment', 'Duration', 'Completed' ) )

			# Looks like WholeStart is already a DateTime object
			#oStart = datetime.strptime( oRow[ 'WholeStart' ], '%Y-%m-%d %H:%M:%S.000' )
			#oEnd = datetime.strptime( oRow[ 'WholeEnd' ], '%Y-%m-%d %H:%M:%S.000' )
			oStart = oRow[ 'WholeStart' ]
			oEnd = oRow[ 'WholeEnd' ]

			sType = 'N/A'
			oTimeDelta = oEnd - oStart
			bHours = oTimeDelta.seconds / 3600

			# Normalize the hours
			if bHours == 9:
				bHours = 8
			if bHours > 2 and bHours <= 4:
				bHours = 4

			if oRow[ 'Subject' ].lower().startswith( 'sick' ):
				bSick += bHours
				sType = 'Sick'
			elif oRow[ 'Subject' ].lower().startswith( 'vacation' ):
				bVacation += bHours
				sType = 'Vacation'
			elif oRow[ 'Subject' ].lower().startswith( 'company' ):
				bCompany += bHours
				sType = 'Company'

			sComment = ''
			if oRow[ 'TaskComment' ] is not None and len( oRow[ 'TaskComment' ] ) > 0:
				sComment = oRow[ 'TaskComment' ].replace( '\r\n', ' ' )[ 0:28 ]
			# Remove default TP Comment like 'Ryan Ayers at Dividia'
			if sComment == 'Ryan Ayers at DIVIDIA (817)	': sComment = ''

			rgsBody.append( '%-12s%-10s%-30s%-12s%d' % (
				oStart.strftime( '%m/%d/%Y' ),
				sType,
				sComment,
				'%sHR' % bHours,
				oRow[ 'TaskCompletedIndicator' ]
			) )

			oRow = self._oCursor.fetchone()

		if sRep != '':
			rgsBody.append( '\n- Sick-[%0.2f] Vacation-[%0.2f] Company-[%0.2f]\n' % ( bSick / 8.0, bVacation / 8.0, bCompany / 8.0 ) )

		#rgsBody.append( '\n' )

		return rgsBody


	def run( self, sRunFrom, sRunTo, fHTML=True ):

		sReport = 'Employee Time Off'
		rgsBody = []
		sRunFrom = '2019-01-01'
		sRunTo = '2019-12-31'

		self = App()

		if fHTML:
			rgsBody = self.prepHeaderHTML( rgsBody, sReport, sRunFrom, sRunTo )

			# Time Off Detail
			self.getTimeOff( sRunFrom, sRunTo )
			rgsBody = self.prepTimeOffHTML( rgsBody )

			rgsBody = self.prepFooterHTML( rgsBody )

		else:
			rgsBody = self.prepHeaderPlain( rgsBody, sReport, sRunFrom, sRunTo )

			# Time Off Detail
			self.getTimeOff( sRunFrom, sRunTo )
			rgsBody = self.prepTimeOffPlain( rgsBody )

			rgsBody = self.prepFooterPlain( rgsBody )

		self.finish()

		return( "\n".join( rgsBody ) )

def main( argv ):

	sRunFrom = '2019-01-01'
	sRunTo = '2019-12-31'

	oApp = App()
	print oApp.run( sRunFrom, sRunTo, True )

	return 0

if __name__ == '__main__':
	sys.exit( main( sys.argv ) )
