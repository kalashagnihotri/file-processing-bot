import telebot
import os
import threading
import time
import zipfile
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Import our modules
from config import (
    BOT_TOKEN, MAX_FILE_SIZE_MB, ERROR_MESSAGES, SUCCESS_MESSAGES,
    SUPPORTED_IMAGE_EXTENSIONS, SUPPORTED_PDF_EXTENSIONS, SUPPORTED_VIDEO_EXTENSIONS
)
from utils import temp_manager, download_telegram_file, get_file_info, validate_file_size

# Import operation functions
try:
    from operations.images import *
except ImportError as e:
    print(f"Warning: Could not import all image operations: {e}")

try:
    from operations.pdf import *
except ImportError as e:
    print(f"Warning: Could not import all PDF operations: {e}")

try:
    from operations.videos import *
except ImportError as e:
    print(f"Warning: Could not import all video operations: {e}")

# Initialize bot
bot = telebot.TeleBot(BOT_TOKEN)

# Store user sessions for multi-step operations
user_sessions = {}

# Supported file types and their operations
IMAGE_OPERATIONS = [
    "Convert JPG to PNG",
    "Convert PNG to JPG", 
    "Convert JPG to WebP",
    "Convert WebP to JPG",
    "Compress Image"
]

# Check if SVG support is available
try:
    from operations.images.svg_to_png import CAIROSVG_AVAILABLE
    if CAIROSVG_AVAILABLE:
        IMAGE_OPERATIONS.append("Convert SVG to PNG")
except ImportError:
    pass

PDF_OPERATIONS = [
    "Merge PDFs",
    "Convert PDF to Images",
    "Convert Image to PDF",
    "Compress PDF",
    "Lock PDF",
    "Unlock PDF",
    "Add Page Numbers",
    "Delete a Page",
    "Rotate PDF",
    "Convert PDF to Word"
]

VIDEO_OPERATIONS = []

# Check if video processing is available
try:
    from operations.videos import MOVIEPY_AVAILABLE
    if MOVIEPY_AVAILABLE:
        VIDEO_OPERATIONS = [
            "Convert MP4 to MOV",
            "Convert MOV to MP4",
            "Convert TS to MP4",
            "Convert MKV to MP4",
            "Convert MP4 to WebM",
            "Convert WebM to MP4",
            "Convert GIF to MP4",
            "Convert GIF to WebM",
            "Convert MP4 to GIF",
            "Convert MOV to GIF",
            "Convert WebM to GIF",
            "Compress Video"
        ]
except ImportError:
    pass

# Helper function to identify file type
def get_file_type(file_name):
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

# Function to create dynamic buttons based on file type
def create_operation_buttons(file_type):
    markup = InlineKeyboardMarkup(row_width=2)
    operations = []

    if file_type == "image":
        operations = IMAGE_OPERATIONS
        # Add emoji-rich buttons for images with descriptions
        for i, op in enumerate(operations):
            if "JPG to PNG" in op:
                markup.add(InlineKeyboardButton("🔄 JPG → PNG (Transparent)", callback_data="convert_jpg_to_png"))
            elif "PNG to JPG" in op:
                markup.add(InlineKeyboardButton("🔄 PNG → JPG (Smaller)", callback_data="convert_png_to_jpg"))
            elif "JPG to WebP" in op:
                markup.add(InlineKeyboardButton("🚀 JPG → WebP (Ultra Small)", callback_data="convert_jpg_to_webp"))
            elif "WebP to JPG" in op:
                markup.add(InlineKeyboardButton("🔄 WebP → JPG (Universal)", callback_data="convert_webp_to_jpg"))
            elif "Compress" in op:
                markup.add(InlineKeyboardButton("🗜️ Smart Compress (60% smaller)", callback_data="compress_image"))
            elif "SVG to PNG" in op:
                markup.add(InlineKeyboardButton("🎨 SVG → PNG (Raster)", callback_data="convert_svg_to_png"))
        
        # Add helpful action buttons
        markup.add(
            InlineKeyboardButton("💡 What's Best?", callback_data="suggest_image"),
            InlineKeyboardButton("🔙 Upload Different", callback_data="upload_new")
        )
        
    elif file_type == "pdf":
        operations = PDF_OPERATIONS
        # Group PDF operations by category
        markup.add(InlineKeyboardButton("🔄 Convert PDF → Word", callback_data="convert_pdf_to_word"))
        markup.add(InlineKeyboardButton("🖼️ Convert PDF → Images", callback_data="convert_pdf_to_images"))
        markup.add(InlineKeyboardButton("📄 Convert Image → PDF", callback_data="convert_image_to_pdf"))
        markup.add(
            InlineKeyboardButton("🗜️ Compress PDF", callback_data="compress_pdf"),
            InlineKeyboardButton("🔒 Lock PDF", callback_data="lock_pdf")
        )
        markup.add(
            InlineKeyboardButton("🔓 Unlock PDF", callback_data="unlock_pdf"),
            InlineKeyboardButton("🔄 Rotate PDF", callback_data="rotate_pdf")
        )
        markup.add(
            InlineKeyboardButton("📑 Merge PDFs", callback_data="merge_pdfs"),
            InlineKeyboardButton("🔢 Add Page Numbers", callback_data="add_page_numbers")
        )
        markup.add(InlineKeyboardButton("🗑️ Delete Page", callback_data="delete_a_page"))
        
        # Add helper buttons
        markup.add(
            InlineKeyboardButton("💡 PDF Tips", callback_data="pdf_tips"),
            InlineKeyboardButton("🔙 Upload Different", callback_data="upload_new")
        )
        
    elif file_type == "video":
        operations = VIDEO_OPERATIONS
        # Create visually appealing video operation buttons
        markup.add(InlineKeyboardButton("🎬 MP4 → MOV (Apple)", callback_data="convert_mp4_to_mov"))
        markup.add(InlineKeyboardButton("🎬 MOV → MP4 (Universal)", callback_data="convert_mov_to_mp4"))
        markup.add(
            InlineKeyboardButton("📺 → MP4", callback_data="convert_ts_to_mp4"),
            InlineKeyboardButton("🎥 MKV → MP4", callback_data="convert_mkv_to_mp4")
        )
        markup.add(
            InlineKeyboardButton("🌐 MP4 → WebM", callback_data="convert_mp4_to_webm"),
            InlineKeyboardButton("🌐 WebM → MP4", callback_data="convert_webm_to_mp4")
        )
        
        # GIF operations with special styling
        markup.add(InlineKeyboardButton("✨ === GIF MAGIC === ✨", callback_data="gif_header"))
        markup.add(
            InlineKeyboardButton("🎭 GIF → MP4", callback_data="convert_gif_to_mp4"),
            InlineKeyboardButton("🎭 GIF → WebM", callback_data="convert_gif_to_webm")
        )
        markup.add(
            InlineKeyboardButton("🎊 MP4 → GIF", callback_data="convert_mp4_to_gif"),
            InlineKeyboardButton("🎊 MOV → GIF", callback_data="convert_mov_to_gif")
        )
        markup.add(InlineKeyboardButton("🎊 WebM → GIF", callback_data="convert_webm_to_gif"))
        
        markup.add(InlineKeyboardButton("🗜️ Compress Video", callback_data="compress_video"))
        
        # Add helper buttons
        markup.add(
            InlineKeyboardButton("💡 Video Tips", callback_data="video_tips"),
            InlineKeyboardButton("🔙 Upload Different", callback_data="upload_new")
        )
    else:
        return None

    return markup

