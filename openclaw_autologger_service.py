#!/usr/bin/env python3
"""
OpenClaw Auto-Logger Service
Self-managing service that runs as a proper daemon.
"""
import os
import sys
import time
import signal
import logging
from datetime import datetime
from pathlib import Path

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from simple_auto_logger import SimpleAutoLogger

class AutoLoggerService:
    """Self-managing auto-logger service."""
    
    def __init__(self):
        self.workspace = Path("/Users/jimmy/.openclaw/workspace")
        self.pid_file = self.workspace / "autologger_service.pid"
        self.log_file = self.workspace / "autologger_service.log"
        self.running = False
        self.logger = None
        self.auto_logger = None
        
        # Setup logging
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging for the service."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger('OpenClawAutoLogger')
        
    def check_environment(self):
        """Check if environment is properly configured."""
        self.logger.info("Checking environment...")
        
        # Check .env file
        env_file = self.workspace / ".env"
        if not env_file.exists():
            self.logger.error(f".env file not found: {env_file}")
            return False
        
        # Check PostgreSQL connection
        try:
            from db_storage import get_db
            db = get_db()
            with db.conn.cursor() as cur:
                cur.execute("SELECT 1")
            db.close()
            self.logger.info("✅ PostgreSQL connection OK")
        except Exception as e:
            self.logger.error(f"PostgreSQL connection failed: {e}")
            return False
        
        # Check OpenClaw sessions directory
        sessions_dir = Path("/Users/jimmy/.openclaw/agents/main/sessions")
        if not sessions_dir.exists():
            self.logger.warning(f"OpenClaw sessions directory not found: {sessions_dir}")
            # Not fatal, might start before OpenClaw
        
        return True
    
    def write_pid_file(self):
        """Write PID file."""
        with open(self.pid_file, 'w') as f:
            f.write(str(os.getpid()))
        self.logger.info(f"PID file written: {self.pid_file}")
    
    def remove_pid_file(self):
        """Remove PID file."""
        if self.pid_file.exists():
            self.pid_file.unlink()
            self.logger.info("PID file removed")
    
    def signal_handler(self, signum, frame):
        """Handle termination signals."""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.running = False
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGINT, self.signal_handler)
        self.logger.info("Signal handlers setup")
    
    def monitor_openclaw_sessions(self):
        """Monitor OpenClaw for new sessions and log them."""
        self.logger.info("Starting OpenClaw session monitor...")
        
        sessions_dir = Path("/Users/jimmy/.openclaw/agents/main/sessions")
        processed_files = set()
        
        while self.running:
            try:
                # Check for new session files
                if sessions_dir.exists():
                    session_files = list(sessions_dir.glob("*.jsonl"))
                    
                    for filepath in session_files:
                        if str(filepath) not in processed_files:
                            self.logger.info(f"New session file: {filepath.name}")
                            # Here you would process the session file
                            # For now, just mark as processed
                            processed_files.add(str(filepath))
                
                # Check if auto-logger is still running
                if not self.auto_logger:
                    self.logger.info("Starting auto-logger...")
                    self.auto_logger = SimpleAutoLogger()
                
                # Sleep before next check
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Error in monitor: {e}")
                time.sleep(60)  # Longer sleep on error
    
    def run(self):
        """Main service loop."""
        self.logger.info("=" * 50)
        self.logger.info("OpenClaw Auto-Logger Service Starting")
        self.logger.info(f"Time: {datetime.now()}")
        self.logger.info(f"PID: {os.getpid()}")
        self.logger.info(f"Workspace: {self.workspace}")
        self.logger.info("=" * 50)
        
        # Check environment
        if not self.check_environment():
            self.logger.error("Environment check failed. Exiting.")
            return 1
        
        # Write PID file
        self.write_pid_file()
        
        # Setup signal handlers
        self.setup_signal_handlers()
        
        # Set running flag
        self.running = True
        
        # Start monitoring
        try:
            self.monitor_openclaw_sessions()
        except KeyboardInterrupt:
            self.logger.info("Service interrupted by user")
        except Exception as e:
            self.logger.error(f"Service error: {e}")
        finally:
            self.cleanup()
        
        return 0
    
    def cleanup(self):
        """Cleanup resources."""
        self.logger.info("Cleaning up...")
        self.running = False
        
        if self.auto_logger:
            try:
                self.auto_logger.end_conversation("Service shutting down")
            except:
                pass
        
        self.remove_pid_file()
        self.logger.info("Cleanup complete")
    
    def stop(self):
        """Stop the service."""
        if self.pid_file.exists():
            try:
                with open(self.pid_file, 'r') as f:
                    pid = int(f.read().strip())
                
                self.logger.info(f"Stopping service with PID: {pid}")
                os.kill(pid, signal.SIGTERM)
                
                # Wait for process to terminate
                time.sleep(2)
                
                if self.pid_file.exists():
                    self.logger.warning("PID file still exists, forcing removal")
                    self.remove_pid_file()
                
                self.logger.info("Service stopped")
                return True
                
            except Exception as e:
                self.logger.error(f"Error stopping service: {e}")
                return False
        else:
            self.logger.warning("No PID file found. Service may not be running.")
            return False
    
    def status(self):
        """Check service status."""
        if self.pid_file.exists():
            try:
                with open(self.pid_file, 'r') as f:
                    pid = int(f.read().strip())
                
                # Check if process is running
                try:
                    os.kill(pid, 0)  # Signal 0 just checks if process exists
                    self.logger.info(f"✅ Service is running (PID: {pid})")
                    
                    # Show recent logs
                    if self.log_file.exists():
                        with open(self.log_file, 'r') as f:
                            lines = f.readlines()
                            if lines:
                                self.logger.info("Recent logs:")
                                for line in lines[-5:]:
                                    print(f"  {line.strip()}")
                    
                    return True
                except OSError:
                    self.logger.warning(f"⚠️ PID file exists but process {pid} not running")
                    self.remove_pid_file()
                    return False
                    
            except Exception as e:
                self.logger.error(f"Error checking status: {e}")
                return False
        else:
            self.logger.info("❌ Service is not running")
            return False

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="OpenClaw Auto-Logger Service")
    parser.add_argument("action", choices=["start", "stop", "restart", "status", "run"],
                       help="Action to perform")
    
    args = parser.parse_args()
    
    service = AutoLoggerService()
    
    if args.action == "start":
        # Run in background (daemonize)
        pid = os.fork()
        if pid > 0:
            # Parent process
            print(f"Service started with PID: {pid}")
            sys.exit(0)
        else:
            # Child process
            os.setsid()
            service.run()
            
    elif args.action == "stop":
        service.stop()
        
    elif args.action == "restart":
        service.stop()
        time.sleep(2)
        
        pid = os.fork()
        if pid > 0:
            print(f"Service restarted with PID: {pid}")
            sys.exit(0)
        else:
            os.setsid()
            service.run()
            
    elif args.action == "status":
        service.status()
        
    elif args.action == "run":
        # Run in foreground (for debugging)
        service.run()

if __name__ == "__main__":
    main()