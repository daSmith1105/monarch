##
## pricelist.py
##

##
# Includes
#
# System
import time, threading, os, re
# Logging
from lib.messaging import dbgMsg, errMsg
# Cache (Object store)
import lib.cache


IMPORT_FILE = '/usr/share/monarch-backend/price-list.csv'


class CategoryEntry:
	"""
	Price List Category Object
	"""

	def __init__( self, bID=None, sName='' ):
		""" Setup Category Object """

		self._bID = bID
		self._sName = sName

	def getID( self ):
		""" Return ID associated with this category. """
		return self._bID

	def setID( self, bID ):
		""" Set new ID for category object. """
		self._bID = bID

	def getName( self ):
		""" Return Category Name. """
		return self._sName

	def setName( self, sName ):
		""" Set new Name for category. """
		self._sName = sName


class ItemEntry:
	"""
	Price List Item Object
	"""

	def __init__( self, bID=None, bCategory=None, sName='', sDescription='', bCost=0.0, bRetail=0.0, bDiscount=0.0 ):
		""" Setup Item Object """

		self._bID = bID
		self._bCategory = bCategory
		self._sName = sName
		self._sDescription = sDescription
		self._bCost = bCost
		self._bRetail = bRetail
		self._bDiscount = bDiscount

	def getID( self ):
		""" Return ID associated with this item. """
		return self._bID

	def setID( self, bID ):
		""" Set new ID for item object. """
		self._bID = bID

	def getCategory( self ):
		""" Return Category associated with this item. """
		return self._bCategory

	def setCategory( self, bCategory ):
		""" Set new Category for item object. """
		self._bCategory = bCategory

	def getName( self ):
		""" Return Item Name. """
		return self._sName

	def setName( self, sName ):
		""" Set new Name for item. """
		self._sName = sName

	def getDescription( self ):
		""" Return Item Description. """
		return self._sDescription

	def setDescription( self, sDescription ):
		""" Set new Description for item. """
		self._sDescription = sDescription

	def getCost( self ):
		""" Return Cost associated with this item. """
		return self._bCost

	def setCost( self, bCost ):
		""" Set new Cost for item object. """
		self._bCost = bCost

	def getRetail( self ):
		""" Return Retail associated with this item. """
		return self._bRetail

	def setRetail( self, bRetail ):
		""" Set new Retail for item object. """
		self._bRetail = bRetail

	def getDiscount( self ):
		""" Return Discount associated with this item. """
		return self._bDiscount

	def setDiscount( self, bDiscount ):
		""" Set new Discount for item object. """
		self._bDiscount = bDiscount


