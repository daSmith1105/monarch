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
		rgsBody.append( '<title>Report Name: %s - Items to Purchase</title>' % sName )
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
		rgsBody.append( '<h2>Items to Purchase</h2>' )
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

	def getItemsToPurchase( self ):

		self._oCursor.execute( """
			SELECT
				P.SONumber,
				A.AccountName,
				P.ItemID,
				P.ItemDescription,
				P.Quantity,
				P.QuantityFilled,
				P.QuantityOrdered,
				P.QuantityReceived
			FROM 
				tblSOPartsUsed AS P,
				tblServiceOrders AS S,
				tblAccounts AS A
			WHERE 
				S.AccountNumber = A.AccountNumber AND
				S.SONumber = P.SONumber AND
				S.Status <> 'Void' AND
				S.Status <> 'Closed' AND
				P.QuantityFilled < P.Quantity AND
				P.Quantity - P.QuantityFilled > P.QuantityOrdered AND
				P.Type='M'
			ORDER BY
				P.SONumber, P.ItemID
		""" )

	def prepItemsToPurchaseHTML( self, rgsBody ):

		oRow = self._oCursor.fetchone()

		if not oRow: return rgsBody

		rgsBody.append( '<table>' )
		rgsBody.append( '<thead><tr><th>SO</th><th>Account</th><th>Item</th><th>Description</th><th>Quantity</th><th>Filled</th><th>On Order</th><th>Received</th></tr></thead><tbody>' )

		while oRow:

			rgsBody.append( '<tr><td>%d</td><td>%s</td><td>%s</td><td>%s</td><td>%d</td><td>%d</td><td>%d</td><td>%d</td></tr>' % (
				oRow[ 'SONumber' ],
				oRow[ 'AccountName' ],
				oRow[ 'ItemID' ],
				oRow[ 'ItemDescription' ],
				oRow[ 'Quantity' ],
				oRow[ 'QuantityFilled' ],
				oRow[ 'QuantityOrdered' ],
				oRow[ 'QuantityReceived' ]
			) )

			oRow = self._oCursor.fetchone()

		rgsBody.append( '</tbody></table>' )

		return rgsBody

	def prepItemsToPurchasePlain( self, rgsBody ):

		oRow = self._oCursor.fetchone()

		if not oRow: return rgsBody

		rgsBody.append( '\nItems To Purchase\n' )

		rgsBody.append( '%-7s%-25s%-7s%-25s%-7s%-7s%-7s%s\n' % (
			'SO', 'Account', 'Item', 'Decription', 'Quantity', 'Filled', 'On Order', 'Received' ) )

		while oRow:

			rgsBody.append( '%-7d%-25s%-7s%-25s%-7s%-7s%-7s%s' % (
				oRow[ 'SONumber' ],
				oRow[ 'AccountName' ],
				oRow[ 'ItemID' ],
				oRow[ 'ItemDescription' ],
				oRow[ 'Quantity' ],
				oRow[ 'QuantityFilled' ],
				oRow[ 'QuantityOrdered' ],
				oRow[ 'QuantityReceived' ]
			) )

			oRow = self._oCursor.fetchone()

		rgsBody.append( '\n' )

		return rgsBody

	def run( self, fHTML=True ):
		sReport = 'Van Inventory'
		rgsBody = []

		if fHTML:
			rgsBody = self.prepHeaderHTML( rgsBody, sReport )

			# Inventory
			self.getItemsToPurchase()
			rgsBody = self.prepItemsToPurchaseHTML( rgsBody )

			rgsBody = self.prepFooterHTML( rgsBody )

		else:
			rgsBody = self.prepHeaderPlain( rgsBody, sReport )

			# Inventory
			self.getItemsToPurchase()
			rgsBody = self.prepItemsToPurchasePlain( rgsBody )

			rgsBody = self.prepFooterPlain( rgsBody )

		self.finish()

		return( "\n".join( rgsBody ) )


def main( argv ):

	oApp = App()
	print oApp.run( False )

	return 0

if __name__ == '__main__':
	sys.exit( main( sys.argv ) )
