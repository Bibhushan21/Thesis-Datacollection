# Strategic Intelligence App

A modern, AI-powered strategic intelligence analysis platform built with FastAPI and PostgreSQL. This comprehensive application provides advanced analytical capabilities with intelligent automation, smart templates, and sophisticated agent workflows for strategic decision-making.

## 🚀 Key Features

### **Core Analytics Platform**
- **9 Specialized AI Agents**: Advanced agent workflow for comprehensive strategic analysis
- **Real-time Streaming**: Live updates and progress tracking for long-running analyses
- **PostgreSQL Database**: Robust data storage with connection pooling and session tracking
- **PDF Report Generation**: Professional PDF reports with detailed formatting
- **Modern UI**: Clean, responsive interface built with Tailwind CSS and marked.js

### **🤖 AI-Powered Smart Template System**
- **Personalized Recommendations**: AI suggests templates based on your analysis history
- **Real-time Template Matching**: Intelligent suggestions as you type strategic questions
- **Save Analysis as Template**: Convert successful analyses into reusable templates
- **Usage-Based Learning**: System improves recommendations over time
- **Pattern Recognition**: Automatic domain and intent classification

### **⚡ Advanced Agent Workflow**
- **Orchestrator Agent**: Coordinates multi-agent workflows
- **Problem Explorer**: Deep-dive analysis of strategic challenges
- **Best Practices Agent**: Industry best practices identification
- **Horizon Scanning**: Emerging trends and weak signals detection
- **Scenario Planning**: Strategic scenario generation and evaluation
- **Research Synthesis**: Intelligent synthesis of multiple data sources
- **Strategic Action Planning**: Actionable strategic roadmaps
- **High Impact Initiatives**: Execution-ready implementation blueprints
- **Backcasting Agent**: Priority-based action item ranking

## 🏗️ Architecture

### **Technology Stack**
- **Backend**: FastAPI with Python 3.8+
- **Database**: PostgreSQL with SQLAlchemy 2.0+ and psycopg2-binary
- **AI Integration**: Google Gemini API with LangChain framework
- **Frontend**: HTML/CSS/JavaScript with Tailwind CSS
- **PDF Generation**: ReportLab with advanced formatting
- **Real-time Features**: Server-sent events and WebSocket support

### **Database Schema**
- **Analysis Sessions**: Complete analysis tracking and storage
- **Agent Results**: Individual agent outputs and metadata
- **User Query Patterns**: Smart template learning and analytics
- **Analysis Templates**: Reusable template library
- **User Generated Templates**: Custom templates from successful analyses

### **Agent Architecture**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Orchestrator   │───▶│ Problem Explorer │───▶│ Best Practices  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
          │                       │                       │
          ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Horizon Scanning│───▶│ Scenario Planning│───▶│Research Synthesis│
└─────────────────┘    └─────────────────┘    └─────────────────┘
          │                       │                       │
          ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│Strategic Action │───▶│ High Impact     │───▶│   Backcasting   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Getting Started

### **Prerequisites**
- Python 3.8 or higher
- PostgreSQL 12+ (not SQLite)
- pip (Python package manager)
- Virtual environment (recommended)
- Google Gemini API key

### **Installation**

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/strategic-intelligence-app.git
cd strategic-intelligence-app
```

2. **Create and activate virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables:**
```bash
cp .env.example .env
# Edit .env with your configuration:
# - GOOGLE_API_KEY=your_google_api_key
# - DATABASE_URL=postgresql://user:password@localhost/dbname
```

5. **Set up PostgreSQL database:**
```sql
-- Create database
CREATE DATABASE strategic_intelligence;

-- The application will automatically create tables on first run
```

### **Running the Application**

1. **Start the development server:**
```bash
uvicorn app.main:app --reload
```

2. **Access the application:**
```
http://localhost:8000
```

3. **API Documentation:**
```
http://localhost:8000/docs
```

## 🔧 Google Gemini API Setup

### Overview
The Strategic Intelligence App uses Google Gemini API for better performance and reliability.

### 1. Get Google API Key
1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated API key
5. Add it to your `.env` file

### 2. Environment Variables
Add your Google API key to your `.env` file:

```bash
# Add this to your .env file
GOOGLE_API_KEY=your_google_api_key_here

