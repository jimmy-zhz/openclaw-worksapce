#!/bin/bash
# OpenClaw PostgreSQL Logging Script
# Call this from OpenClaw to log conversations to PostgreSQL

set -e

WORKSPACE_ROOT="/Users/jimmy/.openclaw/workspace"
VENV_PATH="$WORKSPACE_ROOT/venv"
SCRIPT_PATH="$WORKSPACE_ROOT/openclaw_postgres_integration.py"

# Check if virtual environment exists
if [ ! -d "$VENV_PATH" ]; then
    echo "Creating virtual environment..."
    cd "$WORKSPACE_ROOT"
    python3 -m venv venv
    source venv/bin/activate
    pip install python-dotenv psycopg2-binary --quiet
fi

# Activate virtual environment
source "$VENV_PATH/bin/activate"

# Parse command line arguments
ACTION="$1"
shift

case "$ACTION" in
    start)
        SESSION_ID="$1"
        CHANNEL="$2"
        TOPIC="$3"
        python3 -c "
import sys
sys.path.append('$WORKSPACE_ROOT')
from openclaw_postgres_integration import OpenClawPostgresIntegration
integration = OpenClawPostgresIntegration('$WORKSPACE_ROOT')
integration.start_conversation('$SESSION_ID', '$CHANNEL', '$TOPIC')
print(f'CONVERSATION_ID:{integration.current_conversation_id}')
"
        ;;
    
    message)
        CONVERSATION_ID="$1"
        ROLE="$2"
        CONTENT="$3"
        MODEL="$4"
        TOKENS="$5"
        python3 -c "
import sys, json
sys.path.append('$WORKSPACE_ROOT')
from openclaw_postgres_integration import OpenClawPostgresIntegration
from db_storage import get_db

db = get_db()
# We need to save message directly since we don't have the integration instance
messages = db.get_conversation_messages($CONVERSATION_ID)
next_order = len(messages) + 1

# Escape content for JSON
content = '''$CONTENT'''.replace('\"', '\\\\\"').replace(\"'\", \"\\\\'\")

db.save_message(
    $CONVERSATION_ID, next_order, '$ROLE', content,
    '$MODEL', '$TOKENS' if '$TOKENS' != '' else None,
    None, None, None
)
print(f'MESSAGE_SAVED:{next_order}')
"
        ;;
    
    end)
        CONVERSATION_ID="$1"
        SUMMARY="$2"
        python3 -c "
import sys
sys.path.append('$WORKSPACE_ROOT')
from db_storage import get_db
db = get_db()
db.end_conversation($CONVERSATION_ID, '$SUMMARY')
print('CONVERSATION_ENDED')
"
        ;;
    
    backup)
        python3 -c "
import sys
sys.path.append('$WORKSPACE_ROOT')
from openclaw_postgres_integration import OpenClawPostgresIntegration
integration = OpenClawPostgresIntegration('$WORKSPACE_ROOT')
integration.backup_workspace()
"
        ;;
    
    search)
        QUERY="$1"
        LIMIT="${2:-10}"
        python3 -c "
import sys
sys.path.append('$WORKSPACE_ROOT')
from openclaw_postgres_integration import OpenClawPostgresIntegration
integration = OpenClawPostgresIntegration('$WORKSPACE_ROOT')
results = integration.search_conversations('$QUERY', $LIMIT)
for conv in results:
    print(f\"{conv['id']}: {conv['topic']} ({conv['start_time']})\")
"
        ;;
    
    *)
        echo "Usage: $0 <action> [args]"
        echo "Actions:"
        echo "  start <session_id> <channel> <topic>  - Start new conversation"
        echo "  message <conv_id> <role> <content> [model] [tokens] - Save message"
        echo "  end <conv_id> [summary] - End conversation"
        echo "  backup - Backup workspace to PostgreSQL"
        echo "  search [query] [limit] - Search conversations"
        exit 1
        ;;
esac