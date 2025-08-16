"""
Production-ready Telegram File Converter Bot for Google Cloud Run
Webhook-based architecture with Flask for optimal performance
"""

import os
import json
import logging
import tempfile
import threading
from flask import Flask, request, jsonify
import requests
from datetime import datetime

# Configure logging for Cloud Run
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import our modules with fallback handling
try:
    from config import (
        BOT_TOKEN, MAX_FILE_SIZE_MB, ERROR_MESSAGES, SUCCESS_MESSAGES,
        SUPPORTED_IMAGE_EXTENSIONS, SUPPORTED_PDF_EXTENSIONS, SUPPORTED_VIDEO_EXTENSIONS
    )
    logger.info("✅ Config module imported successfully")
except ImportError as e:
    logger.error(f"❌ Failed to import config module: {e}")
    # Fallback configuration for deployment
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    MAX_FILE_SIZE_MB = 50
    ERROR_MESSAGES = {'unsupported_file': 'Unsupported file type'}
    SUCCESS_MESSAGES = {'file_received': 'File received successfully'}
    SUPPORTED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.webp']
    SUPPORTED_PDF_EXTENSIONS = ['.pdf']
    SUPPORTED_VIDEO_EXTENSIONS = ['.mp4', '.mov', '.webm']

try:
    from utils import temp_manager
    logger.info("✅ Utils module imported successfully")
except ImportError as e:
    logger.warning(f"⚠️ Utils module not available: {e}")
    # Create a simple temp manager fallback
    class SimpleTempManager:
        def create_temp_file(self, extension="", prefix="temp_"):
            return tempfile.mktemp(suffix=extension, prefix=prefix)
        def get_output_filename(self, original, operation):
            return f"converted_{operation}_{original}"
    temp_manager = SimpleTempManager()

# Import operations with graceful fallback handling
operations_available = {
    'images': False,
    'pdf': False,
    'videos': False
}

try:
    from operations.images import *
    operations_available['images'] = True
    logger.info("✅ Image operations loaded")
except ImportError as e:
    logger.warning(f"⚠️ Image operations not available: {e}")

try:
    from operations.pdf import *
    operations_available['pdf'] = True
    logger.info("✅ PDF operations loaded")
except ImportError as e:
    logger.warning(f"⚠️ PDF operations not available: {e}")

try:
    from operations.videos import *
    operations_available['videos'] = True
    logger.info("✅ Video operations loaded")
except ImportError as e:
    logger.warning(f"⚠️ Video operations not available: {e}")

# Initialize Flask app
app = Flask(__name__)

# Telegram API base URL
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# User sessions for file processing
user_sessions = {}

# UI/UX Constants following enhanced patterns
EMOJIS = {
    'success': '✅',
    'error': '❌', 
    'processing': '⏳',
    'loading': '🔄',
    'fire': '🔥',
    'star': '⭐',
    'rocket': '🚀',
    'magic': '✨'
}

def send_telegram_message(chat_id, text, reply_markup=None, parse_mode='Markdown'):
    """Send message via Telegram API"""
    try:
        payload = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': parse_mode
        }
        
        if reply_markup:
            payload['reply_markup'] = json.dumps(reply_markup)
        
        response = requests.post(f"{TELEGRAM_API_URL}/sendMessage", data=payload)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Failed to send message: {e}")
        return None

def send_telegram_document(chat_id, file_path, caption=None):
    """Send document via Telegram API"""
    try:
        with open(file_path, 'rb') as file:
            files = {'document': file}
            data = {'chat_id': chat_id}
            
            if caption:
                data['caption'] = caption
                data['parse_mode'] = 'Markdown'
            
            response = requests.post(f"{TELEGRAM_API_URL}/sendDocument", files=files, data=data)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"Failed to send document: {e}")
        return None

def get_file_type(file_name):
    """Determine file type based on extension"""
    if not file_name:
        return "unsupported"
    
    ext = os.path.splitext(file_name)[1].lower()
    
    # Enhanced file type detection following #copilot-instructions
    image_extensions = ['.jpg', '.jpeg', '.png', '.webp', '.gif']
    pdf_extensions = ['.pdf']
    video_extensions = ['.mp4', '.mov', '.mkv', '.webm', '.ts']
    
    if ext in image_extensions:
        return "image"
    elif ext in pdf_extensions:
        return "pdf"
    elif ext in video_extensions:
        return "video"
    return "unsupported"

