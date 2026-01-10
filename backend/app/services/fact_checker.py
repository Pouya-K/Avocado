import logging
import time
from typing import Optional
from google import genai
from google.genai import types, errors

from app.core.config import settings
from app.schemas.result import FactCheckResult, CredibilityLevel, ReliableSource
from app.schemas.tiktok import TikTokData
from app.services.exceptions import (
    GeminiAPIError,
    GeminiAuthError,
    GeminiRateLimitError,
    GeminiQuotaExceededError
)

logger = logging.getLogger(__name__)

class FactChecker:
    def __init__(self):
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not configured")
        
        # 2026 Standard: Use the centralized Client
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        
        # Modern Tooling: Use the unified google_search tool
        self.tools = []
        if settings.GEMINI_USE_SEARCH:
            self.tools.append(types.Tool(google_search=types.GoogleSearch()))

    def _construct_prompt(self, tiktok_data: TikTokData) -> str:
        # Gemini 3 Pro/Flash is a reasoning model; it works best with 
        # concise context followed by direct, anchored instructions.
        prompt = f"""VIDEO CONTEXT:
- Author: @{tiktok_data.author}
- Caption: {tiktok_data.title or tiktok_data.description}
- Engagement: {tiktok_data.views:,} views, {tiktok_data.likes:,} likes
"""
        if tiktok_data.has_transcript and tiktok_data.transcript:
            prompt += f"\nTRANSCRIPT:\n{tiktok_data.transcript}"
        
        prompt += """
INSTRUCTIONS:
Analyze the video content and transcript to verify the most critical information.
1. TARGET KEY CLAIMS: Identify the top 3 most significant factual claims.
2. DIRECT VERIFICATION: Perform a single, efficient Google Search to verify these claims.
3. CONCISE REPORTING: For each claim, provide a 1-2 sentence verification.
4. VALID SOURCES: For each claim, provide a singular reliable source with the specific details found in your Google Search results.
   - RELIABILITY CRITERIA: Prioritize hard news organizations, academic journals, and government agencies. 
   - EXAMPLES: Reuters, Associated Press (AP), BBC News, The New York Times, Wall Street Journal, Nature, Science, NIH.gov, etc.
   - AVOID: Social media posts (Twitter/X, Reddit), YouTube, personal blogs, tabloid sites (The Sun, TMZ), or unverified news outlets.
   - For each source, you MUST provide:
     a) THE EXACT ARTICLE TITLE.
     b) THE NAME OF THE PUBLICATION/SOURCE.
   - If no highly reliable source is found for a specific claim, explain that in the verification text and leave the sources list empty for that claim.
5. SCORING: Provide an overall credibility score (0.0 to 1.0) and a brief summary."""
        return prompt

    async def analyze_credibility(self, tiktok_data: TikTokData) -> FactCheckResult:
        start_time = time.time()
        try:
            # 1. Configuration: Unified Structured Output & Reasoning
            config = types.GenerateContentConfig(
                tools=self.tools,
                response_mime_type="application/json",
                response_schema=FactCheckResult,
                thinking_config=types.ThinkingConfig(
                    thinking_level="minimal" 
                ),
                # Lower resolution saves ingestion time
                media_resolution=types.MediaResolution.MEDIA_RESOLUTION_LOW,
                temperature=1.0
            )

            # 2. Execution: Use the ASYNC client models service
            response = await self.client.aio.models.generate_content(
                model=settings.GEMINI_MODEL, # "gemini-3-flash-preview"
                contents=self._construct_prompt(tiktok_data),
                config=config
            )

            # 3. Direct Parsing: response.parsed is now your Pydantic object
            result: Optional[FactCheckResult] = response.parsed
            
            if not result:
                # Fallback: Check if the model was blocked or just didn't return JSON
                error_msg = "Gemini failed to generate a structured analysis."
                if hasattr(response, 'candidates') and response.candidates:
                    finish_reason = response.candidates[0].finish_reason
                    error_msg += f" (Finish Reason: {finish_reason})"
                
                logger.error(f"Analysis failed for {tiktok_data.video_id}: {error_msg}")
                raise GeminiAPIError(error_msg)
            
            # 4. Post-processing: Attach metadata that AI doesn't generate
            result.video_url = tiktok_data.url
            result.has_transcript = tiktok_data.has_transcript
            result.analyzed_text = tiktok_data.transcript
            result.processing_time_ms = int((time.time() - start_time) * 1000)


            logger.info(f"Analysis successful for {tiktok_data.video_id} (Score: {result.credibility_score})")
            return result

        except errors.ClientError as e:
            # Handle API-specific errors (using the Client's error context)
            if "429" in str(e) or "quota" in str(e).lower():
                raise GeminiQuotaExceededError(original_error=e)
            if "401" in str(e) or "key" in str(e).lower():
                raise GeminiAuthError(original_error=e)
            
            logger.error(f"Gemini API Client Error: {e}")
            raise GeminiAPIError(f"API Error: {str(e)}", e)
        except Exception as e:
            logger.error(f"Unexpected Fact-Check Error: {e}")
            raise GeminiAPIError(f"Failed to analyze content: {str(e)}", e)

# Global fact checker instance
fact_checker = FactChecker()