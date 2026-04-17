# Oracle Cloud Server Configuration

**Machine:** Oracle Cloud 4Core24G Server
**Role:** Computation, 24/7 tasks, data processing
**Location:** Cloud (region to be specified)

## Responsibilities
- 24/7 availability for scheduled tasks
- Heavy computation (model training, data processing)
- Data storage and backup
- API serving and web hosting
- Cron job execution
- Resource-intensive operations

## Hardware Specifications
- **CPU:** 4 cores
- **RAM:** 24GB
- **Storage:** [To be configured]
- **Network:** Public IP, always-on

## Scheduled Tasks
- Data processing pipelines
- Model training jobs
- Web scraping operations
- System health monitoring
- Backup routines
- Report generation

## Services to Run
- OpenClaw agent for server tasks
- Python data processing scripts
- Jupyter notebooks for analysis
- API servers for projects
- Database services if needed
- Web servers for demos

## Git Strategy
- Clone from GitHub repo
- Pull updates from Mac
- Commit server-generated results
- Push processed data/results
- Maintain separate branch if needed

## Security Considerations
- Firewall configuration
- SSH key authentication only
- Regular security updates
- Limited open ports
- Process isolation