# Old Mistral AI key can be commented out or removed
# MISTRAL_API_KEY=your_mistral_key
```

### 3. Install Google Gemini API (Choose One Method)

#### Method A: Simple Gemini-Only Installation (RECOMMENDED)
```bash
python install_gemini_only.py
```

#### Method B: Full Dependency Resolution
```bash
python fix_dependencies.py
```

#### Method C: Manual Installation (if scripts fail)
```bash
# Uninstall conflicting Google packages only
pip uninstall google-generativeai langchain-google-genai -y

# Install compatible versions
pip install "google-generativeai>=0.8.0,<0.9.0"
pip install "langchain-google-genai>=1.0.0,<2.1.0"

# Test installation
python -c "import google.generativeai as genai; from langchain_google_genai import ChatGoogleGenerativeAI; print('✅ Success!')"
```

### 4. Model Configuration
- **Model**: `gemini-1.5-pro-latest`
- **Temperature**: 0.7 (consistent with previous setup)
- **Max Output Tokens**: 8192
- **Timeout**: 120 seconds
- **Max Retries**: 5

### 5. Verification
After setup, test the system by:
1. Starting the application: `python run.py`
2. Running a strategic analysis
3. Checking that the "References & Sources" section appears after the Implementation Roadmap
4. Verifying that Best Practices include real reference links

### 6. Troubleshooting

#### Dependency Conflicts (Most Common Issue)
If you see errors like:
```
langchain-google-genai 2.0.6 depends on google-generativeai<0.9.0 and >=0.8.0
open-webui 0.5.20 requires google-generativeai==0.7.2
```

**Quick Solutions:**

**Option 1 - Use Simple Installer (Recommended):**
```bash
python install_gemini_only.py
```

**Option 2 - Force Install Specific Versions:**
```bash
pip install google-generativeai==0.8.3 --force-reinstall
pip install langchain-google-genai==2.0.6 --force-reinstall
```

**Option 3 - Accept Conflicts with open-webui:**
- Your Strategic Intelligence App will work perfectly
- open-webui may show warnings but usually still functions
- This is the fastest solution for getting Gemini working

#### Error: "GOOGLE_API_KEY not found"
- Ensure you've added the API key to your `.env` file
- Restart the application after adding the key

#### Import Errors
- Run the dependency fix script: `python fix_dependencies.py`
- Ensure you're using Python 3.8+
- Check that all packages installed successfully

#### API Rate Limits
- Google Gemini has generous free tier limits
- Monitor usage at [Google AI Studio](https://aistudio.google.com/)
- Consider upgrading if you hit limits

## 🚀 Cloud Deployment Guide

### Overview
Complete instructions for deploying the Strategic Intelligence Platform to cloud environments.

### Database Schema
The platform uses PostgreSQL with the following tables:

#### Core Tables
- **`users`** - User authentication and profiles
- **`analysis_sessions`** - Strategic analysis requests
- **`agent_results`** - Individual agent outputs
- **`analysis_templates`** - Reusable analysis configurations

#### Supporting Tables
- **`system_logs`** - Application logging
- **`agent_performance`** - Performance metrics
- **`agent_ratings`** - User feedback and ratings
- **`agent_rating_summaries`** - Aggregated rating statistics

### Deployment Scripts

#### Single Comprehensive Script: `init_cloud_database.py` ⭐
**Complete database setup for both new deployments and existing database updates.**

```bash
python init_cloud_database.py
```

**What it does**: 
- 🔌 **Tests database connection**
- 🔧 **Updates schema** - adds missing columns to existing tables
- 📋 **Creates all tables** using SQLAlchemy  
- 👤 **Sets up admin user** using direct SQL (more reliable)
- 📝 **Creates templates** using direct SQL (more reliable)  
- ⭐ **Initializes rating summaries** using direct SQL
- 🔍 **Comprehensive verification** - checks everything is working

**Works for:**
- ✅ **New deployments** - full setup from scratch
- ✅ **Existing databases** - schema updates and missing data
- ✅ **Both local and cloud databases**

### Environment Variables

Required environment variables for cloud deployment:

```env
# Database Configuration
DATABASE_URL=postgresql://username:password@host:port/database
DB_HOST=your-database-host
DB_PORT=5432
DB_NAME=challenges_one_db
DB_USER=your-db-username
DB_PASSWORD=your-db-password

