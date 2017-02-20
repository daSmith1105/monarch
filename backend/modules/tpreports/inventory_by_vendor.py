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


	def prepHeaderHTML( self, rgsBody, sName, sVendor ):

		# Prepend Report Name
		rgsBody.append( '<html>' )
		rgsBody.append( '<title>Report Name: %s - %s</title>' % ( sName, sVendor ) )
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
		rgsBody.append( '<h1>Report Name:&nbsp;%s - %s</h1>' % ( sName, sVendor ) )
		rgsBody.append( '<h2>Inventory By Vendor</h2>' )
		rgsBody.append( '</div>' )

		return rgsBody

	def prepHeaderPlain( self, rgsBody, sName, sVendor ):

		# Prepend Report Name
		rgsBody.append( 'Report Name: %s - %s' % ( sName, sVendor ) )

		return rgsBody

	def prepFooterHTML( self, rgsBody ):

		rgsBody.append( '<div class="footer">This report was generated at %s from TigerPaw.</div></body></html>' % time.asctime() )

		return rgsBody

	def prepFooterPlain( self, rgsBody ):

		rgsBody.append( '\nThis report was generated at %s from TigerPaw.' % time.asctime() )

		return rgsBody

	def getInventoryByVendor( self, sVendor ):

		self._oCursor.execute( """
			SELECT
				L.Location, L.Quantity, L.Min, L.Max, P.ItemCategory, P.ItemSubCategory, P.PartNumber, P.ItemDescription
			FROM
				tblPriceBook AS P,
				tblLocator AS L,
				tblAccounts AS A
			WHERE
				P.ItemID = L.ItemID AND
				P.PrimaryVendorAccountNumber = A.AccountNumber AND
				P.Inactive=0 AND
				L.Location='WH1' AND
				A.AccountName LIKE '%s%%'
			ORDER BY
				L.Location, P.ItemCategory, P.ItemSubCategory, P.PartNumber
		""" % sVendor.upper() )

	def prepInventoryByVendorHTML( self, rgsBody ):

		oRow = self._oCursor.fetchone()

		if not oRow: return rgsBody

		sLocation = ''

		while oRow:

			if sLocation != oRow[ 'Location' ]:
				if sLocation != '':
					rgsBody.append( '</tbody></table>' )

				sLocation = oRow[ 'Location' ]

				rgsBody.append( '<h3>%s</h3>' % sLocation )

				rgsBody.append( '<table>' )
				rgsBody.append( '<thead><tr><th>Qty</th><th>Min</th><th>Max</th><th>Count</th><th>Category</th><th>Part Number</th><th>Description</th></tr></thead><tbody>' )

			rgsBody.append( '<tr><td>%d</td><td>%d</td><td>%d</td><td>&nbsp;</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (
				oRow[ 'Quantity' ],
				oRow[ 'Min' ],
				oRow[ 'Max' ],
				'%s:%s' % ( oRow[ 'ItemCategory' ], oRow[ 'ItemSubCategory' ] ),
				oRow[ 'PartNumber' ],
				oRow[ 'ItemDescription' ]
			) )

			oRow = self._oCursor.fetchone()

		if sLocation != '':
			rgsBody.append( '</tbody></table>' )

		return rgsBody

	def prepInventoryByVendorPlain( self, rgsBody ):

		oRow = self._oCursor.fetchone()

		if not oRow: return rgsBody

		rgsBody.append( '\nInventory By Location\n' )
		sLocation = ''

		while oRow:

			if sLocation != oRow[ 'Location' ]:
				if sLocation != '':
					rgsBody.append( '\n' )

				sLocation = oRow[ 'Location' ]

				rgsBody.append( '\n%s\n' % sLocation )

				rgsBody.append( '%-7s%-7s%-7s%-7s%-25s%-10s%s\n' % (
					'Qty', 'Min', 'Max', 'Count', 'Category', 'Part Number', 'Description' ) )

			rgsBody.append( '%-7d%-7d%-7d%-7s%-25s%-10s%s' % (
				oRow[ 'Quantity' ],
				oRow[ 'Min' ],
				oRow[ 'Max' ],
				'_____',
				'%s:%s' % ( oRow[ 'ItemCategory'    ][ 0:15 ], oRow[ 'ItemSubCategory' ][ 0:15 ] ),
				oRow[ 'PartNumber'  ][ 0:15 ],
				oRow[ 'ItemDescription' ]
			) )

			oRow = self._oCursor.fetchone()

		if sLocation != '':
			rgsBody.append( '\n' )

		rgsBody.append( '\n' )

		return rgsBody


	def run( self, fHTML=True ):

		sReport = 'Inventory Count'
		sVendor = 'Zavio'
		rgsBody = []

		if fHTML:
			rgsBody = self.prepHeaderHTML( rgsBody, sReport, sVendor )

			# Inventory
			self.getInventoryByVendor( sVendor )
			rgsBody = self.prepInventoryByVendorHTML( rgsBody )

			rgsBody = self.prepFooterHTML( rgsBody )

		else:
			rgsBody = self.prepHeaderPlain( rgsBody, sReport, sVendor )

			# Inventory
			self.getInventoryByVendor( sVendor )
			rgsBody = self.prepInventoryByVendorPlain( rgsBody )

			rgsBody = self.prepFooterPlain( rgsBody )

		self.finish()

		return( "\n".join( rgsBody ) )

def main( argv ):

	oApp = App()
	print oApp.run( False )

	return 0

if __name__ == '__main__':
	sys.exit( main( sys.argv ) )
