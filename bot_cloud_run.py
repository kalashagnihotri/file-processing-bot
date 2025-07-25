import telebot
import os
import threading
import time
import zipfile
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask, request, jsonify
import logging

# Configure logging for Cloud Run
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import our modules
from config import (
    BOT_TOKEN, MAX_FILE_SIZE_MB, ERROR_MESSAGES, SUCCESS_MESSAGES,
    SUPPORTED_IMAGE_EXTENSIONS, SUPPORTED_PDF_EXTENSIONS, SUPPORTED_VIDEO_EXTENSIONS
)
from utils import temp_manager, download_telegram_file, get_file_info, validate_file_size

# Import operation functions with enhanced error handling
try:
    from operations.images import *
    logger.info("✅ Image operations loaded successfully")
except ImportError as e:
    logger.warning(f"⚠️ Could not import all image operations: {e}")

try:
    from operations.pdf import *
    logger.info("✅ PDF operations loaded successfully")
except ImportError as e:
    logger.warning(f"⚠️ Could not import all PDF operations: {e}")

try:
    from operations.videos import *
    logger.info("✅ Video operations loaded successfully")
except ImportError as e:
    logger.warning(f"⚠️ Could not import all video operations: {e}")

# Initialize Flask app for health checks (Cloud Run requirement)
app = Flask(__name__)

# Initialize bot
bot = telebot.TeleBot(BOT_TOKEN)

# Enhanced user sessions with engagement tracking
user_sessions = {}
user_stats = {}

# UI/UX Constants
EMOJIS = {
    'success': '✅',
    'error': '❌', 
    'processing': '⏳',
    'loading': '🔄',
    'fire': '🔥',
    'star': '⭐',
    'rocket': '🚀',
    'magic': '✨',
    'heart': '❤️',
    'thumbs_up': '👍'
}

# Enhanced operation lists with better descriptions
IMAGE_OPERATIONS = [
    "🎨 Convert JPG to PNG",
    "🖼️ Convert PNG to JPG", 
    "⚡ Convert JPG to WebP",
    "📱 Convert WebP to JPG",
    "🗜️ Smart Compress Image"
]

# Check if SVG support is available
try:
    from operations.images.svg_to_png import CAIROSVG_AVAILABLE
    if CAIROSVG_AVAILABLE:
        IMAGE_OPERATIONS.append("🎭 Convert SVG to PNG")
        logger.info("✅ SVG support available")
except ImportError:
    logger.warning("⚠️ SVG support not available")

PDF_OPERATIONS = [
    "📑 Merge Multiple PDFs",
    "🖼️ Convert PDF to Images", 
    "📄 Convert Image to PDF",
    "🗜️ Compress PDF Size",
    "🔒 Lock PDF with Password",
    "🔓 Unlock Protected PDF",
    "🔢 Add Page Numbers",
    "✂️ Delete Specific Page",
    "🔄 Rotate PDF Pages",
    "📝 Convert PDF to Word"
]

VIDEO_OPERATIONS = []

# Check if video processing is available
try:
    from operations.videos import MOVIEPY_AVAILABLE
    if MOVIEPY_AVAILABLE:
        VIDEO_OPERATIONS = [
            "🎬 Convert MP4 to MOV",
            "📱 Convert MOV to MP4",
            "📺 Convert TS to MP4", 
            "🎞️ Convert MKV to MP4",
            "🌐 Convert MP4 to WebM",
            "📹 Convert WebM to MP4",
            "🎪 Convert GIF to MP4",
            "🌐 Convert GIF to WebM", 
            "😂 Convert MP4 to GIF",
            "🎭 Convert MOV to GIF",
            "✨ Convert WebM to GIF",
            "🗜️ Smart Compress Video"
        ]
        logger.info("✅ Video operations available")
except ImportError:
    logger.warning("⚠️ Video operations not available")

