# Database Technology Decision

## Decision: PostgreSQL over SQLite

**Date:** April 17, 2026  
**Decision Maker:** Jimmy (James Zhao)  
**Implemented by:** ZhaoClaw 🐾

## Why PostgreSQL Instead of SQLite

### **Primary Reason: Cross-Machine Sync**
- **PostgreSQL:** Centralized database accessible from both Mac and Server
- **SQLite:** Local file-based, would require complex sync between machines
- **Result:** Both machines can read/write to same conversation history

### **Technical Advantages:**
1. **Concurrent access** - Mac and Server can write simultaneously
2. **Built-in replication** - Future scaling possibilities
3. **Advanced features** - JSONB, full-text search, geospatial
4. **Security** - User permissions, encryption, auditing
5. **Backup tools** - Standard PostgreSQL backup/restore

### **Architectural Benefits:**
```
Mac OpenClaw → PostgreSQL ← Server OpenClaw
      ↑                           ↑
   Web UI                    Telegram/SSH
   (127.0.0.1:18790)         (24/7 access)
   
Both instances share:
- Conversation history
- Memory entries  
- Project files
- Search index
```

## Implementation Details

### **Database Location:**
- **Host:** 40.233.110.234 (remote server)
- **Port:** 5432
- **Database:** `openclaw`
- **Access:** Both Mac and Server instances

### **Sync Guarantees:**
1. **Real-time conversation sync** - Messages appear immediately for both machines
2. **File sync** - Project and memory files backed up to shared database
3. **Search consistency** - Both machines search same dataset
4. **Conflict resolution** - Database handles concurrent writes

### **Machine-Specific Context:**
While conversations are shared, each machine maintains:
- **Local configuration** in `local-mac/` or `server-oracle/`
- **Machine detection** via `machine-id` files
- **Capability awareness** - Knows what it can/can't do

## Usage Examples

### **Scenario: Continuing Conversation Across Machines**
```
Mac (Web UI):
Jimmy: "Let's work on the AI assignment"
ZhaoClaw (Mac): Saves to PostgreSQL

Later, on phone via Telegram:
Jimmy: "What were we discussing about AI?"
ZhaoClaw (Server): Reads from PostgreSQL
ZhaoClaw: "We were working on your AI assignment. You asked about CRISP-DM..."
```

### **Scenario: File Access**
```
Server (processing):
- Processes large dataset
- Saves results to PostgreSQL projects table

Mac (next day):
- Pulls processed results from database
- Displays in Web UI for review
```

## Security Considerations

### **Shared Database Security:**
1. **Single source of truth** - No sync conflicts
2. **Access control** - Database user permissions
3. **Encryption** - SSL for remote connections
4. **Audit trail** - Who accessed what, when

### **Compared to SQLite Sync:**
- **PostgreSQL:** Centralized security model
- **SQLite:** Would need file encryption + sync security
- **Result:** Simpler, more robust security with PostgreSQL

## Performance Impact

### **Network Latency:**
- **Acceptable:** ~50-100ms for database operations
- **Benefit:** Worth it for cross-machine sync
- **Optimization:** Connection pooling, local caching

### **Compared to SQLite:**
- **SQLite:** Faster local reads/writes
- **PostgreSQL:** Slower per-operation but enables sync
- **Trade-off:** Acceptable performance cost for sync capability

## Backup Strategy

### **Advantage over SQLite:**
- **Single backup point** - One database to backup
- **Transactional consistency** - No partial sync states
- **Standard tools** - `pg_dump`, replication, etc.

### **Backup Schedule:**
1. **Daily automated backups** of PostgreSQL
2. **Point-in-time recovery** capability
3. **Both machines benefit** from same backup

## Future Scalability

### **Beyond Two Machines:**
- **Add more instances** - Phones, tablets, other servers
- **Read replicas** - For performance scaling
- **Sharding** - If conversation volume grows large

### **SQLite Limitation:**
Would require custom sync protocol for >2 machines

## Decision Confirmation

**✅ Final Decision:** Use PostgreSQL as centralized conversation storage  
**✅ Reason:** Enable real-time sync between Mac and Server OpenClaw instances  
**✅ Implementation:** Complete and tested  
**✅ Documentation:** This file + POSTGRES_SETUP.md

---
*"We use PostgreSQL instead of SQLite, which means conversations will be synced on both machines."*  
*- Jimmy, April 17, 2026*

*Implemented by ZhaoClaw 🐾*