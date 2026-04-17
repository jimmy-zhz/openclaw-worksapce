#!/usr/bin/env python3
"""
OpenClaw PostgreSQL Storage Module
Stores conversations, messages, memory, and projects in PostgreSQL.
"""
import os
import json
from datetime import datetime
from typing import Optional, Dict, List, Any
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

# Load environment variables
load_dotenv()

class OpenClawDB:
    """PostgreSQL storage for OpenClaw conversations and data."""
    
    def __init__(self):
        self.db_host = os.getenv('DB_HOST')
        self.db_port = os.getenv('DB_PORT', '5432')
        self.db_name = os.getenv('DB_NAME', 'openclaw')
        self.db_user = os.getenv('DB_USER', 'postgres')
        self.db_password = os.getenv('DB_PASSWORD')
        
        if not self.db_password:
            raise ValueError("DB_PASSWORD not set in .env file")
        
        self.conn = None
        self.connect()
    
    def connect(self):
        """Establish database connection."""
        try:
            self.conn = psycopg2.connect(
                host=self.db_host,
                port=self.db_port,
                database=self.db_name,
                user=self.db_user,
                password=self.db_password,
                cursor_factory=RealDictCursor
            )
            # Enable JSONB support
            self.conn.autocommit = False
        except Exception as e:
            raise ConnectionError(f"Failed to connect to PostgreSQL: {e}")
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
    
    def save_conversation(self, session_id: str, machine: str, 
                         channel: Optional[str] = None, 
                         topic: Optional[str] = None) -> int:
        """
        Save a new conversation and return its ID.
        """
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO conversations (session_id, machine, channel, topic, start_time)
                VALUES (%s, %s, %s, %s, NOW())
                RETURNING id
            """, (session_id, machine, channel, topic))
            conv_id = cur.fetchone()['id']
            self.conn.commit()
            return conv_id
    
    def end_conversation(self, conversation_id: int, summary: Optional[str] = None):
        """Mark conversation as ended with optional summary."""
        with self.conn.cursor() as cur:
            cur.execute("""
                UPDATE conversations 
                SET end_time = NOW(), summary = %s, updated_at = NOW()
                WHERE id = %s
            """, (summary, conversation_id))
            self.conn.commit()
    
    def save_message(self, conversation_id: int, message_order: int, 
                    role: str, content: str, model: Optional[str] = None,
                    tokens: Optional[int] = None, tool_calls: Optional[Dict] = None,
                    tool_results: Optional[Dict] = None, metadata: Optional[Dict] = None):
        """Save a single message."""
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO messages 
                (conversation_id, message_order, role, content, model, tokens, 
                 tool_calls, tool_results, metadata)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                conversation_id, message_order, role, content, model, tokens,
                json.dumps(tool_calls) if tool_calls else None,
                json.dumps(tool_results) if tool_results else None,
                json.dumps(metadata) if metadata else None
            ))
            self.conn.commit()
    
    def get_conversation_messages(self, conversation_id: int) -> List[Dict]:
        """Get all messages for a conversation."""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT * FROM messages 
                WHERE conversation_id = %s 
                ORDER BY message_order
            """, (conversation_id,))
            return cur.fetchall()
    
    def find_conversation(self, session_id: str, machine: str) -> Optional[int]:
        """Find active conversation by session ID and machine."""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT id FROM conversations 
                WHERE session_id = %s AND machine = %s AND end_time IS NULL
                ORDER BY start_time DESC LIMIT 1
            """, (session_id, machine))
            result = cur.fetchone()
            return result['id'] if result else None
    
    def save_memory(self, key: str, content: str, category: Optional[str] = None,
                   importance: int = 1) -> int:
        """Save or update memory entry."""
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO memory (key, content, category, importance)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (key) DO UPDATE SET
                    content = EXCLUDED.content,
                    category = EXCLUDED.category,
                    importance = EXCLUDED.importance,
                    updated_at = NOW(),
                    last_accessed = NOW()
                RETURNING id
            """, (key, content, category, importance))
            memory_id = cur.fetchone()['id']
            self.conn.commit()
            return memory_id
    
    def get_memory(self, key: str) -> Optional[Dict]:
        """Get memory entry by key."""
        with self.conn.cursor() as cur:
            cur.execute("""
                UPDATE memory SET last_accessed = NOW() 
                WHERE key = %s
                RETURNING *
            """, (key,))
            result = cur.fetchone()
            if result:
                self.conn.commit()
            return result
    
    def search_memory(self, query: str, limit: int = 10) -> List[Dict]:
        """Search memory entries by content."""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT * FROM memory 
                WHERE content ILIKE %s
                ORDER BY importance DESC, last_accessed DESC
                LIMIT %s
            """, (f"%{query}%", limit))
            return cur.fetchall()
    
    def save_project_file(self, path: str, content: str) -> int:
        """Save or update project file."""
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO projects (path, content)
                VALUES (%s, %s)
                ON CONFLICT (path) DO UPDATE SET
                    content = EXCLUDED.content,
                    updated_at = NOW()
                RETURNING id
            """, (path, content))
            project_id = cur.fetchone()['id']
            self.conn.commit()
            return project_id
    
    def get_project_file(self, path: str) -> Optional[Dict]:
        """Get project file by path."""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT * FROM projects WHERE path = %s
            """, (path,))
            return cur.fetchone()
    
    def list_project_files(self, prefix: Optional[str] = None) -> List[Dict]:
        """List project files, optionally filtered by prefix."""
        with self.conn.cursor() as cur:
            if prefix:
                cur.execute("""
                    SELECT * FROM projects 
                    WHERE path LIKE %s
                    ORDER BY path
                """, (f"{prefix}%",))
            else:
                cur.execute("SELECT * FROM projects ORDER BY path")
            return cur.fetchall()
    
    def get_recent_conversations(self, machine: Optional[str] = None, 
                                limit: int = 20) -> List[Dict]:
        """Get recent conversations."""
        with self.conn.cursor() as cur:
            if machine:
                cur.execute("""
                    SELECT * FROM conversations 
                    WHERE machine = %s
                    ORDER BY start_time DESC
                    LIMIT %s
                """, (machine, limit))
            else:
                cur.execute("""
                    SELECT * FROM conversations 
                    ORDER BY start_time DESC
                    LIMIT %s
                """, (limit,))
            return cur.fetchall()
    
    def backup_file_to_db(self, file_path: str, db_path: Optional[str] = None):
        """
        Backup a local file to database.
        
        Args:
            file_path: Local file path to backup
            db_path: Database path (defaults to file_path relative to workspace)
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        db_path = db_path or file_path
        return self.save_project_file(db_path, content)
    
    def restore_file_from_db(self, db_path: str, file_path: Optional[str] = None):
        """
        Restore a file from database to local filesystem.
        
        Args:
            db_path: Database path of the file
            file_path: Local file path to restore to (defaults to db_path)
        """
        file_entry = self.get_project_file(db_path)
        if not file_entry:
            raise ValueError(f"File not found in database: {db_path}")
        
        file_path = file_path or db_path
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(file_entry['content'])
        
        return file_path

