dojo.provide( "rda.util.TextBox" );

dojo.require( "dijit._Widget" );
dojo.require( "dijit._Templated" );

dojo.declare(
	"rda.util.TextBox",
	[ dijit._Widget, dijit._Templated ],
	{
		boxClass: "",
		value: "",

		// The fedds combo widget template
		templateString: "<input class=\"${boxClass}\" type=\"text\" value=\"${value}\" />",

		getValue: function()
		{
			return this.domNode.value;
		},
		
		setValue:function( value )
		{
			this.domNode.value = value;
		}
	}
);
