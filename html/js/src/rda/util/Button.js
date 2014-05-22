dojo.provide( "rda.util.Button" );

dojo.require( "dijit._Widget" );
dojo.require( "dijit._Templated" );

dojo.declare(
	"rda.util.Button",
	[ dijit._Widget, dijit._Templated ],
	{
		buttonClass: "",
		label: "",
		width: 0,
		height: 0,

		// The fedds combo widget template
		templateString: "<input class=\"${buttonClass}\" type=\"button\" dojoAttachEvent=\"onclick:onClick\" value=\"${label}\" />",

		postCreate: function()
		{
			if ( this.width > 0 )
				this.domNode.style.width = this.width + "px";

			if ( this.height > 0 )
				this.domNode.style.height = this.height + "px";
		},

		// Callback on change 
		onClick: function( e )
		{
		},

		doClick: function()
		{
			this.onClick( { target: this.domNode } );
		},
	
		getLabel: function()
		{
			return this.domNode.value;
		},
		
		setLabel:function( value )
		{
			this.domNode.value = value;
		}
	}
);
