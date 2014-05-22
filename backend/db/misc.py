##
## db_misc.py
##

##
# Includes
#
# System
import threading
from lib.messaging import stdMsg, dbgMsg, errMsg
# Cache
import lib.cache


class Misc:
	""" Misc object used to store application wide settings """

	def __init__( self ):
		# Get Database handle
		libCache = lib.cache.Cache()
		self._libDB = libCache.get( 'libDB' )

	def get( self, sModule, sName ):
		""" Return one of our properties. """

		oValue = None
		rgoResult = self._libDB.query( 'SELECT sValue FROM Misc WHERE sModule=%s AND sName=%s', sModule, sName )
		if len( rgoResult ) == 0:
			raise Exception, 'unknown property [%s:%s]' % ( sModule, sName )
		oValue = rgoResult[ 0 ][ 0 ]

		if ( sModule == 'placeholder' and sName == 'placeholder' ):
			try:
				oValue = int( oValue )
			except ValueError:
				raise Exception, '%s:%s value is invalid [%s]' % ( sModule, sName, oValue )

		elif ( sModule == 'placeholder' and sName == 'placeholder' ):
			if oValue == 'on':
				oValue = True
			elif oValue == 'off':
				oValue = False
			else:
				raise Exception, '%s:%s value is invalid [%s]' % ( sModule, sName, oValue )

		return oValue

	def set( self, sModule, sName, oValue ):
		""" Update one of our properties. """

		if ( sModule == 'placeholder' and sName == 'placeholder' ):
			self._libDB.query( 'UPDATE Misc SET sValue=%s WHERE sModule=%s AND sName=%s', str( oValue ), sModule, sName )

		elif ( sModule == 'placeholder' and sName == 'placeholder' ):
			if oValue == True:
				sValue = 'on'
			elif oValue == False:
				sValue = 'off'
			else:
				raise Exception, '%s:%s is not valid [%s]' % ( sModule, sName, oValue )
			self._libDB.query( 'UPDATE Misc SET sValue=%s WHERE sModule=%s AND sName=%s', sValue, sModule, sName )

		self._libDB.query( 'UPDATE Misc SET sValue=%s WHERE sModule=%s AND sName=%s', oValue, sModule, sName )
