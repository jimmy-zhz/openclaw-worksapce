#!/usr/bin/env python3
"""
Test PostgreSQL connection and create conversation storage schema.
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database credentials
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD')

if not all([DB_HOST, DB_PORT, DB_NAME, DB_PASSWORD]):
    print("Error: Missing database credentials in .env file")
    print(f"DB_HOST: {DB_HOST}")
    print(f"DB_PORT: {DB_PORT}")
    print(f"DB_NAME: {DB_NAME}")
    print(f"DB_PASSWORD: {'*' * len(DB_PASSWORD) if DB_PASSWORD else 'NOT SET'}")
    sys.exit(1)

print(f"Testing connection to PostgreSQL at {DB_HOST}:{DB_PORT}")

try:
    import psycopg2
    print("✓ psycopg2 is available")
except ImportError:
    print("Installing psycopg2-binary...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "psycopg2-binary"])
    import psycopg2
    print("✓ psycopg2-binary installed")

# Try to connect
try:
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user="postgres",  # Default superuser
        password=DB_PASSWORD,
        connect_timeout=10
    )
    print("✓ Successfully connected to PostgreSQL")
    
    # Create cursor
    cur = conn.cursor()
    
    # Check if openclaw database exists
    cur.execute("SELECT 1 FROM pg_database WHERE datname = 'openclaw'")
    if cur.fetchone():
        print("✓ Database 'openclaw' already exists")
    else:
        print("Creating database 'openclaw'...")
        # Need to connect to postgres database to create new database
        conn.close()
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database="postgres",
            user="postgres",
            password=DB_PASSWORD
        )
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("CREATE DATABASE openclaw")
        print("✓ Database 'openclaw' created")
        
        # Reconnect to openclaw database
        conn.close()
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database="openclaw",
            user="postgres",
            password=DB_PASSWORD
        )
        cur = conn.cursor()
    
    # Create tables
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
    
    # Memory table (for MEMORY.md content)
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
    
    # Projects table (for projects/ content)
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
    
    # Commit changes
    conn.commit()
    
    # Test insert
    print("\nTesting insert...")
    cur.execute("""
    INSERT INTO conversations (session_id, machine, topic) 
    VALUES (%s, %s, %s)
    RETURNING id
    """, ("test-session-001", "mac", "PostgreSQL setup test"))
    
    conv_id = cur.fetchone()[0]
    
    cur.execute("""
    INSERT INTO messages (conversation_id, message_order, role, content)
    VALUES (%s, %s, %s, %s)
    """, (conv_id, 1, 'user', 'Testing PostgreSQL storage'))
    
    cur.execute("""
    INSERT INTO messages (conversation_id, message_order, role, content)
    VALUES (%s, %s, %s, %s)
    """, (conv_id, 2, 'assistant', 'PostgreSQL storage is working!'))
    
    conn.commit()
    print(f"✓ Test data inserted (conversation ID: {conv_id})")
    
    # Verify
    cur.execute("SELECT COUNT(*) FROM conversations")
    conv_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM messages")
    msg_count = cur.fetchone()[0]
    
    print(f"\nDatabase status:")
    print(f"  Conversations: {conv_count}")
    print(f"  Messages: {msg_count}")
    
    # Clean up test data
    cur.execute("DELETE FROM conversations WHERE session_id = 'test-session-001'")
    conn.commit()
    print("✓ Cleaned up test data")
    
    conn.close()
    print("\n✅ PostgreSQL setup complete! Database is ready for OpenClaw conversation storage.")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nTroubleshooting tips:")
    print("1. Check if PostgreSQL is running on the server")
    print("2. Verify firewall allows connections on port 5432")
    print("3. Check if password is correct")
    print("4. Ensure 'postgres' user exists and has permissions")
    sys.exit(1)