# Authentication
SECRET_KEY=your-super-secret-jwt-key-change-this-in-production

# AI Configuration
GOOGLE_API_KEY=your-google-api-key
```

### Default Admin Account

After deployment, the system creates a default admin account:

```
Username: admin
Email: admin@challenges.one
Password: admin123
```

⚠️ **IMPORTANT**: Change the default password immediately after first login!

### Deployment Steps

#### Universal Deployment (Works for Both New & Existing)
1. **Create PostgreSQL database** (if new deployment)
2. **Set environment variables** (see section above)
3. **Run comprehensive setup**: `python init_cloud_database.py`
4. **Deploy application code**
5. **Start application**: `python run.py`

#### Verification
1. Access the application URL
2. Login with admin credentials (`admin` / `admin123`)
3. Verify all features work correctly
4. Create a test user account
5. Run a sample analysis
6. **Change default admin password** ⚠️

### Security Considerations

#### Authentication
- JWT-based authentication with configurable expiration
- Bcrypt password hashing
- HTTP-only cookies for session management
- Role-based access control (Admin/User)

#### Database Security
- Foreign key constraints for data integrity
- Parameterized queries to prevent SQL injection
- Connection pooling with proper timeout settings

#### Environment Security
- Secure secret key management
- Environment-based configuration
- Database connection encryption

## 🌐 Render Deployment

### Render Service Settings

#### Build Command
```
pip install -r requirements.txt
```

#### Start Command (Option 1 - With Database Init - RECOMMENDED)
```
bash start.sh
```

#### Start Command (Option 2 - Direct start)
```
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
```

### Render Environment Variables Setup

When deploying to Render, set these environment variables in your Render dashboard:

#### Database Configuration (Option 1 - Individual variables)
```
DB_HOST=dpg-d11b1u95pdvs73eq2kf0-a.frankfurt-postgres.render.com
DB_PORT=5432
DB_NAME=strategicintelligenceanalysis_db
DB_USER=strategicintelligenceanalysis_db_user
DB_PASSWORD=Gzan5HtrMLr5sv0zszmRT0eAK6GDajBO
```

#### Database Configuration (Option 2 - Single URL - RECOMMENDED)
```
DATABASE_URL=postgresql://strategicintelligenceanalysis_db_user:Gzan5HtrMLr5sv0zszmRT0eAK6GDajBO@dpg-d11b1u95pdvs73eq2kf0-a.frankfurt-postgres.render.com/strategicintelligenceanalysis_db
```

#### How to set these in Render:

1. Go to your Render Dashboard
2. Select your web service
3. Go to the "Environment" tab
4. Add the environment variable(s) above
5. Click "Save Changes"
6. Your service will automatically redeploy with the new database connection

### Database Initialization
The app now includes automatic database table creation:

1. **Database tables will be created automatically** when the app starts
2. **Sample templates** will be added if none exist
3. **Backup initialization** happens on FastAPI startup event

#### Manual Database Initialization (if needed)
If you want to initialize the database manually:
```bash
python init_cloud_database.py
```

### Render Deployment Steps

1. **Update your code** - Push all updated files to your repository:
   - Updated `requirements.txt` 
   - New `init_cloud_database.py`
   - Updated `start.sh`
   - Updated `app/main.py` with startup event

2. **In Render Dashboard:**
   - Go to your Web Service
   - Settings → Build & Deploy
   - Set Build Command: `pip install -r requirements.txt`
   - Set Start Command: `bash start.sh` (RECOMMENDED)
3. **Environment Tab:**
   - Add the `DATABASE_URL` environment variable
4. **Deploy** - Click "Manual Deploy" or push to trigger auto-deploy

### What This Fixes

✅ **Database Tables**: All required tables (`analysis_sessions`, `agent_results`, etc.) will be created automatically

✅ **Frontend Updates**: Agent results will now be properly saved and displayed 

✅ **Error Handling**: Better error handling for database operations

✅ **Sample Data**: Sample templates created for immediate use

### Render Troubleshooting

#### If you still get database errors:
1. Check that `DATABASE_URL` environment variable is set correctly
2. Verify PostgreSQL database is accessible
3. Check application logs for database connection issues

#### If frontend still doesn't update:
1. Check browser developer console for JavaScript errors
2. Verify that analysis results are being saved to database
3. Check that WebSocket/streaming connections are working

## 📊 Smart Template System

### **How It Works**
The AI-powered template system learns from your analysis patterns to provide personalized suggestions:

1. **Pattern Tracking**: Every analysis builds your behavioral profile
2. **Domain Classification**: Automatic categorization (Market, Technology, Risk, etc.)
3. **Intent Recognition**: Identifies analysis purpose (Market Entry, Competitive Analysis, etc.)
4. **Smart Suggestions**: AI generates relevant templates based on your history
5. **Real-time Recommendations**: Templates appear as you type strategic questions

### **Key Features**
- **🎯 Personalized AI Suggestions**: Based on your unique analysis patterns
- **⚡ Real-time Recommendations**: Intelligent matching as you type
- **💾 Save Analysis as Template**: Convert successful analyses into reusable templates
- **📊 Usage Analytics**: Track patterns and improve recommendations
- **🧠 Continuous Learning**: System gets smarter with every use

### **Domain Classification**
- **Market**: Customer, competitor, market analysis
- **Technology**: Digital transformation, AI, innovation
- **Finance**: Investment, budget, ROI analysis
- **Risk**: Security, compliance, threat assessment
- **Strategy**: Planning, vision, direction
- **Operations**: Process, efficiency, supply chain
- **Geopolitical**: Regulatory, policy, regional analysis

## 🔧 API Reference

### **Core Endpoints**
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/start-analysis` | POST | Start a new strategic analysis |
| `/analysis-status/{session_id}` | GET | Check analysis progress |
| `/analysis-results/{session_id}` | GET | Get complete analysis results |
| `/generate-pdf` | POST | Generate PDF report |

