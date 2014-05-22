##
## dvslog.py
##

##
# Includes
#
# General
import os, time
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
            # Initialize default return value
            rgoResult = [ bSerial, bEventID ]

            if sData == 'None': sData = None
            if bEventID == 'None': bEventID = None
                        
            try:
                bSerial = int( bSerial )
            except ValueError:
                return rgoResult
            try:
                if bEventID is not None:
                    bEventID = int( bEventID )
            except ValueError:
                return rgoResult
            
    
            # Verify the Serial is known
            oServer = self._dbServerList.getServer( bSerial=bSerial )
            if oServer is None:
                raise Exception, 'unknown serial [%s]' % bSerial
            
            
            # Update return information
            rgoResult[ 1 ] = bEventID
           
            sTimeStamp = time.time();
            
            self._dbDVSLogList.addDVSLogEntry(bSerial, bEventID, sData, sTimeStamp)

            #===================================================================
            # oDVSLogEntry.setSerial(bSerial)
            # oDVSLogEntry.setEventID(bEventID)
            # oDVSLogEntry.setData(sData)
            # oDVSLogEntry.setTimestamp( time.time() )
            # 
            # self._dbDVSLogEntryList.setDVSLogEntry( oDVSLogEntry )
            #===================================================================
            

            stdMsg( 'DVSLog Entry added for serial-[%3s] event-[%s]' % ( bSerial, bEventID ) )

            return rgoResult

        except Exception, e:
            errMsg('error updating DVSLog [%s]' % e)
            #raise Exception, "System error updating ip."
            return rgoResult

