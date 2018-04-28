#!/usr/bin/python

import sys
import pymssql
import time

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


	def prepHeaderHTML( self, rgsBody, sName ):

		# Prepend Report Name
		rgsBody.append( '<html>' )
		rgsBody.append( '<title>Report Name: %s - Merge Locator Bins to Price Book</title>' % sName )
		rgsBody.append( """
<head>
<style type="text/css">
@media all {
	H1, H2, H3 {
		font-family: "Lucida Sans Unicode", "Lucida Grande", Sans-Serif;
		color: #039;
		background: #fff;
		text-align: left;
	}
	TABLE {
		font-family: "Lucida Sans Unicode", "Lucida Grande", Sans-Serif;
		font-size: 12px;
		background: #fff;
		margin: 2%;
		width: 96%;
		border-collapse: collapse;
		text-align: left;
	}

	TABLE TH {
		font-size: 14px;
		font-weight: normal;
		color: #039;
		padding: 10px 8px;
		border-bottom: 2px solid #6678b1;
	}

	TABLE TD {
		border-bottom: 1px solid #ccc;
		color: #669;
		padding: 6px 8px;
	}

	TABLE TBODY TR:hover TD {
		color: #000;
	}
}
@media print {
	.header { display: none; }
	.footer { display: none; }
	TABLE { page-break-after: always; }
}
</style>
</head>
		""" )
		rgsBody.append( '<body>' )
		rgsBody.append( '<div class="header">' )
		rgsBody.append( '<h1>Report Name:&nbsp;%s</h1>' % sName )
		rgsBody.append( '<h2>Merge Locator Bins to Price Book</h2>' )
		rgsBody.append( '</div>' )

		return rgsBody

	def prepHeaderPlain( self, rgsBody, sName ):

		# Prepend Report Name
		rgsBody.append( 'Report Name: %s' % sName )

		return rgsBody

	def prepFooterHTML( self, rgsBody ):

		rgsBody.append( '<div class="footer">This report was generated at %s from TigerPaw.</div></body></html>' % time.asctime() )

		return rgsBody

	def prepFooterPlain( self, rgsBody ):

		rgsBody.append( '\nThis report was generated at %s from TigerPaw.' % time.asctime() )

		return rgsBody

	def getBinsByLocator( self ):

		self._oCursor.execute( """
			SELECT
				L.ItemID, L.Bin
			FROM
				tblLocator AS L
			WHERE
				L.Location = %s AND
				L.Bin IS NOT NULL
			ORDER BY
				L.Bin, L.ItemID
		""", ( 'WH1' ) )

		return self._oCursor.fetchall()

	def updatePriceBookBin( self, sItem, sBin ):

		self._oCursor.execute( """
			UPDATE
				tblPriceBook
			SET
				Bin = %s
			WHERE
				ItemID = %s
		""", ( sBin, sItem ) )
		self._oDB.commit()

	def mergeLocatorBinsToPriceBookHTML( self, rgoRows, rgsBody ):

		if len( rgoRows ) == 0: return rgsBody

		sBin = ''

		for oRow in rgoRows:

			if sBin != oRow[ 'Bin' ]:
				if sBin != '':
					rgsBody.append( '</tbody></table>' )

				sBin = oRow[ 'Bin' ]

				rgsBody.append( '<h3>Bin [%s]</h3>' % sBin )

				rgsBody.append( '<table>' )
				rgsBody.append( '<thead><tr><th>Item</th></tr></thead><tbody>' )

			self.updatePriceBookBin( oRow[ 'ItemID' ], oRow[ 'Bin' ] )

			rgsBody.append( '<tr><td>%s</td></tr>' % (
				oRow[ 'ItemID' ]
			) )

		if sBin != '':
			rgsBody.append( '</tbody></table>' )

		return rgsBody

	def mergeLocatorBinsToPriceBookPlain( self, rgoRows, rgsBody ):

		if len( rgoRows ) == 0: return rgsBody

		rgsBody.append( '\nLocator Bins for WH1\n' )
		sBin = ''

		for oRow in rgoRows:

			if sBin != oRow[ 'Bin' ]:
				if sBin != '':
					rgsBody.append( '\n' )

				sBin = oRow[ 'Bin' ]

				rgsBody.append( '\nBin [%s]\n' % sBin )

				rgsBody.append( '%s\n' % (
					'Item' ) )

			self.updatePriceBookBin( oRow[ 'ItemID' ], oRow[ 'Bin' ] )

			rgsBody.append( '%s' % (
				oRow[ 'ItemID' ]
			) )

		if sBin != '':
			rgsBody.append( '\n' )

		rgsBody.append( '\n' )

		return rgsBody

	def run( self, fHTML=True ):
		sReport = 'Merge Location Bin to Price Book'
		fHTML = False
		rgsBody = []

		if fHTML:
			rgsBody = self.prepHeaderHTML( rgsBody, sReport )

			# Inventory
			rgoRows = self.getBinsByLocator()
			rgsBody = self.mergeLocatorBinsToPriceBookHTML( rgoRows, rgsBody )

			rgsBody = self.prepFooterHTML( rgsBody )

		else:
			rgsBody = self.prepHeaderPlain( rgsBody, sReport )

			# Inventory
			rgoRows = self.getBinsByLocator()
			rgsBody = self.mergeLocatorBinsToPriceBookPlain( rgoRows, rgsBody )

			rgsBody = self.prepFooterPlain( rgsBody )

		self.finish()

		return( "\n".join( rgsBody ) )


def main( argv ):

	oApp = App()
	print oApp.run( False )

	return 0

if __name__ == '__main__':
	sys.exit( main( sys.argv ) )
