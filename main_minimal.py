"""
Minimal Telegram File Converter Bot for Google Cloud Run
Fast startup with essential features only
"""

import os
import json
import logging
from flask import Flask, request, jsonify
import requests
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Get configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}" if BOT_TOKEN else None

@app.route('/health')
def health_check():
    """Simple health check"""
    return jsonify({
        "status": "healthy",
        "service": "telegram-file-converter",
        "timestamp": datetime.now().isoformat()
    }), 200

@app.route('/webhook', methods=['POST'])
def webhook():
    """Webhook endpoint for Telegram updates"""
    try:
        update = request.get_json()
        logger.info(f"Received update: {update}")
        
        if not update:
            return jsonify({"status": "error", "message": "No data received"}), 400
        
        # Simple response for now
        if 'message' in update:
            chat_id = update['message']['chat']['id']
            
            # Send a simple response
            payload = {
                'chat_id': chat_id,
                'text': '🤖 Bot is running! File conversion features coming soon...'
            }
            
            if BOT_TOKEN:
                requests.post(f"{TELEGRAM_API_URL}/sendMessage", data=payload)
        
        return jsonify({"status": "ok"}), 200
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/')
def root():
    """Root endpoint"""
    return jsonify({
        "service": "Telegram File Converter Bot",
        "status": "running",
        "version": "minimal",
        "bot_configured": bool(BOT_TOKEN)
    })

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    logger.info(f"🚀 Starting minimal bot on port {port}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False
    )