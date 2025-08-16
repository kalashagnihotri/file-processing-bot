# Technology Stack & Build System

## Core Technologies

### Backend Framework
- **Python 3.10+**: Primary programming language
- **Flask**: Web framework for webhook handling and health checks
- **pyTelegramBotAPI**: Telegram bot API integration
- **python-dotenv**: Environment variable management

### File Processing Libraries
- **Pillow**: Image processing and format conversions
- **PyPDF2**: PDF manipulation and operations
- **MoviePy**: Video processing and conversions
- **CairoSVG**: SVG to raster format conversion
- **pdf2image**: PDF to image conversion
- **python-docx**: Word document handling

### Cloud & Deployment
- **Google Cloud Run**: Serverless container platform
- **Docker**: Containerization
- **Google Cloud Build**: CI/CD pipeline
- **Google Container Registry**: Image storage

### Development Tools
- **FFmpeg**: Video/audio processing backend
- **Tesseract OCR**: Text recognition capabilities
- **Poppler**: PDF rendering utilities

## Build & Deployment Commands

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run locally (polling mode)
python bot_main.py

# Run webhook mode locally
python main.py
```

### Docker Build
```bash
# Build container
docker build -t telegram-file-converter .

# Run container locally
docker run -p 8080:8080 --env-file .env telegram-file-converter
```

### Cloud Deployment
```bash
# Deploy via Cloud Build
gcloud builds submit --config cloudbuild.yaml

# Manual deployment
gcloud run deploy telegram-file-converter \
  --source . \
  --region asia-south1 \
  --allow-unauthenticated
```

### Testing & Health Checks
```bash
# Health check endpoint
curl http://localhost:8080/health

# Bot statistics
curl http://localhost:8080/stats
```

## Environment Configuration
- `BOT_TOKEN`: Telegram bot token (required)
- `ENVIRONMENT`: production/development
- `PORT`: Server port (default: 8080)

## Performance Considerations
- **Memory**: 2GB allocated for Cloud Run
- **CPU**: 2 vCPU with boost enabled
- **Timeout**: 600 seconds for large file processing
- **Concurrency**: Up to 10 instances for scaling