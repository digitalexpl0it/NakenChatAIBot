import re
import asyncio
from typing import Optional, List, Dict, Any

def sanitize_message(message: str) -> str:
    """Clean and sanitize incoming messages"""
    if not message:
        return ""
    
    # Remove null characters and extra whitespace
    message = re.sub(r'\x00', '', message)
    message = re.sub(r'\r\n', '\n', message)
    message = re.sub(r'\r', '\n', message)
    message = message.strip()
    
    return message

def extract_username_from_message(message: str) -> Optional[str]:
    """Extract username from NakenChat message format"""
    # Common patterns: [1]username: message, <1>username: message, username: message
    patterns = [
        r'^\[(\d+)\]([^:]+):\s*(.+)$',
        r'^<(\d+)>([^:]+):\s*(.+)$',
        r'^([^:]+):\s*(.+)$'
    ]
    
    for pattern in patterns:
        try:
            match = re.match(pattern, message)
            if match:
                groups = match.groups()
                if len(groups) >= 3:
                    # Pattern with group number: [1]username: message
                    return groups[1]  # Username is the second group
                elif len(groups) >= 2:
                    # Pattern without group number: username: message
                    return groups[0]  # Username is the first group
        except (IndexError, AttributeError) as e:
            # Log the error for debugging but continue with next pattern
            print(f"Error parsing message '{message}' with pattern '{pattern}': {e}")
            continue
    
    return None

def extract_message_content(message: str) -> str:
    """Extract the actual message content from NakenChat format"""
    # Remove user prefixes and get just the message part
    patterns = [
        r'^\[(\d+)\]([^:]+):\s*(.+)$',
        r'^<(\d+)>([^:]+):\s*(.+)$',
        r'^([^:]+):\s*(.+)$'
    ]
    
    for pattern in patterns:
        try:
            match = re.match(pattern, message)
            if match:
                groups = match.groups()
                if len(groups) >= 3:
                    # Pattern with group number: [1]username: message
                    return groups[2]  # Message content is the third group
                elif len(groups) >= 2:
                    # Pattern without group number: username: message
                    return groups[1]  # Message content is the second group
        except (IndexError, AttributeError) as e:
            # Log the error for debugging but continue with next pattern
            print(f"Error parsing message '{message}' with pattern '{pattern}': {e}")
            continue
    
    return message

def is_bot_trigger(message: str, trigger: str) -> bool:
    """Check if message contains bot trigger (case insensitive)"""
    if not message or not trigger:
        return False
    
    # Case insensitive search
    return trigger.lower() in message.lower()

def is_bot_command(message: str, trigger: str) -> bool:
    """Check if message is a bot command (trigger followed by command)"""
    if not message or not trigger:
        return False
    
    # Look for trigger followed by a command
    # Pattern: trigger command (e.g., "BotName help", "BotName model llama2")
    trigger_lower = trigger.lower()
    message_lower = message.lower()
    
    # Find trigger position
    trigger_pos = message_lower.find(trigger_lower)
    if trigger_pos == -1:
        return False
    
    # Check if there's text after the trigger that could be a command
    after_trigger = message[trigger_pos + len(trigger):].strip()
    return len(after_trigger) > 0

def truncate_response(response: str, max_length: int) -> str:
    """Truncate response to maximum length"""
    if len(response) <= max_length:
        return response
    
    # Try to truncate at word boundary
    truncated = response[:max_length-3]
    last_space = truncated.rfind(' ')
    
    if last_space > max_length * 0.8:  # If we can find a good break point
        return truncated[:last_space] + "..."
    
    return truncated + "..."

def parse_command(message: str, trigger: str) -> Optional[Dict[str, Any]]:
    """Parse bot commands like 'trigger help', 'trigger model llama2', etc."""
    if not is_bot_command(message, trigger):
        return None
    
    trigger_lower = trigger.lower()
    message_lower = message.lower()
    
    # Find trigger position
    trigger_pos = message_lower.find(trigger_lower)
    if trigger_pos == -1:
        return None
    
    # Extract text after trigger
    after_trigger = message[trigger_pos + len(trigger):].strip()
    
    # Split into command and args
    parts = after_trigger.split(maxsplit=1)
    command = parts[0].lower()  # Convert to lowercase
    
    if len(parts) > 1:
        args = parts[1]
    else:
        args = ""
    
    return {
        'command': command,
        'args': args,
        'full_message': message
    }

async def safe_delay(seconds: float):
    """Safe delay that can be interrupted"""
    try:
        await asyncio.sleep(seconds)
    except asyncio.CancelledError:
        pass

def format_context(context: List[str]) -> str:
    """Format conversation context for AI prompt"""
    if not context:
        return ""
    
    formatted = []
    for i, msg in enumerate(context[-5:], 1):  # Last 5 messages
        formatted.append(f"Message {i}: {msg}")
    
    return "\n".join(formatted) 