from typing import Dict, Any, Optional, Callable
from utils.helpers import parse_command

class CommandHandler:
    """Handles bot commands like /help, /model, /stats, etc."""
    
    def __init__(self, config: dict, logger, ollama_client, rate_limiter, context_manager):
        self.config = config
        self.logger = logger
        self.ollama_client = ollama_client
        self.rate_limiter = rate_limiter
        self.context_manager = context_manager
        
        # Register commands
        self.commands = {
            'help': self._cmd_help,
            'model': self._cmd_model,
            'models': self._cmd_models,
            'stats': self._cmd_stats,
            'context': self._cmd_context,
            'clear': self._cmd_clear,
            'ping': self._cmd_ping,
            'info': self._cmd_info,
            'reset': self._cmd_reset
        }
        
        self.current_model = config['ollama']['model']
    
    async def handle_command(self, username: str, message: str, trigger: str) -> Optional[str]:
        """Handle a bot command and return response"""
        parsed = parse_command(message, trigger)
        if not parsed:
            return None
        
        command = parsed['command']
        args = parsed['args']
        
        self.logger.info(f"Command from {username}: {command} {args}")
        
        # Check if command exists
        if command not in self.commands:
            return f"Unknown command: {command}. Type '{trigger} help' for available commands."
        
        # Execute command
        try:
            response = await self.commands[command](username, args)
            return response
        except Exception as e:
            self.logger.error(f"Error executing command {command}: {e}")
            return f"Error executing command: {str(e)}"
    
    async def _cmd_help(self, username: str, args: str) -> str:
        """Show help information"""
        bot_name = self.config['bot']['name']
        help_text = f"""
Available commands:
{bot_name} help - Show this help message
{bot_name} model <name> - Change AI model (e.g., {bot_name} model llama2)
{bot_name} models - List available models
{bot_name} stats - Show bot statistics
{bot_name} context - Show context information
{bot_name} clear - Clear your conversation context
{bot_name} ping - Test bot response
{bot_name} info - Show bot information
{bot_name} reset - Reset rate limiting for your user

To ask me something, just mention my name followed by your question!
        """.strip()
        
        return help_text
    
    async def _cmd_model(self, username: str, args: str) -> str:
        """Change the AI model"""
        if not args:
            return f"Current model: {self.current_model}\nUsage: /model <model_name>"
        
        new_model = args.strip()
        
        # Check if model exists
        if await self.ollama_client.check_model_exists(new_model):
            self.current_model = new_model
            self.logger.info(f"Model changed to {new_model} by {username}")
            return f"Model changed to {new_model}"
        else:
            return f"Model '{new_model}' not found. Use /models to see available models."
    
    async def _cmd_models(self, username: str, args: str) -> str:
        """List available models"""
        models = await self.ollama_client.list_models()
        if models:
            current = self.current_model
            model_list = "\n".join([f"• {model}" + (" (current)" if model == current else "") for model in models])
            return f"Available models:\n{model_list}"
        else:
            return "Could not retrieve model list. Check if Ollama is running."
    
    async def _cmd_stats(self, username: str, args: str) -> str:
        """Show bot statistics"""
        rate_stats = self.rate_limiter.get_user_stats(username)
        context_stats = self.context_manager.get_context_stats()
        
        stats_text = f"""
Bot Statistics:
• Current model: {self.current_model}
• Rate limit: {rate_stats['user_requests']}/{rate_stats['user_limit']} requests
• Context enabled: {context_stats['enabled']}
• Active users: {context_stats['total_users']}
• Global context: {context_stats['global_context_length']} messages
        """.strip()
        
        return stats_text
    
    async def _cmd_context(self, username: str, args: str) -> str:
        """Show context information"""
        context = self.context_manager.get_context(username, include_global=False)
        
        if context:
            # Truncate if too long
            if len(context) > 500:
                context = context[:500] + "..."
            return f"Your conversation context:\n{context}"
        else:
            return "No conversation context found."
    
    async def _cmd_clear(self, username: str, args: str) -> str:
        """Clear user's conversation context"""
        self.context_manager.clear_user_context(username)
        return "Your conversation context has been cleared."
    
    async def _cmd_ping(self, username: str, args: str) -> str:
        """Test bot response"""
        return f"Pong! Hello {username}, I'm here and ready to help!"
    
    async def _cmd_info(self, username: str, args: str) -> str:
        """Show bot information"""
        bot_name = self.config['bot']['name']
        info_text = f"""
{bot_name} Information:
• Version: 1.0.0
• Trigger: {self.config['bot']['trigger']}
• Model: {self.current_model}
• Max response length: {self.config['bot']['max_response_length']}
• Context length: {self.config['bot']['context_length']}
• Rate limiting: {'Enabled' if self.config['behavior']['rate_limit']['enabled'] else 'Disabled'}
        """.strip()
        
        return info_text
    
    async def _cmd_reset(self, username: str, args: str) -> str:
        """Reset rate limiting for user"""
        self.rate_limiter.reset_user(username)
        return "Your rate limiting has been reset."
    
    def get_current_model(self) -> str:
        """Get the current model being used"""
        return self.current_model
    
    def set_current_model(self, model: str):
        """Set the current model"""
        self.current_model = model 