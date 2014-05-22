##
## rights.py
##

##
# Includes
#
# General
import threading, copy
# Cache (Object store)
import lib.cache

class RightEntry:

	def __init__( self, bValue=0, sName="", sDescription="" ):
		self._bValue = bValue
		self._sName = sName
		self._sDescription = sDescription

	def setValue( self, bValue ):
		self._bValue = bValue

	def getValue( self ):
		return self._bValue

	def setName( self, sName ):
		self._sName = sName

	def getName( self ):
		return self._sName

	def setDescription( self, sDescription ):
		self._sDescription = sDescription

	def getDescription( self ):
		return self._sDescription


class RightList:

	def __init__( self ):
		libCache = lib.cache.Cache()
		self._libDB = libCache.get( 'libDB' )
		self._oLock = threading.RLock()

	def size( self ):
		""" Return the number of rights we have loaded. """

		return len( self.getList() )

	def getList( self ):
		""" Return a list copy of Rights. """

		try:
			self._oLock.acquire()

			try:
				rgoRight = []

				rgoResult = self._libDB.query( 'SELECT bID, sName, sDescription FROM Rights ORDER BY bID' )

				for oRow in rgoResult:
					bValue       = oRow[0]
					sName        = oRow[1]
					sDescription = oRow[2]

					rgoRight.append(
						RightEntry(
							bValue,
							sName,
							sDescription
						)
					)

				return copy.copy( rgoRight )

			except Exception, e:
				raise Exception, 'error loading rights from database [%s]' % e

		finally:
			self._oLock.release()

	def getValue( self ):
		""" Return a total of all our values. """

		bValue = 0
		for oRight in self.getList():
			bValue |= oRight.getValue()

		return bValue

	def getValueByName( self, sName ):
		""" Return Right value by name. """

		for oRight in self.getList():
			if oRight.getName() == sName:
				return oRight.getValue()

		raise Exception( 'Right [%s] does not exist' % sName )

	def getNameByValue( self, bValue ):
		""" Return Right name by value. """

		for oRight in self.getList():
			if oRight.getValue() == bValue:
				return oRight.getName()

		raise Exception( 'Right [%d] does not exist' % bValue )

	def getRightByValue( self, bValue ):
		""" Return Right by value. """

		for oRight in self.getList():
			if oRight.getValue() == bValue:
				return oRight

		raise Exception( 'Right [%d] does not exist' % bValue )
