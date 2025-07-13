import asyncio
from typing import Optional, Dict, Any
from utils.helpers import is_bot_trigger, truncate_response, safe_delay

class MessageProcessor:
    """Processes incoming messages and manages bot responses"""
    
    def __init__(self, config: dict, logger, ollama_client, chat_client, 
                 rate_limiter, context_manager, command_handler):
        self.config = config
        self.logger = logger
        self.ollama_client = ollama_client
        self.chat_client = chat_client
        self.rate_limiter = rate_limiter
        self.context_manager = context_manager
        self.command_handler = command_handler
        
        self.bot_config = config['bot']
        self.trigger = self.bot_config['trigger']
        self.response_delay = self.bot_config['response_delay']
        self.max_response_length = self.bot_config['max_response_length']
        
        # Track processing tasks to avoid duplicates
        self.processing_tasks = set()
    
    async def process_message(self, full_message: str, username: str, content: str):
        """Process an incoming message and determine if bot should respond"""
        
        # Skip if no username
        if not username:
            return
        
        # Add message to context
        self.context_manager.add_message(username, content, is_bot=False)
        
        # Check if message contains bot trigger (for AI responses)
        if not is_bot_trigger(content, self.trigger):
            return
        
        # Extract the actual question/prompt
        prompt = self._extract_prompt(content)
        if not prompt:
            return
        
        # Check rate limiting
        if not self.rate_limiter.is_allowed(username):
            await self._send_rate_limit_message(username)
            return
        
        # Record the request
        self.rate_limiter.record_request(username)
        
        # Process the request
        await self._process_ai_request(username, prompt)
    
    async def _process_ai_request(self, username: str, prompt: str):
        """Process an AI request and generate response"""
        
        # Create a unique task ID
        task_id = f"{username}_{asyncio.get_event_loop().time()}"
        
        # Check if already processing for this user
        if task_id in self.processing_tasks:
            self.logger.debug(f"Already processing request for {username}")
            return
        
        self.processing_tasks.add(task_id)
        
        try:
            # Add delay before responding
            await safe_delay(self.response_delay)
            
            # Get conversation context
            context = self.context_manager.get_context(username)
            
            # Get current model
            current_model = self.config['ollama']['model']
            
            # Generate response
            self.logger.info(f"Generating response for {username}: {prompt[:50]}...")
            
            async with self.ollama_client as client:
                response = await client.generate_response(prompt, context, current_model)
            
            if response:
                # Truncate response if needed
                response = truncate_response(response, self.max_response_length)
                
                # Add bot response to context
                self.context_manager.add_message(self.bot_config['username'], response, is_bot=True)
                
                # Send response
                await self.chat_client.send_message(response)
                
                self.logger.info(f"Response sent to {username}")
            else:
                error_msg = "Sorry, I couldn't generate a response right now. Please try again later."
                await self.chat_client.send_message(error_msg)
                self.logger.warning(f"Failed to generate response for {username}")
                
        except Exception as e:
            self.logger.error(f"Error processing AI request for {username}: {e}")
            error_msg = "Sorry, I encountered an error while processing your request."
            await self.chat_client.send_message(error_msg)
        
        finally:
            # Remove task from processing set
            self.processing_tasks.discard(task_id)
    
    def _extract_prompt(self, content: str) -> Optional[str]:
        """Extract the actual prompt from a message containing the bot trigger"""
        if not content:
            return None
        
        # Remove the trigger word and clean up
        trigger_lower = self.trigger.lower()
        content_lower = content.lower()
        
        # Find trigger position
        trigger_pos = content_lower.find(trigger_lower)
        if trigger_pos == -1:
            return None
        
        # Extract text after trigger
        after_trigger = content[trigger_pos + len(self.trigger):].strip()
        
        # Remove common separators
        separators = [':', '-', '>', '|']
        for sep in separators:
            if after_trigger.startswith(sep):
                after_trigger = after_trigger[1:].strip()
        
        return after_trigger if after_trigger else None
    
    async def _send_rate_limit_message(self, username: str):
        """Send rate limit message to user"""
        stats = self.rate_limiter.get_user_stats(username)
        message = f"You've reached the rate limit ({stats['user_requests']}/{stats['user_limit']} requests per {stats['time_window']} seconds). Please wait a moment before asking again."
        
        await self.chat_client.send_message(message)
        self.logger.info(f"Rate limit message sent to {username}")
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics"""
        return {
            'active_tasks': len(self.processing_tasks),
            'trigger_word': self.trigger,
            'response_delay': self.response_delay,
            'max_response_length': self.max_response_length
        } 