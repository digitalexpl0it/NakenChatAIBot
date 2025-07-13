from typing import List, Dict, Optional
from collections import deque
import time

class ContextManager:
    """Manages conversation context for AI responses"""
    
    def __init__(self, config: dict):
        self.config = config['bot']
        self.enabled = self.config['enable_context']
        self.max_context_length = self.config['context_length']
        
        # Store context per user
        self.user_contexts: Dict[str, deque] = {}
        
        # Global context for general chat
        self.global_context = deque(maxlen=self.max_context_length)
        
        # Context timestamps for cleanup
        self.context_timestamps: Dict[str, float] = {}
        self.context_ttl = 3600  # 1 hour TTL for context
        
    def add_message(self, username: str, message: str, is_bot: bool = False):
        """Add a message to the conversation context"""
        if not self.enabled:
            return
        
        current_time = time.time()
        
        # Format message for context
        formatted_message = f"{username}: {message}" if not is_bot else f"Assistant: {message}"
        
        # Add to user-specific context
        if username not in self.user_contexts:
            self.user_contexts[username] = deque(maxlen=self.max_context_length)
        
        self.user_contexts[username].append(formatted_message)
        self.context_timestamps[username] = current_time
        
        # Add to global context
        self.global_context.append(formatted_message)
        
        # Cleanup old contexts
        self._cleanup_old_contexts(current_time)
    
    def get_context(self, username: str, include_global: bool = True) -> str:
        """Get conversation context for a user"""
        if not self.enabled:
            return ""
        
        context_parts = []
        
        # Get user-specific context
        if username in self.user_contexts:
            user_context = list(self.user_contexts[username])
            if user_context:
                context_parts.extend(user_context)
        
        # Add global context if requested
        if include_global and self.global_context:
            global_context = list(self.global_context)
            # Avoid duplicating messages already in user context
            if context_parts:
                # Only add global messages not already in user context
                for msg in global_context:
                    if msg not in context_parts:
                        context_parts.append(msg)
            else:
                context_parts.extend(global_context)
        
        return "\n".join(context_parts)
    
    def clear_user_context(self, username: str):
        """Clear context for a specific user"""
        if username in self.user_contexts:
            del self.user_contexts[username]
        
        if username in self.context_timestamps:
            del self.context_timestamps[username]
    
    def clear_all_context(self):
        """Clear all conversation context"""
        self.user_contexts.clear()
        self.global_context.clear()
        self.context_timestamps.clear()
    
    def _cleanup_old_contexts(self, current_time: float):
        """Remove contexts older than TTL"""
        cutoff_time = current_time - self.context_ttl
        
        # Find users with old contexts
        users_to_remove = []
        for username, timestamp in self.context_timestamps.items():
            if timestamp < cutoff_time:
                users_to_remove.append(username)
        
        # Remove old contexts
        for username in users_to_remove:
            self.clear_user_context(username)
    
    def get_context_stats(self) -> Dict[str, int]:
        """Get statistics about context usage"""
        return {
            'total_users': len(self.user_contexts),
            'global_context_length': len(self.global_context),
            'max_context_length': self.max_context_length,
            'enabled': self.enabled
        }
    
    def set_context_length(self, length: int):
        """Change the maximum context length"""
        self.max_context_length = length
        
        # Update existing deques
        for username in list(self.user_contexts.keys()):
            old_context = list(self.user_contexts[username])
            self.user_contexts[username] = deque(old_context, maxlen=length)
        
        # Update global context
        old_global = list(self.global_context)
        self.global_context = deque(old_global, maxlen=length) 