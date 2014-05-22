#!/usr/bin/env python

##
# Includes
#
# General support, command call, etc
import sys, os, traceback, signal, commands, time
# Logging
from lib.messaging import stdMsg, dbgMsg, errMsg, setDebugging
# Threads
import thread_xmlrpc
import thread_process_control
import thread_bugzilla
import thread_check_sick


##
# Global config
#
PIDFILE = '/var/run/monarch-backend.pid'
# Flag to determine if all the modules are setup
# This prevents a race condition if someone tries to
# reload us before we are completely loaded
fReady = False
# cmdline options
optDaemon = True
optDebug = False
oXmlRpc = None

def usage():
	print
	print 'Usage: monarch-backend'
	print '\t--help         Display this help screen'
	print '\t--debug        Enable debugging options'
	print '\t--nodaemon     Run in foreground'
	print

def parseArgs(argv):
	global optDebug, optDaemon

	setDebugging(0)
	for arg in argv:
		if arg == '--help':
			usage()
			return 1
		if arg == '--debug':
			optDebug = True
			setDebugging(1)
		if arg == '--nodaemon':
			optDaemon = False

	return 0

def checkIsRunning():
	try:
		bPID = int(commands.getoutput('cat %s' % PIDFILE))
		try:
			os.kill(bPID, 0)
		except OSError:
			return False
		return True
	except:
		return False

def enterDaemonMode(sIn='/dev/null', sOut='/dev/null', sError='/dev/null'):
	# Do first fork.
	try: 
		bPid = os.fork() 
		if bPid > 0:
			# Exit first parent
			sys.exit(0)
	except OSError, (bError, sError): 
		errMsg('first fork failed: (%d) %s' % (bError, sError))
		return 1
        
	# Decouple from parent environment.
	os.chdir("/") 
	os.umask(0) 
	os.setsid() 
    
	# Do second fork.
	try: 
		bPid = os.fork() 
		if bPid > 0:
			# Exit second parent.
			sys.exit(0)
	except OSError, (bError, sError): 
		errMsg('second fork failed: (%d) %s' % (bError, sError))
		return 1
        
	# Redirect standard file descriptors.
	si = file(sIn, 'r')
	so = file(sOut, 'a+')
	se = file(sError, 'a+', 0)
	os.dup2(si.fileno(), sys.stdin.fileno())
	os.dup2(so.fileno(), sys.stdout.fileno())
	os.dup2(se.fileno(), sys.stderr.fileno())

	return 0

def savePID():
	# Save pidfile
	try:
		pid = os.getpid()
		if os.access(PIDFILE, os.F_OK):
			os.unlink(PIDFILE)
		f = open(PIDFILE, 'w')
		f.write('%d' % pid)
		f.close()
	except IOError:
		stdMsg('could not create pid file')

def removePID():
	if os.access(PIDFILE, os.F_OK):
		os.unlink(PIDFILE)

def hdlrSignal(signum, frame):
	global oXmlRpc, fReady

	if signum == signal.SIGINT or signum == signal.SIGTERM:
		raise KeyboardInterrupt
	elif signum == signal.SIGHUP:
		try:
			if not fReady: return
			oXmlRpc.reloadConfig()
		except Exception, e:
			errMsg('error reloading config [%s]' % e)

def main(argv):
	global oXmlRpc, fReady

	try:
		os.environ[ 'HOME' ] = '/root'

		if parseArgs(sys.argv) != 0:
			return 0

		signal.signal(signal.SIGINT, hdlrSignal)
		signal.signal(signal.SIGTERM, hdlrSignal)
		signal.signal(signal.SIGHUP, hdlrSignal)

		# Detect is running
		if checkIsRunning():
			stdMsg('Already running ... aborting')
			return 0

		# Create our server and start listening
		if optDaemon:
			# Run as a daemon in the background.
			if enterDaemonMode('/dev/null','/var/log/monarch-backend.log','/var/log/monarch-backend.log') != 0:
				errMsg('error with daemon mode')
				return 1
			stdMsg('starting daemon')
		else:
			stdMsg('starting')

		# Save our pid file
		savePID()

		# Initialize Threads
		rgoThread = {}
		rgoThread['ProcessControl'] = thread_process_control.ThreadProcessControl('ProcessControl')
		rgoThread['Bugzilla'] = thread_bugzilla.ThreadBugzilla('Bugzilla')
		rgoThread['CheckSick'] = thread_check_sick.ThreadCheckSick('CheckSick')
		oXmlRpc = thread_xmlrpc.ThreadXmlRpc('XmlRpc Server', rgoThread)

		oXmlRpc.start()
		rgoThread['ProcessControl'].start()
		rgoThread['Bugzilla'].start()
		rgoThread['CheckSick'].start()

		while True:
			time.sleep(35)
			fReady = True

		return 1

	except KeyboardInterrupt:
		stdMsg('terminating')
		# Stop all threads
		oXmlRpc.stop()
		rgoThread['ProcessControl'].stop()
		rgoThread['Bugzilla'].stop()
		rgoThread['CheckSick'].stop()
		bCount = 100
		while bCount > 0:
			if not oXmlRpc.checkIsRunning() and \
			   not rgoThread['ProcessControl'].checkIsRunning() and \
			   not rgoThread['Bugzilla'].checkIsRunning() and \
			   not rgoThread['CheckSick'].checkIsRunning():
				break
			bCount -= 1
			time.sleep(0.1)
		# Do any cleanup here
		removePID()
		stdMsg('stopped')
		return 0

	except SystemExit:
		return 0

	except Exception, e:
		if optDebug:
			print 'Exception in user code:'
			print '-'*60
			traceback.print_exc(file=sys.stdout)
			print '-'*60
		else:
			errMsg('caught exception: %s' % e)
			stdMsg('aborting')
		removePID()
		return 1

if __name__ == '__main__':
	os._exit(main(sys.argv))
