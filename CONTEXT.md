# OpenClaw Context Detection System

## Purpose
Determine which machine instance is currently running and adjust file access accordingly, since conversations are not synced between Mac and Server instances.

## Machine Detection Methods

### 1. File System Indicators
```bash
# Check for machine-specific files
if [ -f "/Users/jimmy/.openclaw/workspace/local-mac/machine-id" ]; then
    echo "Running on Mac"
elif [ -f "/home/ubuntu/openclaw-workspace/server-oracle/machine-id" ]; then
    echo "Running on Oracle Server"
fi
```

### 2. Environment Variables
```bash
# Set during OpenClaw startup
export OPENCLAW_MACHINE="mac"  # or "server"
```

### 3. Network/Hostname Detection
```bash
hostname
# Mac: Jimmy-MacBook-Pro.local
# Server: oracle-server-hostname
```

### 4. Capability Testing
```bash
# Test for GUI capabilities (Mac has, Server doesn't)
if command -v osascript &> /dev/null; then
    echo "Likely Mac (has AppleScript)"
fi
```

## File Access Rules

### When Running on Mac:
**READ/WRITE freely:**
- `local-mac/` - Mac-specific configuration, logs, personal data
- `projects/` - Shared project files (coursework, immigration, etc.)
- Base workspace files (AGENTS.md, SOUL.md, etc.)

**READ only (via GitHub pull):**
- `server-oracle/results/` - Server computation results
- `server-oracle/status/` - Server status updates

**DO NOT WRITE directly:**
- `server-oracle/` - Can create tasks in GitHub for server to process

### When Running on Server:
**READ/WRITE freely:**
- `server-oracle/` - Server-specific configuration, computation files
- `projects/` - Shared project files

**READ only (via GitHub pull):**
- `local-mac/shared/` - Any Mac data meant for server
- `projects/` updates from Mac

**DO NOT WRITE directly:**
- `local-mac/` - Cannot access Mac local files directly

## Conversation Context Preservation

### Mac Conversations:
- Store context in `local-mac/conversations/YYYY-MM-DD.md`
- Reference `projects/` for shared knowledge
- Update `local-mac/` with personal insights
- When task needs server: Create in GitHub, notify via commit

### Server Conversations:
- Store context in `server-oracle/conversations/YYYY-MM-DD.md`
- Reference `projects/` for shared knowledge
- Update `server-oracle/` with computation results
- When results ready: Commit to GitHub, Mac will pull

## GitHub Sync as Context Bridge

### Mac → Server Communication:
1. Mac creates `server-tasks/task-001.json` in GitHub
2. Mac commits + pushes with message "Task for server"
3. Server (periodic pull) sees new task
4. Server executes, saves results to `server-results/result-001.json`
5. Server commits + pushes results
6. Mac pulls and reads results

### Server → Mac Communication:
1. Server creates `mac-notifications/alert-001.json` in GitHub
2. Server commits + pushes
3. Mac (on next interaction) pulls and sees notification
4. Mac acts on notification during conversation

## Lost Conversation Handling

### Problem:
Conversation on Mac Web UI doesn't sync to Server Telegram

### Solutions:
1. **Intentional bridging:** If conversation needs both contexts, document in shared `projects/`
2. **Summary commits:** End important conversations with GitHub commit summarizing key points
3. **Context files:** Maintain `context-YYYY-MM-DD.md` in shared area for cross-machine reference
4. **Explicit handoff:** "This discussion about X is now in `projects/ai-diploma/topic.md`"

## Default Behavior

### On Startup:
1. Detect machine type
2. Pull latest from GitHub
3. Read machine-specific context files
4. Check for pending tasks/notifications from other machine
5. Initialize with appropriate capabilities

### During Conversation:
1. Use machine-specific directories for personal context
2. Use shared `projects/` for collaborative knowledge
3. When topic spans machines: commit to GitHub as bridge
4. Be explicit about context limitations: "As I'm on the server, I can't access your Mac files directly"

## Example Workflow

### Scenario: AI Coursework Discussion
```
Mac Web UI Conversation:
Jimmy: "Help me with neural networks assignment"
ZhaoClaw (on Mac): 
  - Checks local-mac/ for previous neural network discussions
  - Checks projects/ai-diploma/ for assignment details
  - Realizes need for computation
  - Creates server-tasks/train-model.json in GitHub
  - Commits + pushes
  - Tells Jimmy: "Task queued for server computation"

Server (via cron job):
  - Pulls from GitHub
  - Sees train-model.json
  - Executes training
  - Saves results to server-results/model-trained.json
  - Commits + pushes
  - Optionally sends Telegram notification

Next Mac Conversation:
ZhaoClaw (on Mac):
  - Pulls from GitHub
  - Sees results
  - "Model training complete! Results in projects/ai-diploma/models/"
```

## Implementation Checklist

- [ ] Create machine-id files in local-mac/ and server-oracle/
- [ ] Set OPENCLAW_MACHINE environment variable in each instance
- [ ] Create startup script that detects machine and sets context
- [ ] Implement file access wrapper that respects machine boundaries
- [ ] Create GitHub sync routines for cross-machine communication
- [ ] Document context limitations in user interactions

---
*This system ensures each OpenClaw instance operates within its capabilities while using GitHub as a coordination layer.*