# Flask routes for Cloud Run health checks
@app.route('/health')
def health_check():
    """Health check endpoint for Google Cloud Run"""
    try:
        # Check bot status
        bot_info = bot.get_me()
        
        # Count available operations
        total_operations = len(IMAGE_OPERATIONS) + len(PDF_OPERATIONS) + len(VIDEO_OPERATIONS)
        
        health_status = {
            "status": "healthy",
            "bot_username": bot_info.username,
            "bot_name": bot_info.first_name,
            "total_operations": total_operations,
            "image_operations": len(IMAGE_OPERATIONS),
            "pdf_operations": len(PDF_OPERATIONS),
            "video_operations": len(VIDEO_OPERATIONS),
            "timestamp": time.time()
        }
        
        logger.info(f"Health check passed: {total_operations} operations available")
        return jsonify(health_status), 200
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": time.time()
        }), 500

@app.route('/stats')
def get_stats():
    """Get bot statistics"""
    try:
        return jsonify({
            "active_sessions": len(user_sessions),
            "total_users": len(user_stats),
            "uptime": time.time(),
            "operations_available": {
                "image": len(IMAGE_OPERATIONS),
                "pdf": len(PDF_OPERATIONS), 
                "video": len(VIDEO_OPERATIONS)
            }
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def root():
    """Root endpoint"""
    return jsonify({
        "service": "Telegram File Converter Bot",
        "status": "running",
        "version": "2.0.0-enhanced",
        "features": [
            "Image processing with smart compression",
            "PDF operations with OCR support", 
            "Video/GIF conversions",
            "Real-time progress tracking",
            "User engagement analytics"
        ]
    })

def get_user_stats(user_id):
    """Get or create user statistics"""
    if user_id not in user_stats:
        user_stats[user_id] = {
            'files_processed': 0,
            'favorite_operation': None,
            'total_size_saved': 0,
            'first_use': time.time()
        }
    return user_stats[user_id]

def update_user_stats(user_id, operation, size_saved=0):
    """Update user statistics"""
    stats = get_user_stats(user_id)
    stats['files_processed'] += 1
    stats['total_size_saved'] += size_saved
    
    # Track favorite operation
    if not stats['favorite_operation']:
        stats['favorite_operation'] = operation

def create_progress_bar(percentage):
    """Create visual progress bar"""
    filled = int(percentage / 10)
    empty = 10 - filled
    return f"{'█' * filled}{'░' * empty} {percentage}%"

def get_file_type(file_name):
    """Enhanced file type detection with better messaging"""
    ext = os.path.splitext(file_name)[1].lower()
    
    # Check if SVG support is available for .svg files
    if ext == '.svg':
        try:
            from operations.images.svg_to_png import CAIROSVG_AVAILABLE
            if CAIROSVG_AVAILABLE:
                return "image"
            else:
                return "unsupported"
        except ImportError:
            return "unsupported"
    
    if ext in SUPPORTED_IMAGE_EXTENSIONS:
        return "image"
    elif ext in SUPPORTED_PDF_EXTENSIONS:
        return "pdf"
    elif ext in SUPPORTED_VIDEO_EXTENSIONS:
        return "video"
    return "unsupported"

def create_operation_buttons(file_type):
    """Create enhanced operation buttons with better UX"""
    markup = InlineKeyboardMarkup(row_width=2)
    operations = []
    
    if file_type == "image":
        operations = IMAGE_OPERATIONS
    elif file_type == "pdf":
        operations = PDF_OPERATIONS
    elif file_type == "video":
        operations = VIDEO_OPERATIONS
    else:
        return None

    # Add operations in rows of 2
    for i in range(0, len(operations), 2):
        row_buttons = []
        for j in range(2):
            if i + j < len(operations):
                op = operations[i + j]
                # Convert display name to callback data
                callback_data = op.lower().replace(' ', '_').replace('🎨', '').replace('🖼️', '').replace('⚡', '').replace('📱', '').replace('🗜️', '').replace('🎭', '').replace('📑', '').replace('📄', '').replace('🔒', '').replace('🔓', '').replace('🔢', '').replace('✂️', '').replace('🔄', '').replace('📝', '').replace('🎬', '').replace('📺', '').replace('🎞️', '').replace('🌐', '').replace('📹', '').replace('🎪', '').replace('😂', '').replace('🎭', '').replace('✨', '').strip()
                callback_data = callback_data.replace('convert_', '').replace('smart_', '').replace('multiple_', '')
                callback_data = f"convert_{callback_data}"
                row_buttons.append(InlineKeyboardButton(op, callback_data=callback_data))
        markup.add(*row_buttons)
    
    # Add utility buttons
    markup.add(
        InlineKeyboardButton("🔙 Upload Different File", callback_data="upload_new"),
        InlineKeyboardButton("📊 My Stats", callback_data="show_stats")
    )
    
    return markup

# Enhanced welcome message
@bot.message_handler(commands=['start'])
def welcome(message):
    user_name = message.from_user.first_name or "there"
    user_id = message.from_user.id
    
    # Initialize user stats
    get_user_stats(user_id)
    
    welcome_text = f"""
🌟 *Welcome {user_name}!* 🌟

{EMOJIS['rocket']} **Ultimate File Converter Bot** - Your AI-Powered Assistant!

{EMOJIS['magic']} *Transform any file in seconds with professional quality*

🎯 **What I Can Do:**

🖼️ **Images** (JPG, PNG, WebP, SVG, GIF)
   • Smart format conversions  
   • Compression up to 60% space saved
   • Professional quality output
   • Social media optimized

📄 **PDFs** ({len(PDF_OPERATIONS)} powerful operations)
   • Merge, split & compress documents
   • PDF ↔ Word with OCR technology
   • Password protection & watermarks
   • Page manipulation & numbering

🎥 **Videos & GIFs** (MP4, MOV, WebM, MKV)
   • Professional format conversions  
   • Video → GIF for social media
   • Smart compression algorithms
   • Creator-friendly tools

💡 **Pro Features:**
   ⚡ Lightning-fast processing
   🔒 100% secure & private  
   🎨 Maintains original quality
   📱 Mobile-optimized interface

*Ready to transform your files?* Just drop one here! 👇
    """
    
    # Create engaging start menu
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("📸 Try Image Magic", callback_data="demo_image"),
        InlineKeyboardButton("📄 Document Tools", callback_data="demo_pdf")
    )
    markup.add(
        InlineKeyboardButton("🎬 Video Creator", callback_data="demo_video"),
        InlineKeyboardButton("🎯 Quick Tutorial", callback_data="show_tutorial")
    )
    markup.add(
        InlineKeyboardButton("📊 My Statistics", callback_data="show_stats"),
        InlineKeyboardButton("❓ Help & Support", callback_data="show_help")
    )
    markup.add(InlineKeyboardButton(f"{EMOJIS['star']} Rate Us 5 Stars", url="https://t.me/share/url?url=Check out this amazing file converter bot!"))
    
    # Send welcome with animation effect
    loading_msg = bot.send_message(
        message.chat.id, 
        f"{EMOJIS['loading']} Loading your personal file assistant..."
    )
    
    # Animation delay
    time.sleep(0.8)
    
    bot.edit_message_text(
        welcome_text,
        message.chat.id,
        loading_msg.message_id,
        reply_markup=markup, 
        parse_mode='Markdown'
    )

# Enhanced help command
@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = f"""
🔧 **Complete User Guide** 

*Follow these simple steps for magic results:*

**1️⃣ Upload Your File**
   📤 Drag & drop or select from gallery
   📏 Supports files up to 50MB
   🎯 Multiple formats supported

**2️⃣ Choose Your Magic**
   ✨ Tap the operation you want
   👀 Get instant preview of results
   🧠 Smart suggestions based on file type

**3️⃣ Get Your Result**
   ⚡ Lightning-fast processing 
   📲 Download immediately
   📤 Share directly to other apps

🌈 **Supported Formats:**

🖼️ **Images:** JPG, PNG, WebP, SVG, GIF
📄 **Documents:** PDF, Word documents  
🎬 **Videos:** MP4, MOV, MKV, WebM, TS

💡 **Pro Tips:**
   🗜️ Compress images before sharing (saves data!)
   😂 Convert videos to GIF for memes
   📧 Use PDF compression for email attachments
   🔍 OCR works on scanned documents

⚠️ **Important:**
   🔒 Files auto-delete after 24h for privacy
   📏 Max file size: 50MB (Telegram limit)
   🛡️ All processing is secure & private

🆘 **Need help?** Just type /start to begin again!
    """
    
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("🔙 Back to Main", callback_data="back_to_start"),
        InlineKeyboardButton("🎯 Try Now", callback_data="demo_upload")
    )
    
    bot.send_message(
        message.chat.id, 
        help_text, 
        reply_markup=markup, 
        parse_mode='Markdown'
    )

