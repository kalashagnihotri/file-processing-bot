# Project Structure & Organization

## Directory Layout

```
telegram-file-converter/
├── main.py                     # Production webhook-based entry point
├── bot_main.py                 # Development polling-based entry point  
├── bot_cloud_run.py           # Enhanced Cloud Run version
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Container configuration
├── cloudbuild.yaml           # CI/CD pipeline configuration
├── cloud-run-service.yaml    # Cloud Run service definition
├── README.md                 # Project documentation
├── .dockerignore             # Docker build exclusions
├── .gitignore               # Git exclusions
│
├── config/                   # Configuration module
│   ├── __init__.py
│   └── settings.py          # Bot settings and constants
│
├── utils/                   # Utility functions
│   ├── __init__.py
│   ├── file_manager.py      # Temporary file management
│   ├── logging_config.py    # Logging configuration
│   └── telegram_utils.py    # Telegram API helpers
│
└── operations/              # File processing operations
    ├── __init__.py
    ├── images/              # Image processing operations
    │   ├── __init__.py
    │   ├── jpg_to_png.py
    │   ├── png_to_jpg.py
    │   ├── jpg_to_webp.py
    │   ├── webp_to_jpg.py
    │   ├── svg_to_png.py
    │   └── compress_image.py
    ├── pdf/                 # PDF operations
    │   ├── __init__.py
    │   ├── merge_pdfs.py
    │   ├── pdf_to_image.py
    │   ├── image_to_pdf.py
    │   ├── compress_pdf.py
    │   ├── lock_pdf.py
    │   ├── unlock_pdf.py
    │   ├── add_page_numbers.py
    │   ├── delete_pdf_page.py
    │   ├── rotate_pdf.py
    │   └── pdf_to_word.py
    └── videos/              # Video processing operations
        ├── __init__.py
        ├── mp4_to_mov.py
        ├── mov_to_mp4.py
        ├── mkv_to_mp4.py
        ├── ts_to_mp4.py
        ├── mp4_to_webm.py
        ├── webm_to_mp4.py
        ├── video_to_gif.py
        ├── gif_to_video.py
        └── compress_video.py
```

## Architecture Patterns

### Entry Points
- **main.py**: Production webhook mode for Cloud Run deployment
- **bot_main.py**: Development polling mode for local testing
- **bot_cloud_run.py**: Enhanced version with advanced features

### Configuration Management
- Centralized settings in `config/settings.py`
- Environment variables loaded via python-dotenv
- Separate configurations for development/production

### File Processing Architecture
- Modular operations organized by file type (images/pdf/videos)
- Each operation is a standalone function with consistent interface
- Graceful fallback when optional dependencies are missing
- Temporary file management with automatic cleanup

### Error Handling Strategy
- Comprehensive try-catch blocks with logging
- User-friendly error messages with actionable guidance
- Graceful degradation when features are unavailable
- Health check endpoints for monitoring

### Code Organization Principles
- **Single Responsibility**: Each module handles one concern
- **Dependency Injection**: Operations receive file paths as parameters
- **Fail-Safe Design**: Missing dependencies don't crash the bot
- **Clean Imports**: Conditional imports with fallback handling

### Naming Conventions
- **Files**: snake_case for Python files
- **Functions**: snake_case with descriptive names
- **Classes**: PascalCase (e.g., TempFileManager)
- **Constants**: UPPER_SNAKE_CASE in settings.py
- **Operations**: Verb-noun pattern (e.g., convert_jpg_to_png)

### Development Guidelines
- All operations should accept (input_path, output_path) parameters
- Return success/error messages as strings
- Use temp_manager for file lifecycle management
- Import operations conditionally to handle missing dependencies
- Follow the established error message patterns from config/settings.py