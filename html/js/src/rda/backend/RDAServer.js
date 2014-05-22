/**
 * RDAServer.js
 *
 * Wrapper around XMLRPC library to throw errors when rda-backend
 * has an exception.
 *
 * @author Ryan Ayers
 */

dojo.provide( "rda.backend.RDAServer" );

dojo.declare(
	"rda.backend.RDAServer",
	null,
	{
		_sRPCpath: "/MONARCH/",

		Query: function()
		{
			if ( arguments.length < 1 )
				throw new Error( "Must have a function to call" );
			sFunc = arguments[ 0 ];
			var rgoArg = new Array();
			for ( var ix = 1; ix < arguments.length; ix++ )
				rgoArg.push( arguments[ ix ] );

			var oResult = XMLRPC.call( this._sRPCpath, sFunc, rgoArg );
			if ( ! oResult[ 0 ] )
				throw new Error( oResult[ 1 ] );

			return oResult[ 1 ];
		},

		setServer: function( sUrl )
		{
			this._sRPCpath = sUrl + '/MONARCH/';
		}

	}
);
