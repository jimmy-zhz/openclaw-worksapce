#!/usr/bin/env python3
"""
Simple Real-time OpenClaw Auto-Logger
Logs current conversation to PostgreSQL in real-time.
"""
import os
import sys
import time
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db_storage import get_db
from openclaw_postgres_integration import OpenClawPostgresIntegration

class SimpleAutoLogger:
    """
    Simple auto-logger that logs the current conversation.
    Runs alongside OpenClaw and logs messages as they happen.
    """
    
    def __init__(self):
        self.integration = OpenClawPostgresIntegration()
        self.current_conversation_id = None
        self.session_counter = 1
        
        print("🤖 Simple Auto-Logger Started")
        print(f"Running on: {self.integration.current_machine}")
    
    def start_new_conversation(self, topic: str = "Auto-logged conversation"):
        """Start logging a new conversation."""
        session_id = f"auto-session-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        self.current_conversation_id = self.integration.start_conversation(
            session_id, "webchat", topic
        )
        print(f"📝 Started auto-logging conversation {self.current_conversation_id}")
        return self.current_conversation_id
    
    def log_user_message(self, content: str):
        """Log a user message."""
        if not self.current_conversation_id:
            self.start_new_conversation("User message")
        
        self.integration.save_message("user", content, model="deepseek-chat")
        print(f"👤 Logged user message ({len(content)} chars)")
    
    def log_assistant_message(self, content: str, tokens: int = None):
        """Log an assistant message."""
        if not self.current_conversation_id:
            self.start_new_conversation("Assistant message")
        
        self.integration.save_message("assistant", content, model="deepseek-chat", tokens=tokens)
        print(f"🤖 Logged assistant message ({len(content)} chars, tokens: {tokens or 'N/A'})")
    
    def end_conversation(self, summary: str = "Auto-logged conversation ended"):
        """End the current conversation."""
        if self.current_conversation_id:
            self.integration.end_conversation(summary)
            print(f"✅ Ended conversation {self.current_conversation_id}")
            self.current_conversation_id = None
    
    def log_current_conversation(self):
        """
        Log the current conversation we're having right now.
        This is a manual trigger for testing.
        """
        print("🔄 Logging current conversation...")
        
        # Start new conversation
        conv_id = self.start_new_conversation("Manual logging test")
        
        # Log some example messages (in real use, these would come from OpenClaw)
        self.log_user_message("Can you automatically log our conversations to PostgreSQL?")
        self.log_assistant_message("Yes! I'm now automatically logging our conversation to PostgreSQL. Every message will be saved.", tokens=75)
        self.log_user_message("That's great! Now I can search past conversations.")
        self.log_assistant_message("Exactly! You can query the database with: SELECT * FROM messages WHERE content LIKE '%PostgreSQL%'", tokens=85)
        
        # End conversation
        self.end_conversation("Test of automatic logging")
        
        return conv_id
    
    def run_interactive(self):
        """Run in interactive mode for testing."""
        print("\n" + "="*50)
        print("Simple Auto-Logger Interactive Mode")
        print("="*50)
        print("Commands:")
        print("  start [topic] - Start new conversation")
        print("  user <message> - Log user message")
        print("  assistant <message> - Log assistant message")
        print("  end [summary] - End conversation")
        print("  status - Show current status")
        print("  exit - Exit")
        print("="*50)
        
        while True:
            try:
                command = input("\nauto-logger> ").strip()
                
                if not command:
                    continue
                
                if command == "exit":
                    if self.current_conversation_id:
                        self.end_conversation("Interactive session ended")
                    print("👋 Goodbye!")
                    break
                
                elif command == "status":
                    print(f"Current conversation: {self.current_conversation_id or 'None'}")
                    if self.current_conversation_id:
                        messages = self.integration.db.get_conversation_messages(self.current_conversation_id)
                        print(f"Messages logged: {len(messages)}")
                
                elif command.startswith("start"):
                    parts = command.split(" ", 1)
                    topic = parts[1] if len(parts) > 1 else "Interactive conversation"
                    self.start_new_conversation(topic)
                
                elif command.startswith("user "):
                    message = command[5:].strip()
                    if message:
                        self.log_user_message(message)
                    else:
                        print("❌ Please provide a message")
                
                elif command.startswith("assistant "):
                    message = command[10:].strip()
                    if message:
                        # Estimate tokens (roughly 4 chars per token)
                        tokens = len(message) // 4
                        self.log_assistant_message(message, tokens)
                    else:
                        print("❌ Please provide a message")
                
                elif command.startswith("end"):
                    parts = command.split(" ", 1)
                    summary = parts[1] if len(parts) > 1 else "Conversation ended"
                    self.end_conversation(summary)
                
                else:
                    print(f"❌ Unknown command: {command}")
                    print("Available: start, user, assistant, end, status, exit")
            
            except KeyboardInterrupt:
                print("\n\n🛑 Interrupted")
                if self.current_conversation_id:
                    self.end_conversation("Interrupted by user")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Simple OpenClaw Auto-Logger")
    parser.add_argument("--test", action="store_true", help="Run a test conversation")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    
    args = parser.parse_args()
    
    logger = SimpleAutoLogger()
    
    if args.test:
        logger.log_current_conversation()
    elif args.interactive:
        logger.run_interactive()
    else:
        print("Please specify --test or --interactive")
        print("Example: python3 simple_auto_logger.py --test")

if __name__ == "__main__":
    main()