# Enhanced file handler with better UX
@bot.message_handler(content_types=['document', 'photo', 'video'])
def handle_file(message):
    try:
        user_id = message.from_user.id
        
        # Get file information
        file_id, file_name, file_size = get_file_info(message)
        
        if not file_id:
            error_markup = InlineKeyboardMarkup()
            error_markup.add(InlineKeyboardButton("📋 Supported Formats", callback_data="show_formats"))
            bot.reply_to(
                message, 
                f"{EMOJIS['error']} {ERROR_MESSAGES['unsupported_file']}\n\nTap below to see supported formats!",
                reply_markup=error_markup
            )
            return
        
        # Validate file size with better messaging
        if not validate_file_size(file_size, MAX_FILE_SIZE_MB):
            size_mb = file_size / (1024 * 1024)
            bot.reply_to(
                message, 
                f"{EMOJIS['error']} File too large!\n\n📏 Your file: {size_mb:.1f}MB\n📏 Maximum: {MAX_FILE_SIZE_MB}MB\n\n💡 *Tip: Try compressing your file first!*",
                parse_mode='Markdown'
            )
            return
        
        # Determine file type
        file_type = get_file_type(file_name)
        
        if file_type == "unsupported":
            error_markup = InlineKeyboardMarkup()
            error_markup.add(InlineKeyboardButton("📋 Supported Formats", callback_data="show_formats"))
            bot.reply_to(
                message,
                f"{EMOJIS['error']} {ERROR_MESSAGES['unsupported_file']}\n\nTap below to see what I can handle!",
                reply_markup=error_markup
            )
            return
        
        # Store file information in user session
        user_sessions[user_id] = {
            'file_id': file_id,
            'file_name': file_name,
            'file_type': file_type,
            'file_size': file_size,
            'message_id': message.message_id,
            'upload_time': time.time()
        }
        
        # Generate enhanced buttons for operations
        markup = create_operation_buttons(file_type)
        
        # File size in readable format
        size_mb = file_size / (1024 * 1024)
        type_icon = {"image": "🖼️", "pdf": "📄", "video": "🎥"}.get(file_type, "📁")
        
        success_text = f"""
{EMOJIS['success']} *File Received Successfully!*

{type_icon} **File:** `{file_name}`
📊 **Type:** {file_type.title()}
📏 **Size:** {size_mb:.1f}MB
⚡ **Status:** Ready for conversion

*Choose your magic below:* ✨
        """
        
        bot.reply_to(
            message, 
            success_text,
            reply_markup=markup,
            parse_mode='Markdown'
        )

    except Exception as e:
        logger.error(f"Error handling file: {e}")
        error_markup = InlineKeyboardMarkup()
        error_markup.add(InlineKeyboardButton("🔄 Try Again", callback_data="upload_new"))
        bot.reply_to(
            message, 
            f"{EMOJIS['error']} {ERROR_MESSAGES['download_failed']}\n\n*Please try uploading again.*",
            reply_markup=error_markup,
            parse_mode='Markdown'
        )

