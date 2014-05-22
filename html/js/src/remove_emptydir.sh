#!/bin/bash

BASE=
DEBUG=0

showUsage() {
	echo "Usage: `basename $0` [-d] /path/to/directory"
}

parseArgs() {
	if [ -z "$1" ]
	then
		showUsage $@
		exit 0
	elif [ "$1" = "-d" ]
	then
		DEBUG=1
		if [ -z "$2" ]
		then
			showUsage $@
			exit 0
		elif [ ! -d "$2" ]
		then
			showUsage $@
			exit 0
		else
			BASE=$2
		fi
	elif [ ! -d "$1" ]
	then
		showUsage $@
		exit 0
	else
		BASE=$1
	fi
}

walkDir() {
	local sDir=$1
	[ ${DEBUG} -eq 1 ] && echo "walking ${sDir}"
	local bCount=0

	for sFileFull in "${sDir}"/*
	do
		sFile=$(basename "${sFileFull}")
		if [ "${sFile}" = "." ] || [ "${sFile}" = ".." ] || [ "${sFile}" = "*" ]
		then
			continue
		fi

		bCount=$((bCount+1))

		if [ -d "${sFileFull}" ]
		then
			walkDir "${sFileFull}"
			if [ $? -eq 1 ]
			then
				bCount=$((bCount-1))
			fi
		fi
	done

	if [ "${sDir}" != "${BASE}" ]
	then
		if [ ${bCount} -eq 0 ]
		then
			[ ${DEBUG} -eq 1 ] && echo "rmdir ${sDir}"
			rmdir "${sDir}"
			return 1
		else
			return 0
		fi
	fi
}

main() {
	parseArgs $@

	walkDir "${BASE}"

	exit 0
}

#main $@
main ../dojo/rda
