##
## tigerpaw.py
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


class TPReportEntry:
	"""
	TigerPaw Report Object
	"""

	def __init__( self, bID=None, sName='', sPath='' ):
		""" Setup Report Object """

		self._bID = bID
		self._sName = sName
		self._sPath = sPath

	def getID( self ):
		""" Return ID associated with this report. """
		return self._bID

	def setID( self, bID ):
		""" Set new ID for report object. """
		self._bID = bID

	def getName( self ):
		""" Return Report Name. """
		return self._sName

	def setName( self, sName ):
		""" Set new Name for report. """
		self._sName = sName

	def getPath( self ):
		""" Return Report file path. """
		return self._sPath

	def setPath( self, sPath ):
		""" Set new file Path for report. """
		self._sPath = sPath


class Tigerpaw:

	def __init__( self ):
		libCache = Cache()

		# Reports
		self._rgoReport = []
		self._rgoReport.append( TPReportEntry( 1, 'Inventory by Location', 'inventory_by_location' ) )
		self._rgoReport.append( TPReportEntry( 2, 'Inventory by Vendor', 'inventory_by_vendor' ) )
		self._rgoReport.append( TPReportEntry( 3, 'Sales Commission', 'commission_sales' ) )
		self._rgoReport.append( TPReportEntry( 4, 'Tech Commission', 'commission_tech' ) )
		self._rgoReport.append( TPReportEntry( 5, 'Employee Time Off', 'employee_time_off' ) )

	###
	# Handle getting Report lists
	###
	def _freezeTPReport( self, o ):
		""" Flatten tpreport object to associative array. """

		try:
			rgs = {}
			rgs[ 'bID' ] = o.getID()
			if rgs[ 'bID' ] is None: rgs[ 'bID' ] = 0
			rgs[ 'sName' ] = o.getName()
			if rgs[ 'sName' ] is None: rgs[ 'sName' ] = ''

			return rgs

		except Exception, e:
			raise Exception, 'error freezing tpreport [%s]' % e

	def _thawTPReport( self, rgs ):
		""" Create tpreport object from associative array. """

		try:
			o = TPReportEntry()
			o.setID( rgs[ 'bID' ] )
			o.setName( rgs[ 'sName' ] )

			return o

		except Exception, e:
			raise Exception, 'error thawing tpreport [%s]' % e

	def _getReport( self, bReport ):
		""" Get report by ID """

		try:
			for oReport in self._rgoReport:
				if oReport.getID() == bReport:
					return oReport

			return None

		except Exception, e:
			errMsg('error getting tigerpaw report by id [%s]' % e)
			raise Exception, 'error getting tigerpaw report by id'

	def getReports( self ):
		""" Get list of reports """

		try:
			rgoResult = []
			for oReport in self._rgoReport:
				rgoResult.append( self._freezeTPReport( oReport ) )

			return rgoResult

		except Exception, e:
			errMsg('error getting tpreport list [%s]' % e)
			raise Exception, 'error getting tpreport list'

	###
	# Run Report
	###
	def runReport( self, bReport, sDateFrom='2016-01-01', sDateTo='2016-01-01' ):
		""" Run report and return HTML result page """

		try:
			oReport = self._getReport( bReport )
			if oReport is None:
				return 'Could not find report'

			if oReport.getPath() == 'inventory_by_location':
				import modules.tpreports.inventory_by_location
				oApp = modules.tpreports.inventory_by_location.App()
				return oApp.run()

			elif oReport.getPath() == 'inventory_by_vendor':
				import modules.tpreports.inventory_by_vendor
				oApp = modules.tpreports.inventory_by_vendor.App()
				return oApp.run()

			elif oReport.getPath() == 'commission_sales':
				import modules.tpreports.commission_sales
				oApp = modules.tpreports.commission_sales.App()
				return oApp.run( sDateFrom, sDateTo )

			elif oReport.getPath() == 'commission_tech':
				import modules.tpreports.commission_tech
				oApp = modules.tpreports.commission_tech.App()
				return oApp.run( sDateFrom, sDateTo )

			elif oReport.getPath() == 'employee_time_off':
				import modules.tpreports.employee_time_off
				oApp = modules.tpreports.employee_time_off.App()
				return oApp.run( sDateFrom, sDateTo )

			return 'Could not run report [%s]' % oReport.getName()

		except Exception, e:
			errMsg('error running tigerpaw report [%s]' % e)
			raise Exception, 'error running tigerpaw report'
