"""
TikTok data scraper service using Supadata API.
Fetches metadata and transcript in parallel using async httpx.
Includes caching and retry logic to handle rate limits.
"""
import asyncio
import httpx
from typing import Optional
import logging
import hashlib
from cachetools import TTLCache

from app.core.config import settings
from app.schemas.tiktok import TikTokData, TikTokMetadata, TikTokTranscript
from app.utils.url_utils import clean_tiktok_url, resolve_short_url, extract_video_id
from app.services.exceptions import (
    SupadataAPIError,
    SupadataAuthError,
    SupadataCreditsExhausted,
    InvalidTikTokURLError,
    TranscriptNotAvailableError
)

logger = logging.getLogger(__name__)


class TikTokScraper:
    """Service for scraping TikTok video data via Supadata API with caching and retry logic."""
    
    def __init__(self):
        self.base_url = settings.SUPADATA_BASE_URL
        self.api_key = settings.SUPADATA_API_KEY
        self.timeout = settings.REQUEST_TIMEOUT
        
        # Initialize cache (TTL cache expires items after configured time)
        self.cache = TTLCache(
            maxsize=settings.CACHE_MAX_SIZE,
            ttl=settings.CACHE_TTL
        )
        
        if not self.api_key:
            raise ValueError("SUPADATA_API_KEY is not configured")
    
    def _get_cache_key(self, url: str, endpoint: str) -> str:
        """Generate a cache key for a URL and endpoint."""
        combined = f"{endpoint}:{url}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def _get_headers(self) -> dict:
        """Get HTTP headers with API key."""
        return {
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        }
    
    async def _retry_request(self, request_func, *args, max_retries: int = None, **kwargs):
        """
        Retry a request with exponential backoff on rate limit errors.
        
        Args:
            request_func: Async function to call
            max_retries: Maximum retry attempts (uses settings.MAX_RETRIES if None)
            *args, **kwargs: Arguments to pass to request_func
            
        Returns:
            Result from request_func
            
        Raises:
            SupadataAPIError: If all retries fail
        """
        if max_retries is None:
            max_retries = settings.MAX_RETRIES
        
        last_exception = None
        delay = settings.RETRY_DELAY
        
        for attempt in range(max_retries + 1):
            try:
                return await request_func(*args, **kwargs)
            except SupadataAPIError as e:
                last_exception = e
                
                # Only retry on rate limit errors (429)
                if e.status_code == 429:
                    if attempt < max_retries:
                        logger.warning(
                            f"Rate limit hit (attempt {attempt + 1}/{max_retries + 1}). "
                            f"Retrying in {delay:.1f}s..."
                        )
                        await asyncio.sleep(delay)
                        delay *= settings.RETRY_BACKOFF  # Exponential backoff
                        continue
                    else:
                        logger.error(f"Rate limit exceeded after {max_retries + 1} attempts")
                
                # Don't retry on other errors
                raise
        
        # If we get here, all retries failed
        raise last_exception
    
    async def _fetch_metadata(self, url: str, client: httpx.AsyncClient) -> TikTokMetadata:
        """
        Fetch TikTok video metadata from Supadata with caching.
        
        Args:
            url: The TikTok video URL
            client: The httpx AsyncClient instance
            
        Returns:
            TikTokMetadata object
            
        Raises:
            SupadataAPIError: If the API request fails
        """
        # Check cache first
        cache_key = self._get_cache_key(url, "metadata")
        if cache_key in self.cache:
            logger.info(f"Cache hit for metadata: {url}")
            return self.cache[cache_key]
        
        # Make the actual request with retry logic
        async def _make_request():
            endpoint = f"{self.base_url}{settings.SUPADATA_METADATA_ENDPOINT}"
            params = {"url": url}
            
            response = await client.get(
                endpoint,
                params=params,
                headers=self._get_headers(),
                timeout=self.timeout
            )
            
            # Handle various error status codes
            if response.status_code == 401:
                raise SupadataAuthError()
            elif response.status_code == 402:
                raise SupadataCreditsExhausted()
            elif response.status_code == 429:
                raise SupadataAPIError(
                    f"Rate limit exceeded: {response.text}",
                    status_code=429
                )
            elif response.status_code >= 400:
                raise SupadataAPIError(
                    f"Metadata API error: {response.status_code} - {response.text}",
                    status_code=response.status_code
                )
            
            data = response.json()
            logger.info(f"Metadata fetched successfully for URL: {url}")
            
            # Parse response into our schema based on Supadata unified format
            author_data = data.get("author", {})
            stats_data = data.get("stats", {})
            
            metadata = TikTokMetadata(
                title=data.get("title"),
                description=data.get("description"),
                audio_url=None,  # Supadata doesn't return audio URL in metadata
                author=author_data.get("username") or author_data.get("displayName"),
                likes=stats_data.get("likes"),
                views=stats_data.get("views"),
                shares=stats_data.get("shares"),
                comments=stats_data.get("comments")
            )
            
            # Cache the result
            self.cache[cache_key] = metadata
            return metadata
        
        try:
            return await self._retry_request(_make_request)
        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching metadata: {e}")
            raise SupadataAPIError(f"Failed to fetch metadata: {str(e)}")
    
    async def _fetch_transcript(self, url: str, client: httpx.AsyncClient) -> Optional[TikTokTranscript]:
        """
        Fetch TikTok video transcript from Supadata with caching.
        
        Args:
            url: The TikTok video URL
            client: The httpx AsyncClient instance
            
        Returns:
            TikTokTranscript object or None if transcript not available
            
        Raises:
            SupadataAPIError: If the API request fails (excluding 404)
        """
        # Check cache first
        cache_key = self._get_cache_key(url, "transcript")
        if cache_key in self.cache:
            logger.info(f"Cache hit for transcript: {url}")
            return self.cache[cache_key]
        
        # Make the actual request with retry logic
        async def _make_request():
            endpoint = f"{self.base_url}{settings.SUPADATA_TRANSCRIPT_ENDPOINT}"
            params = {
                "url": url,
                "text": "true",  # Get plain text instead of timestamped chunks
                "lang": "en",    # Request English transcript
                "mode": "auto"   # Try native English first, fallback to AI generation if needed
            }
            
            response = await client.get(
                endpoint,
                params=params,
                headers=self._get_headers(),
                timeout=self.timeout
            )
            
            # Handle 404 - no transcript available (not an error)
            if response.status_code == 404:
                logger.info(f"No transcript available for URL: {url}")
                self.cache[cache_key] = None  # Cache the "not available" result too
                return None
            
            # Handle auth/credits errors
            if response.status_code == 401:
                raise SupadataAuthError()
            elif response.status_code == 402:
                raise SupadataCreditsExhausted()
            elif response.status_code == 429:
                raise SupadataAPIError(
                    f"Rate limit exceeded: {response.text}",
                    status_code=429
                )
            elif response.status_code >= 400:
                raise SupadataAPIError(
                    f"Transcript API error: {response.status_code} - {response.text}",
                    status_code=response.status_code
                )
            
            data = response.json()
            logger.info(f"Transcript fetched successfully for URL: {url}")
            
            # Parse response based on Supadata API format
            # Response has 'content' (string) and 'lang' fields
            transcript_text = data.get("content")
            language = data.get("lang")
            
            transcript = None
            if transcript_text:
                transcript = TikTokTranscript(
                    text=transcript_text,
                    language=language
                )
            
            # Cache the result
            self.cache[cache_key] = transcript
            return transcript
        
        try:
            return await self._retry_request(_make_request)
        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching transcript: {e}")
            raise SupadataAPIError(f"Failed to fetch transcript: {str(e)}")
    
    async def fetch_tiktok_data(self, video_url: str) -> TikTokData:
        """
        Fetch complete TikTok video data (metadata + transcript) in parallel.
        
        This is the main entry point for the scraper service.
        
        Args:
            video_url: The TikTok video URL
            
        Returns:
            TikTokData object with all available information
            
        Raises:
            InvalidTikTokURLError: If URL is invalid
            SupadataAPIError: If API requests fail
        """
        try:
            # Step 1: Clean and validate URL
            cleaned_url = clean_tiktok_url(video_url)
            
            # Step 2: Resolve shortened URLs if needed
            resolved_url = await resolve_short_url(cleaned_url)
            
            # Step 3: Extract video ID for reference
            video_id = extract_video_id(resolved_url)
            
            logger.info(f"Processing TikTok URL: {resolved_url}")
            
            # Step 4: Fetch metadata and transcript in parallel
            async with httpx.AsyncClient() as client:
                metadata_task = self._fetch_metadata(resolved_url, client)
                transcript_task = self._fetch_transcript(resolved_url, client)
                
                # Execute both requests concurrently
                metadata, transcript = await asyncio.gather(
                    metadata_task,
                    transcript_task,
                    return_exceptions=False
                )
            
            # Step 5: Combine into unified TikTokData object
            has_transcript = transcript is not None and transcript.text is not None
            
            return TikTokData(
                url=resolved_url,
                video_id=video_id,
                # Metadata
                title=metadata.title,
                description=metadata.description,
                audio_url=metadata.audio_url,
                author=metadata.author,
                likes=metadata.likes,
                views=metadata.views,
                shares=metadata.shares,
                comments=metadata.comments,
                # Transcript
                transcript=transcript.text if transcript else None,
                transcript_language=transcript.language if transcript else None,
                has_transcript=has_transcript
            )
            
        except ValueError as e:
            # URL validation errors
            raise InvalidTikTokURLError(str(e))
        except (SupadataAuthError, SupadataCreditsExhausted) as e:
            # Re-raise auth/credits errors as-is
            raise
        except Exception as e:
            logger.error(f"Unexpected error in fetch_tiktok_data: {e}")
            raise SupadataAPIError(f"Failed to fetch TikTok data: {str(e)}")


# Global scraper instance
scraper = TikTokScraper()


async def fetch_tiktok_data(video_url: str) -> TikTokData:
    """
    Convenience function to fetch TikTok data using the global scraper instance.
    
    Args:
        video_url: The TikTok video URL
        
    Returns:
        TikTokData object
    """
    return await scraper.fetch_tiktok_data(video_url)
