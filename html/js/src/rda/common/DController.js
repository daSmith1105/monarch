dojo.provide( "rda.common.DController" );

dojo.declare(
	"rda.common.DController",
	null,
	{
		rgoListener: null,

		constructor: function()
		{
			this.rgoListener = new Array();
		},

		addActionListener: function( oListener )
		{
			this.rgoListener.push( oListener );
		},

		activate: function(){},

		deactivate: function(){},

		throwAction: function( sCommand )
		{
			for ( var ix = this.rgoListener.length - 1; ix >= 0; ix-- )
				this.rgoListener[ ix ].actionPerformed( sCommand );
		}
	}
);
