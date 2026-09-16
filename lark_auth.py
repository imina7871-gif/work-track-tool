"""Lark OAuth2 authentication module."""

import os
import json
import requests
from datetime import datetime
from functools import wraps
from flask import session, redirect, request, url_for

# ── Lark App Configuration ──────────────────────────────────
# To get these credentials:
# 1. Go to https://open.larksuite.com (or https://open.feishu.cn for China)
# 2. Create a new enterprise internal app
# 3. Enable "User Authorization" under Permissions
# 4. Add callback URL: http://YOUR_DOMAIN/auth/lark/callback
# 5. Copy App ID and App Secret below

LARK_CONFIG = {
    "app_id": os.environ.get("LARK_APP_ID", "YOUR_LARK_APP_ID"),
    "app_secret": os.environ.get("LARK_APP_SECRET", "YOUR_LARK_APP_SECRET"),
    # Use feishu.cn for China, larksuite.com for international
    "base_url": os.environ.get("LARK_BASE_URL", "https://open.larksuite.com"),
    "callback_url": os.environ.get("LARK_CALLBACK_URL", "http://localhost:5000/auth/lark/callback"),
}

# ── OAuth URLs ──────────────────────────────────────────────

def get_auth_url(state: str) -> str:
    """Generate Lark OAuth authorization URL."""
    return (
        f"{LARK_CONFIG['base_url']}/open-apis/authen/v1/authorize"
        f"?app_id={LARK_CONFIG['app_id']}"
        f"&redirect_uri={LARK_CONFIG['callback_url']}"
        f"&state={state}"
    )


def get_user_access_token(code: str) -> dict:
    """Exchange authorization code for user access token."""
    url = f"{LARK_CONFIG['base_url']}/open-apis/authen/v1/access_token"
    payload = {
        "grant_type": "authorization_code",
        "code": code,
    }
    headers = {
        "Content-Type": "application/json",
    }
    auth = (LARK_CONFIG["app_id"], LARK_CONFIG["app_secret"])
    
    resp = requests.post(url, json=payload, headers=headers, auth=auth, timeout=10)
    resp.raise_for_status()
    return resp.json()


def get_user_info(access_token: str) -> dict:
    """Get user profile info using access token."""
    url = f"{LARK_CONFIG['base_url']}/open-apis/authen/v1/user_info"
    headers = {
        "Authorization": f"Bearer {access_token}",
    }
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    return data.get("data", {})


def login_required(f):
    """Decorator to require login for a route."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


def get_current_user() -> dict:
    """Get current logged-in user from session."""
    return {
        "user_id": session.get("user_id"),
        "name": session.get("user_name", "Unknown"),
        "email": session.get("user_email", ""),
        "avatar": session.get("user_avatar", ""),
    }


def is_configured() -> bool:
    """Check if Lark credentials are configured."""
    return (
        LARK_CONFIG["app_id"] != "YOUR_LARK_APP_ID"
        and LARK_CONFIG["app_secret"] != "YOUR_LARK_APP_SECRET"
    )
