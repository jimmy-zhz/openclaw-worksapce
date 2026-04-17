#!/usr/bin/env python3
"""
Setup OpenClaw database tables in the correct database.
"""
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'openclaw')  # Changed from 'postgres' to 'openclaw'
DB_PASSWORD = os.getenv('DB_PASSWORD')

print(f"Setting up database: {DB_NAME}@{DB_HOST}:{DB_PORT}")

try:
    # Connect to the database
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user="postgres",
        password=DB_PASSWORD
    )
    conn.autocommit = True
    cur = conn.cursor()
    
    print("✓ Connected to database")
    
    # Drop tables if they exist (for clean setup)
    print("\nCreating tables...")
    
    # Conversations table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS conversations (
        id SERIAL PRIMARY KEY,
        session_id VARCHAR(255) NOT NULL,
        machine VARCHAR(50) NOT NULL,
        channel VARCHAR(50),
        start_time TIMESTAMP DEFAULT NOW(),
        end_time TIMESTAMP,
        topic VARCHAR(255),
        summary TEXT,
        metadata JSONB DEFAULT '{}'::jsonb,
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW()
    )
    """)
    print("✓ Created 'conversations' table")
    
    # Messages table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id SERIAL PRIMARY KEY,
        conversation_id INTEGER REFERENCES conversations(id) ON DELETE CASCADE,
        message_order INTEGER NOT NULL,
        role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
        content TEXT NOT NULL,
        tokens INTEGER,
        model VARCHAR(100),
        tool_calls JSONB,
        tool_results JSONB,
        metadata JSONB DEFAULT '{}'::jsonb,
        created_at TIMESTAMP DEFAULT NOW(),
        UNIQUE(conversation_id, message_order)
    )
    """)
    print("✓ Created 'messages' table")
    
    # Memory table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS memory (
        id SERIAL PRIMARY KEY,
        key VARCHAR(255) UNIQUE NOT NULL,
        content TEXT NOT NULL,
        category VARCHAR(100),
        importance INTEGER DEFAULT 1,
        last_accessed TIMESTAMP DEFAULT NOW(),
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW()
    )
    """)
    print("✓ Created 'memory' table")
    
    # Projects table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS projects (
        id SERIAL PRIMARY KEY,
        path VARCHAR(500) UNIQUE NOT NULL,
        content TEXT NOT NULL,
        last_modified TIMESTAMP DEFAULT NOW(),
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW()
    )
    """)
    print("✓ Created 'projects' table")
    
    # Create indexes
    cur.execute("CREATE INDEX IF NOT EXISTS idx_conversations_session ON conversations(session_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_conversations_machine ON conversations(machine)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_conversations_start_time ON conversations(start_time)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_messages_role ON messages(role)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_memory_key ON memory(key)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_memory_category ON memory(category)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_projects_path ON projects(path)")
    
    print("✓ Created indexes")
    
    # Test insert
    print("\nTesting with sample data...")
    cur.execute("""
    INSERT INTO conversations (session_id, machine, channel, topic) 
    VALUES (%s, %s, %s, %s)
    RETURNING id
    """, ("setup-test", "mac", "cli", "Database setup"))
    
    conv_id = cur.fetchone()[0]
    
    cur.execute("""
    INSERT INTO messages (conversation_id, message_order, role, content)
    VALUES (%s, %s, %s, %s), (%s, %s, %s, %s)
    """, (conv_id, 1, 'user', 'Is the database setup complete?',
          conv_id, 2, 'assistant', 'Yes, PostgreSQL is ready for OpenClaw!'))
    
    cur.execute("""
    INSERT INTO memory (key, content, category)
    VALUES (%s, %s, %s)
    """, ("database_setup", "PostgreSQL database configured on 2026-04-17", "system"))
    
    cur.execute("""
    INSERT INTO projects (path, content)
    VALUES (%s, %s)
    """, ("README.md", "# OpenClaw Database\nStoring conversations in PostgreSQL"))
    
    # Verify
    cur.execute("SELECT COUNT(*) FROM conversations")
    conv_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM messages")
    msg_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM memory")
    mem_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM projects")
    proj_count = cur.fetchone()[0]
    
    print(f"\nDatabase status:")
    print(f"  Conversations: {conv_count}")
    print(f"  Messages: {msg_count}")
    print(f"  Memory entries: {mem_count}")
    print(f"  Project files: {proj_count}")
    
    # Cleanup test data
    cur.execute("DELETE FROM conversations WHERE session_id = 'setup-test'")
    cur.execute("DELETE FROM memory WHERE key = 'database_setup'")
    cur.execute("DELETE FROM projects WHERE path = 'README.md'")
    
    print("✓ Cleaned up test data")
    
    conn.close()
    print("\n✅ Database setup complete! Ready for OpenClaw storage.")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()