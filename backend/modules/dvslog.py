##
## dvslog.py
##

##
# Includes
#
# General
import os, time, re
# Logging
from lib.messaging import stdMsg, dbgMsg, errMsg
# Internal
import lib.cache


class DVSLog:
    
	def __init__( self ):
		""" Initialize DVSLog Module """

		libCache = lib.cache.Cache()
		self._dbDVSLogList = libCache.get( 'dbDVSLogList' )
		self._dbServerList = libCache.get( 'dbServerList' )

	def updateDVSLog(self, bSerial=None, bEventID=None, sData=None):
		""" Update the Log """
		try:
			if sData == 'None': sData = None
			if bEventID == 'None': bEventID = None
				
			try:
				bSerial = int( bSerial )
			except ValueError:
				raise Exception( 'bad serial' )
			try:
				if bEventID is not None:
				bEventID = int( bEventID )
			except ValueError:
				raise Exception( 'bad event id' )


			# See if we should skip anything for this serial
			oMatchTest = re.compile( '.*test.*' )           # Regex to skip any "test" systems
			oServer = self._dbServerList.getServer( bSerial=bSerial )
			if oServer is None:
				return False # server does not exist?
			if oServer.checkHasSkip():
				return False
			if oMatchTest.match( oServer.getCategories() ):
				return False
			if oServer.getMaintenance() == 'no':
				return False

			sTimeStamp = time.time();

			self._dbDVSLogList.addDVSLogEntry(bSerial, bEventID, sData, sTimeStamp)

			#===================================================================
			# oDVSLogEntry.setSerial(bSerial)
			# oDVSLogEntry.setEventID(bEventID)
			# oDVSLogEntry.setData(sData)
			# oDVSLogEntry.setTimestamp( time.time() )
			# 
			# self._dbDVSLogList.setDVSLogEntry( oDVSLogEntry )
			#===================================================================

			stdMsg( 'DVSLog Entry added for serial-[%3s] event-[%s]' % ( bSerial, bEventID ) )

			return True

		except Exception, e:
			errMsg('error updating DVSLog [%s]' % e)
			return False