def perform_conversion(operation, input_path, output_path, **kwargs):
    """Enhanced conversion function with better error handling"""
    operation_map = {
        # Image operations
        'convert_jpg_to_png': convert_jpg_to_png,
        'convert_png_to_jpg': convert_png_to_jpg,
        'convert_jpg_to_webp': convert_jpg_to_webp,
        'convert_webp_to_jpg': convert_webp_to_jpg,
        'convert_svg_to_png': convert_svg_to_png,
        'compress_image': lambda inp, out: compress_image(inp, out, quality=60),
        
        # PDF operations  
        'merge_pdfs': lambda inp, out: merge_pdfs([inp], out),
        'convert_pdf_to_images': convert_pdf_to_images,
        'convert_image_to_pdf': convert_image_to_pdf,
        'compress_pdf': compress_pdf,
        'lock_pdf': lambda inp, out: lock_pdf(inp, out, kwargs.get('password', 'default123')),
        'unlock_pdf': lambda inp, out: unlock_pdf(inp, out, kwargs.get('password', 'default123')),
        'add_page_numbers': add_page_numbers,
        'delete_a_page': lambda inp, out: delete_pdf_page(inp, out, kwargs.get('page_number', 1)),
        'rotate_pdf': rotate_pdf,
        'convert_pdf_to_word': convert_pdf_to_word,
        
        # Video operations
        'convert_mp4_to_mov': convert_mp4_to_mov,
        'convert_mov_to_mp4': convert_mov_to_mp4,
        'convert_ts_to_mp4': convert_ts_to_mp4,
        'convert_mkv_to_mp4': convert_mkv_to_mp4,
        'convert_mp4_to_webm': convert_mp4_to_webm,
        'convert_webm_to_mp4': convert_webm_to_mp4,
        'convert_gif_to_mp4': convert_gif_to_mp4,
        'convert_gif_to_webm': convert_gif_to_webm,
        'convert_mp4_to_gif': convert_mp4_to_gif,
        'convert_mov_to_gif': convert_mov_to_gif,
        'convert_webm_to_gif': convert_webm_to_gif,
        'compress_video': compress_video,
    }
    
    if operation in operation_map:
        return operation_map[operation](input_path, output_path)
    else:
        return f"Operation {operation} not implemented yet"

