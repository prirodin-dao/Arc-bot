"""
Logging module with rotation support
"""
import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime
from config import LOG_CONFIG, BOT_CONFIG

class BotLogger:
    """Logger with file rotation to prevent large file sizes"""
    
    def __init__(self):
        self.log_dir = LOG_CONFIG["LOG_DIR"]
        self.log_file = LOG_CONFIG["LOG_FILE"]
        
        # Create logs directory
        os.makedirs(self.log_dir, exist_ok=True)
        
        self.logger = logging.getLogger("ArcBot")
        self.logger.setLevel(logging.DEBUG)
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # File handler with rotation (max 1GB, keep 5 backups)
        log_path = os.path.join(self.log_dir, self.log_file)
        file_handler = RotatingFileHandler(
            log_path,
            maxBytes=BOT_CONFIG["MAX_LOG_SIZE"],
            backupCount=BOT_CONFIG["LOG_BACKUP_COUNT"]
        )
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            LOG_CONFIG["LOG_FORMAT"],
            datefmt=LOG_CONFIG["DATE_FORMAT"]
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def info(self, msg, *args, **kwargs):
        """Log info message"""
        self.logger.info(msg, *args, **kwargs)
    
    def debug(self, msg, *args, **kwargs):
        """Log debug message"""
        self.logger.debug(msg, *args, **kwargs)
    
    def warning(self, msg, *args, **kwargs):
        """Log warning message"""
        self.logger.warning(msg, *args, **kwargs)
    
    def error(self, msg, *args, **kwargs):
        """Log error message"""
        self.logger.error(msg, *args, **kwargs)
    
    def critical(self, msg, *args, **kwargs):
        """Log critical message"""
        self.logger.critical(msg, *args, **kwargs)
    
    def banner(self, text):
        """Log a banner"""
        line = "=" * 60
        self.info(line)
        self.info(text)
        self.info(line)

# Global logger instance
logger = BotLogger()
