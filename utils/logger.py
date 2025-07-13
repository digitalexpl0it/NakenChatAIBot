import logging
import sys
from colorama import init, Fore, Style
from pathlib import Path

# Initialize colorama for cross-platform colored output
init()

class ColoredFormatter(logging.Formatter):
    """Custom formatter with colored output for console"""
    
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Style.BRIGHT
    }
    
    def format(self, record):
        # Add color to levelname
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{Style.RESET_ALL}"
        
        return super().format(record)

def setup_logger(name, config):
    """Setup logger with console and file handlers"""
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, config['logging']['level']))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Console handler with colors
    if config['logging']['console']:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, config['logging']['level']))
        
        console_formatter = ColoredFormatter(
            f"{Fore.BLUE}%(asctime)s{Style.RESET_ALL} - %(name)s - %(levelname)s - %(message)s"
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    # File handler
    if config['logging']['file']:
        log_file = Path(config['logging']['file'])
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, config['logging']['level']))
        
        file_formatter = logging.Formatter(config['logging']['format'])
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger 