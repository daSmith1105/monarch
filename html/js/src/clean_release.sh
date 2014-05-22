#!/bin/bash

find ../dojo/rda -name '*.js' | \
	grep -v "includes.js$" | \
	grep -v "includes_i.js$" | \
	grep -v "nls" | \
	grep -v "vcXMLRPC.js" | \
		xargs -n 1 rm -f

exit 0
