from derex_ecommerce_django.settings.default import *

JWT_AUTH.update(
    {
        "JWT_PUBLIC_SIGNING_JWK_SET": JWT_PUBLIC_SIGNING_JWK_SET,
        "JWT_SIGNING_ALGORITHM": JWT_SIGNING_ALGORITHM,
    }
)
