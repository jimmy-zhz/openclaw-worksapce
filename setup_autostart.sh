#!/bin/bash
# Setup OpenClaw Auto-Logger for automatic startup
# Run this once to configure auto-start on boot/login

set -e

WORKSPACE_ROOT="/Users/jimmy/.openclaw/workspace"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
PLIST_FILE="$LAUNCH_AGENTS_DIR/com.jimmy.openclaw-autologger.plist"
SERVICE_SCRIPT="$WORKSPACE_ROOT/autologger_service_wrapper.sh"

echo "🔧 Setting up OpenClaw Auto-Logger for automatic startup..."

# Create service wrapper script
cat > "$SERVICE_SCRIPT" << 'EOF'
#!/bin/bash
# OpenClaw Auto-Logger Service Wrapper
# Managed by launchd

set -e

WORKSPACE_ROOT="/Users/jimmy/.openclaw/workspace"
LOG_FILE="$WORKSPACE_ROOT/autologger_service.log"
PID_FILE="$WORKSPACE_ROOT/autologger_service.pid"

# Function to log messages
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# Trap signals for graceful shutdown
trap 'log "Service stopping..."; exit 0' TERM INT

log "=== OpenClaw Auto-Logger Service Starting ==="
log "Time: $(date)"
log "PID: $$"
log "User: $(whoami)"

# Write PID file
echo $$ > "$PID_FILE"
log "PID file written: $PID_FILE"

# Change to workspace directory
cd "$WORKSPACE_ROOT"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    log "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install python-dotenv psycopg2-binary --quiet
    log "Virtual environment created"
fi

# Activate virtual environment
source venv/bin/activate

# Check .env file
if [ ! -f ".env" ]; then
    log "ERROR: .env file not found"
    exit 1
fi

# Start the auto-logger
log "Starting auto-logger..."
exec python3 -c "
import sys
sys.path.append('.')
from simple_auto_logger import SimpleAutoLogger
import time
import signal

logger = SimpleAutoLogger()
print('🚀 Auto-logger service started')

# Keep running
try:
    while True:
        # Heartbeat - log every hour
        time.sleep(3600)
except KeyboardInterrupt:
    print('\\n🛑 Auto-logger service stopped')
except Exception as e:
    print(f'❌ Auto-logger error: {e}')
"
EOF

chmod +x "$SERVICE_SCRIPT"

# Create launchd plist file
cat > "$PLIST_FILE" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.jimmy.openclaw-autologger</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>$SERVICE_SCRIPT</string>
    </array>
    
    <key>RunAtLoad</key>
    <true/>
    
    <key>KeepAlive</key>
    <dict>
        <key>SuccessfulExit</key>
        <false/>
    </dict>
    
    <key>StandardOutPath</key>
    <string>$WORKSPACE_ROOT/autologger_service.out.log</string>
    
    <key>StandardErrorPath</key>
    <string>$WORKSPACE_ROOT/autologger_service.err.log</string>
    
    <key>WorkingDirectory</key>
    <string>$WORKSPACE_ROOT</string>
    
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
        <key>HOME</key>
        <string>$HOME</string>
    </dict>
</dict>
</plist>
EOF

echo "✅ Created LaunchAgent plist: $PLIST_FILE"

# Load the service
echo "🔄 Loading service..."
launchctl unload "$PLIST_FILE" 2>/dev/null || true
launchctl load "$PLIST_FILE"

# Check if service is running
sleep 2
if launchctl list | grep -q "com.jimmy.openclaw-autologger"; then
    echo "✅ Service loaded successfully"
    echo "📊 Service status:"
    launchctl list | grep "com.jimmy.openclaw-autologger"
else
    echo "⚠️ Service may not have loaded correctly"
fi

# Create management script
cat > "$WORKSPACE_ROOT/manage_autologger.sh" << 'EOF'
#!/bin/bash
# Manage OpenClaw Auto-Logger Service

set -e

WORKSPACE_ROOT="/Users/jimmy/.openclaw/workspace"
PLIST_FILE="$HOME/Library/LaunchAgents/com.jimmy.openclaw-autologger.plist"

case "$1" in
    start)
        echo "Starting auto-logger service..."
        launchctl load "$PLIST_FILE"
        ;;
    
    stop)
        echo "Stopping auto-logger service..."
        launchctl unload "$PLIST_FILE"
        ;;
    
    restart)
        echo "Restarting auto-logger service..."
        launchctl unload "$PLIST_FILE" 2>/dev/null || true
        sleep 2
        launchctl load "$PLIST_FILE"
        ;;
    
    status)
        echo "Auto-logger service status:"
        if launchctl list | grep -q "com.jimmy.openclaw-autologger"; then
            echo "✅ Running"
            # Show recent logs
            if [ -f "$WORKSPACE_ROOT/autologger_service.log" ]; then
                echo "Recent logs:"
                tail -10 "$WORKSPACE_ROOT/autologger_service.log"
            fi
        else
            echo "❌ Not running"
        fi
        ;;
    
    logs)
        if [ -f "$WORKSPACE_ROOT/autologger_service.log" ]; then
            tail -50 "$WORKSPACE_ROOT/autologger_service.log"
        else
            echo "No log file found"
        fi
        ;;
    
    enable)
        echo "Enabling auto-start on login..."
        launchctl enable "gui/$(id -u)/com.jimmy.openclaw-autologger"
        ;;
    
    disable)
        echo "Disabling auto-start on login..."
        launchctl disable "gui/$(id -u)/com.jimmy.openclaw-autologger"
        ;;
    
    *)
        echo "Usage: $0 <command>"
        echo "Commands:"
        echo "  start    - Start service"
        echo "  stop     - Stop service"
        echo "  restart  - Restart service"
        echo "  status   - Check status"
        echo "  logs     - Show logs"
        echo "  enable   - Enable auto-start"
        echo "  disable  - Disable auto-start"
        exit 1
        ;;
esac
EOF

chmod +x "$WORKSPACE_ROOT/manage_autologger.sh"

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Management commands:"
echo "  $WORKSPACE_ROOT/manage_autologger.sh status   # Check status"
echo "  $WORKSPACE_ROOT/manage_autologger.sh logs     # View logs"
echo "  $WORKSPACE_ROOT/manage_autologger.sh restart  # Restart service"
echo ""
echo "The auto-logger will now:"
echo "✅ Start automatically on login"
echo "✅ Restart if it crashes"
echo "✅ Run in background"
echo "✅ Log to $WORKSPACE_ROOT/autologger_service.log"
echo ""
echo "For Oracle Server, similar setup with systemd will be needed."