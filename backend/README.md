# Avocado TikTok Fact Checker - Backend

FastAPI backend service for analyzing TikTok video credibility using the Supadata API.

## Features

- ✅ **Async TikTok Data Scraping**: Parallel fetching of metadata and transcripts
- ✅ **Supadata API Integration**: Native support for TikTok video analysis
- ✅ **URL Handling**: Automatic resolution of shortened TikTok URLs
- ✅ **Error Handling**: Comprehensive error handling with custom exceptions
- ✅ **Pydantic Validation**: Type-safe data models for all requests/responses
- 🚧 **Fact Checking**: LLM-based credibility analysis (planned)
- 🚧 **Audio Transcription**: ElevenLabs integration for videos without captions (planned)

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── deps.py          # API dependencies
│   │   └── v1/
│   │       └── check.py     # Main /check endpoint
│   ├── core/
│   │   └── config.py        # Configuration management
│   ├── schemas/
│   │   ├── tiktok.py        # TikTok data models
│   │   └── result.py        # API response models
│   ├── services/
│   │   ├── scraper.py       # Supadata API integration ✅
│   │   ├── exceptions.py    # Custom exceptions
│   │   └── fact_checker.py  # (Future) LLM fact-checking
│   ├── utils/
│   │   └── url_utils.py     # URL cleaning & validation
│   └── main.py              # FastAPI application
├── tests/
├── .env.example
├── .gitignore
└── requirements.txt
```

## Installation

### 1. Create Virtual Environment

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and add your Supadata API key:

```env
SUPADATA_API_KEY=your_actual_api_key_here
```

## Running the Server

### Development Mode

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Documentation

Once running, access:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### POST /api/v1/check

Check the credibility of a TikTok video.

**Request:**
```json
{
  "url": "https://www.tiktok.com/@username/video/1234567890"
}
```

**Response:**
```json
{
  "video_url": "https://www.tiktok.com/@username/video/1234567890",
  "credibility_score": 0.5,
  "credibility_level": "unknown",
  "summary": "Data successfully fetched...",
  "concerns": ["No native transcript available"],
  "strengths": ["Audio URL available for transcription"],
  "has_transcript": false,
  "analyzed_text": null,
  "processing_time_ms": 1234
}
```

### GET /api/v1/health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "avocado-fact-checker"
}
```

## Implementation Details

### Scraper Service (`services/scraper.py`)

The scraper service implements the core TikTok data fetching logic:

1. **URL Validation**: Cleans and validates TikTok URLs
2. **Short URL Resolution**: Follows redirects for `vm.tiktok.com` links
3. **Parallel Fetching**: Uses `asyncio.gather()` to fetch metadata and transcript simultaneously
4. **Error Handling**: Distinguishes between different API errors (401, 402, 404, etc.)
5. **Fallback Support**: Returns audio URL even when transcript is unavailable

### Error Handling

Custom exceptions for different failure scenarios:
- `InvalidTikTokURLError`: Malformed URLs
- `SupadataAuthError`: Invalid API key (401)
- `SupadataCreditsExhausted`: Out of API credits (402)
- `SupadataAPIError`: General API failures

### Configuration

All settings managed via Pydantic Settings in `core/config.py`:
- API keys loaded from environment
- Configurable timeouts and retry logic
- CORS settings for browser extension support

## Testing

Run tests with pytest:

```bash
pytest tests/
```

## Development Checklist

- [x] Backend folder structure created
- [x] httpx installed and used for all API calls
- [x] Service returns audio_url as fallback when transcript is null
- [x] No hardcoded strings; all URLs and keys in config.py or .env
- [x] Parallel execution with asyncio.gather
- [x] Short link resolution implemented
- [x] Pydantic schema integration
- [x] Comprehensive error handling
- [ ] LLM-based fact checking (future)
- [ ] Audio transcription via ElevenLabs (future)
- [ ] Unit tests for scraper service
- [ ] Integration tests for API endpoints

## Next Steps

1. **Implement Fact Checker**: Add LLM integration for credibility analysis
2. **Add Transcriber**: Integrate ElevenLabs for audio transcription
3. **Testing**: Write comprehensive test suite
4. **Rate Limiting**: Implement request rate limiting
5. **Authentication**: Add API key authentication for clients
6. **Monitoring**: Add logging and metrics collection

## Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `SUPADATA_API_KEY` | Your Supadata API key | Yes | - |
| `DEBUG` | Enable debug mode | No | `False` |
| `REQUEST_TIMEOUT` | API request timeout (seconds) | No | `30` |
| `MAX_RETRIES` | Max retry attempts | No | `3` |
| `CORS_ORIGINS` | Allowed CORS origins | No | `["*"]` |

## License

MIT

## Support

For issues or questions, please open an issue on GitHub.
