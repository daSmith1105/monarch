dojo.provide( "rda.common.Observable" );

dojo.declare(
	"rda.common.Observable",
	null,
	{
		rgoObserver: null,
		fChanged: false,

		constructor: function()
		{
			this.rgoObserver = new Array();
		},

		addObserver: function( oObserver )
		{
			if ( ! oObserver.update )
				throw new Error( "Observer must implement update function" );
			this.rgoObserver.push( oObserver );
		},

		hasChanged: function()
		{
			return this.fChanged;
		},

		setChanged: function()
		{
			this.fChanged = true;
		},

		clearChanged: function()
		{
			this.fChanged = false;
		},

		notifyObservers: function()
		{
			if ( ! this.hasChanged() ) return;
			for ( var ix = this.rgoObserver.length - 1; ix >= 0; ix-- )
				this.rgoObserver[ ix ].update( this );
			this.clearChanged();
		},

		countObservers: function()
		{
			return this.rgoObserver.length;
		}
	}
);
