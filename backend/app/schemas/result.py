"""
Pydantic schemas for fact check results.
"""
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class CredibilityLevel(str, Enum):
    """Credibility assessment levels."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


class FactCheckResult(BaseModel):
    """Schema for the final fact check result."""
    
    video_url: str = Field(..., description="The TikTok video URL")
    credibility_score: float = Field(..., ge=0.0, le=1.0, description="Score from 0-1")
    credibility_level: CredibilityLevel = Field(..., description="Categorical credibility")
    
    # Analysis details
    summary: Optional[str] = Field(None, description="Brief summary of findings")
    concerns: list[str] = Field(default_factory=list, description="List of credibility concerns")
    strengths: list[str] = Field(default_factory=list, description="Positive credibility indicators")
    
    # Source data
    has_transcript: bool = Field(..., description="Whether video had native captions")
    analyzed_text: Optional[str] = Field(None, description="Text that was analyzed")
    
    # Metadata
    processing_time_ms: Optional[int] = Field(None, description="Processing time in milliseconds")


class CheckRequest(BaseModel):
    """Request schema for the /check endpoint."""
    
    url: str = Field(..., description="TikTok video URL to check", min_length=1)
