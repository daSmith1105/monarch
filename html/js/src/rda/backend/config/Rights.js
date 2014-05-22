/**
 * Store Right information for a Rights/Server.
 *
 * @author Ryan Ayers
 */

dojo.provide( "rda.backend.config.Rights" );

dojo.declare(
	"rda.backend.config.Rights",
	null,
	{
		_bID: 0,
		_rgbRight: null,

		constructor: function()
		{
			if ( arguments.length > 1 )
				this.load( arguments[ 0 ] );
		},

		/**
		 * Load rights information
		 *
		 * @param rgbRight
		 *  List of User Rights
		 */
		load: function( rgbRight )
		{
			try {
				// Rights
				if ( rgbRight != null ) {
					this._rgbRight = new Array( rgbRight.length );
					for ( var ix = 0; ix < rgbRight.length; ix++ )
						this._rgbRight[ ix ] = parseInt( rgbRight[ ix ] );
				}

			} catch ( e ) {
				console.debug( "Rights Model Load [" + e + "]" );
				alert( "Error querying rghts list" );
			}
		},

		/**
		 * Determine if our user has this right
		 *
		 * @param bRight
		 *  Value of right to check for
		 *
		 * @return True/False if we have this right or not
		 */
		checkHasRight: function( bRight )
		{
			for ( var ix = 0; ix < this._rgbRight.length; ix++ )
				if ( this._rgbRight[ ix ] == bRight )
					return true;
			return false;
		}

	}
);
