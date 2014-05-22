#!/bin/bash -x

CDIR=$(pwd)
BASE=/var/www/dividia.net-sub/monarch
if [ ! -d ${BASE} ] ; then
	if [ -d /rda/devel/trunk/monarch ] ; then
		BASE=/var/www/html
	else
		echo "${BASE} not found!"
		exit 1
	fi
fi

# compile
rm -rf ${BASE}/js/src/dojoroot
tar -zxpSf ${BASE}/dls/dojo-release-1.3.0-src.tar.gz -C ${BASE}/js/src
mv ${BASE}/js/src/dojo-release-1.3.0-src ${BASE}/js/src/dojoroot
cd ${BASE}/js/src
./gen_includes.py
cd ${BASE}/js/src/dojoroot/util/buildscripts
./build.sh profileFile=../../../monarch.profile.js action=release cssOptimize=comments optimize=shrinkSafe
cd ${CDIR}

# dist
rm -rf ${BASE}/js/dojo
cp -a ${BASE}/js/src/dojoroot/release/dojo ${BASE}/js
cd ${BASE}/js/src
./clean_release.sh
./remove_emptydir.sh
cd ${CDIR}

exit 0
