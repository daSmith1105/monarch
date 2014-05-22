#!/usr/bin/python

import os, sys, re


def getFilename( sModule ):
	""" Convert module name into actual file name path. """

	try:
		rgs = sModule.split( "." )
		sPath = "/".join( rgs )
		return sPath + ".js"

	except:
		raise Exception, "cannot convert module name [%s] into filename" % sModule


def getModule( sRequire ):
	""" Parse dojo.require line and return simple module name. """

	m = re.match( "^dojo.require\( \"(.*)\" \);", sRequire )
	if m:
		return m.group( 1 )
	raise Exception, "require line not in proper format [%s]" % sRequire


def getRequire( sModule ):
	""" Convert module name into dojo.require line. """

	return "dojo.require( \"%s\" );" % sModule


def findDeps( sModule, oFileOut ):
	""" Recursively print out a list of all requires listed in sFile. """

	oFileOut.write( getRequire( sModule ) + "\n" )

	# Only traverse rda modules
	if sModule[ 0:3 ] != "rda": return

	rgsModule = []
	oFile = open( getFilename( sModule ), "r" )
	for sLine in oFile.readlines():
		if sLine[ 0:12 ] != "dojo.require": continue
		rgsModule.append( getModule( sLine ) )
	oFile.close()

	for sModule in rgsModule:
		findDeps( sModule, oFileOut )


def main( argv ):
	""" Generate includes.js and includes_i.js files for DView Lite build. """

	try:
		# Generate Standard codebase first
		oFileOut = open( "/tmp/includes.js", "w" )
		findDeps( "rda.Monarch", oFileOut )
		oFileOut.close()
		oFileOut = open( "rda/includes.js", "w" )
		oFileOut.write( "dojo.provide( \"includes.js\" );\n" )
		oFileOut.close()
		os.system( "cat /tmp/includes.js | sort | uniq >> rda/includes.js" )
		os.unlink( "/tmp/includes.js" )

		# Generate iPhone codebase
		oFileOut = open( "/tmp/includes_i.js", "w" )
		findDeps( "rda.iMonarch", oFileOut )
		oFileOut.close()
		oFileOut = open( "rda/includes_i.js", "w" )
		oFileOut.write( "dojo.provide( \"includes_i.js\" );\n" )
		oFileOut.close()
		os.system( "cat /tmp/includes_i.js | sort | uniq >> rda/includes_i.js" )
		os.unlink( "/tmp/includes_i.js" )

		return 0

	except Exception, e:
		print "Error:", e
		return 1


if __name__ == "__main__":
	sys.exit( main( sys.argv ) )
