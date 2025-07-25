# Telegram File Converter Bot

A professional Telegram bot that provides comprehensive file format conversion and processing services for images, PDFs, and videos.

## Features

### Image Processing
- **Format Conversions**: JPG ↔ PNG, JPG ↔ WebP, SVG → PNG
- **Image Compression**: Advanced compression algorithms
- **Quality Optimization**: Intelligent size reduction

### PDF Operations
- **Document Merging**: Combine multiple PDF files
- **Format Conversion**: PDF ↔ Word, PDF ↔ Image
- **Compression**: Reduce file size while maintaining quality
- **Security**: Password protection and removal
- **Page Management**: Add numbers, delete pages, rotate content

### Video Processing
- **Format Conversions**: MP4, MOV, WebM, MKV, TS support
- **GIF Support**: GIF ↔ Video conversions (MP4, WebM)
- **Compression**: Efficient video size reduction
- **Quality Control**: Configurable output settings

## Installation

### Requirements
- Python 3.8+
- Telegram Bot Token from [@BotFather](https://t.me/botfather)

### Setup

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env and add your BOT_TOKEN
   ```

3. **Run the bot**
   ```bash
   python start_bot.py
   ```

4. **Run the bot**
   ```bash
   python bot_main.py
## Architecture

```
fileExtensionsChangerForTelegram/
├── bot_main.py                 # Main bot application
├── start_bot.py               # Production startup script
├── config/                    # Configuration module
├── operations/                # File conversion operations
│   ├── images/               # Image processing
│   ├── pdf/                  # PDF operations
│   └── videos/               # Video processing
├── utils/                    # Utility functions
├── temp/                     # Temporary file storage
├── requirements.txt          # Dependencies
└── .env.example             # Environment template
```

## Configuration

### Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your bot token
BOT_TOKEN=your_telegram_bot_token_here
```

### Dependencies
```bash
pip install -r requirements.txt
```

## Usage

1. Start the bot: Send `/start`
2. Upload any supported file
3. Select conversion operation
4. Download converted file

### Supported Formats

| Type | Input Formats | Output Formats |
|------|---------------|----------------|
| **Images** | JPG, PNG, WebP, SVG | JPG, PNG, WebP (compressed) |
| **Documents** | PDF, Word, Images | PDF, Word, Images |
| **Videos** | MP4, MOV, MKV, WebM, TS, GIF | MP4, MOV, WebM, GIF (compressed) |

## Technical Details

- **File Limit**: 50MB (Telegram API limit)
- **Processing**: Asynchronous with automatic cleanup
- **Storage**: Temporary files auto-deleted after 24 hours
- **Error Handling**: Comprehensive logging and user feedback

## Production Deployment

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with production settings

# Start bot
python start_bot.py
```

## License

MIT License - see LICENSE file for details.