import logging
import sys
from datetime import datetime
from pathlib import Path

class Logger:
    """Custom logger with timestamp and configurable output destination"""
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, name="stable_genius", level=logging.INFO, log_to_file=False, log_dir=None):
        if self._initialized:
            return
            
        self._initialized = True
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.logger.propagate = False
        
        # Clear any existing handlers
        if self.logger.handlers:
            self.logger.handlers.clear()
        
        # Create formatter with timestamp
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', 
                                     datefmt='%Y-%m-%d %H:%M:%S')
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # File handler (optional)
        if log_to_file:
            if log_dir is None:
                log_dir = Path(__file__).parents[2] / "logs"
            
            log_dir = Path(log_dir)
            log_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = log_dir / f"{name}_{timestamp}.log"
            
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def debug(self, message):
        self.logger.debug(message)
        
    def info(self, message):
        self.logger.info(message)
        
    def warning(self, message):
        self.logger.warning(message)
        
    def error(self, message):
        self.logger.error(message)
        
    def critical(self, message):
        self.logger.critical(message)


def get_logger(name=None, level=None, log_to_file=False, log_dir=None):
    """Get the logger instance with optional reconfiguration"""
    if name is not None or level is not None or log_to_file:
        if level is None:
            level = logging.INFO
        return Logger(name=name, level=level, log_to_file=log_to_file, log_dir=log_dir)
    else:
        # Always return a Logger instance, even when no arguments are provided
        return Logger()

logger = get_logger()