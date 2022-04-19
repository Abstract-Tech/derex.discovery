from derex_django.settings.default import *

FEATURES["ENABLE_OAUTH2_PROVIDER"] = True

OAUTH_OIDC_ISSUER = "http://discovery-ironwood-minimal.localhost/oauth2"
