# OpenClaw Context Management Strategy

## Problem
DeepSeek Chat has 128k token limit. Long conversations exceed this, causing:
- Context truncation (older messages lost)
- Memory discontinuity
- Performance degradation
- Cost inefficiency

## Solution: PostgreSQL-Based Context Management

### Core Principle
**Store in PostgreSQL, retrieve on demand** instead of keeping everything in context.

### Implementation

#### 1. Conversation Summarization
```python
def summarize_conversation(conversation_id):
    """Generate summary of conversation for context."""
    messages = db.get_conversation_messages(conversation_id)
    # Generate concise summary (100-200 tokens)
    return summary
```

#### 2. Context Window Management
```python
class ContextManager:
    def __init__(self, max_tokens=100000):
        self.max_tokens = max_tokens
        self.current_tokens = 0
        self.messages = []
    
    def add_message(self, role, content):
        tokens = estimate_tokens(content)
        
        # If adding would exceed limit, remove oldest
        while self.current_tokens + tokens > self.max_tokens and self.messages:
            removed = self.messages.pop(0)
            self.current_tokens -= estimate_tokens(removed['content'])
        
        self.messages.append({'role': role, 'content': content})
        self.current_tokens += tokens
    
    def get_context(self):
        """Get current context within token limits."""
        return self.messages
```

#### 3. Smart Retrieval from PostgreSQL
```python
def get_relevant_context(query, limit_messages=10):
    """Retrieve relevant past messages from database."""
    # Search PostgreSQL for relevant past discussions
    relevant = db.search_messages(query, limit=limit_messages)
    
    # Summarize if too long
    if estimate_tokens(relevant) > 2000:
        relevant = summarize_messages(relevant)
    
    return relevant
```

### 4. Conversation Chunking
- **Session chunks:** Break long conversations into logical chunks
- **Automatic summarization:** End of chunk → generate summary → store in PostgreSQL
- **Context switching:** Load summary instead of full history

## Immediate Actions

### 1. Stop Context Bloat
```bash
# Stop auto-logger if it's adding to context
./auto_log_conversations.sh stop

# Check current context usage
./check_context_usage.sh
```

### 2. Implement Context-Aware Logging
Modify auto-logger to:
1. **Estimate token count** for each message
2. **Monitor context usage**
3. **Trigger summarization** when nearing limit
4. **Store summaries** in PostgreSQL `conversation_summaries` table

### 3. Create Context Recovery System
```python
def recover_context(session_id):
    """Recover context from PostgreSQL when starting new session."""
    # Get last conversation summary
    summary = db.get_last_summary(session_id)
    
    # Get recent messages (last 20)
    recent = db.get_recent_messages(session_id, limit=20)
    
    # Combine for new context
    return [summary] + recent
```

## Database Schema Additions

### New Table: `conversation_summaries`
```sql
CREATE TABLE conversation_summaries (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversations(id),
    summary TEXT NOT NULL,
    token_count INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### New Table: `context_checkpoints`
```sql
CREATE TABLE context_checkpoints (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255),
    checkpoint_name VARCHAR(100),
    messages JSONB,  -- Snapshot of context at checkpoint
    token_count INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## Workflow

### Normal Operation:
1. **Conversation starts** - Load recent context from PostgreSQL
2. **Messages exchanged** - Log to PostgreSQL, add to context
3. **Context grows** - Monitor token count
4. **Near limit (e.g., 100k)** - Trigger summarization
5. **Summary created** - Store in PostgreSQL, replace old context with summary
6. **Continue** - With summarized context + recent messages

### Session Recovery:
1. **New session starts** - Query PostgreSQL for last summary
2. **Load summary** - As system message
3. **Load recent messages** - Last 10-20 messages
4. **Continue** - Seamless context recovery

## Tools to Build

### 1. Context Monitor
```bash
./context_monitor.sh
# Output: Context: 85.2k/128k tokens (66%)
# Action: OK (below 90% threshold)
```

### 2. Context Summarizer
```bash
./summarize_context.sh --conversation-id 123 --output summary.md
```

### 3. Context Recovery
```bash
./recover_context.sh --session-id abc123 --output context.json
```

## Token Estimation

### Simple Estimation:
```python
def estimate_tokens(text):
    # Rough estimate: 1 token ≈ 4 characters for English
    return len(text) // 4
```

### Better Estimation (using tiktoken):
```python
import tiktoken

def estimate_tokens(text, model="deepseek-chat"):
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))
```

## Thresholds & Triggers

### Warning Levels:
- **70% (89.6k tokens):** Warning - "Context approaching limit"
- **85% (108.8k tokens):** Alert - "Consider summarizing"
- **90% (115.2k tokens):** Critical - "Auto-summarization triggered"
- **95% (121.6k tokens):** Emergency - "Forced summarization"

### Auto-summarization Rules:
1. **Keep:** Last 20 messages (full)
2. **Summarize:** Messages 21-100
3. **Archive:** Messages >100 (store in PostgreSQL only)

## Integration with Auto-Logger

### Modified Auto-Logger:
```python
class SmartAutoLogger(AutoLogger):
    def __init__(self):
        super().__init__()
        self.context_manager = ContextManager(max_tokens=115000)
        self.token_counter = TokenCounter()
    
    def log_message(self, role, content):
        # Log to PostgreSQL
        super().log_message(role, content)
        
        # Add to context manager
        tokens = self.token_counter.estimate(content)
        self.context_manager.add_message(role, content)
        
        # Check if need to summarize
        if self.context_manager.current_tokens > 100000:
            self.trigger_summarization()
```

## Benefits

1. **No context loss** - Everything in PostgreSQL
2. **Continuity preserved** - Summaries maintain context
3. **Performance optimized** - Context window managed
4. **Cost effective** - No wasted tokens
5. **Scalable** - Handle unlimited conversation length

## Next Steps

1. **Immediate:** Stop current context bloat
2. **Short-term:** Implement basic summarization
3. **Medium-term:** Build context manager
4. **Long-term:** Full context-aware system

---
*Created: April 17, 2026*  
*Trigger: Context window exceeded (414.3k/128k tokens)*