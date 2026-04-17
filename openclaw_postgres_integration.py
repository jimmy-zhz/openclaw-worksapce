#!/usr/bin/env python3
"""
OpenClaw PostgreSQL Integration
Bridges OpenClaw conversations to PostgreSQL storage.
"""
import os
import json
import sys
from datetime import datetime
from pathlib import Path

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db_storage import get_db

class OpenClawPostgresIntegration:
    """
    Integrates OpenClaw with PostgreSQL storage.
    
    This class provides methods to:
    1. Store conversations and messages in PostgreSQL
    2. Sync memory files to database
    3. Sync project files to database
    4. Provide search and retrieval from database
    """
    
    def __init__(self, workspace_root: str = None):
        self.workspace_root = workspace_root or os.path.dirname(os.path.abspath(__file__))
        self.db = get_db()
        self.current_conversation_id = None
        self.current_session_id = None
        self.current_machine = self._detect_machine()
    
    def _detect_machine(self) -> str:
        """Detect which machine we're running on."""
        # Check for machine-specific directories
        if os.path.exists(os.path.join(self.workspace_root, "local-mac", "machine-id")):
            return "mac"
        elif os.path.exists(os.path.join(self.workspace_root, "server-oracle", "machine-id")):
            return "server"
        else:
            # Default based on hostname or environment
            import socket
            hostname = socket.gethostname().lower()
            if "mac" in hostname or "jimmy" in hostname:
                return "mac"
            else:
                return "server"
    
    def start_conversation(self, session_id: str, channel: str = None, topic: str = None):
        """Start a new conversation in database."""
        self.current_session_id = session_id
        self.current_conversation_id = self.db.save_conversation(
            session_id, self.current_machine, channel, topic
        )
        print(f"📝 Started conversation {self.current_conversation_id} "
              f"(session: {session_id}, machine: {self.current_machine})")
        return self.current_conversation_id
    
    def save_message(self, role: str, content: str, model: str = None, 
                    tokens: int = None, tool_calls: dict = None, 
                    tool_results: dict = None, metadata: dict = None):
        """Save a message to the current conversation."""
        if not self.current_conversation_id:
            raise ValueError("No active conversation. Call start_conversation first.")
        
        # Get next message order
        messages = self.db.get_conversation_messages(self.current_conversation_id)
        next_order = len(messages) + 1
        
        self.db.save_message(
            self.current_conversation_id, next_order, role, content,
            model, tokens, tool_calls, tool_results, metadata
        )
        
        print(f"💬 Saved {role} message (order: {next_order}, "
              f"tokens: {tokens or 'N/A'})")
    
    def end_conversation(self, summary: str = None):
        """End the current conversation."""
        if self.current_conversation_id:
            self.db.end_conversation(self.current_conversation_id, summary)
            print(f"✅ Ended conversation {self.current_conversation_id}")
            self.current_conversation_id = None
            self.current_session_id = None
    
    def sync_memory_file(self, file_path: str):
        """Sync a memory file to database."""
        abs_path = os.path.join(self.workspace_root, file_path)
        if not os.path.exists(abs_path):
            print(f"⚠️  File not found: {file_path}")
            return
        
        with open(abs_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Use file path as key, but sanitize
        key = file_path.replace('/', '_').replace('\\', '_')
        self.db.save_memory(key, content, category="file")
        print(f"🧠 Synced memory file: {file_path} -> key: {key}")
    
    def sync_project_file(self, file_path: str):
        """Sync a project file to database."""
        abs_path = os.path.join(self.workspace_root, file_path)
        if not os.path.exists(abs_path):
            print(f"⚠️  File not found: {file_path}")
            return
        
        with open(abs_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        self.db.save_project_file(file_path, content)
        print(f"📁 Synced project file: {file_path}")
    
    def sync_directory(self, directory: str, file_pattern: str = "*.md"):
        """Sync all files in a directory matching pattern."""
        import glob
        abs_dir = os.path.join(self.workspace_root, directory)
        
        if not os.path.exists(abs_dir):
            print(f"⚠️  Directory not found: {directory}")
            return
        
        pattern = os.path.join(abs_dir, "**", file_pattern)
        files = glob.glob(pattern, recursive=True)
        
        for file_path in files:
            # Convert to relative path
            rel_path = os.path.relpath(file_path, self.workspace_root)
            if "memory/" in rel_path:
                self.sync_memory_file(rel_path)
            else:
                self.sync_project_file(rel_path)
    
    def search_conversations(self, query: str = None, limit: int = 10):
        """Search recent conversations."""
        conversations = self.db.get_recent_conversations(
            machine=self.current_machine, limit=limit
        )
        
        results = []
        for conv in conversations:
            if query:
                # Get messages and check if query appears
                messages = self.db.get_conversation_messages(conv['id'])
                content = " ".join([msg['content'] for msg in messages])
                if query.lower() in content.lower():
                    results.append(conv)
            else:
                results.append(conv)
        
        return results
    
    def get_conversation_context(self, conversation_id: int, limit_messages: int = 20):
        """Get conversation context for continuing a discussion."""
        messages = self.db.get_conversation_messages(conversation_id)
        
        # Format as conversation history
        context = []
        for msg in messages[-limit_messages:]:  # Get most recent messages
            context.append({
                "role": msg['role'],
                "content": msg['content']
            })
        
        return context
    
    def backup_workspace(self):
        """Backup important workspace files to database."""
        print("💾 Backing up workspace to PostgreSQL...")
        
        # Backup memory files
        memory_dir = os.path.join(self.workspace_root, "memory")
        if os.path.exists(memory_dir):
            self.sync_directory("memory", "*.md")
        
        # Backup project files
        projects_dir = os.path.join(self.workspace_root, "projects")
        if os.path.exists(projects_dir):
            self.sync_directory("projects", "*.md")
        
        # Backup important root files
        root_files = ["AGENTS.md", "SOUL.md", "TOOLS.md", "IDENTITY.md", 
                     "RULES.md", "CONTEXT.md", "HEARTBEAT.md"]
        for file in root_files:
            file_path = os.path.join(self.workspace_root, file)
            if os.path.exists(file_path):
                self.sync_project_file(file)
        
        print("✅ Workspace backup complete!")
    
    def restore_file(self, db_path: str, local_path: str = None):
        """Restore a file from database to local filesystem."""
        local_path = local_path or db_path
        restored_path = self.db.restore_file_from_db(db_path, local_path)
        print(f"🔄 Restored file: {db_path} -> {restored_path}")
        return restored_path

# Example usage
def example_usage():
    """Example of how to use the integration."""
    integration = OpenClawPostgresIntegration()
    
    print(f"Running on: {integration.current_machine}")
    
    # Start a conversation
    session_id = f"session-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    integration.start_conversation(session_id, channel="webchat", topic="PostgreSQL integration")
    
    # Save some messages
    integration.save_message("user", "Hello, can you store this conversation in PostgreSQL?")
    integration.save_message("assistant", "Yes! I'm saving our conversation to the database right now.", 
                           model="deepseek-chat", tokens=150)
    
    # Sync some files
    integration.sync_memory_file("MEMORY.md")
    integration.sync_project_file("projects/ai-diploma/data-science-crisp-dm.md")
    
    # Backup entire workspace
    integration.backup_workspace()
    
    # End conversation
    integration.end_conversation("Tested PostgreSQL integration")
    
    # Search conversations
    print("\n📊 Recent conversations:")
    recent = integration.search_conversations(limit=5)
    for conv in recent:
        print(f"  - {conv['topic']} ({conv['start_time']})")

if __name__ == "__main__":
    example_usage()