### **Smart Template Endpoints**
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/ai-template-suggestions/{user_id}` | GET | Get personalized AI suggestions |
| `/api/get-template-recommendations` | POST | Get real-time template recommendations |
| `/api/save-analysis-as-template` | POST | Save analysis as reusable template |
| `/api/track-query-pattern` | POST | Track user query patterns |
| `/api/user-analytics/{user_id}` | GET | Get user behavior analytics |
| `/api/popular-query-patterns` | GET | Get trending analysis patterns |

### **Agent Management**
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/agents` | GET | List all available agents |
| `/agents/{agent_name}/process` | POST | Process data with specific agent |
| `/agent-status` | GET | Get agent health and status |

## 📁 Project Structure

```
strategic-intelligence-app/
├── app/
│   ├── agents/                    # AI Agents
│   │   ├── base_agent.py         # Base agent class
│   │   ├── orchestrator_agent.py # Workflow coordination
│   │   ├── problem_explorer_agent.py
│   │   ├── best_practices_agent.py
│   │   ├── horizon_scan_agent.py
│   │   ├── scenario_planning_agent.py
│   │   ├── research_synthesis_agent.py
│   │   ├── strategic_action_agent.py
│   │   ├── high_impact_agent.py
│   │   └── backcasting_agent.py
│   ├── core/                     # Core functionality
│   │   ├── llm.py               # LLM configuration (Gemini)
│   │   └── auth.py              # Authentication logic
│   ├── routers/                  # API routers
│   │   ├── agents.py            # Agent endpoints
│   │   ├── analysis.py          # Analysis endpoints
│   │   ├── auth.py              # Auth endpoints
│   │   ├── projects.py          # Project management
│   │   └── ratings.py           # Rating system
│   ├── database/                 # Database layer
│   │   ├── models.py            # SQLAlchemy models
│   │   ├── database.py          # Database connection
│   │   └── database_service.py  # Business logic
│   ├── static/                   # Frontend assets
│   │   ├── css/                 # CSS files
│   │   └── js/                  # JavaScript files
│   ├── templates/               # HTML templates
│   │   ├── analysis.html        # Main interface
│   │   ├── home.html           # Landing page
│   │   ├── history.html        # Analysis history
│   │   └── auth/               # Authentication pages
│   └── main.py                  # FastAPI application
├── data/                        # Data storage
│   ├── models.py               # Database models
│   ├── database_config.py      # Database configuration
│   ├── database_service.py     # Database operations
│   └── migrations/             # Database migrations
├── init_cloud_database.py      # Cloud database setup
├── requirements.txt             # Python dependencies
├── .env.example                # Environment template
├── start.sh                    # Startup script
├── run.py                      # Application runner
└── README.md                   # This file
```

