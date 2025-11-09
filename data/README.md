# Strategic Intelligence App - Database Setup

This directory contains all the database-related files for the Strategic Intelligence App, including PostgreSQL integration with SQLAlchemy ORM.

## Database Configuration

**Database Details:**
- **Host:** localhost
- **Port:** 5432
- **Database:** strategic_intelligence_app
- **Username:** postgres
- **Password:** postgre321

## Files Overview

### Core Database Files

1. **`database_config.py`** - Database connection configuration and SQLAlchemy setup
2. **`models.py`** - SQLAlchemy ORM models defining the database schema
3. **`database_service.py`** - Service layer with high-level CRUD operations
4. **`init_database.py`** - Database initialization script

### Support Files

5. **`requirements.txt`** - Python packages required for database operations
6. **`README.md`** - This documentation file

## Database Schema

### Tables

#### 1. `analysis_sessions`
Main table storing each strategic intelligence analysis request.

| Column | Type | Description |
|--------|------|-------------|
| id | Integer (PK) | Unique session identifier |
| strategic_question | Text | The main strategic question |
| time_frame | String(50) | Analysis time frame |
| region | String(100) | Geographic region |
| additional_instructions | Text | Additional user instructions |
| status | String(50) | processing/completed/failed |
| total_processing_time | Float | Total time in seconds |
| created_at | DateTime | When session was created |
| completed_at | DateTime | When session was completed |

#### 2. `agent_results`
Individual agent outputs for each analysis session.

| Column | Type | Description |
|--------|------|-------------|
| id | Integer (PK) | Unique result identifier |
| session_id | Integer (FK) | Links to analysis_sessions |
| agent_name | String(100) | Name of the agent |
| agent_type | String(100) | Type/category of agent |
| raw_response | Text | Raw LLM response |
| formatted_output | Text | Markdown formatted output |
| structured_data | JSON | Parsed structured data |
| processing_time | Float | Processing time in seconds |
| status | String(50) | processing/completed/failed/timeout |
| error_message | Text | Error details if failed |
| created_at | DateTime | When processing started |
| completed_at | DateTime | When processing finished |

#### 3. `analysis_templates`
Reusable analysis templates for common use cases.

| Column | Type | Description |
|--------|------|-------------|
| id | Integer (PK) | Unique template identifier |
| name | String(200) | Template name |
| description | Text | Template description |
| strategic_question_template | Text | Question template with placeholders |
| default_time_frame | String(50) | Default time frame |
| default_region | String(100) | Default region |
| default_instructions | Text | Default instructions |
| usage_count | Integer | How many times used |
| is_active | Boolean | Whether template is active |
| created_at | DateTime | When template was created |
| updated_at | DateTime | Last update time |

#### 4. `system_logs`
System logs for monitoring and debugging.

| Column | Type | Description |
|--------|------|-------------|
| id | Integer (PK) | Unique log identifier |
| session_id | Integer (FK) | Optional session reference |
| log_level | String(20) | INFO/WARNING/ERROR/DEBUG |
| component | String(100) | System component name |
| message | Text | Log message |
| details | JSON | Additional structured details |
| timestamp | DateTime | When log was created |

#### 5. `agent_performance`
Performance metrics for each agent.

| Column | Type | Description |
|--------|------|-------------|
| id | Integer (PK) | Unique metric identifier |
| agent_name | String(100) | Name of the agent |
| date | DateTime | Date of metrics |
| total_executions | Integer | Total number of executions |
| successful_executions | Integer | Successful executions |
| failed_executions | Integer | Failed executions |
| timeout_executions | Integer | Timed out executions |
| average_processing_time | Float | Average processing time |
| min_processing_time | Float | Minimum processing time |
| max_processing_time | Float | Maximum processing time |

## Installation & Setup

### 1. Install Required Packages

From the main project directory, install the database requirements:

```bash
pip install -r data/requirements.txt
```

### 2. Verify PostgreSQL is Running

Make sure your PostgreSQL server is running and accessible:

```bash
# Test connection (replace with your actual details)
psql -h localhost -p 5432 -U postgres -d strategic_intelligence_app
```

### 3. Initialize the Database

Run the initialization script to create all tables:

```bash
cd data
python init_database.py
```

This script will:
- Test the database connection
- Create all required tables
- Insert sample analysis templates
- Run basic operation tests

