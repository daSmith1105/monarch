/**
 * LoginStatus.js
 *
 * Status enumeration
 */

if ( ! dojo._hasResource[ "rda.login.LoginStatus" ] ) {
	dojo._hasResource[ "rda.login.LoginStatus" ] = true;
	dojo.provide( "rda.login.LoginStatus" );

	dojo.declare(
		"rda.login.LoginStatus",
		null,
		{
		}
	);

	rda.login.LoginStatus.SUCCESS = 0;
	rda.login.LoginStatus.NOAUTH  = 1;
	rda.login.LoginStatus.EXISTS  = 2;
	rda.login.LoginStatus.ERROR   = 3;
}
