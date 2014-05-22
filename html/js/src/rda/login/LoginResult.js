/**
 * LoginResult.js
 *
 * Object to hold our status, session, and name
 */

dojo.provide( "rda.login.LoginResult" );

dojo.declare(
	"rda.login.LoginResult",
	null,
	{
		_bStatus: 0,
		_sSess: "",
		_sName: "",

		constructor: function()
		{
			if ( arguments.length < 3 ) {
				this._bStatus = arguments[ 0 ];

			} else {
				this._bStatus = arguments[ 0 ];
				this._sSess = arguments[ 1 ];
				this._sName = arguments[ 2 ];

			}
		},

		getStatus: function()
		{
			return this._bStatus;
		},

		getSession: function()
		{
			return this._sSess;
		},

		getName: function()
		{
			return this._sName;
		}
	}
);
