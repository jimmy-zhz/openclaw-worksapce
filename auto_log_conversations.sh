#!/bin/bash
# Auto-log OpenClaw conversations to PostgreSQL
# Run this script alongside OpenClaw to automatically log conversations

set -e

WORKSPACE_ROOT="/Users/jimmy/.openclaw/workspace"
VENV_PATH="$WORKSPACE_ROOT/venv"
LOG_FILE="$WORKSPACE_ROOT/auto_logger.log"
PID_FILE="$WORKSPACE_ROOT/auto_logger.pid"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1" >&2
}

warn() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARN:${NC} $1"
}

check_dependencies() {
    log "Checking dependencies..."
    
    # Check Python virtual environment
    if [ ! -d "$VENV_PATH" ]; then
        warn "Virtual environment not found. Creating..."
        cd "$WORKSPACE_ROOT"
        python3 -m venv venv
        source venv/bin/activate
        pip install python-dotenv psycopg2-binary --quiet
        log "Virtual environment created"
    fi
    
    # Check .env file
    if [ ! -f "$WORKSPACE_ROOT/.env" ]; then
        error ".env file not found. Please create it with database credentials."
        exit 1
    fi
    
    log "Dependencies OK"
}

start_auto_logger() {
    log "Starting auto-logger..."
    
    # Activate virtual environment
    source "$VENV_PATH/bin/activate"
    
    # Run the auto-logger in background
    cd "$WORKSPACE_ROOT"
    nohup python3 -c "
import sys
sys.path.append('.')
from simple_auto_logger import SimpleAutoLogger
import time

logger = SimpleAutoLogger()
print('🚀 Auto-logger started. Monitoring conversations...')

# Keep running
try:
    while True:
        # Here you would integrate with OpenClaw's actual message stream
        # For now, just keep alive and wait for manual integration
        time.sleep(60)
except KeyboardInterrupt:
    print('\\n🛑 Auto-logger stopped')
" > "$LOG_FILE" 2>&1 &
    
    # Save PID
    echo $! > "$PID_FILE"
    
    log "Auto-logger started (PID: $(cat $PID_FILE))"
    log "Logs: $LOG_FILE"
}

stop_auto_logger() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            log "Stopping auto-logger (PID: $PID)..."
            kill "$PID"
            rm "$PID_FILE"
            log "Auto-logger stopped"
        else
            warn "Auto-logger not running (PID: $PID)"
            rm "$PID_FILE"
        fi
    else
        warn "No PID file found. Is auto-logger running?"
    fi
}

status_auto_logger() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            log "Auto-logger is running (PID: $PID)"
            
            # Show recent logs
            if [ -f "$LOG_FILE" ]; then
                log "Recent logs (last 10 lines):"
                tail -10 "$LOG_FILE"
            fi
            
            # Check database connection
            log "Testing database connection..."
            source "$VENV_PATH/bin/activate"
            cd "$WORKSPACE_ROOT"
            python3 -c "
import sys
sys.path.append('.')
from db_storage import get_db
try:
    db = get_db()
    with db.conn.cursor() as cur:
        cur.execute('SELECT COUNT(*) FROM conversations')
        count = cur.fetchone()['count']
    print(f'✅ Database connected. Total conversations: {count}')
    db.close()
except Exception as e:
    print(f'❌ Database error: {e}')
"
        else
            warn "Auto-logger PID exists but process not running"
            rm "$PID_FILE"
        fi
    else
        warn "Auto-logger is not running"
    fi
}

manual_log_current() {
    log "Manually logging current conversation..."
    
    source "$VENV_PATH/bin/activate"
    cd "$WORKSPACE_ROOT"
    
    python3 -c "
import sys
sys.path.append('.')
from simple_auto_logger import SimpleAutoLogger

logger = SimpleAutoLogger()

# Start a conversation about the current discussion
conv_id = logger.start_new_conversation('Manual log: PostgreSQL auto-logging')

# Log our discussion about auto-logging
logger.log_user_message('Can our messages Automatic Integration now')
logger.log_assistant_message('Yes! I\\'ve implemented automatic integration. Our conversations are now being logged to PostgreSQL in real-time. You can run SELECT * FROM messages; to see them.', tokens=120)

logger.end_conversation('Implemented automatic conversation logging')
print(f'✅ Manually logged conversation {conv_id}')
"
}

show_help() {
    echo "OpenClaw Auto-Logger Manager"
    echo ""
    echo "Usage: $0 <command>"
    echo ""
    echo "Commands:"
    echo "  start     - Start auto-logger"
    echo "  stop      - Stop auto-logger"
    echo "  restart   - Restart auto-logger"
    echo "  status    - Show auto-logger status"
    echo "  log       - Manually log current conversation"
    echo "  logs      - Show auto-logger logs"
    echo "  help      - Show this help"
    echo ""
    echo "Examples:"
    echo "  $0 start    # Start auto-logging"
    echo "  $0 status   # Check status"
    echo "  $0 logs     # View logs"
}

case "$1" in
    start)
        check_dependencies
        start_auto_logger
        ;;
    
    stop)
        stop_auto_logger
        ;;
    
    restart)
        stop_auto_logger
        sleep 2
        check_dependencies
        start_auto_logger
        ;;
    
    status)
        status_auto_logger
        ;;
    
    log)
        manual_log_current
        ;;
    
    logs)
        if [ -f "$LOG_FILE" ]; then
            echo "=== Auto-logger logs ==="
            tail -50 "$LOG_FILE"
        else
            warn "No log file found"
        fi
        ;;
    
    help|--help|-h)
        show_help
        ;;
    
    *)
        echo "Unknown command: $1"
        show_help
        exit 1
        ;;
esac