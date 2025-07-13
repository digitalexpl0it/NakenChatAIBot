#!/usr/bin/env python3
"""
Demo GUI for NakenChat AI Bot

This script shows the GUI interface without requiring the full bot setup.
Useful for testing the interface design.
"""

import customtkinter as ctk
from datetime import datetime
import threading
import time

class DemoGUI:
    """Demo GUI for NakenChat AI Bot"""
    
    def __init__(self):
        # Setup CustomTkinter
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Create main window
        self.root = ctk.CTk()
        self.root.title("NakenChat AI Bot - Demo")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Demo state
        self.running = False
        
        # Setup GUI
        self.setup_gui()
        
        # Start demo logs
        self.start_demo_logs()
    
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
        
        subtitle = ctk.CTkLabel(sidebar, text="Demo Mode", font=ctk.CTkFont(size=12), text_color="gray")
        subtitle.grid(row=1, column=0, padx=20, pady=(0, 20))
        
        # Control buttons
        self.start_btn = ctk.CTkButton(sidebar, text="Start Demo", command=self.start_demo, height=40)
        self.start_btn.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        
        self.stop_btn = ctk.CTkButton(sidebar, text="Stop Demo", command=self.stop_demo, height=40, state="disabled")
        self.stop_btn.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        
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
        
        # Settings button
        settings_btn = ctk.CTkButton(sidebar, text="Settings", command=self.open_settings, height=35)
        settings_btn.grid(row=6, column=0, padx=20, pady=10, sticky="ew")
    
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
        
        self.status_label = ctk.CTkLabel(status_frame, text="Demo Mode", font=ctk.CTkFont(size=12))
        self.status_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        self.connection_label = ctk.CTkLabel(status_frame, text="Disconnected", font=ctk.CTkFont(size=12))
        self.connection_label.grid(row=0, column=1, padx=10, pady=5, sticky="e")
    
    def add_log(self, message):
        """Add a log message to the GUI"""
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
    
    def update_stats(self):
        """Update statistics display"""
        if not self.running:
            stats = "Demo not running"
        else:
            stats = f"""Status: Running (Demo)
Model: llama2 (Demo)
Rate Limit: 5/10 requests
Active Users: 3
Context Messages: 12
Active Tasks: 1
Demo Mode: Enabled"""
        
        self.stats_text.delete("1.0", "end")
        self.stats_text.insert("1.0", stats)
    
    def start_demo(self):
        """Start the demo"""
        if self.running:
            return
        
        self.running = True
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.status_label.configure(text="Demo Running...")
        self.connection_label.configure(text="Connected (Demo)")
        
        # Simulate bot startup
        self.add_log("INFO: Logging system initialized")
        self.add_log("INFO: Rate limiter initialized")
        self.add_log("INFO: Context manager initialized")
        self.add_log("INFO: Ollama client initialized")
        self.add_log("INFO: Command handler initialized")
        self.add_log("INFO: Message processor initialized")
        self.add_log("INFO: Chat client initialized")
        self.add_log("INFO: Starting NakenChat AI Bot...")
        self.add_log("INFO: Testing connections...")
        self.add_log("INFO: Available models: ['llama2:7b', 'deepseek-r1:latest']")
        self.add_log("INFO: All connections tested successfully")
        self.add_log("INFO: Connecting to NakenChat server at localhost:6666")
        self.add_log("INFO: Successfully connected to NakenChat server")
        self.add_log("INFO: Sent .n Mia to set bot name")
        self.add_log("INFO: Bot started successfully!")
        self.add_log("INFO: Bot name: Mia")
        self.add_log("INFO: Trigger word: Mia")
        self.add_log("INFO: Current model: llama2:7b")
        
        # Start demo logs
        self.demo_thread = threading.Thread(target=self.demo_logs, daemon=True)
        self.demo_thread.start()
        
        # Start stats update timer
        self.update_stats_timer()
    
    def stop_demo(self):
        """Stop the demo"""
        if not self.running:
            return
        
        self.running = False
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.status_label.configure(text="Demo Stopped")
        self.connection_label.configure(text="Disconnected")
        
        self.add_log("INFO: Stopping bot...")
        self.add_log("INFO: Bot stopped successfully")
    
    def clear_logs(self):
        """Clear the logs display"""
        self.logs_text.delete("1.0", "end")
        self.add_log("INFO: Logs cleared")
    
    def open_settings(self):
        """Open settings window"""
        settings_window = ctk.CTkToplevel(self.root)
        settings_window.title("Bot Settings - Demo")
        settings_window.geometry("600x500")
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # Settings content
        settings_label = ctk.CTkLabel(settings_window, text="Settings (Demo Mode)", font=ctk.CTkFont(size=20, weight="bold"))
        settings_label.pack(pady=20)
        
        # Create notebook for tabs
        notebook = ctk.CTkTabview(settings_window)
        notebook.pack(padx=20, pady=20, fill="both", expand=True)
        
        # Bot tab
        bot_tab = notebook.add("Bot")
        bot_tab.grid_columnconfigure(1, weight=1)
        
        # Bot settings
        ctk.CTkLabel(bot_tab, text="Bot Name:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        name_entry = ctk.CTkEntry(bot_tab)
        name_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        name_entry.insert(0, "Mia")
        
        ctk.CTkLabel(bot_tab, text="Trigger Word:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        trigger_entry = ctk.CTkEntry(bot_tab)
        trigger_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        trigger_entry.insert(0, "Mia")
        
        # Ollama tab
        ollama_tab = notebook.add("Ollama")
        ollama_tab.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(ollama_tab, text="Model:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        model_menu = ctk.CTkOptionMenu(ollama_tab, values=["llama2", "llama2:7b", "mistral", "codellama"])
        model_menu.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        model_menu.set("llama2")
        
        ctk.CTkLabel(ollama_tab, text="Host:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        host_entry = ctk.CTkEntry(ollama_tab)
        host_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        host_entry.insert(0, "http://localhost")
        
        # Buttons
        button_frame = ctk.CTkFrame(settings_window)
        button_frame.pack(padx=20, pady=(0, 20), fill="x")
        
        save_btn = ctk.CTkButton(button_frame, text="Save (Demo)", command=lambda: print("Demo: Settings saved!"))
        save_btn.pack(side="left", padx=10, pady=10)
        
        cancel_btn = ctk.CTkButton(button_frame, text="Cancel", command=settings_window.destroy)
        cancel_btn.pack(side="right", padx=10, pady=10)
    
    def demo_logs(self):
        """Generate demo log messages"""
        # Demo messages
        demo_messages = [
            "DEBUG: Received message from user1: Hello Mia",
            "INFO: Generating response for user1: Hello Mia",
            "INFO: Response sent to user1",
            "DEBUG: Received message from user2: Mia, what's the weather?",
            "INFO: Generating response for user2: Mia, what's the weather?",
            "INFO: Response sent to user2",
            "DEBUG: Received message from user3: /help",
            "INFO: Command from user3: help",
            "INFO: Response sent to user3",
            "DEBUG: Received message from user1: Mia, tell me a joke",
            "INFO: Generating response for user1: Mia, tell me a joke",
            "INFO: Response sent to user1"
        ]
        
        i = 0
        while self.running:
            if i < len(demo_messages):
                self.root.after(0, lambda msg=demo_messages[i]: self.add_log(msg))
                i += 1
            else:
                i = 0  # Loop back to start
            
            time.sleep(3)  # Add a message every 3 seconds
    
    def start_demo_logs(self):
        """Start initial demo logs"""
        self.add_log("INFO: NakenChat AI Bot Demo Started")
        self.add_log("INFO: This is a demonstration of the GUI interface")
        self.add_log("INFO: Click 'Start Demo' to see the bot in action")
        self.add_log("INFO: The demo will simulate bot activity")
    
    def update_stats_timer(self):
        """Update stats periodically"""
        if self.running:
            self.update_stats()
            self.root.after(2000, self.update_stats_timer)  # Update every 2 seconds
    
    def run(self):
        """Start the GUI"""
        self.root.mainloop()

def main():
    """Main entry point for demo GUI"""
    app = DemoGUI()
    app.run()

if __name__ == "__main__":
    main() 