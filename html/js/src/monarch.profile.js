dependencies = {
	stripConsole: "normal",

	layers: [
		{
			name: "../rda/includes.js",
			dependencies: [
				"rda.includes"
			]
		},
		{
			name: "../rda/includes_i.js",
			dependencies: [
				"rda.includes_i"
			]
		}
	],

	prefixes: [
		[ "dijit", "../dijit" ],
		[ "dojox", "../dojox" ],
		[ "rda", "../../rda" ]
	]
}