class PriceList:
	"""
	Price List module takes care of
	 - Update database with CSV file from Quickbooks
	 - Query categories
	 - Query items
	 - Update discounts
	"""

	def __init__( self ):
		""" Initialize PriceList module """

		libCache = lib.cache.Cache()
		self._libDB = libCache.get('libDB')
		self._oLock = threading.RLock()

		self._load()

	def _load( self ):
		""" Load QB pricelist CSV file into database. """

		try:
			self._oLock.acquire()

			try:
				# Do we have a new CSV file to import?
				if not os.access( IMPORT_FILE, os.F_OK ):
					return

				dbgMsg( 'loading price list from file [%s]' % IMPORT_FILE )
				rgoCategory, rgoItem = self._getObjectsFromFile()
				dbgMsg( 'found categories-[%d] items-[%s] in file' % ( len( rgoCategory ), len( rgoItem ) ) )

				self._addToDatabase( rgoCategory, rgoItem )
				self._removeFromDatabase( rgoCategory, rgoItem )

				# Backup import file
				if os.access( '%s.bak' % IMPORT_FILE, os.F_OK ):
					os.unlink( '%s.bak' % IMPORT_FILE )
				os.rename( IMPORT_FILE, '%s.bak' % IMPORT_FILE )

			except Exception, e:
				raise Exception, 'error loading price list into database [%s]' % e

		finally:
			self._oLock.release()

	def _findCategory( self, rgo, sName ):
		for o in rgo:
			if o.getName() == sName:
				return o
		return None

	def _findItem( self, rgo, bCategory, sName ):
		for o in rgo:
			if o.getCategory() == bCategory and o.getName() == sName:
				return o
		return None

	def _getObjectsFromFile( self ):
		""" Process CSV file and turn them into objects. """

		try:
			# Slurp the file Yummy!
			oFile = open( IMPORT_FILE, 'r' )
			rgsLine = oFile.readlines()
			oFile.close()

			# Convert CSV into objects
			rgoCategory = []
			rgoItem = []
			# Should be Blank, Item, Description, Vendor, Cost, Price
			oRegEx = re.compile( ',"(.*)","(.*)",.*,(\d+.\d+),(\d+.\d+)' )
			for sLine in rgsLine:
				oMatch = oRegEx.match( sLine )
				if oMatch is None: continue
				if oMatch.group( 1 ) == 'Item': continue

				s = oMatch.group( 1 )
				rgs = s.split( ':' )
				sCategory = rgs[ 1 ]
				sName = rgs[ 2 ]
				sDescription = oMatch.group( 2 )
				bCost = oMatch.group( 3 )
				bRetail = oMatch.group( 4 )

				oCategory = self._findCategory( rgoCategory, sCategory )
				if oCategory is None:
					bCategory = len( rgoCategory ) + 1001
					oCategory = CategoryEntry( bID=bCategory, sName=sCategory )
					rgoCategory.append( oCategory )

				bID = len( rgoItem ) + 1001
				oItem = ItemEntry(
					bID,
					bCategory,
					sName,
					sDescription,
					bCost,
					bRetail
				)
				rgoItem.append( oItem )

			return rgoCategory, rgoItem

		except Exception, e:
			raise Exception, 'error parsing CSV file [%s]' % e

	def _addToDatabase( self, rgoCategory, rgoItem ):
		""" Add new items found in CSV file. """

		try:
			# Add new categories first
			bCount = 0
			for oCategory in rgoCategory:
				bCategoryOld = oCategory.getID()
				oResult = self._libDB.query( 'SELECT bID FROM PLCategory WHERE sName=%s', oCategory.getName() )
				if len( oResult ) == 0:
					self._libDB.query( 'INSERT INTO PLCategory (sName) VALUES (%s)', oCategory.getName() )
					oResult = self._libDB.query( 'SELECT bID FROM PLCategory WHERE sName=%s', oCategory.getName() )
					bCount += 1
				bCategoryNew = oResult[ 0 ][ 0 ]
				oCategory.setID( bCategoryNew )
				self._updateItemCategory( rgoItem, bCategoryOld, bCategoryNew )
			dbgMsg( 'added [%d] new categories' % bCount )

			# Add new items now
			bCount = 0
			for oItem in rgoItem:
				oResult = self._libDB.query( 'SELECT bID FROM PLItem WHERE bCategory=%s AND sName=%s', oItem.getCategory(), oItem.getName() )
				if len( oResult ) == 0:
					self._libDB.query( 'INSERT INTO PLItem (bCategory,sName,sDescription,bCost,bRetail) VALUES (%s,%s,%s,%s,%s)',
						oItem.getCategory(),
						oItem.getName(),
						oItem.getDescription(),
						oItem.getCost(),
						oItem.getRetail()
					)
					oResult = self._libDB.query( 'SELECT bID FROM PLItem WHERE bCategory=%s AND sName=%s', oItem.getCategory(), oItem.getName() )
					oItem.setID( oResult[ 0 ][ 0 ] )
					bCount += 1

				else:
					self._libDB.query( 'UPDATE PLItem SET sDescription=%s, bCost=%s, bRetail=%s WHERE bCategory=%s AND sName=%s',
						oItem.getDescription(),
						oItem.getCost(),
						oItem.getRetail(),
						oItem.getCategory(),
						oItem.getName()
					)
			dbgMsg( 'added [%d] new items' % bCount )

		except Exception, e:
			raise Exception, 'error adding new items to database [%s]' % e

	def _removeFromDatabase( self, rgoCategory, rgoItem ):
		""" Remove old items not found in CSV file. """

		try:
			# Remove old Categories
			bCount = 0
			rgoResult = self._libDB.query( 'SELECT bID, sName FROM PLCategory' )
			for oResult in rgoResult:
				if self._findCategory( rgoCategory, oResult[ 1 ] ) is None:
					self._libDB.query( 'DELETE FROM PLCategory WHERE sName=%s', oResult[ 1 ] )
					self._libDB.query( 'DELETE FROM PLItem WHERE bCategory=%s', oResult[ 0 ] )
					bCount += 1
			dbgMsg( 'removed [%d] old categories' % bCount )

			# Remove old Items
			bCount = 0
			rgoResult = self._libDB.query( 'SELECT bCategory, sName FROM PLItem' )
			for oResult in rgoResult:
				if self._findItem( rgoItem, oResult[ 0 ], oResult[ 1 ] ) is None:
					self._libDB.query( 'DELETE FROM PLItem WHERE bCategory=%s AND sName=%s', oResult[ 0 ], oResult[ 1 ] )
					bCount += 1
			dbgMsg( 'removed [%d] old items' % bCount )

		except Exception, e:
			raise Exception, 'error removing old items from database [%s]' % e

	def _updateItemCategory( self, rgoItem, bIDOld, bIDNew ):
		""" Change all items with old category ID's to new. """

		for ix in range( 0, len( rgoItem ) ):
			if rgoItem[ ix ].getCategory() == bIDOld:
				rgoItem[ ix ].setCategory( bIDNew )

	def getCategories( self ):
		""" Return a list of all categories on our pricelist. """

		try:
			rgoCategory = []

			rgoResult = self._libDB.query( 'SELECT bID, sName FROM PLCategory ORDER BY sName' )
			for oResult in rgoResult:
				oCategory = CategoryEntry(
					oResult[ 0 ],
					oResult[ 1 ]
				)
				rgoCategory.append( oCategory )

			return rgoCategory

		except Exception, e:
			errMsg( 'error getting category list' )
			errMsg( e )
			return []

	def getItems( self ):
		""" Return a list of all items on our pricelist. """

		try:
			rgoItem = []

			rgoResult = self._libDB.query( 'SELECT i.bID, i.bCategory, i.sName, i.sDescription, i.bCost, i.bRetail, i.bDiscount FROM PLItem i, PLCategory c WHERE i.bCategory=c.bID ORDER BY c.sName, i.sName' )
			for oResult in rgoResult:
				oItem = ItemEntry(
					oResult[ 0 ],
					oResult[ 1 ],
					oResult[ 2 ],
					oResult[ 3 ],
					float( oResult[ 4 ] ),
					float( oResult[ 5 ] ),
					float( oResult[ 6 ] )
				)
				rgoItem.append( oItem )

			return rgoItem

		except Exception, e:
			errMsg( 'error getting item list' )
			errMsg( e )
			return []

	def getDiscount( self ):
		""" Get default discount percentage. """

		try:
			oResult = self._libDB.query( 'SELECT sValue FROM PLMisc WHERE sName=%s', 'discount' )
			return float( oResult[ 0 ][ 0 ] )

		except Exception, e:
			errMsg( 'error getting default discount' )
			errMsg( e )
			return 0.0

	def setDiscount( self, bDiscount ):
		""" Set default discount percentage. """

		try:
			bDiscount = float( bDiscount )
			self._libDB.query( 'UPDATE PLMisc SET sValue=%s WHERE sName=%s', bDiscount, 'discount' )
			dbgMsg( 'setting new default discount-[%.2f]' % bDiscount )
			return True

		except Exception, e:
			errMsg( 'error setting default discount [%s]' % bDiscount )
			errMsg( e )
			return False

	def setItemDiscount( self, bItem, bDiscount ):
		""" Set new distributor discount for item. """

		try:
			bDiscount = float( bDiscount )
			self._libDB.query( 'UPDATE PLItem SET bDiscount=%s WHERE bID=%s', bDiscount, bItem )
			dbgMsg( 'setting new discount-[%.2f] for item-[%d]' % ( bDiscount, bItem ) )
			return True

		except Exception, e:
			errMsg( 'error setting new item discount [%s]' % bDiscount )
			errMsg( e )
			return False