## 🎯 Agent Details

### **High Impact Agent**
Creates exactly **3 comprehensive initiatives**:
- **Near-Term Initiative**: 0-2 years, immediate strategic actions
- **Medium-Term Initiative**: 2-5 years, strategic positioning
- **Long-Term Initiative**: 5-10 years, transformational changes

Each initiative includes:
- Descriptive title based on actual high-priority actions
- Strategic importance explanation
- Stakeholder impact analysis
- Resource requirements estimation
- Success metrics (3+ indicators)
- Immediate implementation tasks (5 tasks)

### **Strategic Action Agent**
Generates comprehensive action plans with:
- **Structured parsing** of strategic ideas
- **Priority classification** (High/Medium/Low)
- **Time horizon organization** (Near/Medium/Long-term)
- **Action item extraction** with detailed descriptions
- **Enhanced parsing patterns** for accurate content extraction

### **Backcasting Agent**
Prioritizes action items using:
- **Urgency assessment** (immediate impact)
- **Impact evaluation** (strategic value)
- **Feasibility analysis** (implementation difficulty)
- **JSON-structured output** with rankings and justifications

## 🔧 Recent Major Fixes

### **PDF Generation (✅ Fixed)**
- **Issue**: 500 Internal Server Error when generating PDFs
- **Root Cause**: Missing ReportLab imports (`A4`, `colors`)
- **Solution**: Added proper imports and enhanced error handling
- **Status**: ✅ Working perfectly - generates professional PDF reports

### **High Impact Agent (✅ Fixed)**
- **Issue**: Generic output with only 1 initiative showing
- **Root Cause**: Parsing issues and incorrect data flow
- **Solution**: Fixed data extraction, parsing logic, and output formatting
- **Status**: ✅ Creates exactly 3 meaningful initiatives per time horizon

### **Agent Data Flow (✅ Fixed)**
- **Issue**: Agents not finding high-priority items
- **Root Cause**: Strategic Action Agent parsing and status handling
- **Solution**: Enhanced parsing patterns and proper status returns
- **Status**: ✅ All agents communicate properly with structured data

### **Gemini API Integration (✅ Implemented)**
- **Update**: Migrated from Mistral AI to Google Gemini API
- **Benefits**: Better performance, reliability, and enhanced reference linking
- **Features**: Real reference links in Best Practices agent output
- **Status**: ✅ Fully functional with comprehensive setup documentation

## 📊 Performance Analytics

### **System Capabilities**
- **Processing Speed**: Handles complex multi-agent workflows in 60-120 seconds
- **Scalability**: PostgreSQL backend supports concurrent users
- **Reliability**: Comprehensive error handling with graceful fallbacks
- **Learning**: Template system improves with usage patterns

### **Usage Metrics**
- **Template Suggestions**: AI-generated based on behavioral patterns
- **Pattern Recognition**: Automatic domain and intent classification
- **Success Tracking**: Analysis completion rates and template reuse
- **Performance Monitoring**: Agent response times and success rates

## 🔮 Future Enhancements

### **Planned Features**
- **🌐 Multi-user Collaboration**: Team workspaces and shared templates
- **📱 Mobile Optimization**: Responsive design for mobile devices
- **🔗 External Integrations**: API connectors for data sources
- **📊 Advanced Analytics**: Deeper insights and trend analysis
- **🤖 Enhanced AI Models**: More sophisticated prediction algorithms

### **AI Improvements**
- **Natural Language Processing**: Better question understanding
- **Predictive Analytics**: Proactive strategic suggestions
- **Multi-language Support**: Global accessibility
- **Advanced Learning**: Cross-user pattern recognition (privacy-protected)

## 🛡️ Security & Privacy

- **Data Encryption**: Sensitive information protection
- **Anonymous Tracking**: Privacy-first analytics approach
- **User Consent**: Opt-in data collection policies
- **Secure APIs**: Authentication and authorization controls
- **Database Security**: PostgreSQL security best practices

## Features