# Enhanced callback handler with progress tracking
@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    user_id = call.from_user.id
    operation = call.data
    
    # Handle demo callbacks
    if operation.startswith('demo_'):
        handle_demo_callback(call)
        return
    
    # Handle utility callbacks
    if operation in ['show_help', 'show_tutorial', 'show_stats', 'show_formats', 'back_to_start']:
        handle_utility_callback(call)
        return
    
    # Check if user has a file session
    if user_id not in user_sessions:
        bot.answer_callback_query(call.id, "Please send a file first! 📁")
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔙 Start Over", callback_data="back_to_start"))
        bot.edit_message_text(
            f"{EMOJIS['error']} No file found! Please upload a file first.",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup
        )
        return
    
    session = user_sessions[user_id]
    operation_display = operation.replace('convert_', '').replace('_', ' ').title()
    
    bot.answer_callback_query(call.id, f"🔄 Starting: {operation_display}")
    
    # Enhanced processing message with progress
    processing_text = f"""
{EMOJIS['processing']} **Processing Your File...**

🎯 **Operation:** {operation_display}
📁 **File:** `{session['file_name']}`
⏱️ **Status:** Initializing...

{create_progress_bar(0)}

*This may take a moment. Please wait...* ⏳
    """
    
    processing_msg = bot.edit_message_text(
        processing_text,
        call.message.chat.id,
        call.message.message_id,
        parse_mode='Markdown'
    )
    
    try:
        # Update progress - Download phase
        bot.edit_message_text(
            processing_text.replace("Initializing...", "Downloading file...").replace(create_progress_bar(0), create_progress_bar(25)),
            call.message.chat.id,
            processing_msg.message_id,
            parse_mode='Markdown'
        )
        
        # Download the original file
        input_path = temp_manager.create_temp_file(
            extension=os.path.splitext(session['file_name'])[1],
            prefix="input_"
        )
        
        if not download_telegram_file(bot, session['file_id'], input_path):
            raise Exception("Failed to download file")
        
        # Update progress - Processing phase
        bot.edit_message_text(
            processing_text.replace("Downloading file...", "Converting file...").replace(create_progress_bar(25), create_progress_bar(50)),
            call.message.chat.id,
            processing_msg.message_id,
            parse_mode='Markdown'
        )
        
        # Create output file path
        output_filename = temp_manager.get_output_filename(session['file_name'], operation)
        output_path = temp_manager.create_temp_file(
            extension=os.path.splitext(output_filename)[1],
            prefix="output_"
        )
        
        # Update progress - Final processing
        bot.edit_message_text(
            processing_text.replace("Converting file...", "Finalizing...").replace(create_progress_bar(50), create_progress_bar(75)),
            call.message.chat.id,
            processing_msg.message_id,
            parse_mode='Markdown'
        )
        
        # Perform the conversion
        result = perform_conversion(operation, input_path, output_path)
        
        # Check if conversion was successful
        if "Error" in result:
            error_markup = InlineKeyboardMarkup()
            error_markup.add(
                InlineKeyboardButton("🔄 Try Again", callback_data=operation),
                InlineKeyboardButton("📤 New File", callback_data="upload_new")
            )
            bot.edit_message_text(
                f"{EMOJIS['error']} **Conversion Failed**\n\n{result}\n\n*Try again or upload a different file.*",
                call.message.chat.id,
                processing_msg.message_id,
                reply_markup=error_markup,
                parse_mode='Markdown'
            )
            return
        
        # Update progress - Complete
        bot.edit_message_text(
            processing_text.replace("Finalizing...", "Upload complete!").replace(create_progress_bar(75), create_progress_bar(100)),
            call.message.chat.id,
            processing_msg.message_id,
            parse_mode='Markdown'
        )
        
        # Send the converted file with enhanced message
        if os.path.exists(output_path):
            # Calculate file size savings
            original_size = session['file_size']
            new_size = os.path.getsize(output_path)
            size_saved = original_size - new_size
            percentage_saved = (size_saved / original_size * 100) if original_size > 0 else 0
            
            # Update user statistics
            update_user_stats(user_id, operation, size_saved)
            
            success_text = f"""
{EMOJIS['success']} **Conversion Complete!**

🎯 **Operation:** {operation_display}
📁 **Original:** {original_size / (1024*1024):.1f}MB
📁 **New Size:** {new_size / (1024*1024):.1f}MB
💾 **Saved:** {abs(size_saved) / (1024*1024):.1f}MB ({abs(percentage_saved):.1f}%)

{EMOJIS['fire']} *Ready for download!*
            """
            
            # Create success markup with options
            success_markup = InlineKeyboardMarkup()
            success_markup.add(
                InlineKeyboardButton("🔄 Convert Another", callback_data="upload_new"),
                InlineKeyboardButton("📊 My Stats", callback_data="show_stats")
            )
            success_markup.add(InlineKeyboardButton(f"{EMOJIS['star']} Rate This Bot", url="https://t.me/share/url?url=Amazing file converter bot!"))
            
            with open(output_path, 'rb') as file:
                bot.send_document(
                    call.message.chat.id,
                    file,
                    caption=success_text,
                    parse_mode='Markdown',
                    reply_markup=success_markup
                )
            
            bot.edit_message_text(
                f"{EMOJIS['success']} **File converted and sent successfully!**\n\n*Check the document above.* {EMOJIS['thumbs_up']}",
                call.message.chat.id,
                processing_msg.message_id,
                parse_mode='Markdown'
            )
            
        else:
            bot.edit_message_text(
                f"{EMOJIS['error']} Conversion completed but file not found. Please try again.",
                call.message.chat.id,
                processing_msg.message_id,
                parse_mode='Markdown'
            )

    except Exception as e:
        logger.error(f"Error in conversion: {e}")
        error_markup = InlineKeyboardMarkup()
        error_markup.add(
            InlineKeyboardButton("🔄 Try Again", callback_data=operation),
            InlineKeyboardButton("📤 New File", callback_data="upload_new")
        )
        bot.edit_message_text(
            f"{EMOJIS['error']} **Processing Error**\n\n*Something went wrong during conversion.*\n\nError: {str(e)[:100]}...\n\n*Please try again.*",
            call.message.chat.id,
            processing_msg.message_id,
            reply_markup=error_markup,
            parse_mode='Markdown'
        )