### 4. Verify Installation

If initialization is successful, you should see:
```
✅ Database initialization completed successfully!
✅ Database operations test completed successfully!
Database is ready for use!
```

## Usage Examples

### Basic Database Operations

```python
from data.database_service import DatabaseService

# Create a new analysis session
session_id = DatabaseService.create_analysis_session(
    strategic_question="How will AI impact our industry?",
    time_frame="2-3 years",
    region="Global",
    additional_instructions="Focus on competitive implications"
)

# Save an agent result
result_id = DatabaseService.save_agent_result(
    session_id=session_id,
    agent_name="Problem Explorer",
    agent_type="analysis",
    raw_response="Raw LLM response here...",
    formatted_output="# Analysis Results\n\nFormatted output...",
    processing_time=45.2
)

# Update session status
DatabaseService.update_session_status(session_id, "completed", 180.5)

# Retrieve session data
session_data = DatabaseService.get_analysis_session(session_id)
```

### Query Recent Sessions

```python
# Get recent sessions
recent_sessions = DatabaseService.get_recent_sessions(limit=10)

# Search sessions
search_results = DatabaseService.search_sessions(
    search_term="AI",
    status="completed",
    limit=25
)
```

### Performance Monitoring

```python
# Get agent performance stats
stats = DatabaseService.get_agent_performance_stats(
    agent_name="Problem Explorer",
    days_back=30
)
```

## Integration with Main App

### In your main FastAPI application:

```python
# Add database imports
from data.database_service import DatabaseService
from data.database_config import test_connection

# Test connection on startup
@app.on_event("startup")
async def startup_event():
    if not test_connection():
        logger.error("Database connection failed!")
        raise Exception("Cannot connect to database")
    logger.info("Database connection successful")

# Modify your analysis endpoint
@app.post("/analyze")
async def analyze(request: AnalysisRequest):
    # Create database session
    session_id = DatabaseService.create_analysis_session(
        strategic_question=request.strategic_question,
        time_frame=request.time_frame,
        region=request.region,
        additional_instructions=request.additional_instructions
    )
    
    # Run your analysis with session_id
    # Save each agent result to database
    
    return {"session_id": session_id, "status": "processing"}
```

## Troubleshooting

### Common Issues

1. **Connection Error**: Verify PostgreSQL is running and credentials are correct
2. **Import Errors**: Make sure all packages are installed: `pip install -r data/requirements.txt`
3. **Permission Errors**: Ensure the PostgreSQL user has CREATE/INSERT/UPDATE/DELETE permissions

### Database Connection Test

```python
from data.database_config import test_connection

if test_connection():
    print("✅ Database connection successful!")
else:
    print("❌ Database connection failed!")
```

### Reset Database

To completely reset the database (⚠️ **This will delete all data**):

```sql
-- Connect to PostgreSQL as superuser
DROP DATABASE IF EXISTS strategic_intelligence_app;
CREATE DATABASE strategic_intelligence_app;
```

Then run `python init_database.py` again.

## Performance Optimization

### Connection Pooling
The database configuration uses SQLAlchemy's QueuePool with:
- Pool size: 10 connections
- Max overflow: 20 connections
- Pre-ping: Enabled (verifies connections before use)

### Indexing
Consider adding indexes for frequently queried columns:

```sql
-- Add indexes for better query performance
CREATE INDEX idx_analysis_sessions_created_at ON analysis_sessions(created_at);
CREATE INDEX idx_analysis_sessions_status ON analysis_sessions(status);
CREATE INDEX idx_agent_results_session_id ON agent_results(session_id);
CREATE INDEX idx_agent_results_agent_name ON agent_results(agent_name);
```

## Maintenance

### Cleanup Old Data

```python
# Delete sessions older than 30 days
deleted_count = DatabaseService.delete_old_sessions(days_old=30)
print(f"Deleted {deleted_count} old sessions")
```

### Backup Database

```bash
# Create backup
pg_dump -h localhost -U postgres strategic_intelligence_app > backup.sql

# Restore backup
psql -h localhost -U postgres strategic_intelligence_app < backup.sql
```

## Support

For database-related issues:
1. Check the logs for detailed error messages
2. Verify PostgreSQL service is running
3. Test connection using `test_connection()` function
4. Check database permissions and credentials 