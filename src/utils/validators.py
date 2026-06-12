from typing import Optional
import re


def validate_instagram_url(url: str) -> bool:
    """Validate Instagram URL format"""
    if not url:
        return False
    pattern = r"(https?://)?(www\.)?instagram\.com/([a-zA-Z0-9_.]+)/?(\?.*)?$"
    return bool(re.match(pattern, url))


def extract_instagram_handle(url: str) -> Optional[str]:
    """Extract Instagram handle from URL"""
    try:
        match = re.search(r"instagram\.com/([a-zA-Z0-9_.]+)", url)
        if match:
            return match.group(1).rstrip("/")
    except Exception:
        pass
    return None


def is_valid_analysis_type(analysis_type: str) -> bool:
    """Validate analysis type"""
    valid_types = ["page", "post", "account"]
    return analysis_type.lower() in valid_types
