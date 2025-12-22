from typing import Optional, Dict, Any
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class GoogleOAuthProvider:
    """Google OAuth provider"""

    def __init__(self):
        try:
            from google.auth.transport import requests as google_requests
            from google.oauth2 import id_token

            self.google_requests = google_requests
            self.id_token = id_token
        except ImportError:
            logger.error("Google Auth not installed. Run: pip install google-auth")
            raise ImportError("Google Auth package not installed")

    async def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify Google OAuth token and return user info"""
        try:
            # Verify the token
            id_info = self.id_token.verify_oauth2_token(
                token,
                self.google_requests.Request(),
                settings.GOOGLE_CLIENT_ID
            )

            return {
                'sub': id_info['sub'],  # Google user ID
                'email': id_info.get('email'),
                'name': id_info.get('name'),
                'picture': id_info.get('picture'),
                'email_verified': id_info.get('email_verified', False),
                'provider': 'google'
            }

        except Exception as e:
            logger.error(f"Google OAuth verification failed: {str(e)}")
            return None

class FacebookOAuthProvider:
    """Facebook OAuth provider"""

    def __init__(self):
        try:
            import requests
            self.requests = requests
        except ImportError:
            logger.error("Requests not installed. Run: pip install requests")
            raise ImportError("Requests package not installed")

    async def verify_token(self, access_token: str) -> Optional[Dict[str, Any]]:
        """Verify Facebook OAuth token and return user info"""
        try:
            # Verify the access token and get user info
            # First, verify the token is valid
            app_token_url = f"https://graph.facebook.com/oauth/access_token?client_id={settings.FACEBOOK_APP_ID}&client_secret={settings.FACEBOOK_APP_SECRET}&grant_type=client_credentials"

            app_token_response = self.requests.get(app_token_url)
            app_token_data = app_token_response.json()

            if 'access_token' not in app_token_data:
                logger.error("Failed to get Facebook app token")
                return None

            app_token = app_token_data['access_token']

            # Verify the user access token
            verify_url = f"https://graph.facebook.com/debug_token?input_token={access_token}&access_token={app_token}"
            verify_response = self.requests.get(verify_url)
            verify_data = verify_response.json()

            if not verify_data.get('data', {}).get('is_valid', False):
                logger.error("Invalid Facebook access token")
                return None

            user_id = verify_data['data']['user_id']

            # Get user profile information
            profile_url = f"https://graph.facebook.com/{user_id}?fields=id,name,email,picture&access_token={access_token}"
            profile_response = self.requests.get(profile_url)
            profile_data = profile_response.json()

            return {
                'sub': profile_data['id'],  # Facebook user ID
                'email': profile_data.get('email'),
                'name': profile_data.get('name'),
                'picture': profile_data.get('picture', {}).get('data', {}).get('url') if profile_data.get('picture') else None,
                'email_verified': True,  # Facebook emails are verified
                'provider': 'facebook'
            }

        except Exception as e:
            logger.error(f"Facebook OAuth verification failed: {str(e)}")
            return None

class MockOAuthProvider:
    """Mock OAuth provider for development/testing"""

    async def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Mock OAuth verification - just return fake user data"""
        logger.info(f"MOCK OAUTH: Token received: {token[:20]}...")

        # Create mock user data based on token (for consistent testing)
        import hashlib
        user_id = hashlib.md5(token.encode()).hexdigest()[:16]

        return {
            'sub': user_id,
            'email': f"mock{user_id[:8]}@example.com",
            'name': f"Mock User {user_id[:4]}",
            'picture': f"https://api.dicebear.com/7.x/avataaars/svg?seed={user_id}",
            'email_verified': True,
            'provider': 'mock'
        }

class OAuthService:
    """OAuth service manager"""

    def __init__(self):
        self.google_provider: Optional[GoogleOAuthProvider] = None
        self.facebook_provider: Optional[FacebookOAuthProvider] = None
        self._initialize_providers()

    def _initialize_providers(self):
        """Initialize OAuth providers based on settings"""
        if not getattr(settings, 'OAUTH_ENABLED', False):
            logger.warning("OAuth is disabled. Using mock provider for development.")
            self.google_provider = MockOAuthProvider()
            self.facebook_provider = MockOAuthProvider()
            return

        # Initialize Google OAuth
        if hasattr(settings, 'GOOGLE_CLIENT_ID') and settings.GOOGLE_CLIENT_ID:
            try:
                self.google_provider = GoogleOAuthProvider()
                logger.info("Google OAuth provider initialized successfully")
            except ImportError:
                logger.error("Google Auth package not installed. Using mock provider.")
                self.google_provider = MockOAuthProvider()
        else:
            logger.warning("Google OAuth credentials not configured. Using mock provider.")
            self.google_provider = MockOAuthProvider()

        # Initialize Facebook OAuth
        if hasattr(settings, 'FACEBOOK_APP_ID') and settings.FACEBOOK_APP_ID:
            try:
                self.facebook_provider = FacebookOAuthProvider()
                logger.info("Facebook OAuth provider initialized successfully")
            except ImportError:
                logger.error("Requests package not installed. Using mock provider.")
                self.facebook_provider = MockOAuthProvider()
        else:
            logger.warning("Facebook OAuth credentials not configured. Using mock provider.")
            self.facebook_provider = MockOAuthProvider()

    async def verify_google_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify Google OAuth token"""
        if not self.google_provider:
            logger.error("Google OAuth provider not initialized")
            return None

        return await self.google_provider.verify_token(token)

    async def verify_facebook_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify Facebook OAuth token"""
        if not self.facebook_provider:
            logger.error("Facebook OAuth provider not initialized")
            return None

        return await self.facebook_provider.verify_token(token)

# Global OAuth service instance
oauth_service = OAuthService()
