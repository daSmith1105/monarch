##
## user.py
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
import lib.dispatcher
# User Object
import db.user


class User:

	def __init__(self):
		libCache = Cache()

		# Properties
		self._dbUserList = libCache.get('dbUserList')
		self._dbAccessList = libCache.get('dbAccessList')

	def _freezeUser(self, oUser):
		""" Flatten user object to associative array. """

		try:
			rgsUser = {}
			rgsUser['bID'] = oUser.getID()
			rgsUser['sName'] = oUser.getName()
			rgsUser['sDescription'] = oUser.getDescription()
			rgsUser['sPassword'] = '__notset__'
			rgsUser['bType'] = oUser.getType()

			return rgsUser

		except Exception, e:
			raise Exception, 'error freezing user [%s]' % e

	def _thawUser(self, rgsUser):
		""" Create user object from associative array. """

		try:
			oUser = db.user.UserEntry()
			oUser.setID(rgsUser['bID'])
			oUser.setName(rgsUser['sName'])
			oUser.setDescription(rgsUser['sDescription'])
			if rgsUser['sPassword'] != '__notset__':
				# Password change
				oUser.setPassword(rgsUser['sPassword'])
			oUser.setType(rgsUser['bType'])

			return oUser

		except Exception, e:
			raise Exception, 'error thawing user [%s]' % e

	def _isSuper( self, bID ):
		""" Check if this is a superuser. """

		for oUser in self._dbUserList.getList():
			if oUser.getID() == bID and oUser.getType() == 0:
				return True
		return False

	def addUser(self, sName, sPassword, sDescription):
		""" Add new user to system. """

		oUser = self._dbUserList.addUser(sName, sPassword, sDescription, 20)
		if oUser is None:
			return {}
		return self._freezeUser(oUser)

	def delUser(self, bUserID):
		""" Delete user from system. """

		oUser = self._dbUserList.getUser(bID=bUserID)
		if oUser is None:
			return False

		# Delete all ACL entries
		for oAccessEntry in self._dbAccessList.getList():
			if oAccessEntry.getUser() == oUser.getID():
				self._dbAccessList.delEntry(oAccessEntry)

		return self._dbUserList.delUser(oUser)

	def getAllUsers(self):
		""" Get all registered users """

		try:
			rgoResult = []
			rgoUser = self._dbUserList.getList()
			for oUser in rgoUser:
				if oUser.getName() == 'dividia': continue
				rgoResult.append(self._freezeUser(oUser))

			return rgoResult

		except Exception, e:
			errMsg('error getting user list [%s]' % e)
			raise Exception, 'error getting user list'

	def getUserByID(self, bID):
		""" Get user object by ID """

		try:
			oUser = self._dbUserList.getUser(bID=bID)
			if oUser is None:
				return {}
			return self._freezeUser(oUser)

		except Exception, e:
			errMsg('error getting user by ID [%s]' % e)
			raise Exception, 'error getting user by ID'

	def getUserByName(self, sName):
		""" Set user object by Name """

		try:
			oUser = self._dbUserList.getUser(sName=sName)
			if oUser is None:
				return {}
			return self._freezeUser(oUser)

		except Exception, e:
			errMsg('error getting user by Name [%s]' % e)
			raise Exception, 'error getting user by Name'

	def setUser(self, rgsUser):
		""" Set user from hash """

		try:
			oUser = self._thawUser(rgsUser)
			self._dbUserList.setUser(oUser)
			return True

		except Exception, e:
			errMsg('error setting user [%s]' % e)
			raise Exception, 'error setting user'

	def getRights(self, bUserID):
		""" Get rights for user and server. """

		if self._isSuper( bUserID ):
			return [ 1, 2, 4, 8, 16, 32, 64, 128, 256 ]

		oAccessEntry = self._dbAccessList.getEntry(bUserID)
		if oAccessEntry is None:
			return []

		return oAccessEntry.getRights()

	def setRights(self, bUserID, rgbRight):
		""" Set rights for user and server. """

		if self._isSuper( bUserID ):
			return True

		oAccessEntry = self._dbAccessList.getEntry(bUserID)
		if oAccessEntry is None:
			# No entry for this user/server, create a new one
			oAccessEntry = self._dbAccessList.addEntry(bUserID, rgbRight)
		else:
			oAccessEntry.setRights(rgbRight)
			self._dbAccessList.setEntry(oAccessEntry)

		return True
