#!/usr/bin/env python3
"""
Test script to debug the settings dialog
"""

import yaml
import customtkinter as ctk
from gui import SettingsDialog

def test_config_loading():
    """Test if config loads properly"""
    try:
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        print("✅ Config loaded successfully")
        print(f"Bot section: {config.get('bot', {})}")
        print(f"Ollama section: {config.get('ollama', {})}")
        return config
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        return None

def test_settings_dialog():
    """Test the settings dialog"""
    print("Testing settings dialog...")
    
    # Setup CustomTkinter
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    # Create root window
    root = ctk.CTk()
    root.title("Settings Test")
    root.geometry("300x200")
    
    def open_settings():
        print("Opening settings dialog...")
        try:
            dialog = SettingsDialog(root)
            print("✅ Settings dialog created successfully")
        except Exception as e:
            print(f"❌ Error creating settings dialog: {e}")
            import traceback
            traceback.print_exc()
    
    # Add button to open settings
    btn = ctk.CTkButton(root, text="Open Settings", command=open_settings)
    btn.pack(pady=20)
    
    root.mainloop()

if __name__ == "__main__":
    print("=== Settings Dialog Test ===")
    
    # Test config loading
    config = test_config_loading()
    
    if config:
        # Test settings dialog
        test_settings_dialog()
    else:
        print("Cannot test settings dialog without valid config") 