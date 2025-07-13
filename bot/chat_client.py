import asyncio
import re
from typing import Optional, Callable, Dict, Any
from utils.helpers import sanitize_message, extract_username_from_message

class NakenChatClient:
    """Telnet client for connecting to NakenChat server"""
    
    def __init__(self, config: Dict[str, Any], logger, message_handler: Callable):
        self.config = config['nakenchat']
        self.bot_config = config['bot']
        self.logger = logger
        self.message_handler = message_handler
        
        self.reader = None
        self.writer = None
        self.is_connected = False
        self.reconnect_attempts = 0
        self.reconnect_task = None
        self.should_stop = False
        
    async def connect(self) -> bool:
        """Connect to NakenChat server"""
        try:
            self.logger.info(f"Connecting to NakenChat server at {self.config['host']}:{self.config['port']}")
            
            self.reader, self.writer = await asyncio.open_connection(
                self.config['host'], 
                self.config['port']
            )
            
            self.is_connected = True
            self.reconnect_attempts = 0
            self.logger.info("Successfully connected to NakenChat server")

            # Set bot name using .n <username>
            await self.send_command(f".n {self.bot_config['username']}")
            self.logger.info(f"Sent .n {self.bot_config['username']} to set bot name")
            
            # Wait a moment for the server to process the name change
            await asyncio.sleep(1)
            
            # Start listening for messages
            asyncio.create_task(self._listen_for_messages())
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to NakenChat server: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from NakenChat server"""
        # Send .q command to properly disconnect from the server first
        if self.writer and self.is_connected:
            try:
                await self.send_command(".q")
                self.logger.info("Sent .q command to disconnect from server")
                # Give a moment for the command to be sent
                await asyncio.sleep(0.1)
            except Exception as e:
                self.logger.warning(f"Failed to send .q command: {e}")
        
        # Now set flags and cleanup
        self.is_connected = False
        self.should_stop = True
        
        if self.reconnect_task:
            self.reconnect_task.cancel()
            self.reconnect_task = None
        
        if self.writer:
            self.writer.close()
            try:
                await self.writer.wait_closed()
            except Exception:
                pass
        
        self.logger.info("Disconnected from NakenChat server")
    
    async def send_message(self, message: str):
        """Send message to NakenChat server"""
        if not self.is_connected or not self.writer:
            self.logger.warning("Cannot send message: not connected")
            return False
        
        try:
            # Add newline and encode
            full_message = f"{message}\n"
            self.writer.write(full_message.encode('utf-8'))
            await self.writer.drain()
            
            self.logger.debug(f"Sent message: {message}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send message: {e}")
            await self._handle_connection_error()
            return False
    
    async def send_command(self, command: str):
        """Send command to NakenChat server"""
        return await self.send_message(command)
    
    async def _listen_for_messages(self):
        """Listen for incoming messages from the server"""
        try:
            while self.is_connected and self.reader:
                try:
                    # Read line from server
                    data = await self.reader.readline()
                    
                    if not data:
                        # Connection closed by server
                        self.logger.warning("Server closed connection")
                        break
                    
                    # Decode and process message
                    message = data.decode('utf-8', errors='ignore')
                    
                    # Debug: Log raw message to see what's causing the error
                    self.logger.debug(f"Raw message from server: {repr(message)}")
                    
                    await self._process_message(message)
                    
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    self.logger.error(f"Error reading message: {e}")
                    # Log the last message that might have caused the error
                    if 'data' in locals():
                        self.logger.error(f"Last message was: {repr(data.decode('utf-8', errors='ignore') if data else 'None')}")
                    break
            
        except Exception as e:
            self.logger.error(f"Error in message listener: {e}")
        finally:
            await self._handle_connection_error()
    
    async def _process_message(self, message: str):
        """Process incoming message"""
        # Sanitize message
        clean_message = sanitize_message(message)
        
        if not clean_message:
            return
        
        self.logger.debug(f"Received: {clean_message}")
        
        # Skip system messages and bot's own messages
        if self._is_system_message(clean_message):
            self.logger.debug(f"Skipping system message: {clean_message}")
            return
        
        if self._is_bot_message(clean_message):
            self.logger.debug(f"Skipping bot message: {clean_message}")
            return
        
        # Extract username and content
        username = extract_username_from_message(clean_message)
        content = self._extract_message_content(clean_message)
        
        if not content:
            self.logger.debug(f"No content extracted from: {clean_message}")
            return
        
        # Call message handler
        try:
            await self.message_handler(clean_message, username, content)
        except Exception as e:
            self.logger.error(f"Error in message handler: {e}")
    
    def _is_system_message(self, message: str) -> bool:
        """Check if message is a system message"""
        system_patterns = [
            r'^>>\s+',  # Server messages starting with >>
            r'^\[.*\]\s*$',  # Empty brackets
            r'^Total:\s*\d+',  # User count messages
            r'^Name\s+Channel\s+Location',  # User list headers
            r'^List of commands:',  # Help headers
            r'^You just logged on',  # Login messages
            r'^has joined|has left|has quit',  # Join/leave messages
            r'^http://.*email:',  # Welcome/info messages with website and email
            r'^http://',  # Any HTTP URLs
            r'^email:',  # Email messages
            r'^Command from https:',  # Command info messages
        ]
        
        for pattern in system_patterns:
            if re.match(pattern, message):
                return True
        
        return False
    
    def _is_bot_message(self, message: str) -> bool:
        """Check if message is from the bot itself"""
        bot_username = self.bot_config['username']
        
        # Check various message formats
        patterns = [
            rf'^\[(\d+)\]{re.escape(bot_username)}:',
            rf'^<(\d+)>{re.escape(bot_username)}:',
            rf'^{re.escape(bot_username)}:',
        ]
        
        for pattern in patterns:
            if re.match(pattern, message):
                return True
        
        return False
    
    def _extract_message_content(self, message: str) -> str:
        """Extract message content from various formats"""
        # Remove user prefixes
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
                self.logger.debug(f"Error parsing message '{message}' with pattern '{pattern}': {e}")
                continue
        
        return message
    
    async def _handle_connection_error(self):
        """Handle connection errors and attempt reconnection"""
        self.is_connected = False
        
        # Check if we should stop reconnecting (bot might be shutting down)
        if hasattr(self, 'should_stop') and self.should_stop:
            self.logger.info("Bot is shutting down, stopping reconnection attempts")
            return
        
        if self.reconnect_attempts >= self.config['max_reconnect_attempts']:
            self.logger.error("Max reconnection attempts reached")
            return
        
        self.reconnect_attempts += 1
        self.logger.info(f"Attempting reconnection {self.reconnect_attempts}/{self.config['max_reconnect_attempts']}")
        
        # Schedule reconnection
        self.reconnect_task = asyncio.create_task(self._reconnect())
    
    async def _reconnect(self):
        """Attempt to reconnect to the server"""
        try:
            await asyncio.sleep(self.config['reconnect_delay'])
            
            # Check if we should stop reconnecting
            if self.should_stop:
                self.logger.info("Bot is shutting down, stopping reconnection attempts")
                return
            
            if await self.connect():
                self.logger.info("Successfully reconnected")
            else:
                # Schedule another reconnection attempt
                self.reconnect_task = asyncio.create_task(self._reconnect())
                
        except asyncio.CancelledError:
            pass
        except Exception as e:
            self.logger.error(f"Reconnection failed: {e}")
            # Schedule another reconnection attempt
            self.reconnect_task = asyncio.create_task(self._reconnect()) 