def create_operation_buttons(file_type):
    """Create operation buttons based on file type"""
    buttons = []
    
    if file_type == "image" and operations_available['images']:
        buttons = [
            [{"text": "🎨 Convert JPG to PNG", "callback_data": "convert_jpg_to_png"}],
            [{"text": "🖼️ Convert PNG to JPG", "callback_data": "convert_png_to_jpg"}],
            [{"text": "⚡ Convert to WebP", "callback_data": "convert_to_webp"}],
            [{"text": "🗜️ Compress Image", "callback_data": "compress_image"}]
        ]
    elif file_type == "pdf" and operations_available['pdf']:
        buttons = [
            [{"text": "🖼️ PDF to Images", "callback_data": "convert_pdf_to_images"}],
            [{"text": "📄 Image to PDF", "callback_data": "convert_image_to_pdf"}],
            [{"text": "🗜️ Compress PDF", "callback_data": "compress_pdf"}],
            [{"text": "📝 PDF to Word", "callback_data": "convert_pdf_to_word"}]
        ]
    elif file_type == "video" and operations_available['videos']:
        buttons = [
            [{"text": "🎬 Convert to MP4", "callback_data": "convert_to_mp4"}],
            [{"text": "😂 Convert to GIF", "callback_data": "convert_to_gif"}],
            [{"text": "🌐 Convert to WebM", "callback_data": "convert_to_webm"}],
            [{"text": "🗜️ Compress Video", "callback_data": "compress_video"}]
        ]
    
    if not buttons:
        buttons = [[{"text": "❌ No operations available", "callback_data": "no_ops"}]]
    
    # Add common utility buttons
    buttons.append([{"text": "📊 Bot Stats", "callback_data": "show_stats"}])
    
    return {"inline_keyboard": buttons}

def process_file_conversion(operation, input_path, output_path):
    """Process file conversion based on operation type"""
    try:
        # Enhanced conversion mapping following #copilot-instructions patterns
        if operation == "convert_jpg_to_png" and operations_available['images']:
            return convert_jpg_to_png(input_path, output_path)
        elif operation == "convert_png_to_jpg" and operations_available['images']:
            return convert_png_to_jpg(input_path, output_path)
        elif operation == "compress_image" and operations_available['images']:
            return compress_image(input_path, output_path, quality=60)
        elif operation == "convert_pdf_to_images" and operations_available['pdf']:
            return convert_pdf_to_images(input_path, output_path)
        elif operation == "compress_pdf" and operations_available['pdf']:
            return compress_pdf(input_path, output_path)
        elif operation == "convert_to_mp4" and operations_available['videos']:
            return convert_mov_to_mp4(input_path, output_path)
        elif operation == "convert_to_gif" and operations_available['videos']:
            return convert_mp4_to_gif(input_path, output_path)
        else:
            return "Error: Operation not available or not implemented"
    except Exception as e:
        logger.error(f"Conversion failed: {e}")
        return f"Error: {str(e)}"

@app.route('/webhook', methods=['POST'])
def webhook():
    """Main webhook endpoint for Telegram updates"""
    try:
        update = request.get_json()
        logger.info(f"Received update: {update}")
        
        if not update:
            return jsonify({"status": "error", "message": "No data received"}), 400
        
        # Handle regular messages
        if 'message' in update:
            handle_message(update['message'])
        
        # Handle callback queries (button presses)
        elif 'callback_query' in update:
            handle_callback_query(update['callback_query'])
        
        return jsonify({"status": "ok"}), 200
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

def handle_message(message):
    """Handle incoming Telegram messages"""
    try:
        chat_id = message['chat']['id']
        user_name = message.get('from', {}).get('first_name', 'there')
        
        # Handle /start command
        if message.get('text') == '/start':
            welcome_text = f"""
{EMOJIS['rocket']} *Welcome {user_name}!*

{EMOJIS['magic']} **Professional File Converter Bot**

Upload any file to get started:
{EMOJIS['star']} Images: JPG, PNG, WebP, GIF
{EMOJIS['star']} Documents: PDF files
{EMOJIS['star']} Videos: MP4, MOV, WebM

*Just send me a file and watch the magic happen!* ✨
            """
            send_telegram_message(chat_id, welcome_text)
            return
        
        # Handle file uploads
        if 'document' in message or 'photo' in message or 'video' in message:
            handle_file_upload(message)
            return
        
        # Handle unknown messages
        help_text = f"""
{EMOJIS['magic']} **I'm your file conversion assistant!**

{EMOJIS['star']} Upload any supported file to begin
{EMOJIS['star']} Supported: Images, PDFs, Videos
{EMOJIS['star']} Max size: {MAX_FILE_SIZE_MB}MB

*Just drag and drop your file here!* 📁
        """
        send_telegram_message(chat_id, help_text)
        
    except Exception as e:
        logger.error(f"Message handling error: {e}")