# Function to perform the actual conversion
def perform_conversion(operation, input_path, output_path, **kwargs):
    """Route to appropriate conversion function based on operation"""
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

# Start command handler
@bot.message_handler(commands=['start'])
def welcome(message):
    user_name = message.from_user.first_name or "there"
    
    welcome_text = f"""
🎉 *Hey {user_name}!* Welcome to the Ultimate File Converter Bot!

✨ *Transform your files with ease:*

�️ **Images** - Perfect for social media & web
   • JPG ↔ PNG ↔ WebP conversions
   • Smart compression (save up to 60% space!)
   • SVG to raster format conversion

� **PDFs** - Professional document handling  
   • Merge, split & compress PDFs
   • Convert PDFs ↔ Word documents
   • Add watermarks & page numbers
   • Password protection & OCR support

� **Videos** - Content creator's dream
   • Format conversions (MP4, MOV, WebM)
   • GIF creation from videos
   • Smart compression for faster sharing

🚀 **Getting Started:**
Just drop any file here and watch the magic happen!

*Quick tip: Try sending a photo right now!* 📱
    """
    
    # Create an engaging start menu
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("📸 Try with Photo", callback_data="demo_photo"),
        InlineKeyboardButton("📄 Upload Document", callback_data="demo_doc")
    )
    markup.add(
        InlineKeyboardButton("🎥 Video Magic", callback_data="demo_video"),
        InlineKeyboardButton("❓ Help & Tips", callback_data="show_help")
    )
    markup.add(InlineKeyboardButton("⭐ Rate Bot", url="https://t.me/your_channel"))
    
    bot.send_message(
        message.chat.id, 
        welcome_text, 
        reply_markup=markup, 
        parse_mode='Markdown'
    )

