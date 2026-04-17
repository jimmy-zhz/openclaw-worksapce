# Master-Slave OpenClaw Nodes Architecture

**Date:** April 17, 2026
**Participants:** Jimmy (James Zhao), ZhaoClaw 🐾
**Status:** Planning phase, pre-installation

## Overview
Distributed OpenClaw deployment across two machines:
- **Master:** Mac (Jimmy's MacBook Pro) - GUI, personal, local access
- **Slave:** Oracle Cloud Server (4Core24G) - Computation, 24/7, remote access

## Architecture Design

### Access Methods
```
┌─────────────────────────────────────────┐
│           Access Methods                 │
├─────────────────────────────────────────┤
│  Telegram ────┐                         │
│  Host (SSH) ──┼──► Oracle Server        │
│               │    (Slave, 24/7)         │
│               │                         │
│  Web UI ──────┼──► Mac                  │
│  (127.0.0.1:18790)  (Master, GUI)       │
└─────────────────────────────────────────┘
```

### Rationale
1. **Cost-effective** - No heartbeat polling between machines
2. **Clear separation** - Each instance optimized for its role
3. **Natural usage** - Matches Jimmy's actual usage patterns
4. **Simple coordination** - Minimal overhead, GitHub for sync when needed

## Machine Responsibilities

### Mac (Master Node)
- **Primary access:** Web UI (http://127.0.0.1:18790)
- **Capabilities:** Browser automation, file management, GUI tasks, personal data
- **When used:** When Jimmy is at computer, needs full GUI access
- **Limitations:** Not 24/7, limited computation power

### Oracle Server (Slave Node)
- **Primary access:** Telegram, SSH
- **Capabilities:** Heavy computation, 24/7 availability, data processing
- **When used:** On-the-go (Telegram), computation tasks (SSH), always-on monitoring
- **Limitations:** No GUI access, no direct Mac file access

## Task Routing Matrix

| Task Type | Best Instance | Access Method | Reason |
|-----------|--------------|---------------|--------|
| Quick questions | Server | Telegram | 24/7 availability |
| Computation | Server | Telegram/SSH | 4 cores, 24GB RAM |
| File management | Mac | Web UI | Local file access |
| Browser automation | Mac | Web UI | GUI required |
| Family reminders | Server | Telegram | Always active |
| Coursework help | Context-dependent | Either | Depends on needs |
| Data processing | Server | SSH | Resource-intensive |
| Personal organization | Mac | Web UI | Personal context |

## Implementation Plan

### Phase 1: Preparation (Current)
- [x] Create GitHub repository for shared projects
- [x] Establish sync rules (RULES.md)
- [x] Document architecture decisions
- [x] Create machine-specific directories

### Phase 2: Server Setup
- [ ] Install OpenClaw on Oracle server
- [ ] Configure Telegram bot for server instance
- [ ] Set up SSH access from Mac to server
- [ ] Configure for 24/7 operation

### Phase 3: Integration
- [ ] Test Telegram → Server communication
- [ ] Test SSH from Mac to Server
- [ ] Establish GitHub sync patterns
- [ ] Create task delegation examples

## GitHub Sync Strategy

### Shared Content (GitHub)
- `projects/` - Coursework, immigration, career transition docs
- `system-architecture/` - This documentation
- `skills/` - Shared OpenClaw skills
- `local-mac/README.md` - Mac configuration (non-sensitive)
- `server-oracle/README.md` - Server configuration (non-sensitive)

### Local Only (Not on GitHub)
- `memory/` - Daily conversation logs
- `MEMORY.md` - Long-term personal memory
- `USER.md` - Jimmy's personal details
- API keys, credentials
- Machine-specific sensitive configs

### Sync Rules
1. **Push to GitHub:** Only when explicitly requested or conversation ending
2. **Commit locally:** Anytime progress needs saving
3. **Pull from GitHub:** When starting fresh conversation or working on shared projects

## Example Workflows

### Workflow A: Telegram to Server
```
Jimmy (on phone) → Telegram → Server OpenClaw
Server: Processes request, responds via Telegram
If computation needed: Uses server resources directly
If Mac file needed: Cannot access (limitation)
```

### Workflow B: Web UI to Mac
```
Jimmy (at computer) → http://127.0.0.1:18790 → Mac OpenClaw
Mac: Full GUI access, local files, browser control
If server computation needed: Can SSH to server
```

### Workflow C: SSH to Server
```
Jimmy → SSH → Server
Direct command execution for heavy tasks
Results saved on server, can be shared via GitHub
```

## Advantages

1. **💰 Cost savings** - No polling, minimal token usage
2. **⚡ Performance** - Each instance optimized for its role
3. **🔒 Security** - Clear boundaries between machines
4. **🧠 Simplicity** - Easy to understand and maintain
5. **🔄 Flexibility** - Can evolve as needs change

## Potential Challenges & Solutions

### Challenge 1: Context switching between instances
**Solution:** GitHub sync for shared projects, clear task routing rules

### Challenge 2: Server cannot access Mac files
**Solution:** Manual sync via GitHub when needed, or SSH from Mac to pull/push

### Challenge 3: Telegram only connected to server
**Solution:** For Mac-specific tasks via Telegram, server can ask Jimmy to switch to Web UI

## Future Evolution Possibilities

1. **Smart routing** - Based on task type and machine availability
2. **Lightweight status** - Simple "last seen" indicators in GitHub
3. **Task queue** - GitHub-based task handoff system
4. **Unified interface** - Single entry point that routes internally

## Decision Log

### April 17, 2026
- Jimmy proposed separating access methods: Telegram/SSH for server, Web UI for Mac
- Agreed to avoid heartbeat polling due to cost/computation concerns
- Established GitHub sync rules for intentional coordination
- Created architecture documentation before server installation

## Next Actions

1. Install OpenClaw on Oracle server
2. Configure Telegram bot for server instance
3. Set up SSH keys between Mac and server
4. Test basic communication flows
5. Refine based on actual usage patterns

---
*Documented by ZhaoClaw 🐾 - Your family member assistant*