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
		rgsBody.append( '<title>Report Name: %s</title>' % ( sName ) )
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
		rgsBody.append( '<h1>Report Name:&nbsp;%s</h1>' % ( sName ) )
		rgsBody.append( '</div>' )

		return rgsBody

	def prepHeaderPlain( self, rgsBody, sName ):

		# Prepend Report Name
		rgsBody.append( 'Report Name: %s' % ( sName ) )

		return rgsBody

	def prepFooterHTML( self, rgsBody ):

		rgsBody.append( '<div class="footer">This report was generated at %s from TigerPaw.</div></body></html>' % time.asctime() )

		return rgsBody

	def prepFooterPlain( self, rgsBody ):

		rgsBody.append( '\nThis report was generated at %s from TigerPaw.' % time.asctime() )

		return rgsBody

	def getPriceBookItems( self ):

		self._oCursor.execute( """
			SELECT
				P.ItemCategory, P.ItemSubCategory, P.ItemID, P.ItemDescription, P.Description2 AS Unit,
				( SELECT
						CV.CustomFieldValue
					FROM
						tblCustomFieldValues AS CV,
					tblCustomFieldDefinitions AS CD
					WHERE
						CV.CustomFieldDefinitionKeyID = CD.CustomFieldDefinitionKeyID AND
					CV.DocumentNumber = P.PriceBookKeyID AND
					CD.CustomFieldLabel = 'Command Alkon Description'
				) AS CommandDescription,
				( SELECT
						PLO.FlatPrice * 1000
				FROM
					tblPriceLevels AS PL,
					tblPriceLevelOverride AS PLO
				WHERE
					PL.PriceLevelsKeyID = PLO.FkPriceLevels AND
					PLO.ItemId = P.ItemID AND
					PL.Description = '07 - Command Alkon'
				) AS CommandAlkonPrice,
				( SELECT
						PLO.FlatPrice * 1000
				FROM
					tblPriceLevels AS PL,
					tblPriceLevelOverride AS PLO
				WHERE
					PL.PriceLevelsKeyID = PLO.FkPriceLevels AND
					PLO.ItemId = P.ItemID AND
					PL.Description = '08 - Command Customer'
				) AS CommandCustomerPrice
			FROM
				tblPriceBook AS P,
				tblCustomFieldValues AS CV,
				tblCustomFieldDefinitions AS CD
			WHERE
				CV.CustomFieldDefinitionKeyID = CD.CustomFieldDefinitionKeyID AND
				CV.DocumentNumber = P.PriceBookKeyID AND
				CD.CustomFieldLabel = 'Command Alkon Price List' AND
				CV.CustomFieldValue = 'True' AND
				P.Inactive = 0
			ORDER BY
				CommandDescription
		""" )

	def prepPriceBookItemsHTML( self, rgsBody ):

		oRow = self._oCursor.fetchone()

		if not oRow: return rgsBody

		## Fields
		# ItemCategory
		# ItemSubCategory
		# ItemID
		# ItemDescription
		# CommandDescription
		# Unit
		# CommandAlkonPrice
		# CommandCustomerPrice

		rgsBody.append( '<h3>%s</h3>' % 'Price Book' )

		rgsBody.append( '<table>' )
		rgsBody.append( '<thead><tr><th>Item ID</th><th>Item</th><th>Command</th><th>Retail</th></tr></thead><tbody>' )

		while oRow:

			# pre-format
			sItem = oRow[ 'CommandDescription' ]
			if sItem is None:
				sItem = 'MISSING Description Custom Field'
			sItem = sItem[ 0:60 ]

			bCommand = 0.0
			if oRow[ 'CommandAlkonPrice' ] is not None:
				bCommand = float( oRow[ 'CommandAlkonPrice' ] )
			bCustomer = 0.0
			if oRow[ 'CommandCustomerPrice' ] is not None:
				bCustomer = float( oRow[ 'CommandCustomerPrice' ] )
			# Kind of backwards, but for some reason the Money column type for FlatPrice
			# is rounding whenever we query, so in my query I'm multiplying all prices by 1000
			if oRow[ 'Unit' ] is None or oRow[ 'Unit' ] != 'BY THE FOOT':
				bCommand = bCommand / 1000.0
				bCustomer = bCustomer / 1000.0

			rgsBody.append( '<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (
				oRow[ 'ItemID' ],
				sItem,
				'{:,.2f}'.format(bCommand),
				'{:,.2f}'.format(bCustomer)
			) )

			oRow = self._oCursor.fetchone()

		rgsBody.append( '</tbody></table>' )

		return rgsBody

	def prepPriceBookItemsPlain( self, rgsBody ):

		oRow = self._oCursor.fetchone()

		if not oRow: return rgsBody

		rgsBody.append( '\nPrice Book\n' )

		## Fields
		# ItemCategory
		# ItemSubCategory
		# ItemID
		# ItemDescription
		# CommandDescription
		# Unit
		# CommandAlkonPrice
		# CommandCustomerPrice

		rgsBody.append( '%-60s %9s %9s\n' % (
			'Item', 'Command', 'Retail' ) )

		while oRow:

			# pre-format
			sItem = oRow[ 'CommandDescription' ]
			if sItem is None:
				sItem = 'MISSING Description Custom Field'
			sItem = sItem[ 0:60 ]

			bCommand = 0.0
			if oRow[ 'CommandAlkonPrice' ] is not None:
				bCommand = float( oRow[ 'CommandAlkonPrice' ] )
			bCustomer = 0.0
			if oRow[ 'CommandCustomerPrice' ] is not None:
				bCustomer = float( oRow[ 'CommandCustomerPrice' ] )
			# Kind of backwards, but for some reason the Money column type for FlatPrice
			# is rounding whenever we query, so in my query I'm multiplying all prices by 1000
			if oRow[ 'Unit' ] is None or oRow[ 'Unit' ] != 'BY THE FOOT':
				bCommand = bCommand / 1000.0
				bCustomer = bCustomer / 1000.0

			rgsBody.append( '%-60s %9s %9s' % (
				sItem,
				'{:,.2f}'.format(bCommand),
				'{:,.2f}'.format(bCustomer)
			) )

			oRow = self._oCursor.fetchone()

		rgsBody.append( '\n' )

		rgsBody.append( '\n' )

		return rgsBody


	def run( self, fHTML=True ):

		sReport = 'Command Price Book'
		rgsBody = []

		if fHTML:
			rgsBody = self.prepHeaderHTML( rgsBody, sReport )

			# PriceBook
			self.getPriceBookItems()
			rgsBody = self.prepPriceBookItemsHTML( rgsBody )

			rgsBody = self.prepFooterHTML( rgsBody )

		else:
			rgsBody = self.prepHeaderPlain( rgsBody, sReport )

			# PriceBook
			self.getPriceBookItems()
			rgsBody = self.prepPriceBookItemsPlain( rgsBody )

			rgsBody = self.prepFooterPlain( rgsBody )

		self.finish()

		return( "\n".join( rgsBody ) )

def main( argv ):

	oApp = App()
	print oApp.run( False )

	return 0

if __name__ == '__main__':
	sys.exit( main( sys.argv ) )
