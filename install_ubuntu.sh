#!/bin/bash

# NakenChat AI Bot - Ubuntu Installation Script
# This script installs all dependencies needed to run the bot

set -e  # Exit on any error

echo "🚀 NakenChat AI Bot - Ubuntu Installation Script"
echo "================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root. Please run as a regular user."
   exit 1
fi

# Update package list
print_status "Updating package list..."
sudo apt update

# Install system dependencies
print_status "Installing system dependencies..."
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-tk \
    curl \
    wget \
    git \
    build-essential \
    pkg-config \
    libssl-dev \
    libffi-dev \
    python3-dev

print_success "System dependencies installed"

# Check Python version
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
REQUIRED_VERSION="3.8"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    print_error "Python 3.8 or higher is required. Found: $PYTHON_VERSION"
    print_status "Installing Python 3.8+..."
    sudo apt install -y python3.9 python3.9-pip python3.9-venv
    PYTHON_VERSION=$(python3.9 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
fi

print_success "Python $PYTHON_VERSION is available"

# Install Ollama
print_status "Checking Ollama installation..."
if ! command -v ollama &> /dev/null; then
    print_status "Ollama not found. Installing Ollama..."
    curl -fsSL https://ollama.ai/install.sh | sh
    
    # Add ollama to PATH for current session
    export PATH="$HOME/.local/bin:$PATH"
    
    # Add to .bashrc for future sessions
    if ! grep -q "ollama" ~/.bashrc; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
    fi
    
    print_success "Ollama installed successfully"
else
    OLLAMA_VERSION=$(ollama --version 2>/dev/null || echo "unknown")
    print_success "Ollama is already installed (version: $OLLAMA_VERSION)"
    
    # Check if Ollama service is running
    if pgrep -f "ollama serve" > /dev/null; then
        print_success "Ollama service is running"
    else
        print_warning "Ollama service is not running"
        print_status "You can start it with: ollama serve"
    fi
    
    # Show available models
    print_status "Checking available models..."
    if command -v ollama &> /dev/null; then
        MODELS=$(ollama list 2>/dev/null | grep -v "NAME" | wc -l)
        if [ "$MODELS" -gt 0 ]; then
            print_success "Found $MODELS installed model(s)"
            print_status "Available models:"
            ollama list 2>/dev/null | grep -v "NAME" | while read line; do
                if [ ! -z "$line" ]; then
                    echo "  - $line"
                fi
            done
        else
            print_warning "No models installed yet"
        fi
    fi
fi

# Create virtual environment
print_status "Creating Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_success "Virtual environment created"
else
    print_warning "Virtual environment already exists"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
print_status "Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    # Check if packages are already installed
    MISSING_PACKAGES=()
    while IFS= read -r package; do
        # Skip empty lines and comments
        [[ -z "$package" || "$package" =~ ^[[:space:]]*# ]] && continue
        
        # Extract package name (remove version specifiers)
        PACKAGE_NAME=$(echo "$package" | cut -d'=' -f1 | cut -d'<' -f1 | cut -d'>' -f1 | cut -d'~' -f1 | cut -d'!' -f1 | xargs)
        
        if ! pip show "$PACKAGE_NAME" &> /dev/null; then
            MISSING_PACKAGES+=("$package")
        fi
    done < requirements.txt
    
    if [ ${#MISSING_PACKAGES[@]} -eq 0 ]; then
        print_success "All Python dependencies are already installed"
    else
        print_status "Installing missing packages: ${MISSING_PACKAGES[*]}"
        pip install -r requirements.txt
        print_success "Python dependencies installed"
    fi
else
    print_warning "requirements.txt not found, installing common dependencies..."
    pip install customtkinter aiohttp pyyaml asyncio
    print_success "Common Python dependencies installed"
fi

# Install a default Ollama model
DEFAULT_MODEL="llama2:7b"
print_status "Checking for default model ($DEFAULT_MODEL)..."
if ollama list 2>/dev/null | grep -q "$DEFAULT_MODEL"; then
    print_success "Default model ($DEFAULT_MODEL) is already installed"
else
    print_status "Installing default Ollama model ($DEFAULT_MODEL)..."
    print_warning "This may take a while depending on your internet connection..."
    ollama pull $DEFAULT_MODEL
    print_success "Default model installed"
fi

# Create startup scripts
print_status "Creating startup scripts..."

# Make scripts executable
chmod +x start.sh start_gui.sh

# Create desktop shortcut
if command -v xdg-desktop-menu &> /dev/null; then
    print_status "Creating desktop shortcut..."
    cat > NakenChatAIBot.desktop << EOF
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

    # Copy to desktop
    cp NakenChatAIBot.desktop ~/Desktop/
    chmod +x ~/Desktop/NakenChatAIBot.desktop
    
    print_success "Desktop shortcut created"
fi

# Create systemd service (optional)
print_status "Creating systemd service (optional)..."
if command -v systemctl &> /dev/null; then
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

    print_success "Systemd service created"
    print_status "To enable the service: sudo systemctl enable nakenchat-ai-bot"
    print_status "To start the service: sudo systemctl start nakenchat-ai-bot"
fi

# Test installation
print_status "Testing installation..."

# Test Python
if python3 --version &> /dev/null; then
    print_success "Python is working"
else
    print_error "Python test failed"
    exit 1
fi

# Test Ollama
if ollama --version &> /dev/null; then
    print_success "Ollama is working"
else
    print_error "Ollama test failed"
    exit 1
fi

# Test Python dependencies
if python3 -c "import customtkinter, aiohttp, yaml" &> /dev/null; then
    print_success "Python dependencies are working"
else
    print_error "Python dependencies test failed"
    exit 1
fi

print_success "All tests passed!"

# Final instructions
echo ""
echo "🎉 Installation Complete!"
echo "========================"
echo ""

# Check if Ollama service is running
if pgrep -f "ollama serve" > /dev/null; then
    echo "✅ Ollama service is running"
else
    echo "⚠️  Ollama service is not running"
    echo "   Start it with: ollama serve"
fi

echo ""
echo "Next steps:"
echo "1. If Ollama is not running: ollama serve"
echo "2. Run the bot GUI: ./start_gui.sh"
echo "3. Or run CLI version: ./start.sh"
echo ""
echo "Configuration:"
echo "- Edit config.yaml to customize settings"
echo "- Use the GUI Settings button to configure the bot"
echo "- Install more models: ollama pull <model_name>"
echo ""
echo "Useful commands:"
echo "- List Ollama models: ollama list"
echo "- Install new model: ollama pull llama2"
echo "- Start GUI: python3 gui.py"
echo "- Start CLI: python3 main.py"
echo "- Check Ollama status: ollama ps"
echo "- Stop Ollama: ollama stop"
echo ""
echo "For help, see README.md or run: python3 main.py --help"
echo "" 