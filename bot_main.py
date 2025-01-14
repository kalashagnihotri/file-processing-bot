import telebot
import os
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Load the bot token from environment variables
BOT_TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

# Supported file types and their operations
IMAGE_OPERATIONS = [
    "Convert JPG to PNG",
    "Convert PNG to JPG",
    "Convert JPG to WebP",
    "Convert WebP to JPG",
    "Convert SVG to PNG",
    "Compress Image"
]

PDF_OPERATIONS = [
    "Merge PDFs",
    "Convert PDF to Images",
    "Convert Image to PDF",
    "Compress PDF",
    "Lock PDF",
    "Unlock PDF",
    "Add Page Numbers",
    "Delete a Page",
    "Rotate PDF"
]

VIDEO_OPERATIONS = [
    "Convert MP4 to MOV",
    "Convert MOV to MP4",
    "Convert TS to MP4",
    "Compress Video"
]

# Helper function to identify file type
def get_file_type(file_name):
    ext = os.path.splitext(file_name)[1].lower()
    if ext in [".jpg", ".jpeg", ".png", ".webp", ".svg"]:
        return "image"
    elif ext in [".pdf"]:
        return "pdf"
    elif ext in [".mp4", ".mov", ".mkv", ".webm", ".ts"]:
        return "video"
    return "unsupported"

# Function to create dynamic buttons based on file type
def create_operation_buttons(file_type):
    markup = InlineKeyboardMarkup()
    operations = []

    if file_type == "image":
        operations = IMAGE_OPERATIONS
    elif file_type == "pdf":
        operations = PDF_OPERATIONS
    elif file_type == "video":
        operations = VIDEO_OPERATIONS
    else:
        return None

    for op in operations:
        markup.add(InlineKeyboardButton(op, callback_data=op.lower().replace(" ", "_")))
    
    return markup

# Start command handler
@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, "Welcome! Please send a file to start processing.")

# File handler for receiving user files
@bot.message_handler(content_types=['document', 'photo', 'video'])
def handle_file(message):
    try:
        # Handle file depending on type
        file_info = bot.get_file(message.document.file_id if message.content_type == 'document' else message.photo[-1].file_id)
        file_extension = os.path.splitext(file_info.file_path)[1]
        file_type = get_file_type(file_info.file_path)

        # Generate buttons for operations
        markup = create_operation_buttons(file_type)
        
        if not markup:
            bot.reply_to(message, "Unsupported file type. Please send an image, PDF, or video file.")
            return

        bot.reply_to(message, f"File type detected: {file_type}. Choose an operation:", reply_markup=markup)

    except Exception as e:
        bot.reply_to(message, f"Error handling file: {e}")

# Callback handler for button presses
@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    operation = call.data.replace("_", " ").title()
    bot.answer_callback_query(call.id, f"Selected operation: {operation}")

    # Here you can call the respective processing functions based on the selected operation.

# Keep the bot running
bot.infinity_polling()
