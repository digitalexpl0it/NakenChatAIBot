# Ubuntu Installation Guide for NakenChat AI Bot

This guide will help you install all dependencies needed to run the NakenChat AI Bot on Ubuntu.

## 🚀 Quick Installation (Recommended)

Run the automated installation script:

```bash
./install_ubuntu.sh
```

This script will install everything automatically and handles cases where:
- Ollama is already installed (checks version and running status)
- Models are already downloaded (skips re-download)
- Python dependencies are already installed (only installs missing packages)
- Virtual environment already exists

If you prefer manual installation, see the sections below.

## 📋 System Requirements

- **Ubuntu 20.04 LTS or newer**
- **Python 3.8 or higher**
- **At least 4GB RAM** (8GB+ recommended for larger models)
- **At least 10GB free disk space** (more for larger models)
- **Internet connection** for downloading models

## 🔧 Manual Installation Steps

### 1. Update System

```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Install System Dependencies

```bash
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    curl \
    wget \
    git \
    build-essential \
    pkg-config \
    libssl-dev \
    libffi-dev \
    python3-dev
```

### 3. Install Ollama

Ollama is required for running AI models locally.

```bash
# Check if Ollama is already installed
if command -v ollama &> /dev/null; then
    echo "Ollama is already installed: $(ollama --version)"
else
    # Download and install Ollama
    curl -fsSL https://ollama.ai/install.sh | sh
    
    # Add to PATH (for current session)
    export PATH="$HOME/.local/bin:$PATH"
    
    # Add to .bashrc for future sessions
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
    source ~/.bashrc
fi
```

**Verify Ollama installation:**
```bash
ollama --version
```

**Check if Ollama service is running:**
```bash
# Check status
ps aux | grep ollama

# Start if not running
ollama serve
```

### 4. Install Python Dependencies

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install Python dependencies
pip install -r requirements.txt
```

### 5. Install AI Models

Install at least one model for the bot to work:

```bash
# Check if models are already installed
ollama list

# Start Ollama service (if not running)
ollama serve

# Install a model (only if not already installed)
if ! ollama list | grep -q "llama2:7b"; then
    ollama pull llama2:7b    # Smaller, faster model
fi

# Alternative models:
# ollama pull llama2       # Larger, more capable model
# ollama pull mistral      # Good balance of speed and quality
```

### 6. Configure the Bot

Edit the configuration file:

```bash
nano config.yaml
```

Key settings to configure:
- **Bot name and trigger word**
- **NakenChat server address**
- **Ollama model selection**

## 🎯 Quick Start

1. **Start Ollama:**
   ```bash
   ollama serve
   ```

2. **Run the bot (choose one):**
   ```bash
   # GUI version (recommended)
   ./start_gui.sh
   
   # CLI version
   ./start.sh
   
   # Direct Python
   python3 gui.py
   ```

## 🔄 Handling Existing Installations

If you already have some components installed, the installation script will handle them gracefully:

### Already Have Ollama?
- ✅ Script detects existing Ollama installation
- ✅ Shows current version and running status
- ✅ Lists already installed models
- ✅ Skips re-installation

### Already Have Python Dependencies?
- ✅ Script checks which packages are missing
- ✅ Only installs required packages
- ✅ Skips already installed dependencies

### Already Have Models?
- ✅ Script checks for default model (llama2:7b)
- ✅ Skips model download if already present
- ✅ Shows list of available models

### Already Have Virtual Environment?
- ✅ Script detects existing venv
- ✅ Uses existing environment
- ✅ Only installs missing packages

## 🔧 Troubleshooting

### Common Issues

#### 1. "Ollama command not found"
```bash
# Add to PATH manually
export PATH="$HOME/.local/bin:$PATH"
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

#### 2. "Python dependencies not found"
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

#### 3. "CustomTkinter import error"
```bash
# Install system dependencies
sudo apt install -y python3-tk

# Reinstall CustomTkinter
pip uninstall customtkinter
pip install customtkinter
```

#### 4. "Permission denied" errors
```bash
# Make scripts executable
chmod +x start.sh start_gui.sh install_ubuntu.sh
```

#### 5. "Ollama connection failed"
```bash
# Check if Ollama is running
ps aux | grep ollama

# Start Ollama if not running
ollama serve

# Test connection
curl http://localhost:11434/api/tags
```

#### 6. "Model not found"
```bash
# List available models
ollama list

# Install a model
ollama pull llama2:7b
```

### Performance Issues

#### Low Memory
- Use smaller models: `llama2:7b`, `mistral:7b`
- Close other applications
- Increase swap space if needed

#### Slow Responses
- Use faster models: `llama2:7b`, `mistral:7b`
- Reduce `max_tokens` in config
- Use SSD storage for models

## 📦 Package Management

### Using Virtual Environment (Recommended)

```bash
# Activate environment
source venv/bin/activate

# Install new package
pip install package_name

# Update requirements.txt
pip freeze > requirements.txt
```

### System-wide Installation (Not Recommended)

```bash
# Install packages system-wide
sudo pip3 install -r requirements.txt
```

## 🔄 Updating

### Update the Bot
```bash
# Pull latest changes
git pull

# Update dependencies
source venv/bin/activate
pip install -r requirements.txt
```

### Update Ollama
```bash
# Update Ollama
curl -fsSL https://ollama.ai/install.sh | sh
```

### Update Models
```bash
# Update specific model
ollama pull llama2:latest

# List models
ollama list
```

## 🛠️ Advanced Configuration

### Systemd Service (Auto-start)

Create a systemd service for automatic startup:

```bash
sudo tee /etc/systemd/system/nakenchat-ai-bot.service > /dev/null << EOF
[Unit]
Description=NakenChat AI Bot
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
ExecStart=$(pwd)/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl enable nakenchat-ai-bot
sudo systemctl start nakenchat-ai-bot
```

### Desktop Shortcut

Create a desktop shortcut:

```bash
cat > ~/Desktop/NakenChatAIBot.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=NakenChat AI Bot
Comment=AI Bot for NakenChat with GUI
Exec=$(pwd)/start_gui.sh
Icon=terminal
Terminal=false
Categories=Network;Chat;
EOF

chmod +x ~/Desktop/NakenChatAIBot.desktop
```

## 📊 System Monitoring

### Check Resource Usage
```bash
# Monitor CPU and memory
htop

# Check disk space
df -h

# Monitor Ollama
ps aux | grep ollama
```

### Logs
```bash
# View bot logs
tail -f bot.log

# View system logs
journalctl -u nakenchat-ai-bot -f
```

## 🆘 Getting Help

1. **Check the logs** in `bot.log`
2. **Test connections** using the GUI settings
3. **Verify Ollama** is running: `ollama list`
4. **Check Python** dependencies: `pip list`
5. **Review configuration** in `config.yaml`

## 📚 Additional Resources

- [Ollama Documentation](https://ollama.ai/docs)
- [CustomTkinter Documentation](https://github.com/TomSchimansky/CustomTkinter)
- [Python asyncio Documentation](https://docs.python.org/3/library/asyncio.html)
- [NakenChat Documentation](https://github.com/nakenchat)

---

**Need more help?** Check the main README.md or create an issue in the repository. 