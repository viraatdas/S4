"""SuperTokens configuration for S4."""

import os
from supertokens_python import init, InputAppInfo, SupertokensConfig
from supertokens_python.recipe import thirdparty, session
from supertokens_python.recipe.thirdparty import ProviderInput, ProviderConfig, ProviderClientConfig, SignInAndUpFeature

from s4 import config

# Get configuration from environment or use defaults
SUPERTOKENS_CONNECTION_URI = os.environ.get("SUPERTOKENS_CONNECTION_URI", "http://localhost:3567")
SUPERTOKENS_API_KEY = os.environ.get("SUPERTOKENS_API_KEY", "")
API_DOMAIN = os.environ.get("API_DOMAIN", "http://localhost:8000")
WEBSITE_DOMAIN = os.environ.get("WEBSITE_DOMAIN", "http://localhost:3000")
API_BASE_PATH = "/auth"
WEBSITE_BASE_PATH = "/auth"

# Google OAuth credentials
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")

if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
    import logging
    logging.warning("Google OAuth credentials not set. Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET environment variables.")


def init_supertokens():
    """Initialize SuperTokens with Google authentication."""
    init(
        app_info=InputAppInfo(
            app_name="S4 - Smart S3 Storage Service",
            api_domain=API_DOMAIN,
            website_domain=WEBSITE_DOMAIN,
            api_base_path=API_BASE_PATH,
            website_base_path=WEBSITE_BASE_PATH
        ),
        supertokens_config=SupertokensConfig(
            connection_uri=SUPERTOKENS_CONNECTION_URI,
            api_key=SUPERTOKENS_API_KEY
        ),
        framework='fastapi',
        recipe_list=[
            session.init(
                cookie_secure=not config.DEBUG,
                cookie_same_site="lax"
            ),
            thirdparty.init(
                sign_in_and_up_feature=SignInAndUpFeature(
                    providers=[
                        ProviderInput(
                            config=ProviderConfig(
                                third_party_id="google",
                                clients=[
                                    ProviderClientConfig(
                                        client_id=GOOGLE_CLIENT_ID,
                                        client_secret=GOOGLE_CLIENT_SECRET,
                                    ),
                                ],
                            ),
                        ),
                    ]
                ),
                # Map SuperTokens user to S4 tenant
                override=thirdparty.InputOverrideConfig(
                    apis=thirdparty.override.InputOverrideAPI(
                        sign_in_up_post=custom_sign_in_up
                    )
                )
            )
        ],
        mode='asgi'  # Use asgi for FastAPI
    )


async def custom_sign_in_up(input_):
    """Custom sign in/up handler to map SuperTokens users to S4 tenants."""
    from s4.db import tenant_manager
    from supertokens_python.recipe.thirdparty.interfaces import SignInUpPostOkResult
    
    # Call the original implementation
    response = await thirdparty.default_apis.sign_in_up_post(input_)
    
    if isinstance(response, SignInUpPostOkResult):
        user = response.user
        user_id = user.user_id
        email = user.email
        
        # Check if tenant exists for this user
        tenant = tenant_manager.get_tenant_by_email(email)
        
        if tenant is None and email:
            # Create a new tenant for this user
            tenant = tenant_manager.create_tenant(
                name=email.split('@')[0],  # Use part before @ as name
                email=email,
                plan_id="free",
                active=True
            )
        
        # You could store the SuperTokens user_id in the tenant record
        # for future reference if needed
        
    return response
