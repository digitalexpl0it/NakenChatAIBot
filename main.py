#!/usr/bin/env python3
"""
NakenChat AI Bot - Main Entry Point

A Python-based AI bot for NakenChat that connects to Ollama for AI responses.
"""

import asyncio
import signal
import sys
import yaml
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from utils.logger import setup_logger
from bot.ollama_client import OllamaClient
from bot.chat_client import NakenChatClient
from bot.rate_limiter import RateLimiter
from bot.context_manager import ContextManager
from bot.message_processor import MessageProcessor

class NakenChatAIBot:
    """Main bot class that orchestrates all components"""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self.config = None
        self.logger = None
        
        # Components
        self.ollama_client = None
        self.chat_client = None
        self.rate_limiter = None
        self.context_manager = None
        self.message_processor = None
        
        # Control flags
        self.running = False
        self.shutdown_event = asyncio.Event()
    
    def load_config(self) -> bool:
        """Load configuration from YAML file"""
        try:
            config_file = Path(self.config_path)
            if not config_file.exists():
                print(f"Configuration file not found: {self.config_path}")
                return False
            
            with open(config_file, 'r') as f:
                self.config = yaml.safe_load(f)
            
            return True
            
        except Exception as e:
            print(f"Error loading configuration: {e}")
            return False
    
    def setup_logging(self):
        """Setup logging system"""
        self.logger = setup_logger("NakenChatAIBot", self.config)
        self.logger.info("Logging system initialized")
    
    def setup_components(self):
        """Initialize all bot components"""
        if not self.config:
            raise ValueError("Configuration not loaded")
        if not self.logger:
            raise ValueError("Logger not initialized")
            
        try:
            # Initialize rate limiter
            self.rate_limiter = RateLimiter(self.config)
            self.logger.info("Rate limiter initialized")
            
            # Initialize context manager
            self.context_manager = ContextManager(self.config)
            self.logger.info("Context manager initialized")
            
            # Initialize Ollama client
            self.ollama_client = OllamaClient(self.config, self.logger, self.config['bot']['name'])
            self.logger.info("Ollama client initialized")
            
            # Initialize message processor
            self.message_processor = MessageProcessor(
                self.config,
                self.logger,
                self.ollama_client,
                None,  # Will be set after chat client is created
                self.rate_limiter,
                self.context_manager,
                None  # No command handler needed
            )
            self.logger.info("Message processor initialized")
            
            # Initialize chat client
            self.chat_client = NakenChatClient(
                self.config,
                self.logger,
                self.message_processor.process_message
            )
            
            # Update message processor with chat client
            self.message_processor.chat_client = self.chat_client
            self.logger.info("Chat client initialized")
            
        except Exception as e:
            self.logger.error(f"Error setting up components: {e}")
            raise
    
    async def test_connections(self) -> bool:
        """Test connections to Ollama and NakenChat"""
        self.logger.info("Testing connections...")
        
        # Test Ollama connection
        try:
            async with self.ollama_client as client:
                if not await client.test_connection():
                    self.logger.error("Failed to connect to Ollama API")
                    return False
                
                # Test if default model exists
                default_model = self.config['ollama']['model']
                if not await client.check_model_exists(default_model):
                    self.logger.warning(f"Default model '{default_model}' not found")
                    models = await client.list_models()
                    if models:
                        self.logger.info(f"Available models: {models}")
                        # Use first available model
                        self.config['ollama']['model'] = models[0]
                        self.logger.info(f"Using model: {models[0]}")
                
        except Exception as e:
            self.logger.error(f"Error testing Ollama connection: {e}")
            return False
        
        self.logger.info("All connections tested successfully")
        return True
    
    async def start(self):
        """Start the bot"""
        try:
            self.logger.info("Starting NakenChat AI Bot...")
            
            # Test connections
            if not await self.test_connections():
                self.logger.error("Connection tests failed. Exiting.")
                return False
            
            # Connect to NakenChat
            if not await self.chat_client.connect():
                self.logger.error("Failed to connect to NakenChat server")
                return False
            
            self.running = True
            self.logger.info("Bot started successfully!")
            self.logger.info(f"Bot name: {self.config['bot']['name']}")
            self.logger.info(f"Trigger word: {self.config['bot']['trigger']}")
            self.logger.info(f"Current model: {self.config['ollama']['model']}")
            
            # Wait for shutdown signal
            await self.shutdown_event.wait()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting bot: {e}")
            return False
    
    async def stop(self):
        """Stop the bot"""
        self.logger.info("Stopping bot...")
        self.running = False
        self.shutdown_event.set()
        
        if self.chat_client:
            await self.chat_client.disconnect()
        
        self.logger.info("Bot stopped")

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    print("\nReceived shutdown signal. Stopping bot...")
    # Set the shutdown event to trigger the main loop to stop
    if bot and hasattr(bot, 'shutdown_event'):
        bot.shutdown_event.set()

async def main():
    """Main entry point"""
    global bot
    
    # Create bot instance
    bot = NakenChatAIBot()
    
    # Load configuration
    if not bot.load_config():
        print("Failed to load configuration. Exiting.")
        return 1
    
    # Setup logging
    bot.setup_logging()
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Setup components
        bot.setup_components()
        
        # Start bot
        success = await bot.start()
        
        if success:
            return 0
        else:
            return 1
            
    except KeyboardInterrupt:
        bot.logger.info("Received keyboard interrupt")
        return 0
    except Exception as e:
        if bot.logger:
            bot.logger.error(f"Unexpected error: {e}")
        else:
            print(f"Unexpected error: {e}")
        return 1
    finally:
        # Ensure bot is properly stopped and disconnected
        if bot and bot.running:
            await bot.stop()

if __name__ == "__main__":
    bot = None
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 