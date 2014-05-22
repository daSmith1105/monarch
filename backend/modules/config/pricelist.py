##
## pricelist.py
##

##
# Includes
#
# System
import os, commands, threading
# Logging
from lib.messaging import stdMsg, dbgMsg, errMsg, setDebugging
# Cache
from lib.cache import Cache
# Price List Object
import db.pricelist


class PriceList:

	def __init__( self ):
		libCache = Cache()

		# Properties
		self._dbPriceList = libCache.get( 'dbPriceList' )

	def _freezeCategory( self, o ):
		""" Flatten category object to associative array. """

		try:
			rgs = {}
			rgs[ 'bID' ] = o.getID()
			if rgs[ 'bID' ] is None: rgs[ 'bID' ] = 0
			rgs[ 'sName' ] = o.getName()
			if rgs[ 'sName' ] is None: rgs[ 'sName' ] = ''

			return rgs

		except Exception, e:
			raise Exception, 'error freezing category [%s]' % e

	def _thawCategory( self, rgs ):
		""" Create category object from associative array. """

		try:
			o = db.pricelist.CategoryEntry()
			o.setID( rgs[ 'bID' ] )
			o.setName( rgs[ 'sName' ] )

			return o

		except Exception, e:
			raise Exception, 'error thawing category [%s]' % e

	def _freezeItem( self, o ):
		""" Flatten item object to associative array. """

		try:
			rgs = {}
			rgs[ 'bID' ] = o.getID()
			if rgs[ 'bID' ] is None: rgs[ 'bID' ] = 0
			rgs[ 'bCategory' ] = o.getCategory()
			if rgs[ 'bCategory' ] is None: rgs[ 'bCategory' ] = 0
			rgs[ 'sName' ] = o.getName()
			if rgs[ 'sName' ] is None: rgs[ 'sName' ] = ''
			rgs[ 'sDescription' ] = o.getDescription()
			if rgs[ 'sDescription' ] is None: rgs[ 'sDescription' ] = ''
			rgs[ 'bCost' ] = o.getCost()
			if rgs[ 'bCost' ] is None: rgs[ 'bCost' ] = 0
			rgs[ 'bRetail' ] = o.getRetail()
			if rgs[ 'bRetail' ] is None: rgs[ 'bRetail' ] = 0
			rgs[ 'bDiscount' ] = o.getDiscount()
			if rgs[ 'bDiscount' ] is None: rgs[ 'bDiscount' ] = 0

			return rgs

		except Exception, e:
			raise Exception, 'error freezing item [%s]' % e

	def _thawItem( self, rgs ):
		""" Create item object from associative array. """

		try:
			o = db.pricelist.ItemEntry()
			o.setID( rgs[ 'bID' ] )
			o.setCategory( rgs[ 'bCategory' ] )
			o.setName( rgs[ 'sName' ] )
			o.setDescription( rgs[ 'sDescription' ] )
			o.setCost( rgs[ 'bCost' ] )
			o.setRetail( rgs[ 'bRetail' ] )
			o.setDiscount( rgs[ 'bDiscount' ] )

			return o

		except Exception, e:
			raise Exception, 'error thawing item [%s]' % e

	def getCategories( self ):
		""" Get list of categories """

		try:
			rgoResult = []
			rgoCategory = self._dbPriceList.getCategories()
			for oCategory in rgoCategory:
				rgoResult.append( self._freezeCategory( oCategory ) )

			return rgoResult

		except Exception, e:
			errMsg('error getting category list [%s]' % e)
			raise Exception, 'error getting category list'

	def getItems( self ):
		""" Get list of items """

		try:
			rgoResult = []
			rgoItem = self._dbPriceList.getItems()
			for oItem in rgoItem:
				rgoResult.append( self._freezeItem( oItem ) )

			return rgoResult

		except Exception, e:
			errMsg('error getting item list [%s]' % e)
			raise Exception, 'error getting item list'

	def getDiscount( self ):
		""" Get default discount percentage. """

		return self._dbPriceList.getDiscount()

	def setDiscount( self, bDiscount ):
		""" Set default discount percentage. """

		return self._dbPriceList.setDiscount( bDiscount )

	def setItemDiscount( self, bItem, bDiscount ):
		""" Set discount price for a certain item manually. """

		return self._dbPriceList.setItemDiscount( bItem, bDiscount )