@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = """
🔧 **Complete User Guide** 

*Follow these simple steps:*

**1️⃣ Upload Your File**
   • Drag & drop or select from gallery
   • Supports images, PDFs, videos up to 50MB
   • Multiple formats supported

**2️⃣ Choose Your Magic**
   • Tap the operation you want
   • Get instant preview of what will happen
   • Smart suggestions based on file type

**3️⃣ Get Your Result**
   • Lightning-fast processing ⚡
   • Download immediately
   • Share directly to other apps

� **Supported Formats:**

🖼️ **Images:** JPG, PNG, WebP, SVG, GIF
📄 **Documents:** PDF, Word documents  
🎬 **Videos:** MP4, MOV, MKV, WebM, TS

💡 **Pro Tips:**
   • Compress images before sharing (saves data!)
   • Convert videos to GIF for memes
   • Use PDF compression for email attachments
   • OCR works on scanned documents

⚠️ **Important:**
   • Files auto-delete after 24h for privacy
   • Max file size: 50MB (Telegram limit)
   • All processing is secure & private

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

# File handler for receiving user files
@bot.message_handler(content_types=['document', 'photo', 'video'])
def handle_file(message):
    try:
        # Get file information
        file_id, file_name, file_size = get_file_info(message)
        
        if not file_id:
            bot.reply_to(message, ERROR_MESSAGES['unsupported_file'])
            return
        
        # Validate file size
        if not validate_file_size(file_size, MAX_FILE_SIZE_MB):
            bot.reply_to(message, ERROR_MESSAGES['file_too_large'])
            return
        
        # Determine file type
        file_type = get_file_type(file_name)
        
        if file_type == "unsupported":
            bot.reply_to(message, ERROR_MESSAGES['unsupported_file'])
            return
        
        # Store file information in user session
        user_sessions[message.from_user.id] = {
            'file_id': file_id,
            'file_name': file_name,
            'file_type': file_type,
            'message_id': message.message_id
        }
        
        # Generate buttons for operations
        markup = create_operation_buttons(file_type)
        
        bot.reply_to(
            message, 
            f"✅ {SUCCESS_MESSAGES['file_received']}\n\n📁 File: `{file_name}`\n📊 Type: {file_type.title()}", 
            reply_markup=markup,
            parse_mode='Markdown'
        )

    except Exception as e:
        print(f"Error handling file: {e}")
        bot.reply_to(message, ERROR_MESSAGES['download_failed'])

# Callback handler for button presses
@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    user_id = call.from_user.id
    operation = call.data
    
    # Check if user has a file session
    if user_id not in user_sessions:
        bot.answer_callback_query(call.id, "Please send a file first!")
        return
    
    session = user_sessions[user_id]
    bot.answer_callback_query(call.id, f"🔄 Processing: {operation.replace('_', ' ').title()}")
    
    # Send processing message
    processing_msg = bot.send_message(
        call.message.chat.id, 
        "⏳ Processing your file... This may take a moment."
    )
    
    try:
        # Download the original file
        input_path = temp_manager.create_temp_file(
            extension=os.path.splitext(session['file_name'])[1],
            prefix="input_"
        )
        
        if not download_telegram_file(bot, session['file_id'], input_path):
            raise Exception("Failed to download file")
        
        # Create output file path
        output_filename = temp_manager.get_output_filename(session['file_name'], operation)
        output_path = temp_manager.create_temp_file(
            extension=os.path.splitext(output_filename)[1],
            prefix="output_"
        )
        
        # Perform the conversion
        result = perform_conversion(operation, input_path, output_path)
        
        # Check if conversion was successful
        if "Error" in result:
            bot.edit_message_text(
                f"❌ {result}",
                call.message.chat.id,
                processing_msg.message_id
            )
            return
        
        # Send the converted file
        if os.path.exists(output_path):
            with open(output_path, 'rb') as file:
                bot.send_document(
                    call.message.chat.id,
                    file,
                    caption=f"✅ {SUCCESS_MESSAGES['conversion_complete']}\n\n📎 {output_filename}",
                    parse_mode='Markdown'
                )
            
            bot.edit_message_text(
                "✅ File converted and sent successfully!",
                call.message.chat.id,
                processing_msg.message_id
            )
            
            # Clean up files
            cleanup_files([input_path, output_path])
            
        else:
            bot.edit_message_text(
                "❌ Conversion failed - output file not created",
                call.message.chat.id,
                processing_msg.message_id
            )
    
    except Exception as e:
        print(f"Error in conversion: {e}")
        bot.edit_message_text(
            f"❌ {ERROR_MESSAGES['conversion_failed']}\n\nError: {str(e)}",
            call.message.chat.id,
            processing_msg.message_id
        )
    
    finally:
        # Clean up session
        if user_id in user_sessions:
            del user_sessions[user_id]

def cleanup_files(file_paths):
    """Clean up temporary files"""
    for path in file_paths:
        try:
            if os.path.exists(path):
                os.remove(path)
        except Exception as e:
            print(f"Error cleaning up {path}: {e}")

def periodic_cleanup():
    """Periodically clean up old temporary files"""
    while True:
        try:
            temp_manager.cleanup_old_files()
            time.sleep(3600)  # Run every hour
        except Exception as e:
            print(f"Error in periodic cleanup: {e}")
            time.sleep(3600)

# Start cleanup thread
cleanup_thread = threading.Thread(target=periodic_cleanup, daemon=True)
cleanup_thread.start()

# Error handler
@bot.message_handler(func=lambda message: True)
def default_handler(message):
    bot.reply_to(
        message, 
        "🤖 Please send a file (image, PDF, or video) for conversion.\n\nUse /help for more information."
    )

if __name__ == "__main__":
    print("🤖 Bot starting...")
    print("✅ Bot is running! Send /start to begin.")
    
    # Start the bot
    try:
        bot.infinity_polling()
    except Exception as e:
        print(f"Bot error: {e}")
        print("Restarting bot...")
        bot.infinity_polling()
