## Preface
SAML session state is maintained in support of the SAML protocol.</br>
This is done using a cookie.</br>
For earlier releases of the SAML library from v2.5.0 to 2.8.8, the ASP.NET session cookie (by default named ASP.NET_SessionId) is used.</br>
For releases of the SAML library from v3.0.0 and onward a custom cookie (by default named SAML_SessionId) is used</br>
**However, not all SAML flows require SAML session state.**

## Service Provider
The following sections apply if your site is acting as the service provider (SP)</br>

- IdP-initiated SSO:</br>
  A SAML response is sent by the IdP to the SP</br>
  No SAML session state is required for this flow</br>

- SP-initiated SSO:</br>
  A SAML authn request is sent by the SP to the IdP.</br>
  A SAML response is sent by the IdP to the SP</br>
  According to the SAML specification, the SAML response returned by the IdP should have an InResponseTo field that matches the authn request ID.</br>
  This ties the SAML response to the authn request.</br>
  The authn request ID is saved in the SAML session state so it can be checked against the InResponseTo</br>
  If the cookie is lost between sending the SAML authn request and receiving the SAML response, the InResponseTo field cannot be checked.</br>
  Consequently, this flow is treated the same as IdP-initiated SSO</br>
  For most scenarios, this probably doesn't matter but strictly speaking it isn't correct</br>

- IdP-initiated SLO:</br>
  A SAML logout request is sent by the IdP to the SP.</br>
  A SAML logout response is sent by the SP to the IdP</br>
  No SAML session state is required for this flow</br>

- SP-initiated SLO:</br>
  A SAML logout request is sent by the SP to the IdP.</br>
  A SAML logout response is sent by the IdP to the SP</br>
  SAML session state is required for this flow</br>

## Identity Provider
The following sections apply if your site is acting as the identity provider (IdP)</br>

- IdP-initiated SSO:</br>
  A SAML response is sent by the IdP to the SP.</br>
  No SAML session state is required for this flow</br>

- SP-initiated SSO:</br>
  A SAML authn request is sent by the SP to the IdP.</br>
  A SAML response is sent by the IdP to the SP</br>
  SAML session state is required for this flow</br>

- IdP-initiated SLO:</br>
  A SAML logout request is sent by the IdP to the SP.</br>
  A SAML logout response is sent by the SP to the IdP</br>
  SAML session state is required for this flow</br>

- SP-initiated SLO:</br>
  A SAML logout request is sent by the SP to the IdP.</br>
  A SAML logout response is sent by the IdP to the SP</br>
  No SAML session state is required for this flow</br>
