"""
URL utility functions for cleaning and validating TikTok URLs.
"""
import httpx
from urllib.parse import urlparse, parse_qs


async def resolve_short_url(url: str) -> str:
    """
    Resolve shortened TikTok URLs (e.g., vm.tiktok.com) to their full URL.
    
    Args:
        url: The TikTok URL (potentially shortened)
        
    Returns:
        The resolved full URL
        
    Raises:
        ValueError: If the URL cannot be resolved
    """
    parsed = urlparse(url)
    
    # Check if it's a shortened URL
    if parsed.netloc in ["vm.tiktok.com", "vt.tiktok.com"]:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            try:
                response = await client.head(url, timeout=10.0)
                return str(response.url)
            except httpx.HTTPError as e:
                raise ValueError(f"Failed to resolve shortened URL: {e}")
    
    return url


def clean_tiktok_url(url: str) -> str:
    """
    Clean and normalize a TikTok URL.
    
    Args:
        url: The TikTok URL to clean
        
    Returns:
        Cleaned URL
        
    Raises:
        ValueError: If the URL is not a valid TikTok URL
    """
    parsed = urlparse(url)
    
    # Validate it's a TikTok URL
    valid_domains = ["tiktok.com", "www.tiktok.com", "vm.tiktok.com", "vt.tiktok.com"]
    if not any(domain in parsed.netloc for domain in valid_domains):
        raise ValueError(f"Invalid TikTok URL: {url}")
    
    return url.strip()


def extract_video_id(url: str) -> str:
    """
    Extract video ID from TikTok URL.
    
    Args:
        url: The TikTok URL
        
    Returns:
        The video ID if found, otherwise empty string
    """
    parsed = urlparse(url)
    
    # Pattern: /video/123456789
    if "/video/" in parsed.path:
        parts = parsed.path.split("/video/")
        if len(parts) > 1:
            video_id = parts[1].split("/")[0].split("?")[0]
            return video_id
    
    return ""
