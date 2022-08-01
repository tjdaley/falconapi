"""
ms_authenticator.py - Microsoft Authenticator
"""

"""
MSAL Environment Variables:
    AZURE_CLIENT_ID
    AZURE_AUTHORITY
"""

import os
import msal
import json
import jwt

import settings

SCOPE = ["User.Read"]

class MSALAuthenticator:
    # Create a preferably long-lived app instance which maintains a token cache.
    client_id = os.environ["MSAL_CLIENT_ID"]
    authority = os.environ["MSAL_AUTHORITY"]
    app = msal.PublicClientApplication(
        client_id=client_id,
        authority=authority
        # token_cache=...  # Default cache is in memory only.
                        # You can learn how to use SerializableTokenCache from
                        # https://msal-python.rtfd.io/en/latest/#msal.SerializableTokenCache
    )

    def __init__(self):
        pass

    def get_token(self, username):
        """
        Get a token for the user.
        """
        result = None
        accounts = self.app.get_accounts(username=username)

        if accounts:
            result = self.app.acquire_token_silent(SCOPE, account=accounts[0])
        if not result:
            result = self.app.acquire_token_interactive(SCOPE)
        
        if 'access_token' in result:
            access_token = result['access_token']
            alg = jwt.get_unverified_header(access_token)['alg']
            decodedAccessToken = jwt.decode(access_token, algorithms=[alg], options={"verify_signature": False})
            return {
                'result': 'OK',
                'token': result.get('access_token'),
                'expires_in': result.get('expires_in'),
                'name': decodedAccessToken.get('name'),
                'upn': decodedAccessToken.get('upn')
            }

        error_codes = result.get('error_codes', [])
        url = MSALAuthenticator.app.get_authorization_request_url(SCOPE)

        if 65001 in error_codes:
            return {'result': 'ERROR', 'message': f"User account locked out. Visit {url} to authorize account."}

        if 50034 in error_codes:
            return {'result': 'ERROR', 'message': f"User account does not exist. Visit {url} to create account."}

        if 50126 in error_codes:
            return {'result': 'ERROR', 'message': f"User account is disabled or password is incorrect. Visit {url} to reset password"}
        
        if 50076 in error_codes:
            return {'result': 'ERROR', 'message': f"Due to a configuration change made by your administrator, or because you moved to a new location, you must use multi-factor authentication to access {username}'s account."}

        return {'result': 'ERROR', 'message': f"Unknown error", 'error_codes': error_codes}


def main():
    """
    Main function.
    """
    import settings
    authenticator = MSALAuthenticator()
    print(authenticator.get_token('test', 'test'))


if __name__ == '__main__':
    main()