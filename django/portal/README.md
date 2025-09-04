# RocketChat integration

## OAuth with Cohiva as IdP

### Add application in Cohiva

 - https://demo.cohiva.ch/o/applications
   -> RocketChat, Confidential, Auth. code, Redirect uris: https://chat.demo.cohiva.ch/_oauth/cohivademo (von RocketChat Admin)

 - RocketChat Admin:
   - URL: https://demo.warmbaechli.ch
   - Pfad des Token: /o/token/       (add trailing slash!)
   - Token gesendet über: Nutzdaten                [default]
   - ID Token gesendet über: Wie "Token Sent Via"  [default]
   - Identitätspfad: /portal/me/
   - Autorisierungspfad: /o/authorize/
   - Bereich: username email realname
   - Param Name für Access token: access_token     [default]
   - ID: Client-ID von Cohiva config oben
   - Geheimer Schlüssel: Client-Secret von Cohiva config oben
   - Anmeldungsart: Redirect
   - Text Button: Mit Musterweg-Konto anmelden
   - Schlüsselfeld: E-Mail
   - Feld für Benutzername: username
   - E-Mail-Feld: email
   - Namensfeld: name


Re-enable login from:
===========================
curl http://localhost:3000/api/v1/login  -d "username=USERNAME&password=PASSWORD"
// get you user-id and auth-token

curl -H "X-Auth-Token: LOGIN-TOKEN"  -H "X-User-Id: SOME-ID" -H "Content-type:application/json"  http://localhost:3000/api/v1/settings/Accounts_ShowFormLogin  -d '{ "value": true }'
===========================


=====================
BookStack SAML2 auth:
=====================

- sign_response = True (also assert etc.)
- algos: SHA_256

==> see also django/warmbaechli/saml2

Patch for logout bug (https://github.com/OTA-Insight/djangosaml2idp/issues/121):
--- site-packages/djangosaml2idp/views.py.orig	2021-07-05 17:40:31.471614643 +0200
+++ site-packages/djangosaml2idp/views.py	2021-08-24 16:30:34.455854131 +0200
@@ -375,6 +375,7 @@
             return error_cbv.handle_error(request, exception=excp, status_code=400)
 
         resp = idp_server.create_logout_response(req_info.message, [binding])
+        rinfo = idp_server.response_args(req_info.message, [binding])
 
         '''
         # TODO: SOAP
@@ -390,13 +391,13 @@
 
         try:
             # hinfo returns request or response, it depends by request arg
-            hinfo = idp_server.apply_binding(binding, resp.__str__(), resp.destination, relay_state, response=True)
+            hinfo = idp_server.apply_binding(rinfo["binding"], resp, rinfo["destination"], relay_state, response=True)
         except Exception as excp:
             logger.error("ServiceError: %s", excp)
             return error_cbv.handle_error(request, exception=excp, status=400)
 
-        logger.debug("--- {} Response [\n{}] ---".format(self.__service_name, repr_saml(resp.__str__().encode())))
-        logger.debug("--- binding: {} destination:{} relay_state:{} ---".format(binding, resp.destination, relay_state))
+        logger.debug("--- {} Response [\n{}] ---".format(self.__service_name, repr_saml(resp.encode())))
+        logger.debug("--- binding: {} destination:{} relay_state:{} ---".format(rinfo["binding"], rinfo["destination"], relay_state))
 
         # TODO: double check username session and saml login request
         # logout user from IDP

Patch for metadata refrech bug:
--- site-packages/djangosaml2idp/models.orig.py	2021-07-05 17:40:31.471614643 +0200
+++ site-packages/djangosaml2idp/models.py	2021-09-01 12:14:15.444974073 +0200
@@ -108,6 +108,9 @@
         ''' If a remote metadata url is set, fetch new metadata if the locally cached one is expired. Returns True if new metadata was set.
             Sets metadata fields on instance, but does not save to db. If force_refresh = True, the metadata will be refreshed regardless of the currently cached version validity timestamp.
         '''
+        # MST: Never refresh --> Hack to fix bug!!!
+        return False
+
         if not self._should_refresh() and not force_refresh:
             return False
 