- **Multi-Agent Strategic Analysis**: Coordinated analysis using specialized AI agents
- **Interactive Dashboard**: Real-time monitoring and analytics
- **Analysis History**: Track and review past strategic assessments
- **Performance Analytics**: Monitor agent effectiveness and response times
- **Template System**: Reusable analysis configurations
- **PDF Export**: Professional reports generation
- **Agent Rating System**: User feedback and evaluation system for agent outputs

## Rating System

The application includes a comprehensive rating system that allows users to evaluate and provide feedback on agent outputs:

### Features
- **5-Star Rating System**: Rate each agent's analysis from 1-5 stars
- **Detailed Reviews**: Optional text reviews and feedback
- **Helpful Aspects**: Tag what was most valuable (clarity, depth, actionable insights, etc.)
- **Improvement Suggestions**: Provide specific feedback for enhancement
- **Recommendation System**: Indicate whether you'd recommend the agent to others
- **Rating Analytics**: View aggregated ratings and trends
- **Agent Performance Metrics**: Track agent effectiveness over time

### API Endpoints
- `POST /ratings/submit` - Submit a rating for an agent result
- `GET /ratings/agent/{agent_name}` - Get ratings for a specific agent
- `GET /ratings/session/{session_id}` - Get all ratings for an analysis session
- `GET /ratings/summaries` - Get rating summaries for all agents
- `GET /ratings/analytics` - Get rating analytics and trends
- `GET /ratings/top-rated` - Get top-rated agents

### Usage
After completing an analysis, users can:
1. Rate each agent's output using the star rating system
2. Provide detailed written feedback
3. Select helpful aspects from predefined categories
4. Suggest improvements
5. Indicate recommendation status
6. View aggregated ratings and analytics

The rating system helps improve agent performance and provides valuable insights for users selecting agents for future analyses. 

## 🚨 Troubleshooting

### Common Issues

#### Database Connection
- Check that `DATABASE_URL` environment variable is set correctly
- Ensure PostgreSQL is running and credentials are correct
- Verify database exists and is accessible

#### Agent Timeouts
- Check Google API key and network connectivity
- Verify API rate limits haven't been exceeded
- Check application logs for specific error messages

#### PDF Generation
- Verify ReportLab installation and imports
- Check file permissions for PDF output directory
- Ensure adequate disk space

#### Template System
- Clear browser cache for JavaScript updates
- Check database connection for template loading
- Verify template data exists in database

#### Gemini API Issues
- Ensure `GOOGLE_API_KEY` is properly set in environment
- Check API key permissions and quotas
- Verify compatible package versions are installed

### Getting Help
- **Technical Issues**: Check application logs and console output
- **Feature Requests**: Submit through GitHub issues
- **Documentation**: Refer to API docs at `/docs`
- **Community**: Join developer discussions

### Recovery Steps
- Use `init_cloud_database.py` for complete database reset
- Check logs for detailed error information
- Verify all environment variables are set correctly
- Test individual components (database, API, frontend)

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature-name`
3. **Make your changes** with proper testing
4. **Commit your changes**: `git commit -am 'Add feature'`
5. **Push to the branch**: `git push origin feature-name`
6. **Submit a pull request**

### **Development Guidelines**
- Follow PEP 8 style guidelines
- Add tests for new features
- Update documentation for changes
- Ensure PostgreSQL compatibility
- Test with both local and cloud databases

## 📞 Support

### Default Admin Access
- **URL**: `/login`
- **Username**: `admin`
- **Email**: `admin@challenges.one`
- **Password**: `admin123`

⚠️ **Change default password immediately after first login**

### Important Files
- `init_cloud_database.py` - Main setup script
- `app/core/llm.py` - Gemini API configuration
- `data/models.py` - Database models
- `app/core/auth.py` - Authentication logic
- `app/templates/auth/` - Login/signup pages
- `data/database_config.py` - Database configuration

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **FastAPI**: Modern, fast web framework for building APIs
- **PostgreSQL**: Powerful, open-source relational database
- **Google Gemini**: Advanced language model capabilities
- **Tailwind CSS**: Utility-first CSS framework
- **ReportLab**: Professional PDF generation
- **SQLAlchemy**: Python SQL toolkit and ORM
- **LangChain**: Framework for developing applications with LLMs

---

**🎉 Your Strategic Intelligence App is ready to transform decision-making with AI-powered insights and intelligent automation!**

**🌐 Access at: http://localhost:8000**






