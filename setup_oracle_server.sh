#!/bin/bash
# Setup OpenClaw Auto-Logger on Oracle Server
# Run this on the Oracle Cloud server

set -e

echo "🖥️  Setting up OpenClaw Auto-Logger on Oracle Server..."
echo "This script will configure auto-logger as a systemd service."

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root or with sudo"
    exit 1
fi

# Configuration
USER="jimmy"
WORKSPACE_DIR="/home/$USER/openclaw-workspace"
SERVICE_NAME="openclaw-autologger"
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME.service"

echo "📁 Workspace directory: $WORKSPACE_DIR"
echo "👤 User: $USER"
echo "🛠️  Service: $SERVICE_NAME"

# Check if workspace exists
if [ ! -d "$WORKSPACE_DIR" ]; then
    echo "❌ Workspace directory not found: $WORKSPACE_DIR"
    echo "Please clone the GitHub repo first:"
    echo "  git clone https://github.com/jimmy-zhz/openclaw-worksapce.git $WORKSPACE_DIR"
    exit 1
fi

# Check for .env file
if [ ! -f "$WORKSPACE_DIR/.env" ]; then
    echo "❌ .env file not found in workspace"
    echo "Please create $WORKSPACE_DIR/.env with PostgreSQL credentials:"
    echo "  DB_HOST=40.233.110.234"
    echo "  DB_PORT=5432"
    echo "  DB_NAME=openclaw"
    echo "  DB_USER=postgres"
    echo "  DB_PASSWORD=your_password"
    exit 1
fi

# Create server machine-id
SERVER_ID_FILE="$WORKSPACE_DIR/server-oracle/machine-id"
mkdir -p "$(dirname "$SERVER_ID_FILE")"
cat > "$SERVER_ID_FILE" << EOF
machine: server
hostname: $(hostname)
role: slave
capabilities: computation, 24/7, heavy_processing, api_serving
resources: 4_cores, 24gb_ram
access_methods: telegram, ssh
owner: James Zhao (Jimmy)
purpose: data_processing, model_training, always_on_tasks
created: $(date +%Y-%m-%d)
EOF

echo "✅ Created server machine-id: $SERVER_ID_FILE"

# Create systemd service file
cat > "$SERVICE_FILE" << EOF
[Unit]
Description=OpenClaw Auto-Logger Service
After=network.target
Wants=network.target

[Service]
Type=simple
User=$USER
Group=$USER
WorkingDirectory=$WORKSPACE_DIR
Environment="PATH=/usr/local/bin:/usr/bin:/bin:/usr/local/sbin:/usr/sbin:/sbin"
Environment="HOME=/home/$USER"

# Setup Python virtual environment
ExecStartPre=/usr/bin/python3 -m venv $WORKSPACE_DIR/venv
ExecStartPre=$WORKSPACE_DIR/venv/bin/pip install python-dotenv psycopg2-binary --quiet

# Start the auto-logger
ExecStart=$WORKSPACE_DIR/venv/bin/python3 -c "
import sys
sys.path.append('$WORKSPACE_DIR')
from simple_auto_logger import SimpleAutoLogger
import time
import signal

def signal_handler(signum, frame):
    print('Service stopping...')
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

logger = SimpleAutoLogger()
print('🚀 OpenClaw Auto-Logger started on Oracle Server')

try:
    # Keep service running
    while True:
        time.sleep(3600)  # Sleep for 1 hour
except KeyboardInterrupt:
    print('Service stopped by user')
except Exception as e:
    print(f'Service error: {e}')
    raise
"

# Restart on failure
Restart=always
RestartSec=10

# Logging
StandardOutput=append:$WORKSPACE_DIR/autologger_service.log
StandardError=append:$WORKSPACE_DIR/autologger_service.err.log

[Install]
WantedBy=multi-user.target
EOF

echo "✅ Created systemd service: $SERVICE_FILE"

