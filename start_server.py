#!/usr/bin/env python3
"""
Startup script for Telegram File Converter Bot
Handles both development and production environments
"""

import os
import sys
import logging
import subprocess

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main startup function"""
    port = int(os.environ.get('PORT', 8080))
    environment = os.environ.get('ENVIRONMENT', 'development')
    
    logger.info(f"🚀 Starting Telegram File Converter Bot")
    logger.info(f"🌍 Environment: {environment}")
    logger.info(f"🔌 Port: {port}")
    
    # Check if BOT_TOKEN is available
    bot_token = os.environ.get('BOT_TOKEN')
    if not bot_token:
        logger.error("❌ BOT_TOKEN environment variable is required")
        sys.exit(1)
    
    try:
        if environment == 'production':
            # Use gunicorn for production
            logger.info("🏭 Starting with gunicorn (production mode)")
            cmd = [
                'gunicorn',
                '--bind', f'0.0.0.0:{port}',
                '--workers', '1',
                '--threads', '8',
                '--timeout', '600',
                '--preload',
                '--access-logfile', '-',
                '--error-logfile', '-',
                'main:app'
            ]
            subprocess.run(cmd, check=True)
        else:
            # Use Flask development server
            logger.info("🔧 Starting with Flask (development mode)")
            from main import app
            app.run(
                host='0.0.0.0',
                port=port,
                debug=False,
                threaded=True
            )
            
    except KeyboardInterrupt:
        logger.info("👋 Shutting down gracefully...")
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()