# Singleton instance
_db_instance = None

def get_db() -> OpenClawDB:
    """Get database instance (singleton)."""
    global _db_instance
    if _db_instance is None:
        _db_instance = OpenClawDB()
    return _db_instance

def test_db_connection():
    """Test database connection and basic operations."""
    db = get_db()
    try:
        # Test conversation
        conv_id = db.save_conversation("test-session", "mac", "webchat", "Database test")
        print(f"✓ Created conversation ID: {conv_id}")
        
        # Test messages
        db.save_message(conv_id, 1, "user", "Testing database storage")
        db.save_message(conv_id, 2, "assistant", "Database storage is working!")
        
        # Test memory
        mem_id = db.save_memory("test_key", "Test memory content", "test", 1)
        print(f"✓ Saved memory ID: {mem_id}")
        
        # Test project file
        proj_id = db.save_project_file("projects/test.md", "# Test Project\nThis is a test.")
        print(f"✓ Saved project file ID: {proj_id}")
        
        # Retrieve and verify
        messages = db.get_conversation_messages(conv_id)
        print(f"✓ Retrieved {len(messages)} messages")
        
        memory = db.get_memory("test_key")
        print(f"✓ Retrieved memory: {memory['key']}")
        
        project = db.get_project_file("projects/test.md")
        print(f"✓ Retrieved project file: {project['path']}")
        
        # Cleanup
        with db.conn.cursor() as cur:
            cur.execute("DELETE FROM conversations WHERE session_id = 'test-session'")
            cur.execute("DELETE FROM memory WHERE key = 'test_key'")
            cur.execute("DELETE FROM projects WHERE path = 'projects/test.md'")
            db.conn.commit()
        
        print("\n✅ All database operations working correctly!")
        
    finally:
        db.close()

if __name__ == "__main__":
    test_db_connection()