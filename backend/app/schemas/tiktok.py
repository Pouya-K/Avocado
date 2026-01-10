"""
Pydantic schemas for TikTok data from Supadata API.
"""
from pydantic import BaseModel, Field
from typing import Optional


class TikTokMetadata(BaseModel):
    """Schema for TikTok video metadata from Supadata."""
    
    title: Optional[str] = Field(None, description="Video title/caption")
    description: Optional[str] = Field(None, description="Video description")
    audio_url: Optional[str] = Field(None, description="URL to the video's audio")
    author: Optional[str] = Field(None, description="Video author username")
    likes: Optional[int] = Field(None, description="Number of likes")
    views: Optional[int] = Field(None, description="Number of views")
    shares: Optional[int] = Field(None, description="Number of shares")
    comments: Optional[int] = Field(None, description="Number of comments")


class TikTokTranscript(BaseModel):
    """Schema for TikTok video transcript from Supadata."""
    
    text: Optional[str] = Field(None, description="Full transcript text")
    language: Optional[str] = Field(None, description="Transcript language code")


class TikTokData(BaseModel):
    """Unified schema combining metadata and transcript."""
    
    url: str = Field(..., description="Original TikTok URL")
    video_id: Optional[str] = Field(None, description="TikTok video ID")
    
    # Metadata fields
    title: Optional[str] = Field(None, description="Video title/caption")
    description: Optional[str] = Field(None, description="Video description")
    audio_url: Optional[str] = Field(None, description="URL to audio (fallback)")
    author: Optional[str] = Field(None, description="Video author")
    
    # Engagement metrics
    likes: Optional[int] = Field(None, description="Number of likes")
    views: Optional[int] = Field(None, description="Number of views")
    shares: Optional[int] = Field(None, description="Number of shares")
    comments: Optional[int] = Field(None, description="Number of comments")
    
    # Transcript
    transcript: Optional[str] = Field(None, description="Video transcript if available")
    transcript_language: Optional[str] = Field(None, description="Transcript language")
    
    # Status
    has_transcript: bool = Field(default=False, description="Whether transcript is available")