# Set permissions
chmod 644 "$SERVICE_FILE"
chown -R $USER:$USER "$WORKSPACE_DIR"

# Reload systemd
systemctl daemon-reload
echo "✅ Reloaded systemd daemon"

# Enable and start service
systemctl enable "$SERVICE_NAME"
systemctl start "$SERVICE_NAME"

echo "✅ Enabled and started service: $SERVICE_NAME"

# Check status
sleep 2
echo ""
echo "📊 Service status:"
systemctl status "$SERVICE_NAME" --no-pager

# Create management script for user
USER_MANAGE_SCRIPT="$WORKSPACE_DIR/manage_server_autologger.sh"
cat > "$USER_MANAGE_SCRIPT" << 'EOF'
#!/bin/bash
# Manage OpenClaw Auto-Logger on Oracle Server

set -e

SERVICE_NAME="openclaw-autologger"
WORKSPACE_DIR="$(cd "$(dirname "$0")" && pwd)"

case "$1" in
    start)
        echo "Starting auto-logger service..."
        sudo systemctl start "$SERVICE_NAME"
        ;;
    
    stop)
        echo "Stopping auto-logger service..."
        sudo systemctl stop "$SERVICE_NAME"
        ;;
    
    restart)
        echo "Restarting auto-logger service..."
        sudo systemctl restart "$SERVICE_NAME"
        ;;
    
    status)
        echo "Auto-logger service status:"
        sudo systemctl status "$SERVICE_NAME" --no-pager
        ;;
    
    logs)
        echo "Service logs:"
        if [ -f "$WORKSPACE_DIR/autologger_service.log" ]; then
            tail -50 "$WORKSPACE_DIR/autologger_service.log"
        else
            echo "No log file found"
        fi
        ;;
    
    enable)
        echo "Enabling auto-start on boot..."
        sudo systemctl enable "$SERVICE_NAME"
        ;;
    
    disable)
        echo "Disabling auto-start on boot..."
        sudo systemctl disable "$SERVICE_NAME"
        ;;
    
    journal)
        echo "Systemd journal logs:"
        sudo journalctl -u "$SERVICE_NAME" -n 50 --no-pager
        ;;
    
    *)
        echo "Usage: $0 <command>"
        echo "Commands:"
        echo "  start    - Start service"
        echo "  stop     - Stop service"
        echo "  restart  - Restart service"
        echo "  status   - Check status"
        echo "  logs     - Show application logs"
        echo "  journal  - Show systemd journal logs"
        echo "  enable   - Enable auto-start on boot"
        echo "  disable  - Disable auto-start on boot"
        exit 1
        ;;
esac
EOF

chmod +x "$USER_MANAGE_SCRIPT"
chown $USER:$USER "$USER_MANAGE_SCRIPT"

echo ""
echo "🎉 Oracle Server setup complete!"
echo ""
echo "Management commands (run as user $USER):"
echo "  $USER_MANAGE_SCRIPT status   # Check status"
echo "  $USER_MANAGE_SCRIPT logs     # View logs"
echo "  $USER_MANAGE_SCRIPT restart  # Restart service"
echo "  $USER_MANAGE_SCRIPT journal  # View systemd logs"
echo ""
echo "The auto-logger will now:"
echo "✅ Start automatically on system boot"
echo "✅ Restart automatically if it crashes"
echo "✅ Run as user $USER"
echo "✅ Log to $WORKSPACE_DIR/autologger_service.log"
echo "✅ Connect to PostgreSQL at 40.233.110.234:5432"
echo ""
echo "To verify PostgreSQL connection:"
echo "  cd $WORKSPACE_DIR"
echo "  source venv/bin/activate"
echo "  python3 -c \"from db_storage import get_db; db = get_db(); print('✅ Connected')\""
echo ""
echo "Next steps:"
echo "1. Install OpenClaw on the server"
echo "2. Configure Telegram bot for server access"
echo "3. Test cross-machine conversation sync"