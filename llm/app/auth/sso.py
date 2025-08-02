"""
Authentication module for SSO and TrustFabric token validation.

This module provides authentication middleware and dependencies for FastAPI.
"""

from typing import Optional, List, Dict, Any
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from loguru import logger

from pycloudclient.auth import OAuthProvider, OAuthConfig
from pycloudclient.auth.auth import TF_TOKEN_HEADER, ISTIO_IP_HEADER
from pycloudclient.microvault import grpc_client

from app.core.config import get_config

security = HTTPBearer(auto_error=False)


class AuthConfig:
    """Authentication configuration."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize with configuration.

        Args:
            config: Application configuration
        """
        self.enabled = config.get("enabled", False)
        self.timeout = config.get("timeout", 30)
        self.endpoint = config.get("endpoint", "")


def get_auth_config() -> AuthConfig:
    """
    Get authentication configuration from application config.

    Returns:
        AuthConfig instance
    """
    app_config = get_config()
    return AuthConfig(app_config.get("auth", {}))


def get_auth_dependencies() -> List:
    """
    Returns list of authentication dependencies based on configuration.

    Returns:
        List of FastAPI dependencies
    """
    config = get_auth_config()
    dependencies = []

    if config.enabled:
        dependencies.append(Depends(verify_token))
        logger.info("Authentication enabled")
        logger.info(f"Dependency added: {dependencies[-1]}")
    else:
        logger.info("Authentication disabled")

    return dependencies


def get_oauth_provider():
    """
    Initialize and return OAuth provider with configuration.

    Returns:
        OAuth provider instance
    """
    config = get_auth_config()
    cfg = {"timeout": config.timeout, "endpoint": config.endpoint}
    return OAuthProvider(OAuthConfig(**cfg))


async def verify_token(
    request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    Verify and return token from either TrustFabric or OAuth.

    Args:
        request: FastAPI request object
        credentials: Authorization credentials

    Returns:
        Dictionary containing token information

    Raises:
        HTTPException: If authentication fails
    """
    config = get_auth_config()

    if not config.enabled:
        return None
    if tf_token := request.headers.get(TF_TOKEN_HEADER):
        client_ip = request.headers.get(ISTIO_IP_HEADER) or request.client.host
        response = grpc_client.validate_token(
            tf_token=tf_token, sso_token=None, client_ip=client_ip
        )
        if not response.valid:
            if response.error:
                logger.error(f"TrustFabric authentication failed: {response.error}")
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=response.error)
            logger.error("TrustFabric authentication failed: Invalid token")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return {"token": tf_token}

    if credentials:
        access_token = credentials.credentials
        oauth_provider = get_oauth_provider()
        _, authenticated = oauth_provider.authenticate("Bearer", access_token)
        if not authenticated:
            logger.error("SSO Authentication failed: Invalid token")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return {"token": access_token}

    logger.error("Authentication failed: Token not provided")
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token not provided")


async def extract_token_from_request(request: Request) -> Optional[str]:
    """
    Extract authentication token directly from request headers without using dependencies.

    Args:
        request: FastAPI request object

    Returns:
        Token string if found, None otherwise
    """
    # Check for TrustFabric token first
    if tf_token := request.headers.get(TF_TOKEN_HEADER):
        return tf_token

    # Then check for Bearer token in Authorization header
    if auth_header := request.headers.get("Authorization"):
        if auth_header.startswith("Bearer "):
            return auth_header.replace("Bearer ", "")

    return None


def get_token_from_auth(
    request: Request, auth_result: Optional[dict] = Depends(verify_token)
) -> dict:
    """
    Get token from auth and prepare config for workflow.

    Args:
        request: FastAPI request object
        auth_result: Result from verify_token

    Returns:
        Dictionary with metadata containing token
    """
    if not auth_result:
        return {"metadata": {}}
    return {"metadata": {"token": auth_result["token"]}}


def setup_auth(app):
    """
    Set up authentication for the FastAPI application.

    Args:
        app: FastAPI application
    """
    config = get_auth_config()

    if not config.enabled:
        logger.info("Authentication is disabled")
        return
    logger.info("Authentication setup complete")
