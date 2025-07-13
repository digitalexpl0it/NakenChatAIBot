# NakenChat AI Bot

A Python-based AI bot for NakenChat that connects to Ollama for intelligent responses. The bot monitors chat messages and responds when triggered by its name.

## Features

- 🤖 **AI-Powered Responses**: Uses Ollama for intelligent chat responses
- 🎯 **Trigger-Based**: Responds when mentioned by name (configurable)
- 💬 **Context Awareness**: Maintains conversation context for better responses
- ⚡ **Rate Limiting**: Prevents spam and abuse
- 🛠️ **Bot Commands**: Built-in commands for configuration and information
- 🔄 **Auto-Reconnect**: Automatically reconnects to chat server
- 📝 **Logging**: Comprehensive logging with colored console output
- 🖥️ **Modern GUI**: Beautiful desktop interface with real-time monitoring
- ⚙️ **Configurable**: Easy configuration via YAML file

## Requirements

- Python 3.8+
- Ollama installed and running locally
- NakenChat server running
- Internet connection (for initial Ollama model download)
- python3-tk (for GUI support; installed automatically by install_ubuntu.sh)
- customtkinter (for GUI; installed via requirements.txt)

## Installation

### Ubuntu (Recommended)

**Quick Installation:**
```bash
./install_ubuntu.sh
```
*This script will install all system and Python dependencies, including python3-tk for GUI support.*

**Manual Installation:**
See [INSTALL_UBUNTU.md](INSTALL_UBUNTU.md) for detailed Ubuntu installation instructions.

### Other Systems

1. **Install Python 3.8+ and pip**
2. **Install Ollama** from [ollama.ai](https://ollama.ai)
3. **Clone or download the bot files**
   ```bash
   cd NakenChatAIBot
   ```

4. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure the bot**
   - Edit `config.yaml` to match your setup
   - Update server addresses, bot name, and other settings

6. **Install Ollama models**
   ```bash
   # Install a model (e.g., llama2)
   ollama pull llama2
   
   # Or use a smaller model
   ollama pull llama2:7b
   ```

## Configuration

Edit `config.yaml` to customize the bot:

```yaml
# Bot Configuration
bot:
  name: "NakenBot"              # Bot's display name
  trigger: "NakenBot"           # Trigger word (case-insensitive)
  username: "NakenBot"          # Username in chat
  response_delay: 1.0        # Delay before responding (seconds)
  max_response_length: 200   # Maximum response length
  enable_context: true       # Enable conversation context
  context_length: 5          # Number of messages to remember

# Ollama Settings
ollama:
  host: "http://localhost"   # Ollama API host
  port: 11434               # Ollama API port
  model: "llama2"           # Default model to use
  timeout: 30               # API timeout (seconds)
  max_tokens: 150           # Maximum tokens per response
  temperature: 0.7          # Response creativity (0.0-1.0)

# NakenChat Server
nakenchat:
  host: "localhost"         # NakenChat server host
  port: 6666               # NakenChat server port
  reconnect_delay: 5       # Reconnection delay (seconds)
  max_reconnect_attempts: 10
```

## Usage

### Starting the Bot

#### Command Line Interface
```bash
python main.py
```

#### Graphical User Interface (Recommended)
```bash
python gui.py
# or
./start_gui.sh
```

The bot will:
1. Load configuration
2. Test connections to Ollama and NakenChat
3. Connect to the chat server
4. Start monitoring for messages

### Using the Bot

**Trigger the bot by mentioning its name:**
```
User: Mia, what's the weather like?
Bot: I don't have access to real-time weather data, but I can help you with other questions!
```

**Use bot commands:**
- `/help` - Show available commands
- `/model llama2` - Change AI model
- `/models` - List available models
- `/stats` - Show bot statistics
- `/context` - Show conversation context
- `/clear` - Clear your conversation context
- `/ping` - Test bot response
- `/info` - Show bot information
- `/reset` - Reset rate limiting

### Stopping the Bot

**CLI**: Press `Ctrl+C` to gracefully stop the bot.

**GUI**: Click the "Stop Bot" button or close the window.

## Bot Commands

| Command | Description |
|---------|-------------|
| `/help` | Show help information |
| `/model <name>` | Change AI model |
| `/models` | List available models |
| `/stats` | Show bot statistics |
| `/context` | Show conversation context |
| `/clear` | Clear your conversation context |
| `/ping` | Test bot response |
| `/info` | Show bot information |
| `/reset` | Reset rate limiting |

## Troubleshooting

### Common Issues

1. **"Failed to connect to Ollama API"**
   - Make sure Ollama is running: `ollama serve`
   - Check if the API is accessible: `curl http://localhost:11434/api/tags`

2. **"Failed to connect to NakenChat server"**
   - Verify NakenChat server is running
   - Check host and port in config.yaml
   - Ensure firewall allows the connection

3. **"Model not found"**
   - Install the model: `ollama pull <model_name>`
   - Check available models: `ollama list`
   - Update config.yaml with correct model name

4. **Bot not responding**
   - Check if trigger word is correct in config.yaml
   - Verify bot username matches config
   - Check logs for error messages

### Logs

The bot creates detailed logs:
- Console output with colors
- Log file: `bot.log` (if enabled in config)

Log levels:
- `DEBUG`: Detailed debugging information
- `INFO`: General information
- `WARNING`: Warning messages
- `ERROR`: Error messages

## Development

### Project Structure

```
NakenChatAIBot/
├── main.py                 # Main entry point (CLI)
├── gui.py                  # GUI application
├── config.yaml            # Configuration file
├── requirements.txt       # Python dependencies
├── start.sh               # CLI startup script
├── start_gui.sh           # GUI startup script
├── bot/                   # Bot components
│   ├── __init__.py
│   ├── chat_client.py     # NakenChat connection
│   ├── ollama_client.py   # Ollama API client
│   ├── message_processor.py # Message handling
│   ├── rate_limiter.py    # Rate limiting
│   ├── context_manager.py # Conversation context
│   └── command_handler.py # Bot commands
├── utils/                 # Utilities
│   ├── __init__.py
│   ├── logger.py          # Logging system
│   └── helpers.py         # Helper functions
└── README.md             # This file
```

### Adding New Commands

1. Add command method to `CommandHandler` class
2. Register command in `self.commands` dictionary
3. Update help text in `_cmd_help` method

### Adding New Features

The bot is modular and extensible:
- `OllamaClient`: Handle AI model interactions
- `NakenChatClient`: Manage chat server connection
- `MessageProcessor`: Process incoming messages
- `RateLimiter`: Control request frequency
- `ContextManager`: Maintain conversation history

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs for error messages
3. Create an issue with detailed information

---

**Happy chatting with your AI bot! 🤖** 