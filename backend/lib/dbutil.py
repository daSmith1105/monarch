# dbutil.py

##
# Includes
#
# General
import threading
# Database
import MySQLdb
# Logging
from messaging import stdMsg, dbgMsg, errMsg


class DBUtil:
	def __init__(self, sHost, sUser, sPass, sDB):
		self._oLock = threading.Lock()

		self._sHost = sHost
		self._sUser = sUser
		self._sPass = sPass
		self._sDB = sDB

		self._oConnection = None
		self._oCursor = None

#	def __del__(self):
#		try:
#			if self._oCursor:
#				self._oCursor.close()
#				self._oCursor = None
#			if self._oConnection:
#				self._oConnection.close()
#				self._oConnection = None
#
#		except MySQLdb.Error, (bError, sError):
#			errMsg('error while delecting database object -- %s' % sError)
#			raise Exception, sError

	def query(self, sQuery, *rgsArgs):
		self._oLock.acquire()
		try:
			# parse query to determine type
			sType = 'select'
			if sQuery[0:6] == 'INSERT':
				sType = 'insert'
			elif sQuery[0:6] == 'DELETE':
				sType = 'delete'
			elif sQuery[0:6] == 'UPDATE':
				sType = 'update'

			try:
				if not self._oConnection:
					self._oConnection = MySQLdb.connect(host=self._sHost, user=self._sUser, passwd=self._sPass, db=self._sDB)
			except MySQLdb.Error, (bError, sError):
				errMsg('error while connecting to database -- %s' % sError)
				raise Exception, sError

			try:
				try:
					if not self._oCursor:
						self._oCursor = self._oConnection.cursor()
				except MySQLdb.Error, (bError, sError):
					errMsg('error while creating cursor for database -- %s' % sError)
					raise Exception, sError

				if len(rgsArgs) == 0:
					self._oCursor.execute(sQuery)
				else:
					self._oCursor.execute(sQuery, rgsArgs)

				rgoResult = self._oCursor.fetchall()
				if len(rgoResult) == 0:
					return ()

				self._oConnection.commit()
				return list(rgoResult)

			except MySQLdb.Error, (bError, sError):
				errMsg('error while querying database [%s]' % sError)
				if self._oCursor:
					self._oCursor.close()
					self._oCursor = None
				if self._oConnection:
					self._oConnection.close()
					self._oConnection = None
				raise Exception, 'error while querying database [%s]' % sError

			except Exception, e:
				errMsg('error while querying database [%s]' % e)
				if self._oCursor:
					self._oCursor.close()
					self._oCursor = None
				if self._oConnection:
					self._oConnection.close()
					self._oConnection = None
				raise Exception, 'error while querying database [%s]' % e

		finally:
			self._oLock.release()
