"""
Pydantic schemas for fact check results.
"""
from pydantic import BaseModel, Field, computed_field
from typing import Optional
import urllib.parse
from enum import Enum


class CredibilityLevel(str, Enum):
    """Credibility assessment levels."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


class ReliableSource(BaseModel):
    """Schema for a reliable news source link."""
    
    title: str = Field(..., description="Article or page title")
    source: str = Field(..., description="Publication or organization name")

    @computed_field
    @property
    def url(self) -> str:
        """Automatically generated Search URL (Google I'm Feeling Lucky)."""
        query = f"{self.title} {self.source}"
        encoded_query = urllib.parse.quote_plus(query)
        return f"https://www.google.com/search?q={encoded_query}&btnI=1"


class ClaimCheck(BaseModel):
    """Schema for an individual claim analysis."""
    
    claim: str = Field(..., description="The specific claim identified from the video")
    is_factual: Optional[bool] = Field(None, description="Whether the claim is factually correct")
    verification: str = Field(..., description="Explanation of why the claim is true, false, or misleading")
    importance: float = Field(..., ge=0.0, le=1.0, description="How important this claim is to the video's message (0-1)")
    sources: list[ReliableSource] = Field(default_factory=list, description="Specific sources verifying this claim")


class FactCheckResult(BaseModel):
    """Schema for the final fact check result."""
    
    video_url: Optional[str] = Field(None, description="The TikTok video URL")
    credibility_score: float = Field(..., ge=0.0, le=1.0, description="Score from 0-1")
    credibility_level: CredibilityLevel = Field(..., description="Categorical credibility")
    
    # Analysis details
    summary: Optional[str] = Field(None, description="Brief summary of findings")
    claims: list[ClaimCheck] = Field(default_factory=list, description="Detailed breakdown of individual claims")
    
    # Source data
    has_transcript: Optional[bool] = Field(None, description="Whether video had native captions")
    analyzed_text: Optional[str] = Field(None, description="Text that was analyzed")
    
    # Metadata
    processing_time_ms: Optional[int] = Field(None, description="Processing time in milliseconds")


class CheckRequest(BaseModel):
    """Request schema for the /check endpoint."""
    
    url: str = Field(..., description="TikTok video URL to check", min_length=1)
