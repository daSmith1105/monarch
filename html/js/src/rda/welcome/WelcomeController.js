dojo.provide( "rda.welcome.WelcomeController" );

dojo.require( "rda.common.DController" );

dojo.declare(
	"rda.welcome.WelcomeController",
	[ rda.common.DController, rda.common.Observer ],
	{
		// Properties
		oView: null,

		constructor: function( oAuthHelper, oAuthModel, oView )
		{
			this.oView = oView;

			this.oView.addActionListener( this );
		},

		activate: function()
		{
		},

		deactivate: function()
		{
		},

		actionPerformed: function( sCommand )
		{
			console.debug( "WelcomeController received action [" + sCommand + "]" );

			this.throwAction( sCommand );
		}

	}
);
