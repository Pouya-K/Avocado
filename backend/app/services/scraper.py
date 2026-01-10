"""
TikTok data scraper service using Supadata API.
Fetches metadata and transcript in parallel using async httpx.
"""
import asyncio
import httpx
from typing import Optional
import logging

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
    """Service for scraping TikTok video data via Supadata API."""
    
    def __init__(self):
        self.base_url = settings.SUPADATA_BASE_URL
        self.api_key = settings.SUPADATA_API_KEY
        self.timeout = settings.REQUEST_TIMEOUT
        
        if not self.api_key:
            raise ValueError("SUPADATA_API_KEY is not configured")
    
    def _get_headers(self) -> dict:
        """Get HTTP headers with API key."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def _fetch_metadata(self, url: str, client: httpx.AsyncClient) -> TikTokMetadata:
        """
        Fetch TikTok video metadata from Supadata.
        
        Args:
            url: The TikTok video URL
            client: The httpx AsyncClient instance
            
        Returns:
            TikTokMetadata object
            
        Raises:
            SupadataAPIError: If the API request fails
        """
        endpoint = f"{self.base_url}{settings.SUPADATA_METADATA_ENDPOINT}"
        params = {"url": url}
        
        try:
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
            elif response.status_code >= 400:
                raise SupadataAPIError(
                    f"Metadata API error: {response.status_code} - {response.text}",
                    status_code=response.status_code
                )
            
            data = response.json()
            logger.info(f"Metadata fetched successfully for URL: {url}")
            
            # Parse response into our schema
            # Adjust field mapping based on actual Supadata API response
            return TikTokMetadata(
                title=data.get("title") or data.get("desc"),
                description=data.get("description") or data.get("desc"),
                audio_url=data.get("audio_url") or data.get("music", {}).get("playUrl"),
                author=data.get("author") or data.get("author", {}).get("uniqueId"),
                likes=data.get("likes") or data.get("stats", {}).get("diggCount"),
                views=data.get("views") or data.get("stats", {}).get("playCount"),
                shares=data.get("shares") or data.get("stats", {}).get("shareCount"),
                comments=data.get("comments") or data.get("stats", {}).get("commentCount")
            )
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching metadata: {e}")
            raise SupadataAPIError(f"Failed to fetch metadata: {str(e)}")
    
    async def _fetch_transcript(self, url: str, client: httpx.AsyncClient) -> Optional[TikTokTranscript]:
        """
        Fetch TikTok video transcript from Supadata.
        
        Args:
            url: The TikTok video URL
            client: The httpx AsyncClient instance
            
        Returns:
            TikTokTranscript object or None if transcript not available
            
        Raises:
            SupadataAPIError: If the API request fails (excluding 404)
        """
        endpoint = f"{self.base_url}{settings.SUPADATA_TRANSCRIPT_ENDPOINT}"
        params = {"url": url}
        
        try:
            response = await client.get(
                endpoint,
                params=params,
                headers=self._get_headers(),
                timeout=self.timeout
            )
            
            # Handle 404 - no transcript available (not an error)
            if response.status_code == 404:
                logger.info(f"No transcript available for URL: {url}")
                return None
            
            # Handle auth/credits errors
            if response.status_code == 401:
                raise SupadataAuthError()
            elif response.status_code == 402:
                raise SupadataCreditsExhausted()
            elif response.status_code >= 400:
                raise SupadataAPIError(
                    f"Transcript API error: {response.status_code} - {response.text}",
                    status_code=response.status_code
                )
            
            data = response.json()
            logger.info(f"Transcript fetched successfully for URL: {url}")
            
            # Parse response - adjust based on actual API response structure
            transcript_text = data.get("text") or data.get("transcript")
            language = data.get("language") or data.get("lang")
            
            if transcript_text:
                return TikTokTranscript(
                    text=transcript_text,
                    language=language
                )
            
            return None
            
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
