"""
Placeholder for future audio transcription service using ElevenLabs.
"""
from typing import Optional


class Transcriber:
    """Service for transcribing TikTok audio when native captions aren't available."""
    
    def __init__(self):
        # Future: Initialize ElevenLabs client
        pass
    
    async def transcribe_audio(self, audio_url: str) -> Optional[str]:
        """
        Transcribe audio from a URL using ElevenLabs API.
        
        Args:
            audio_url: URL to the audio file
            
        Returns:
            Transcribed text or None if transcription fails
        """
        # Future implementation:
        # 1. Download audio from audio_url
        # 2. Call ElevenLabs transcription API
        # 3. Return transcribed text
        
        raise NotImplementedError("Transcription service not yet implemented")


# Global transcriber instance
transcriber = Transcriber()
