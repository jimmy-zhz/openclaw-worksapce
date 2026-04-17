#!/usr/bin/env python3
"""
Automatic OpenClaw Conversation Logger
Monitors OpenClaw session logs and auto-saves to PostgreSQL.
"""
import os
import json
import time
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional
import hashlib

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db_storage import get_db

class AutoLogger:
    """Automatically logs OpenClaw conversations to PostgreSQL."""
    
    def __init__(self):
        self.db = get_db()
        self.openclaw_dir = Path("/Users/jimmy/.openclaw")
        self.sessions_dir = self.openclaw_dir / "agents" / "main" / "sessions"
        self.processed_files = set()
        self.current_sessions = {}  # session_id -> conversation_id
        
        print(f"🔍 Monitoring OpenClaw sessions in: {self.sessions_dir}")
        
        # Load already processed files
        self._load_processed_state()
    
    def _load_processed_state(self):
        """Load state of already processed files."""
        state_file = Path(__file__).parent / ".auto_logger_state"
        if state_file.exists():
            try:
                with open(state_file, 'r') as f:
                    self.processed_files = set(json.load(f))
                print(f"📋 Loaded {len(self.processed_files)} processed files")
            except:
                self.processed_files = set()
    
    def _save_processed_state(self):
        """Save state of processed files."""
        state_file = Path(__file__).parent / ".auto_logger_state"
        with open(state_file, 'w') as f:
            json.dump(list(self.processed_files), f)
    
    def _get_file_hash(self, filepath: Path) -> str:
        """Get hash of file to detect changes."""
        with open(filepath, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    
    def _process_session_file(self, filepath: Path):
        """Process a session JSONL file."""
        if str(filepath) in self.processed_files:
            return
        
        print(f"📄 Processing: {filepath.name}")
        
        try:
            with open(filepath, 'r') as f:
                lines = f.readlines()
            
            session_id = None
            conversation_id = None
            message_count = 0
            
            for line in lines:
                try:
                    data = json.loads(line.strip())
                    
                    # Extract session ID
                    if data.get('type') == 'session':
                        session_id = data.get('id')
                        if session_id and session_id not in self.current_sessions:
                            # Start new conversation in database
                            conversation_id = self.db.save_conversation(
                                session_id, 
                                "mac",  # Assuming Mac for now
                                "webchat", 
                                "Auto-logged conversation"
                            )
                            self.current_sessions[session_id] = conversation_id
                            print(f"  🆕 Started conversation {conversation_id} for session {session_id[:8]}...")
                    
                    # Process messages
                    elif data.get('type') == 'message':
                        message_data = data.get('message', {})
                        role = message_data.get('role')
                        content_parts = message_data.get('content', [])
                        
                        # Extract text content
                        text_content = ""
                        for part in content_parts:
                            if isinstance(part, dict) and part.get('type') == 'text':
                                text_content += part.get('text', '')
                            elif isinstance(part, str):
                                text_content += part
                        
                        if role and text_content and conversation_id:
                            # Clean up content (remove metadata markers)
                            clean_content = self._clean_message_content(text_content)
                            
                            if clean_content and len(clean_content.strip()) > 10:  # Skip very short messages
                                # Get next message order
                                messages = self.db.get_conversation_messages(conversation_id)
                                next_order = len(messages) + 1
                                
                                # Save to database
                                self.db.save_message(
                                    conversation_id, next_order, role, clean_content,
                                    model="deepseek-chat",  # Default, could extract from logs
                                    tokens=len(clean_content.split())  # Rough estimate
                                )
                                message_count += 1
                
                except json.JSONDecodeError:
                    continue
                except Exception as e:
                    print(f"  ⚠️ Error processing line: {e}")
                    continue
            
            if message_count > 0:
                print(f"  ✅ Saved {message_count} messages")
                
                # Mark conversation as ended (since we're processing completed session)
                if conversation_id:
                    self.db.end_conversation(conversation_id, "Auto-logged from session file")
                    print(f"  🏁 Ended conversation {conversation_id}")
            
            # Mark file as processed
            self.processed_files.add(str(filepath))
            self._save_processed_state()
            
        except Exception as e:
            print(f"❌ Error processing {filepath}: {e}")
    
    def _clean_message_content(self, content: str) -> str:
        """Clean message content by removing metadata markers."""
        # Remove Sender metadata blocks
        lines = content.split('\n')
        cleaned_lines = []
        skip_next = False
        
        for line in lines:
            if line.strip().startswith('Sender (untrusted metadata):'):
                skip_next = True
                continue
            elif skip_next and line.strip().startswith('```json'):
                skip_next = True
                continue
            elif skip_next and line.strip().startswith('```'):
                skip_next = False
                continue
            elif skip_next:
                continue
            elif line.strip().startswith('[Fri') and 'CDT]' in line:
                # Remove timestamp prefix like "[Fri 2026-04-17 11:58 CDT]"
                parts = line.split(']', 1)
                if len(parts) > 1:
                    cleaned_lines.append(parts[1].strip())
                continue
            else:
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines).strip()
    
    def _find_new_session_files(self):
        """Find new or updated session files."""
        if not self.sessions_dir.exists():
            print(f"⚠️ Sessions directory not found: {self.sessions_dir}")
            return []
        
        session_files = []
        for filepath in self.sessions_dir.glob("*.jsonl"):
            if filepath.is_file():
                session_files.append(filepath)
        
        # Sort by modification time (newest first)
        session_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        return session_files
    
    def process_existing_sessions(self):
        """Process all existing session files."""
        print("🔄 Processing existing session files...")
        session_files = self._find_new_session_files()
        
        for filepath in session_files:
            self._process_session_file(filepath)
        
        print(f"✅ Processed {len(session_files)} session files")
    
    def monitor_new_sessions(self, interval_seconds: int = 5):
        """Monitor for new session files."""
        print(f"👁️ Monitoring for new sessions (checking every {interval_seconds}s)...")
        print("Press Ctrl+C to stop")
        
        last_check = time.time()
        processed_count = 0
        
        try:
            while True:
                current_time = time.time()
                if current_time - last_check >= interval_seconds:
                    session_files = self._find_new_session_files()
                    
                    for filepath in session_files:
                        if str(filepath) not in self.processed_files:
                            self._process_session_file(filepath)
                            processed_count += 1
                    
                    last_check = current_time
                
                time.sleep(1)
                
        except KeyboardInterrupt:
            print(f"\n🛑 Stopped. Processed {processed_count} new sessions.")
    
    def run_once(self):
        """Run one processing cycle."""
        self.process_existing_sessions()
    
    def run_continuous(self):
        """Run continuous monitoring."""
        self.process_existing_sessions()
        self.monitor_new_sessions()

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Auto-log OpenClaw conversations to PostgreSQL")
    parser.add_argument("--once", action="store_true", help="Process existing sessions once and exit")
    parser.add_argument("--monitor", action="store_true", help="Continuous monitoring (default)")
    parser.add_argument("--interval", type=int, default=5, help="Check interval in seconds (default: 5)")
    
    args = parser.parse_args()
    
    logger = AutoLogger()
    
    if args.once:
        logger.run_once()
    else:
        logger.run_continuous()

if __name__ == "__main__":
    main()