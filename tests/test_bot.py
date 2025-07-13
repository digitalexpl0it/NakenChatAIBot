#!/usr/bin/env python3
"""
Basic tests for NakenChat AI Bot
"""

import unittest
import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.helpers import sanitize_message, is_bot_trigger, truncate_response, parse_command

class TestHelpers(unittest.TestCase):
    """Test helper functions"""
    
    def test_sanitize_message(self):
        """Test message sanitization"""
        # Test null character removal
        self.assertEqual(sanitize_message("Hello\x00World"), "HelloWorld")
        
        # Test whitespace trimming
        self.assertEqual(sanitize_message("  Hello World  "), "Hello World")
        
        # Test empty message
        self.assertEqual(sanitize_message(""), "")
        self.assertEqual(sanitize_message(None), "")
    
    def test_is_bot_trigger(self):
        """Test bot trigger detection"""
        # Test case insensitive
        self.assertTrue(is_bot_trigger("NakenBot, hello", "NakenBot"))
        self.assertTrue(is_bot_trigger("hello NakenBot", "NakenBot"))
        self.assertTrue(is_bot_trigger("NAKENBOT help", "NakenBot"))
        
        # Test no trigger
        self.assertFalse(is_bot_trigger("Hello world", "NakenBot"))
        self.assertFalse(is_bot_trigger("", "NakenBot"))
    
    def test_truncate_response(self):
        """Test response truncation"""
        long_response = "This is a very long response that should be truncated"
        
        # Test truncation
        truncated = truncate_response(long_response, 20)
        self.assertLessEqual(len(truncated), 20)
        self.assertTrue(truncated.endswith("..."))
        
        # Test no truncation needed
        short_response = "Short"
        result = truncate_response(short_response, 20)
        self.assertEqual(result, short_response)
    
    def test_parse_command(self):
        """Test command parsing"""
        # Test valid command
        result = parse_command("/help")
        self.assertIsNotNone(result)
        self.assertEqual(result['command'], 'help')
        self.assertEqual(result['args'], '')
        
        # Test command with args
        result = parse_command("/model llama2")
        self.assertIsNotNone(result)
        self.assertEqual(result['command'], 'model')
        self.assertEqual(result['args'], 'llama2')
        
        # Test not a command
        result = parse_command("Hello world")
        self.assertIsNone(result)

class TestAsyncHelpers(unittest.TestCase):
    """Test async helper functions"""
    
    def test_safe_delay(self):
        """Test safe delay function"""
        async def test_delay():
            import asyncio
            from utils.helpers import safe_delay
            
            start = asyncio.get_event_loop().time()
            await safe_delay(0.1)
            end = asyncio.get_event_loop().time()
            
            # Should delay for at least 0.1 seconds
            self.assertGreaterEqual(end - start, 0.1)
        
        asyncio.run(test_delay())

if __name__ == '__main__':
    unittest.main() 