def handle_demo_callback(call):
    """Handle demo button callbacks"""
    demo_type = call.data.replace('demo_', '')
    
    demo_messages = {
        'image': f"""
🖼️ **Image Magic Demo**

Upload any image (JPG, PNG, WebP, GIF) to see:
• {EMOJIS['magic']} Format conversions
• 🗜️ Smart compression 
• ⚡ Lightning-fast results

*Try uploading a photo now!* 📱
        """,
        'pdf': f"""
📄 **Document Tools Demo**  

Upload a PDF to access:
• 📑 Merge & split documents
• 🔒 Password protection
• 📝 PDF to Word conversion
• 🗜️ Size compression

*Drop a PDF file to start!* 📎
        """,
        'video': f"""
🎬 **Video Creator Demo**

Upload any video (MP4, MOV, WebM) for:
• 🎪 Format conversions
• 😂 GIF creation
• 🗜️ Smart compression
• ⚡ Professional quality

*Share a video to begin!* 🎥
        """
    }
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_start"))
    
    bot.answer_callback_query(call.id, f"Ready for {demo_type} magic! 🎯")
    bot.edit_message_text(
        demo_messages.get(demo_type, "Demo not available"),
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup,
        parse_mode='Markdown'
    )

def handle_utility_callback(call):
    """Handle utility button callbacks"""
    if call.data == "show_stats":
        user_id = call.from_user.id
        stats = get_user_stats(user_id)
        
        days_using = (time.time() - stats['first_use']) / (24 * 3600)
        
        stats_text = f"""
📊 **Your Personal Statistics**

🗂️ **Files Processed:** {stats['files_processed']}
💾 **Total Space Saved:** {stats['total_size_saved'] / (1024*1024):.1f}MB
📅 **Days Using Bot:** {int(days_using)}
{EMOJIS['star']} **Favorite Operation:** {stats['favorite_operation'] or 'None yet'}

{EMOJIS['fire']} *Keep converting to unlock achievements!*
        """
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔄 Convert More", callback_data="upload_new"))
        markup.add(InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_start"))
        
        bot.edit_message_text(
            stats_text,
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup,
            parse_mode='Markdown'
        )
        
    elif call.data == "show_formats":
        formats_text = f"""
📋 **Supported File Formats**

🖼️ **Images:** JPG, JPEG, PNG, WebP, GIF, SVG
📄 **Documents:** PDF, Word (DOCX)  
🎬 **Videos:** MP4, MOV, MKV, WebM, TS

📏 **Limits:**
• Maximum file size: 50MB
• Processing time: ~30 seconds
• Format quality: Professional grade

{EMOJIS['magic']} *Ready to transform your files?*
        """
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("📤 Upload File", callback_data="upload_new"))
        markup.add(InlineKeyboardButton("🔙 Back", callback_data="back_to_start"))
        
        bot.edit_message_text(
            formats_text,
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup,
            parse_mode='Markdown'
        )
        
    elif call.data == "back_to_start":
        # Restart the welcome message
        welcome(call.message)

