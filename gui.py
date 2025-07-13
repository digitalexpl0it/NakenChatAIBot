#!/usr/bin/env python3
"""
NakenChat AI Bot GUI

A modern desktop interface for the NakenChat AI Bot using CustomTkinter.
"""

import asyncio
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox
import customtkinter as ctk
from datetime import datetime
import sys
import yaml
from pathlib import Path
import aiohttp
import json

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from main import NakenChatAIBot
from utils.logger import setup_logger

class SettingsDialog:
    """Comprehensive settings dialog for the bot"""
    
    def __init__(self, parent, config_path="config.yaml"):
        self.parent = parent
        self.config_path = config_path
        self.config = None
        self.ollama_models = []
        
        # Load current config
        self.load_config()
        
        # Create dialog
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("Bot Settings")
        self.dialog.geometry("700x600")
        self.dialog.transient(parent)
        self.dialog.resizable(True, True)
        
        # Wait for dialog to be visible before grabbing
        self.dialog.update_idletasks()
        self.dialog.grab_set()
        
        # Setup dialog
        self.setup_dialog()
        
        # Load Ollama models
        self.load_ollama_models()
    
    def load_config(self):
        """Load configuration from file"""
        try:
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load config: {e}")
            self.config = {}
    
    def save_config(self):
        """Save configuration to file"""
        try:
            # Update config with current values
            self.update_config_from_ui()
            
            with open(self.config_path, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False, indent=2)
            
            messagebox.showinfo("Success", "Settings saved successfully!")
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save config: {e}")
            return False
    
    def setup_dialog(self):
        """Setup the settings dialog"""
        # Configure grid
        self.dialog.grid_columnconfigure(0, weight=1)
        self.dialog.grid_rowconfigure(1, weight=1)
        
        # Title
        title = ctk.CTkLabel(self.dialog, text="Bot Settings", font=ctk.CTkFont(size=20, weight="bold"))
        title.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        # Create notebook for tabs
        self.notebook = ctk.CTkTabview(self.dialog)
        self.notebook.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        
        # Add tabs
        self.setup_bot_tab()
        self.setup_ollama_tab()
        self.setup_chat_tab()
        self.setup_behavior_tab()
        
        # Buttons
        self.setup_buttons()
    
    def setup_bot_tab(self):
        """Setup bot configuration tab"""
        bot_tab = self.notebook.add("Bot")
        bot_tab.grid_columnconfigure(1, weight=1)
        
        # Bot name
        ctk.CTkLabel(bot_tab, text="Bot Name:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.bot_name_entry = ctk.CTkEntry(bot_tab)
        self.bot_name_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        self.bot_name_entry.insert(0, self.config.get('bot', {}).get('name', 'AI Bot'))
        
        # Trigger word
        ctk.CTkLabel(bot_tab, text="Trigger Word:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.trigger_entry = ctk.CTkEntry(bot_tab)
        self.trigger_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        self.trigger_entry.insert(0, self.config.get('bot', {}).get('trigger', 'AI Bot'))
        
        # Username
        ctk.CTkLabel(bot_tab, text="Username:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.username_entry = ctk.CTkEntry(bot_tab)
        self.username_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
        self.username_entry.insert(0, self.config.get('bot', {}).get('username', 'AI Bot'))
        
        # Response delay
        ctk.CTkLabel(bot_tab, text="Response Delay (seconds):").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.delay_entry = ctk.CTkEntry(bot_tab)
        self.delay_entry.grid(row=3, column=1, padx=10, pady=5, sticky="ew")
        self.delay_entry.insert(0, str(self.config.get('bot', {}).get('response_delay', 1.0)))
        
        # Max response length
        ctk.CTkLabel(bot_tab, text="Max Response Length:").grid(row=4, column=0, padx=10, pady=5, sticky="w")
        self.max_length_entry = ctk.CTkEntry(bot_tab)
        self.max_length_entry.grid(row=4, column=1, padx=10, pady=5, sticky="ew")
        self.max_length_entry.insert(0, str(self.config.get('bot', {}).get('max_response_length', 200)))
        
        # Context settings
        ctk.CTkLabel(bot_tab, text="Context Settings:").grid(row=5, column=0, padx=10, pady=5, sticky="w")
        
        context_frame = ctk.CTkFrame(bot_tab)
        context_frame.grid(row=6, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        context_frame.grid_columnconfigure(1, weight=1)
        
        self.enable_context_var = tk.BooleanVar(value=self.config.get('bot', {}).get('enable_context', True))
        context_check = ctk.CTkCheckBox(context_frame, text="Enable Context", variable=self.enable_context_var)
        context_check.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        ctk.CTkLabel(context_frame, text="Context Length:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.context_length_entry = ctk.CTkEntry(context_frame)
        self.context_length_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        self.context_length_entry.insert(0, str(self.config.get('bot', {}).get('context_length', 5)))
    
    def setup_ollama_tab(self):
        """Setup Ollama configuration tab"""
        ollama_tab = self.notebook.add("Ollama")
        ollama_tab.grid_columnconfigure(1, weight=1)
        
        # Host
        ctk.CTkLabel(ollama_tab, text="Host:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.ollama_host_entry = ctk.CTkEntry(ollama_tab)
        self.ollama_host_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        self.ollama_host_entry.insert(0, self.config.get('ollama', {}).get('host', 'http://localhost'))
        
        # Port
        ctk.CTkLabel(ollama_tab, text="Port:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.ollama_port_entry = ctk.CTkEntry(ollama_tab)
        self.ollama_port_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        self.ollama_port_entry.insert(0, str(self.config.get('ollama', {}).get('port', 11434)))
        
        # Model selection
        ctk.CTkLabel(ollama_tab, text="Model:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        
        model_frame = ctk.CTkFrame(ollama_tab)
        model_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        model_frame.grid_columnconfigure(0, weight=1)
        
        self.model_var = tk.StringVar(value=self.config.get('ollama', {}).get('model', 'llama2'))
        self.model_menu = ctk.CTkOptionMenu(model_frame, variable=self.model_var, values=["Loading..."])
        self.model_menu.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        
        refresh_btn = ctk.CTkButton(model_frame, text="Refresh Models", command=self.load_ollama_models, width=120)
        refresh_btn.grid(row=0, column=1, padx=10, pady=5)
        
        # Model parameters
        ctk.CTkLabel(ollama_tab, text="Max Tokens:").grid(row=4, column=0, padx=10, pady=5, sticky="w")
        self.max_tokens_entry = ctk.CTkEntry(ollama_tab)
        self.max_tokens_entry.grid(row=4, column=1, padx=10, pady=5, sticky="ew")
        self.max_tokens_entry.insert(0, str(self.config.get('ollama', {}).get('max_tokens', 150)))
        
        ctk.CTkLabel(ollama_tab, text="Temperature:").grid(row=5, column=0, padx=10, pady=5, sticky="w")
        self.temperature_entry = ctk.CTkEntry(ollama_tab)
        self.temperature_entry.grid(row=5, column=1, padx=10, pady=5, sticky="ew")
        self.temperature_entry.insert(0, str(self.config.get('ollama', {}).get('temperature', 0.7)))
        
        ctk.CTkLabel(ollama_tab, text="Timeout (seconds):").grid(row=6, column=0, padx=10, pady=5, sticky="w")
        self.timeout_entry = ctk.CTkEntry(ollama_tab)
        self.timeout_entry.grid(row=6, column=1, padx=10, pady=5, sticky="ew")
        self.timeout_entry.insert(0, str(self.config.get('ollama', {}).get('timeout', 30)))
        
        # System prompt
        ctk.CTkLabel(ollama_tab, text="System Prompt:").grid(row=7, column=0, padx=10, pady=5, sticky="w")
        self.system_prompt_text = ctk.CTkTextbox(ollama_tab, height=100)
        self.system_prompt_text.grid(row=8, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        self.system_prompt_text.insert("1.0", self.config.get('ollama', {}).get('system_prompt', ''))
    
    def setup_chat_tab(self):
        """Setup NakenChat configuration tab"""
        chat_tab = self.notebook.add("Chat Server")
        chat_tab.grid_columnconfigure(1, weight=1)
        
        # Host
        ctk.CTkLabel(chat_tab, text="Host:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.chat_host_entry = ctk.CTkEntry(chat_tab)
        self.chat_host_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        self.chat_host_entry.insert(0, self.config.get('nakenchat', {}).get('host', 'localhost'))
        
        # Port
        ctk.CTkLabel(chat_tab, text="Port:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.chat_port_entry = ctk.CTkEntry(chat_tab)
        self.chat_port_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        self.chat_port_entry.insert(0, str(self.config.get('nakenchat', {}).get('port', 6666)))
        
        # Reconnect settings
        ctk.CTkLabel(chat_tab, text="Reconnect Delay (seconds):").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.reconnect_delay_entry = ctk.CTkEntry(chat_tab)
        self.reconnect_delay_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
        self.reconnect_delay_entry.insert(0, str(self.config.get('nakenchat', {}).get('reconnect_delay', 5)))
        
        ctk.CTkLabel(chat_tab, text="Max Reconnect Attempts:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.max_reconnect_entry = ctk.CTkEntry(chat_tab)
        self.max_reconnect_entry.grid(row=3, column=1, padx=10, pady=5, sticky="ew")
        self.max_reconnect_entry.insert(0, str(self.config.get('nakenchat', {}).get('max_reconnect_attempts', 10)))
    
    def setup_behavior_tab(self):
        """Setup behavior configuration tab"""
        behavior_tab = self.notebook.add("Behavior")
        behavior_tab.grid_columnconfigure(1, weight=1)
        
        # Rate limiting
        ctk.CTkLabel(behavior_tab, text="Rate Limiting:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        rate_frame = ctk.CTkFrame(behavior_tab)
        rate_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        rate_frame.grid_columnconfigure(1, weight=1)
        
        self.enable_rate_limit_var = tk.BooleanVar(value=self.config.get('behavior', {}).get('rate_limit', {}).get('enabled', True))
        rate_check = ctk.CTkCheckBox(rate_frame, text="Enable Rate Limiting", variable=self.enable_rate_limit_var)
        rate_check.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        ctk.CTkLabel(rate_frame, text="Max Requests:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.max_requests_entry = ctk.CTkEntry(rate_frame)
        self.max_requests_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        self.max_requests_entry.insert(0, str(self.config.get('behavior', {}).get('rate_limit', {}).get('max_requests', 10)))
        
        ctk.CTkLabel(rate_frame, text="Time Window (seconds):").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.time_window_entry = ctk.CTkEntry(rate_frame)
        self.time_window_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
        self.time_window_entry.insert(0, str(self.config.get('behavior', {}).get('rate_limit', {}).get('time_window', 60)))
        
        # Commands
        self.enable_commands_var = tk.BooleanVar(value=self.config.get('behavior', {}).get('enable_commands', True))
        commands_check = ctk.CTkCheckBox(behavior_tab, text="Enable Bot Commands", variable=self.enable_commands_var)
        commands_check.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="w")
        
        # User tracking
        self.enable_user_tracking_var = tk.BooleanVar(value=self.config.get('behavior', {}).get('user_tracking', True))
        tracking_check = ctk.CTkCheckBox(behavior_tab, text="Enable User Tracking", variable=self.enable_user_tracking_var)
        tracking_check.grid(row=3, column=0, columnspan=2, padx=10, pady=5, sticky="w")
        
        # Logging
        ctk.CTkLabel(behavior_tab, text="Logging Level:").grid(row=4, column=0, padx=10, pady=5, sticky="w")
        self.log_level_var = tk.StringVar(value=self.config.get('logging', {}).get('level', 'INFO'))
        log_level_menu = ctk.CTkOptionMenu(behavior_tab, variable=self.log_level_var, 
                                          values=['DEBUG', 'INFO', 'WARNING', 'ERROR'])
        log_level_menu.grid(row=4, column=1, padx=10, pady=5, sticky="ew")
        
        self.enable_console_log_var = tk.BooleanVar(value=self.config.get('logging', {}).get('console', True))
        console_check = ctk.CTkCheckBox(behavior_tab, text="Console Logging", variable=self.enable_console_log_var)
        console_check.grid(row=5, column=0, columnspan=2, padx=10, pady=5, sticky="w")
        
        # File logging enable/disable
        self.enable_file_log_var = tk.BooleanVar(value=self.config.get('logging', {}).get('file_enabled', True))
        file_check = ctk.CTkCheckBox(behavior_tab, text="File Logging", variable=self.enable_file_log_var)
        file_check.grid(row=6, column=0, columnspan=2, padx=10, pady=5, sticky="w")
        
        # Log file name entry
        ctk.CTkLabel(behavior_tab, text="Log File Name:").grid(row=7, column=0, padx=10, pady=5, sticky="w")
        self.log_file_entry = ctk.CTkEntry(behavior_tab)
        self.log_file_entry.grid(row=7, column=1, padx=10, pady=5, sticky="ew")
        self.log_file_entry.insert(0, str(self.config.get('logging', {}).get('file', 'bot.log')))
    
    def setup_buttons(self):
        """Setup dialog buttons"""
        button_frame = ctk.CTkFrame(self.dialog)
        button_frame.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="ew")
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        button_frame.grid_columnconfigure(2, weight=1)
        
        save_btn = ctk.CTkButton(button_frame, text="Save", command=self.save_config)
        save_btn.grid(row=0, column=0, padx=10, pady=10)
        
        cancel_btn = ctk.CTkButton(button_frame, text="Cancel", command=self.dialog.destroy)
        cancel_btn.grid(row=0, column=1, padx=10, pady=10)
        
        test_btn = ctk.CTkButton(button_frame, text="Test Connection", command=self.test_connection)
        test_btn.grid(row=0, column=2, padx=10, pady=10)
    
    async def get_ollama_models(self):
        """Get available Ollama models"""
        try:
            host = self.ollama_host_entry.get()
            port = self.ollama_port_entry.get()
            url = f"{host}:{port}/api/tags"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return [model['name'] for model in data.get('models', [])]
                    else:
                        return []
        except Exception as e:
            print(f"Error getting Ollama models: {e}")
            return []
    
    def load_ollama_models(self):
        """Load Ollama models in a separate thread"""
        def load_models():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                models = loop.run_until_complete(self.get_ollama_models())
                loop.close()
                
                if models:
                    self.ollama_models = models
                    self.model_menu.configure(values=models)
                    if self.model_var.get() not in models and models:
                        self.model_var.set(models[0])
                else:
                    self.model_menu.configure(values=["No models found"])
            except Exception as e:
                self.model_menu.configure(values=["Error loading models"])
                print(f"Error loading models: {e}")
        
        threading.Thread(target=load_models, daemon=True).start()
    
    def update_config_from_ui(self):
        """Update config dictionary with current UI values"""
        # Bot settings
        if 'bot' not in self.config:
            self.config['bot'] = {}
        
        self.config['bot']['name'] = self.bot_name_entry.get()
        self.config['bot']['trigger'] = self.trigger_entry.get()
        self.config['bot']['username'] = self.username_entry.get()
        self.config['bot']['response_delay'] = float(self.delay_entry.get())
        self.config['bot']['max_response_length'] = int(self.max_length_entry.get())
        self.config['bot']['enable_context'] = self.enable_context_var.get()
        self.config['bot']['context_length'] = int(self.context_length_entry.get())
        
        # Ollama settings
        if 'ollama' not in self.config:
            self.config['ollama'] = {}
        
        self.config['ollama']['host'] = self.ollama_host_entry.get()
        self.config['ollama']['port'] = int(self.ollama_port_entry.get())
        self.config['ollama']['model'] = self.model_var.get()
        self.config['ollama']['max_tokens'] = int(self.max_tokens_entry.get())
        self.config['ollama']['temperature'] = float(self.temperature_entry.get())
        self.config['ollama']['timeout'] = int(self.timeout_entry.get())
        self.config['ollama']['system_prompt'] = self.system_prompt_text.get("1.0", "end-1c")
        
        # Chat settings
        if 'nakenchat' not in self.config:
            self.config['nakenchat'] = {}
        
        self.config['nakenchat']['host'] = self.chat_host_entry.get()
        self.config['nakenchat']['port'] = int(self.chat_port_entry.get())
        self.config['nakenchat']['reconnect_delay'] = int(self.reconnect_delay_entry.get())
        self.config['nakenchat']['max_reconnect_attempts'] = int(self.max_reconnect_entry.get())
        
        # Behavior settings
        if 'behavior' not in self.config:
            self.config['behavior'] = {}
        if 'rate_limit' not in self.config['behavior']:
            self.config['behavior']['rate_limit'] = {}
        
        self.config['behavior']['rate_limit']['enabled'] = self.enable_rate_limit_var.get()
        self.config['behavior']['rate_limit']['max_requests'] = int(self.max_requests_entry.get())
        self.config['behavior']['rate_limit']['time_window'] = int(self.time_window_entry.get())
        self.config['behavior']['enable_commands'] = self.enable_commands_var.get()
        self.config['behavior']['user_tracking'] = self.enable_user_tracking_var.get()
        
        # Logging settings
        if 'logging' not in self.config:
            self.config['logging'] = {}
        
        self.config['logging']['level'] = self.log_level_var.get()
        self.config['logging']['console'] = self.enable_console_log_var.get()
        self.config['logging']['file_enabled'] = self.enable_file_log_var.get()
        self.config['logging']['file'] = self.log_file_entry.get()
    
    def test_connection(self):
        """Test Ollama connection"""
        def test():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                host = self.ollama_host_entry.get()
                port = self.ollama_port_entry.get()
                url = f"{host}:{port}/api/tags"
                
                async def test_ollama():
                    async with aiohttp.ClientSession() as session:
                        async with session.get(url) as response:
                            return response.status == 200
                
                success = loop.run_until_complete(test_ollama())
                loop.close()
                
                if success:
                    messagebox.showinfo("Success", "Ollama connection successful!")
                else:
                    messagebox.showerror("Error", "Failed to connect to Ollama")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Connection test failed: {e}")
        
        threading.Thread(target=test, daemon=True).start()

class BotGUI:
    """Modern GUI for NakenChat AI Bot"""
    
    def __init__(self):
        # Setup CustomTkinter
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Create main window
        self.root = ctk.CTk()
        self.root.title("NakenChat AI Bot")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Bot instance
        self.bot = None
        self.bot_thread = None
        self.running = False
        
        # GUI elements
        self.setup_gui()
        
        # Custom logger for GUI
        self.setup_gui_logger()
        
        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_gui(self):
        """Setup the GUI layout"""
        # Configure grid
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # Left sidebar
        self.setup_sidebar()
        
        # Main content area
        self.setup_main_content()
        
        # Status bar
        self.setup_status_bar()
    
    def setup_sidebar(self):
        """Setup the left sidebar"""
        sidebar = ctk.CTkFrame(self.root, width=250)
        sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=10, pady=10)
        sidebar.grid_rowconfigure(4, weight=1)
        
        # Title
        title = ctk.CTkLabel(sidebar, text="NakenChat AI Bot", font=ctk.CTkFont(size=20, weight="bold"))
        title.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # Control buttons
        self.start_btn = ctk.CTkButton(sidebar, text="Start Bot", command=self.start_bot, height=40)
        self.start_btn.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        self.stop_btn = ctk.CTkButton(sidebar, text="Stop Bot", command=self.stop_bot, height=40, state="disabled")
        self.stop_btn.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        
        # Settings button
        settings_btn = ctk.CTkButton(sidebar, text="Settings", command=self.open_settings, height=35)
        settings_btn.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        
        # Stats frame
        stats_frame = ctk.CTkFrame(sidebar)
        stats_frame.grid(row=4, column=0, padx=20, pady=20, sticky="nsew")
        stats_frame.grid_columnconfigure(0, weight=1)
        
        stats_label = ctk.CTkLabel(stats_frame, text="Statistics", font=ctk.CTkFont(size=16, weight="bold"))
        stats_label.grid(row=0, column=0, padx=15, pady=(15, 10))
        
        self.stats_text = ctk.CTkTextbox(stats_frame, height=200, width=200)
        self.stats_text.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="ew")
        
        # Clear logs button
        clear_btn = ctk.CTkButton(sidebar, text="Clear Logs", command=self.clear_logs, height=35)
        clear_btn.grid(row=5, column=0, padx=20, pady=10, sticky="ew")
    
    def setup_main_content(self):
        """Setup the main content area"""
        main_frame = ctk.CTkFrame(self.root)
        main_frame.grid(row=0, column=1, sticky="nsew", padx=(0, 10), pady=10)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)
        
        # Logs label
        logs_label = ctk.CTkLabel(main_frame, text="Bot Logs", font=ctk.CTkFont(size=18, weight="bold"))
        logs_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        # Logs text area
        self.logs_text = ctk.CTkTextbox(main_frame, font=ctk.CTkFont(size=12))
        self.logs_text.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        
        # Scroll to bottom
        self.logs_text.see("end")
    
    def setup_status_bar(self):
        """Setup the status bar"""
        status_frame = ctk.CTkFrame(self.root, height=30)
        status_frame.grid(row=1, column=1, sticky="ew", padx=(0, 10), pady=(0, 10))
        status_frame.grid_columnconfigure(0, weight=1)
        
        self.status_label = ctk.CTkLabel(status_frame, text="Ready", font=ctk.CTkFont(size=12))
        self.status_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        self.connection_label = ctk.CTkLabel(status_frame, text="Disconnected", font=ctk.CTkFont(size=12))
        self.connection_label.grid(row=0, column=1, padx=10, pady=5, sticky="e")
    
    def setup_gui_logger(self):
        """Setup custom logger that writes to GUI"""
        class GUILogHandler:
            def __init__(self, gui):
                self.gui = gui
            
            def write(self, message):
                try:
                    if message.strip():
                        self.gui.add_log(message.strip())
                except Exception:
                    # GUI might be destroyed, ignore logging errors
                    pass
            
            def flush(self):
                pass
        
        # Redirect stdout to GUI
        sys.stdout = GUILogHandler(self)
    
    def add_log(self, message):
        """Add a log message to the GUI"""
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            formatted_message = f"[{timestamp}] {message}\n"
            
            # Add to logs text area
            self.logs_text.insert("end", formatted_message)
            self.logs_text.see("end")
            
            # Limit log size
            lines = self.logs_text.get("1.0", "end").split('\n')
            if len(lines) > 1000:
                # Remove first 200 lines
                self.logs_text.delete("1.0", "201.0")
        except Exception:
            # GUI might be destroyed, ignore logging errors
            pass
    
    def update_stats(self):
        """Update statistics display"""
        if not self.bot or not self.running:
            stats = "Bot not running"
        else:
            try:
                # Get stats from bot components
                rate_stats = self.bot.rate_limiter.get_user_stats("global")
                context_stats = self.bot.context_manager.get_context_stats()
                processing_stats = self.bot.message_processor.get_processing_stats()
                
                stats = f"""Status: Running
Model: {self.bot.config['ollama']['model']}
Rate Limit: {rate_stats['global_requests']}/{rate_stats['global_limit']}
Active Users: {context_stats['total_users']}
Context Messages: {context_stats['global_context_length']}
Active Tasks: {processing_stats['active_tasks']}"""
            except Exception as e:
                stats = f"Error getting stats: {e}"
        
        self.stats_text.delete("1.0", "end")
        self.stats_text.insert("1.0", stats)
    
    def start_bot(self):
        """Start the bot in a separate thread"""
        if self.running:
            return
        
        self.running = True
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.status_label.configure(text="Starting...")
        
        # Start bot in separate thread
        self.bot_thread = threading.Thread(target=self.run_bot, daemon=True)
        self.bot_thread.start()
        
        # Start stats update timer
        self.update_stats_timer()
    
    def run_bot(self):
        """Run the bot (called in separate thread)"""
        try:
            # Create bot instance
            self.bot = NakenChatAIBot()
            
            # Load config
            if not self.bot.load_config():
                self.add_log("ERROR: Failed to load configuration")
                return
            
            # Setup logging
            self.bot.setup_logging()
            
            # Setup components
            self.bot.setup_components()
            
            # Run bot
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Update status
            self.root.after(0, lambda: self.status_label.configure(text="Running"))
            self.root.after(0, lambda: self.connection_label.configure(text="Connected"))
            
            # Run the bot
            loop.run_until_complete(self.bot.start())
            
        except Exception as e:
            self.add_log(f"ERROR: {e}")
            self.root.after(0, self.stop_bot)
    
    def stop_bot(self):
        """Stop the bot"""
        if not self.running:
            return
        
        self.running = False
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.status_label.configure(text="Stopping...")
        self.connection_label.configure(text="Disconnected")
        
        # Stop the bot properly
        if self.bot:
            try:
                # Create a new event loop for stopping
                stop_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(stop_loop)
                
                # Stop the bot with a timeout
                try:
                    stop_loop.run_until_complete(asyncio.wait_for(self.bot.stop(), timeout=5.0))
                except asyncio.TimeoutError:
                    self.add_log("Warning: Bot stop timed out, forcing shutdown")
                except Exception as e:
                    self.add_log(f"Error stopping bot: {e}")
                finally:
                    stop_loop.close()
                    
            except Exception as e:
                self.add_log(f"Error stopping bot: {e}")
        
        self.status_label.configure(text="Stopped")
    
    def clear_logs(self):
        """Clear the logs display"""
        self.logs_text.delete("1.0", "end")
        self.add_log("Logs cleared")
    
    def open_settings(self):
        """Open settings dialog"""
        SettingsDialog(self.root)
    
    def update_stats_timer(self):
        """Update stats periodically"""
        if self.running:
            self.update_stats()
            self.root.after(2000, self.update_stats_timer)  # Update every 2 seconds
    
    def on_closing(self):
        """Handle window closing"""
        if self.running:
            self.add_log("Shutting down bot...")
            self.stop_bot()
            # Give a moment for cleanup
            self.root.after(100, self.root.destroy)
        else:
            self.root.destroy()
    
    def run(self):
        """Start the GUI"""
        self.root.mainloop()

def main():
    """Main entry point for GUI"""
    app = BotGUI()
    app.run()

if __name__ == "__main__":
    main() 