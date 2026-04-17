# OpenClaw GitHub Sync Rules

## Push Rules
1. **Push to GitHub ONLY when:**
   - You receive explicit "push to github" command from Jimmy
   - You are pretty sure the conversation will end this time (will start fresh next time)

2. **Commit locally ANYTIME** you need to save progress

3. **Pull from GitHub when:**
   - You realize we're starting a new conversation (significant time gap, doesn't seem like same conversation)
   - Before starting work on shared projects

## Security & Authorization Rules
1. **SSH Access Control:**
   - If you need to change from Mac to Server via SSH, you MUST ask Jimmy for authorization first
   - Never initiate SSH connection to server without explicit permission
   - Document all SSH sessions with purpose and duration

2. **Cross-Machine Operations:**
   - Mac → Server operations require authorization
   - Server → Mac operations are generally not allowed (security boundary)
   - Use GitHub as communication channel instead of direct machine access when possible

## Conversation Continuity Detection
**New conversation indicators:**
- Significant time gap since last message (>30 minutes?)
- Context shift (different topic, different mood)
- Jimmy explicitly indicates fresh start
- System restart or new session

**Same conversation indicators:**
- Continuous back-and-forth
- Same topic being discussed
- Within reasonable time window

## Machine Directory Strategy
- `workspace/local-mac/` and `workspace/server-oracle/` exist locally on each machine
- These directories are NOT synced via GitHub (in .gitignore)
- Machine detection: Check which local directory exists and is readable
- Each instance only accesses its own machine-specific directory directly

## Implementation Notes
- Default: Assume same conversation unless clear indicators
- When in doubt, ask Jimmy: "Should I pull latest from GitHub?"
- Keep local commits frequent, GitHub pushes intentional
- Maintain conversation context while respecting fresh starts
- Always be transparent about machine limitations and access boundaries