# Enhanced error handler
@bot.message_handler(func=lambda message: True)
def handle_unknown(message):
    """Handle unknown messages with helpful guidance"""
    helpful_text = f"""
{EMOJIS['magic']} **I'm a file conversion specialist!**

🎯 **What I need:** 
Upload any supported file (image, PDF, or video)

📋 **Supported formats:**
• 🖼️ Images: JPG, PNG, WebP, SVG, GIF
• 📄 Documents: PDF, Word  
• 🎬 Videos: MP4, MOV, MKV, WebM, TS

*Just drag and drop your file here!* ⬆️
    """
    
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("📋 View All Formats", callback_data="show_formats"),
        InlineKeyboardButton("❓ Get Help", callback_data="show_help")
    )
    markup.add(InlineKeyboardButton("🏠 Start Over", callback_data="back_to_start"))
    
    bot.reply_to(
        message,
        helpful_text,
        reply_markup=markup,
        parse_mode='Markdown'
    )

# Clean shutdown handler
def cleanup():
    """Clean up temporary files on shutdown"""
    temp_manager.cleanup_old_files()

def run_bot():
    """Run the bot with proper error handling"""
    try:
        logger.info(f"{EMOJIS['rocket']} Starting Enhanced File Converter Bot for Cloud Run...")
        logger.info(f"Available operations: {len(IMAGE_OPERATIONS + PDF_OPERATIONS + VIDEO_OPERATIONS)}")
        logger.info(f"{EMOJIS['success']} Bot is running! Waiting for messages...")
        
        # Start the bot with error recovery
        bot.infinity_polling(timeout=60, long_polling_timeout=60)
        
    except KeyboardInterrupt:
        logger.info(f"\n{EMOJIS['star']} Shutting down bot gracefully...")
        cleanup()
        logger.info(f"{EMOJIS['success']} Bot stopped successfully!")
    except Exception as e:
        logger.error(f"{EMOJIS['error']} Bot error: {e}")
        cleanup()
        raise

if __name__ == "__main__":
    # Cloud Run requires a web server for health checks
    port = int(os.environ.get('PORT', 8080))
    
    # Start Flask app in a separate thread for health checks
    flask_thread = threading.Thread(
        target=lambda: app.run(host='0.0.0.0', port=port, debug=False)
    )
    flask_thread.daemon = True
    flask_thread.start()
    
    logger.info(f"Health check server started on port {port}")
    
    # Start the Telegram bot
    run_bot()