def handle_file_upload(message):
    """Handle file upload and show operation options"""
    try:
        chat_id = message['chat']['id']
        user_id = message['from']['id']
        
        # Extract file information
        file_info = None
        if 'document' in message:
            file_info = message['document']
        elif 'photo' in message:
            file_info = message['photo'][-1]  # Get highest resolution
        elif 'video' in message:
            file_info = message['video']
        
        if not file_info:
            send_telegram_message(chat_id, f"{EMOJIS['error']} No file detected. Please try again.")
            return
        
        file_id = file_info['file_id']
        file_name = file_info.get('file_name', f"file_{file_id}")
        file_size = file_info.get('file_size', 0)
        
        # Validate file size
        if file_size > MAX_FILE_SIZE_MB * 1024 * 1024:
            send_telegram_message(
                chat_id, 
                f"{EMOJIS['error']} File too large! Max size: {MAX_FILE_SIZE_MB}MB"
            )
            return
        
        # Determine file type
        file_type = get_file_type(file_name)
        
        if file_type == "unsupported":
            send_telegram_message(
                chat_id,
                f"{EMOJIS['error']} Unsupported file type. Please send an image, PDF, or video."
            )
            return
        
        # Store file session
        user_sessions[user_id] = {
            'file_id': file_id,
            'file_name': file_name,
            'file_type': file_type,
            'file_size': file_size,
            'chat_id': chat_id
        }
        
        # Send operation options
        size_mb = file_size / (1024 * 1024)
        success_text = f"""
{EMOJIS['success']} *File Received!*

📁 **File:** `{file_name}`
📊 **Type:** {file_type.title()}
📏 **Size:** {size_mb:.1f}MB

*Choose your operation:* {EMOJIS['magic']}
        """
        
        reply_markup = create_operation_buttons(file_type)
        send_telegram_message(chat_id, success_text, reply_markup)
        
    except Exception as e:
        logger.error(f"File upload handling error: {e}")
        send_telegram_message(message['chat']['id'], f"{EMOJIS['error']} Error processing file. Please try again.")

def handle_callback_query(callback_query):
    """Handle button press callbacks"""
    try:
        query_id = callback_query['id']
        user_id = callback_query['from']['id']
        chat_id = callback_query['message']['chat']['id']
        operation = callback_query['data']
        
        # Answer callback query
        requests.post(f"{TELEGRAM_API_URL}/answerCallbackQuery", data={
            'callback_query_id': query_id,
            'text': f"🔄 Processing: {operation.replace('_', ' ').title()}"
        })
        
        # Handle stats request
        if operation == "show_stats":
            stats_text = f"""
📊 **Bot Statistics**

{EMOJIS['rocket']} **Operations Available:**
• Images: {'✅' if operations_available['images'] else '❌'}
• PDFs: {'✅' if operations_available['pdf'] else '❌'} 
• Videos: {'✅' if operations_available['videos'] else '❌'}

{EMOJIS['star']} **Server Status:** Healthy
{EMOJIS['fire']} **Deployment:** Google Cloud Run
            """
            send_telegram_message(chat_id, stats_text)
            return
        
        # Check if user has uploaded a file
        if user_id not in user_sessions:
            send_telegram_message(chat_id, f"{EMOJIS['error']} Please upload a file first!")
            return
        
        session = user_sessions[user_id]
        
        # Send processing message
        processing_text = f"""
{EMOJIS['processing']} **Processing Your File...**

📁 **File:** `{session['file_name']}`
🎯 **Operation:** {operation.replace('_', ' ').title()}

*Please wait...* ⏳
        """
        
        send_telegram_message(chat_id, processing_text)
        
        # Download file from Telegram
        file_response = requests.get(f"{TELEGRAM_API_URL}/getFile?file_id={session['file_id']}")
        file_data = file_response.json()
        
        if not file_data.get('ok'):
            send_telegram_message(chat_id, f"{EMOJIS['error']} Failed to download file.")
            return
        
        file_path = file_data['result']['file_path']
        download_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
        
        # Create temporary files
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(session['file_name'])[1]) as input_file:
            input_path = input_file.name
            
            # Download file content
            file_content = requests.get(download_url).content
            input_file.write(file_content)
        
        # Create output file path
        output_ext = ".png" if "png" in operation else ".jpg" if "jpg" in operation else ".pdf" if "pdf" in operation else ".mp4"
        output_path = input_path.replace(os.path.splitext(input_path)[1], output_ext)
        
        # Process conversion
        result = process_file_conversion(operation, input_path, output_path)
        
        if "Error" in result:
            send_telegram_message(chat_id, f"{EMOJIS['error']} {result}")
        else:
            # Send converted file
            if os.path.exists(output_path):
                output_filename = f"converted_{operation}_{os.path.basename(session['file_name'])}"
                output_filename = output_filename.replace(os.path.splitext(output_filename)[1], output_ext)
                
                success_caption = f"""
{EMOJIS['success']} **Conversion Complete!**

🎯 **Operation:** {operation.replace('_', ' ').title()}
📁 **Result:** `{output_filename}`

{EMOJIS['fire']} *Ready for download!*
                """
                
                send_telegram_document(chat_id, output_path, success_caption)
            else:
                send_telegram_message(chat_id, f"{EMOJIS['error']} Conversion completed but file not found.")
        
        # Cleanup temporary files
        try:
            if os.path.exists(input_path):
                os.unlink(input_path)
            if os.path.exists(output_path):
                os.unlink(output_path)
        except Exception as e:
            logger.warning(f"Cleanup failed: {e}")
        
        # Remove user session
        if user_id in user_sessions:
            del user_sessions[user_id]
        
    except Exception as e:
        logger.error(f"Callback query handling error: {e}")
        send_telegram_message(callback_query['message']['chat']['id'], f"{EMOJIS['error']} Processing failed. Please try again.")

