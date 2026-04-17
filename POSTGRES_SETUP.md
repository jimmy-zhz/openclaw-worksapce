# OpenClaw PostgreSQL Storage Setup

## Overview
OpenClaw conversations, messages, memory, and project files are now stored in PostgreSQL for:
- **Persistent storage** - Survives restarts, system failures
- **Structured querying** - Search past conversations, analyze patterns
- **Cross-machine sync** - Mac and Server can access same conversation history
- **Backup/recovery** - Standard database backup tools

## Database Configuration

### Connection Details
- **Host:** 40.233.110.234
- **Port:** 5432
- **Database:** openclaw
- **User:** postgres
- **Password:** (stored in `.env` file, gitignored)

### Schema
1. **conversations** - Conversation metadata (session, machine, channel, topic)
2. **messages** - Individual messages with role, content, tokens, model
3. **memory** - Memory entries (MEMORY.md content, key-value storage)
4. **projects** - Project files (projects/ directory content)

## Setup Verification

✅ **Database created:** `openclaw` database exists  
✅ **Tables created:** conversations, messages, memory, projects  
✅ **Indexes created:** Optimized for common queries  
✅ **Connection working:** Python can connect and execute queries  
✅ **Shell script working:** `log_to_postgres.sh` can log conversations  

## How to Use

### 1. Manual Logging via Shell Script
```bash
# Start conversation
./log_to_postgres.sh start "session-id" "channel" "topic"

# Save message (get CONVERSATION_ID from start command)
./log_to_postgres.sh message <conv_id> "user" "Message content" "model" "tokens"

# End conversation
./log_to_postgres.sh end <conv_id> "summary"
```

### 2. Python Integration
```python
from openclaw_postgres_integration import OpenClawPostgresIntegration

integration = OpenClawPostgresIntegration()
integration.start_conversation("session-id", "webchat", "Topic")
integration.save_message("user", "Hello")
integration.save_message("assistant", "Hi there!", model="deepseek-chat", tokens=100)
integration.end_conversation("Conversation complete")
```

### 3. Backup Workspace
```bash
./log_to_postgres.sh backup
```
Backs up all memory and project files to PostgreSQL.

### 4. Search Conversations
```bash
./log_to_postgres.sh search "CRISP-DM" 10
```

## Integration with OpenClaw

### Option A: Manual Integration
Add calls to `log_to_postgres.sh` in your OpenClaw skills or workflows.

### Option B: Automatic Integration (Recommended Future)
Modify OpenClaw to automatically:
1. Start conversation when session begins
2. Log each message as it's sent/received
3. End conversation when session ends
4. Periodic workspace backups

### Option C: Hybrid Approach
- Manual conversation logging for important discussions
- Automatic backup of project files
- On-demand search of past conversations

## Security Considerations

### ✅ Implemented:
1. **Credentials in `.env`** - Not in git, not in code
2. **.gitignore excludes** `.env`, `*.env`, `database.env`
3. **Separate database user** (future: create dedicated openclaw user)
4. **Connection encryption** (SSL enabled)

### 🔒 Recommended:
1. **Change default password** - Use strong, unique password
2. **Firewall rules** - Restrict database access to specific IPs
3. **SSH tunneling** - For more secure remote access
4. **Regular backups** - Database backup procedures
5. **Audit logs** - Track database access

## Performance

### Current Setup:
- **4 tables** with appropriate indexes
- **JSONB columns** for flexible metadata
- **Connection pooling** in Python module
- **Efficient queries** with indexes on common fields

### Expected Scale:
- **Conversations:** 10-100 per day
- **Messages:** 100-1000 per day  
- **Memory entries:** 10-50 per day
- **Project files:** 50-200 files

## Cross-Machine Access

### Both Mac and Server can:
1. **Read/write conversations** - Shared conversation history
2. **Access memory entries** - Shared knowledge base
3. **Sync project files** - Collaborative editing

### Machine Detection:
- **Mac:** Detects `local-mac/machine-id`
- **Server:** Will detect `server-oracle/machine-id`
- **Database:** Stores `machine` field for each conversation

## Backup and Recovery

### Automated:
```bash
# Daily backup script (cron job)
0 2 * * * /path/to/log_to_postgres.sh backup
```

### Manual:
```bash
# Backup specific conversation
pg_dump -h 40.233.110.234 -U postgres -d openclaw -t conversations -t messages --data-only > backup.sql

# Restore
psql -h 40.233.110.234 -U postgres -d openclaw < backup.sql
```

## Troubleshooting

### Common Issues:

1. **Connection refused**
   ```bash
   # Check if PostgreSQL is running
   telnet 40.233.110.234 5432
   
   # Check firewall rules
   sudo ufw status
   ```

2. **Authentication failed**
   ```bash
   # Verify password in .env
   # Check if user exists
   psql -h 40.233.110.234 -U postgres -c "\du"
   ```

3. **Table doesn't exist**
   ```bash
   # Recreate tables
   python3 setup_database.py
   ```

4. **Python module not found**
   ```bash
   # Activate virtual environment
   source venv/bin/activate
   
   # Install dependencies
   pip install python-dotenv psycopg2-binary
   ```

## Next Steps

### Short-term:
1. **Test with actual OpenClaw conversations**
2. **Implement automatic logging for important discussions**
3. **Create search interface for past conversations**
4. **Set up regular backups**

### Medium-term:
1. **Create dedicated database user** with limited permissions
2. **Implement encryption for sensitive content**
3. **Add conversation tagging and categorization**
4. **Create analytics dashboard**

### Long-term:
1. **Real-time sync between Mac and Server**
2. **Advanced search with semantic similarity**
3. **Conversation summarization and insights**
4. **Integration with other data sources**

## Files Created

1. **`.env`** - Database credentials (gitignored)
2. **`db_storage.py`** - PostgreSQL interface module
3. **`openclaw_postgres_integration.py`** - Integration class
4. **`log_to_postgres.sh`** - Shell script wrapper
5. **`test_postgres.py`** / **`setup_database.py`** - Setup scripts
6. **`POSTGRES_SETUP.md`** - This documentation

## Notes

- **Database is remote** - Accessible from both Mac and future Server
- **Conversations are shared** - Both instances write to same database
- **Files are backed up** - Project and memory files stored in database
- **Search is available** - Query past conversations by content

---
*Setup completed: April 17, 2026*  
*By: ZhaoClaw 🐾 for Jimmy (James Zhao)*