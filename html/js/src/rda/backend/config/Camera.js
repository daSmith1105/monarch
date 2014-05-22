/**
 *
 * Camera Object holds the properties for each registered DVS.
 *
 * @author Ryan Ayers
 */

dojo.provide( "rda.backend.config.Camera" );

dojo.declare(
	"rda.backend.config.Camera",
	null,
	{
		_bSerial: 0,
		_bCamera: 0,
		_bTimestamp: 0,
		_fSkip: false,

		/**
		 * Creates a new instance of our Camera Object
		 */
		constructor: function()
		{
			if ( arguments.length > 0 )
				this.load( arguments[ 0 ] );
		},

		/**
		 * Load Hash from camera into our structure
		 */
		load: function( rgsCamera )
		{
			for ( var sKey in rgsCamera ) {
				if ( sKey == "bSerial" )
					this._bSerial = parseInt( rgsCamera[ sKey ] );
				else if ( sKey == "sServer" )
					this._sServer = String( rgsCamera[ sKey ] );
				else if ( sKey == "bCamera" )
					this._bCamera = parseInt( rgsCamera[ sKey ] );
				else if ( sKey == "bTimestamp" )
					this._bTimestamp = parseInt( rgsCamera[ sKey ] );
				else if ( sKey == "fSkip" )
					this._fSkip = new Boolean( rgsCamera[ sKey ] );
			}
		},

		/**
		 * Return a Hash of our object ready to send back to camera
		 */
		freeze: function()
		{
			var rgs = new Object();

			rgs[ "bSerial" ] = this._bSerial;
			rgs[ "sServer" ] = this._sServer;
			rgs[ "bCamera" ] = this._bCamera;
			rgs[ "bTimestamp" ] = this._bTimestamp;
			rgs[ "fSkip" ] = this._fSkip;

			return rgs;
		},

		getSerial: function()
		{
			return this._bSerial;
		},
		setSerial: function( bSerial )
		{
			this._bSerial = bSerial;
		},

		getServer: function()
		{
			return this._sServer;
		},
		setServer: function( sServer )
		{
			this._sServer = sServer;
		},

		getCamera: function()
		{
			return this._bCamera;
		},
		setCamera: function( bCamera )
		{
			this._bCamera = bCamera;
		},

		getTimestamp: function()
		{
			return this._bTimestamp;
		},
		setTimestamp: function( bTimestamp )
		{
			this._bTimestamp = bTimestamp;
		},
		getTimestampPretty: function()
		{
			return this._toPretty( this._bTimestamp, true );
		},
		setTimestampPretty: function( sTimestamp )
		{
			this._bTimestamp = this._fromPretty( sTimestamp, true );
		},

		checkHasSkip: function()
		{
			return ( this._fSkip == true ) ? true : false;
		},
		setSkip: function( fSkip )
		{
			this._fSkip = fSkip;
		},

		_toPretty: function( bTimestamp, fTime )
		{
			var o = new Date( bTimestamp * 1000 );
			var bYear = o.getFullYear();
			var bMonth = o.getMonth() + 1;
			var bDay = o.getDate();
			var bHour = o.getHours();
			var bMinute = o.getMinutes();
			var bSecond = o.getSeconds();

			if ( bMonth < 10 ) bMonth = '0' + bMonth;
			if ( bDay < 10 ) bDay = '0' + bDay;
			if ( bHour < 10 ) bHour = '0' + bHour;
			if ( bMinute < 10 ) bMinute = '0' + bMinute;
			if ( bSecond < 10 ) bSecond = '0' + bSecond;

			if ( fTime )
				return bYear + '-' + bMonth + '-' + bDay + ' ' + bHour + ':' + bMinute + ':' + bSecond;
			else
				return bYear + '-' + bMonth + '-' + bDay;
		},

		_fromPretty: function( sTimestamp, fTime )
		{
			var o = new Date();

			o.setFullYear( sTimestamp.substr( 0, 4 ) )
			o.setMonth( sTimestamp.substr( 5, 2 ) - 1 );
			o.setDate( sTimestamp.substr( 8, 2 ) );
			o.setHours( 0 );
			o.setMinutes( 0 );
			o.setSeconds( 0 );

			if ( fTime ) {
				o.setHours( sTimestamp.substr( 11, 2 ) );
				o.setMinutes( sTimestamp.substr( 14, 2 ) );
				o.setSeconds( sTimestamp.substr( 17, 2 ) );
			}

			return parseInt( o.getTime() / 1000 );
		}

	}
);