@app.route('/health')
def health_check():
    """Health check endpoint for Cloud Run"""
    try:
        # Basic health check - just return OK if server is running
        return jsonify({
            "status": "healthy",
            "service": "telegram-file-converter",
            "operations_available": operations_available,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/ready')
def readiness_check():
    """Readiness check endpoint - more thorough validation"""
    try:
        # Check bot token availability
        if not BOT_TOKEN:
            return jsonify({"status": "error", "message": "Bot token not configured"}), 500
        
        # Test Telegram API connectivity
        response = requests.get(f"{TELEGRAM_API_URL}/getMe", timeout=5)
        bot_info = response.json()
        
        if not bot_info.get('ok'):
            return jsonify({"status": "error", "message": "Telegram API unreachable"}), 500
        
        return jsonify({
            "status": "ready",
            "bot_username": bot_info['result'].get('username'),
            "operations_available": operations_available,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/set_webhook', methods=['POST'])
def set_webhook():
    """Endpoint to set Telegram webhook"""
    try:
        webhook_url = request.json.get('webhook_url')
        if not webhook_url:
            return jsonify({"status": "error", "message": "webhook_url required"}), 400
        
        response = requests.post(f"{TELEGRAM_API_URL}/setWebhook", data={
            'url': webhook_url
        })
        
        result = response.json()
        return jsonify(result), 200 if result.get('ok') else 400
        
    except Exception as e:
        logger.error(f"Set webhook failed: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/')
def root():
    """Root endpoint with service information"""
    return jsonify({
        "service": "Telegram File Converter Bot",
        "status": "running",
        "version": "3.0.0-webhook",
        "deployment": "Google Cloud Run",
        "features": [
            "Webhook-based processing",
            "Image format conversions", 
            "PDF operations",
            "Video/GIF processing",
            "Professional UI/UX"
        ],
        "operations_available": operations_available
    })

# Initialize the application
def initialize_app():
    """Initialize the application and validate configuration"""
    logger.info(f"🚀 Initializing Telegram File Converter Bot")
    logger.info(f"📊 Operations available: {operations_available}")
    logger.info(f"🔑 Bot token configured: {'✅' if BOT_TOKEN else '❌'}")
    
    # Validate BOT_TOKEN
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN environment variable is required")
        raise ValueError("BOT_TOKEN is required")
    
    try:
        # Quick bot connectivity test
        logger.info("🔍 Testing bot connectivity...")
        test_response = requests.get(f"{TELEGRAM_API_URL}/getMe", timeout=10)
        if test_response.status_code == 200:
            bot_info = test_response.json()
            if bot_info.get('ok'):
                logger.info(f"✅ Bot connected: @{bot_info.get('result', {}).get('username', 'unknown')}")
            else:
                logger.error(f"❌ Bot API error: {bot_info}")
                raise ValueError("Bot API validation failed")
        else:
            logger.error(f"❌ Bot API test failed: {test_response.status_code}")
            raise ValueError("Bot API connectivity failed")
            
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Bot connectivity test failed: {e}")
        raise ValueError(f"Bot connectivity failed: {e}")
    
    logger.info("✅ Application initialized successfully")

# Initialize when module is loaded (for gunicorn)
try:
    initialize_app()
except Exception as e:
    logger.error(f"❌ Application initialization failed: {e}")
    # Don't exit here for gunicorn compatibility

if __name__ == "__main__":
    # Direct execution (development mode)
    port = int(os.environ.get('PORT', 8080))
    logger.info(f"🌐 Starting Flask development server on 0.0.0.0:{port}")
    
    app.run(
        host='0.0.0.0', 
        port=port, 
        debug=False,
        threaded=True,
        use_reloader=False
    )
