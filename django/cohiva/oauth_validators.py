from oauth2_provider.oauth2_validators import OAuth2Validator

import portal.auth as portal_auth


class CohivaOAuth2Validator(OAuth2Validator):
    # Set `oidc_claim_scope = None` to ignore scopes that limit which claims to return,
    # otherwise the OIDC standard scopes are used.

    def get_claim_dict(self, request):
        profile = portal_auth.get_oauth_profile(request)
        if not profile:
            # Unauthorized
            return {}
        claims = super().get_claim_dict(request)
        claims["sub"] = profile["id"]
        claims.update(
            {
                "given_name": profile["given_name"],
                "family_name": profile["family_name"],
                "name": profile["name"],
                "preferred_username": profile["username"],
                "email": profile["email"],
            }
        )
        return claims

    def get_discovery_claims(self, request):
        return ["sub", "given_name", "family_name", "name", "preferred_username", "email"]
