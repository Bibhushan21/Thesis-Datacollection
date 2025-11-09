import asyncio
import json
import logging
import os
import time
from datetime import datetime
from typing import Dict, List, Optional, Any

from fastapi import FastAPI, HTTPException, Request, Form, BackgroundTasks, status
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.lib import colors
import io
import re
import uvicorn

from data.database_service import DatabaseService
from app.agents.orchestrator_agent import OrchestratorAgent
from app.routers import analysis
# Authentication imports removed for direct access
# Database imports removed for simplified access


def safe_json_dumps(data):
    """Safely serialize data to JSON, with base64 encoding as fallback."""
    try:
        # First attempt with standard json.dumps
        result = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
        # Validate the result by trying to parse it back
        json.loads(result)
        return result
    except (TypeError, ValueError, UnicodeDecodeError) as e:
        print(f"Initial JSON serialization failed: {str(e)}")
        # If that fails, try base64 encoding for string content
        try:
            encoded_data = encode_strings_for_json(data)
            result = json.dumps(encoded_data, ensure_ascii=False, separators=(',', ':'))
            # Validate the encoded result
            json.loads(result)
            print("Successfully encoded and serialized data with base64")
            return result
        except Exception as nested_e:
            print(f"Base64 encoding failed: {str(nested_e)}")
            # Try the old cleaning method as backup
            try:
                cleaned_data = clean_data_for_json(data)
                result = json.dumps(cleaned_data, ensure_ascii=False, separators=(',', ':'))
                json.loads(result)
                print("Successfully cleaned and serialized data")
                return result
            except Exception as final_e:
                # Log the error for debugging
                print(f"All JSON serialization methods failed: {str(final_e)}")
                # Return a clean error response instead of generating debug file
                agent_name = "Unknown"
                if isinstance(data, dict):
                    # Try to extract agent name from the data structure
                    for key in data.keys():
                        if key in ["Problem Explorer", "Best Practices", "Horizon Scanning", "Scenario Planning", 
                                  "Research Synthesis", "Strategic Action", "High Impact", "Backcasting"]:
                            agent_name = key
                            break
                error_response = {
                    agent_name: {
                        "status": "error",
                        "message": "Failed to process response. Please try again.",
                        "error_details": str(final_e)[:200]  # Limit error details length
                    }
                }
                return json.dumps(error_response, ensure_ascii=False, separators=(',', ':'))

def encode_strings_for_json(data):
    """Encode strings using base64 to avoid JSON issues."""
    import base64
    
    if isinstance(data, dict):
        result = {}
        for k, v in data.items():
            # Encode the key if it's a string
            if isinstance(k, str):
                try:
                    encoded_key = k  # Keep keys as regular strings for now
                except:
                    encoded_key = base64.b64encode(k.encode('utf-8')).decode('ascii')
            else:
                encoded_key = k
            result[encoded_key] = encode_strings_for_json(v)
        return result
    elif isinstance(data, list):
        return [encode_strings_for_json(item) for item in data]
    elif isinstance(data, str):
        # For large strings or strings with problematic content, use base64
        if len(data) > 1000 or has_problematic_chars(data):
            try:
                encoded = base64.b64encode(data.encode('utf-8')).decode('ascii')
                return {"_base64_encoded": True, "content": encoded}
            except:
                return clean_string_for_json(data)  # Fall back to cleaning
        else:
            return clean_string_for_json(data)  # Use cleaning for shorter strings
    else:
        return data

def has_problematic_chars(text):
    """Check if text has characters that commonly break JSON."""
    if not isinstance(text, str):
        return False
    
    # Much more aggressive detection - trigger base64 for any potentially problematic content
    problematic_patterns = [
        '\n',    # Any newlines
        '"',     # Any quotes
        '\\',    # Any backslashes  
        '\r',    # Carriage returns
        '\t',    # Tabs
        "'",     # Single quotes
        '`',     # Backticks
        '{',     # Curly braces
        '}',     # Curly braces
        '[',     # Square brackets
        ']',     # Square brackets
    ]
    
    # Also check for markdown patterns that often cause issues
    markdown_patterns = [
        '**',    # Bold text
        '##',    # Headers
        '###',   # Headers
        '- **',  # List items with bold
        '---',   # Horizontal rules
    ]
    
    all_patterns = problematic_patterns + markdown_patterns
    
    for pattern in all_patterns:
        if pattern in text:
            return True
    
    # Also trigger for any string longer than 500 chars (instead of 1000)
    if len(text) > 500:
        return True
    
    return False

def clean_data_for_json(data):
    """Recursively clean data to ensure JSON serialization."""
    if isinstance(data, dict):
        return {clean_string_for_json(k): clean_data_for_json(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [clean_data_for_json(item) for item in data]
    elif isinstance(data, str):
        return clean_string_for_json(data)
    elif data is None:
        return None
    elif isinstance(data, (int, float, bool)):
        return data
    else:
        # For any other type, convert to string and clean it
        return clean_string_for_json(str(data))

def clean_string_for_json(text):
    """Clean a string to make it JSON-safe with aggressive cleaning."""
    if not isinstance(text, str):
        text = str(text)
    
    # Remove null bytes and other problematic control characters
    text = text.replace('\x00', '')
    
    # Replace problematic characters BEFORE escaping quotes
    text = text.replace('\b', ' ')  # backspace to space
    text = text.replace('\f', ' ')  # form feed to space  
    text = text.replace('\r', ' ')  # carriage return to space
    text = text.replace('\t', '    ')  # tab to 4 spaces
    
    # Remove any remaining control characters (ASCII 0-31 except \n)
    import re
    text = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]', '', text)
    
    # Handle backslashes FIRST - escape existing backslashes
    text = text.replace('\\', '\\\\')
    
    # Now escape quotes (after handling backslashes)
    text = text.replace('"', '\\"')
    
    # Handle newlines properly for JSON
    text = text.replace('\n', '\\n')
    
    # Remove any remaining problematic sequences that could break JSON
    # This is more aggressive - remove any remaining unescaped quotes or backslashes
    text = re.sub(r'(?<!\\)"', '\\"', text)  # Escape any remaining unescaped quotes
    
    # Ensure string doesn't end with odd number of backslashes
    while text.endswith('\\') and not text.endswith('\\\\'):
        text = text[:-1] + '\\\\'
    
    # Final safety check - limit length to prevent memory issues
    if len(text) > 50000:  # Limit to 50KB
        text = text[:50000] + "... (content truncated for JSON safety)"
    
    return text

app = FastAPI(title="Strategic Intelligence App")

app.include_router(analysis.router)

# Authentication router removed for direct access

# Authentication helper removed for direct access

@app.on_event("startup")
async def startup_event():
    """Basic database connection test only - no full initialization"""
    try:
        print("Testing database connection...")
        
        # Basic connection test only
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent / 'data'))
        
        from data.database_config import test_connection
        
        if test_connection():
            print("Database connection successful!")
        else:
            print("Database connection failed!")
            
    except Exception as e:
        print(f"Database connection test failed: {e}")
        print("Some features may not work properly.")

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates
templates = Jinja2Templates(directory="app/templates")

# Request models
class AnalysisRequest(BaseModel):
    strategic_question: str
    time_frame: str
    region: str
    prompt: Optional[str] = None
    architecture: str = "parallel"

class PDFRequest(BaseModel):
    analysis_data: Dict[str, Any]
    strategic_question: str
    time_frame: str
    region: str

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Landing page - Direct access to home page without authentication"""
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard (redirect to home)"""
    return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

@app.get("/analysis", response_class=HTMLResponse)
async def analysis(request: Request):
    """Original streaming analysis page (for compatibility)"""
    return templates.TemplateResponse("analysis.html", {"request": request})

@app.get("/history", response_class=HTMLResponse)
async def history(request: Request):
    return templates.TemplateResponse("history.html", {"request": request})



@app.get("/api/analysis-history")
async def get_analysis_history(
    limit: int = 50,
    offset: int = 0,
    status: Optional[str] = None,
    region: Optional[str] = None,
    search: Optional[str] = None,
    request: Request = None
):
    try:
        # Add database imports for this endpoint
        import sys
        import os
        from pathlib import Path
        
        # Get the project root directory
        current_file = Path(__file__).resolve()
        project_root = current_file.parent.parent
        data_path = project_root / 'data'
        
        # Add data directory to Python path
        sys.path.insert(0, str(data_path))
        
        try:
            from database_service import DatabaseService
            
            # Show all sessions (no authentication required)
            sessions = DatabaseService.get_analysis_sessions(
                limit=limit,
                offset=offset,
                status_filter=status,
                region_filter=region,
                search_query=search
            )
            
            # Get total count with same filters
            total_count = DatabaseService.get_analysis_sessions_count(
                status_filter=status,
                region_filter=region,
                search_query=search
            )
            
            return {
                "status": "success",
                "data": {
                    "sessions": sessions,
                    "pagination": {
                        "limit": limit,
                        "offset": offset,
                        "total": total_count,
                        "has_more": len(sessions) == limit and (offset + limit) < total_count
                    }
                }
            }
            
        except ImportError:
            return {
                "status": "error",
                "message": "Database not available",
                "data": []
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch analysis history: {str(e)}")

# Admin user check removed for direct access

@app.get("/api/templates/categories")
async def get_template_categories():
    """Get all template categories with counts"""
    try:
        # Add database imports for this endpoint
        import sys
        import os
        from pathlib import Path
        
        # Get the project root directory
        current_file = Path(__file__).resolve()
        project_root = current_file.parent.parent
        data_path = project_root / 'data'
        
        # Add data directory to Python path
        sys.path.insert(0, str(data_path))
        
        try:
            from database_service import DatabaseService
            
            categories = DatabaseService.get_template_categories()
            return {
                "status": "success",
                "data": {"categories": categories}
            }
            
        except ImportError:
            return {
                "status": "error",
                "message": "Database not available",
                "data": {"categories": []}
            }
            
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/templates/{template_id}")
async def get_template(template_id: int):
    """Get a specific template by ID"""
    try:
        # Add database imports for this endpoint
        import sys
        import os
        from pathlib import Path
        
        # Get the project root directory
        current_file = Path(__file__).resolve()
        project_root = current_file.parent.parent
        data_path = project_root / 'data'
        
        # Add data directory to Python path
        sys.path.insert(0, str(data_path))
        
        try:
            from database_service import DatabaseService
            
            template = DatabaseService.get_template_by_id(template_id)
            if not template:
                return {"status": "error", "message": "Template not found"}
            
            return {
                "status": "success",
                "data": {"template": template}
            }
            
        except ImportError:
            return {
                "status": "error",
                "message": "Database not available"
            }
            
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/templates/{template_id}/use")
async def use_template(template_id: int):
    """Increment template usage count"""
    try:
        # Add database imports for this endpoint
        import sys
        import os
        from pathlib import Path
        
        # Get the project root directory
        current_file = Path(__file__).resolve()
        project_root = current_file.parent.parent
        data_path = project_root / 'data'
        
        # Add data directory to Python path
        sys.path.insert(0, str(data_path))
        
        try:
            from database_service import DatabaseService
            
            success = DatabaseService.increment_template_usage(template_id)
            if success:
                return {"status": "success", "message": "Template usage recorded"}
            else:
                return {"status": "error", "message": "Failed to record template usage"}
                
        except ImportError:
            return {
                "status": "error",
                "message": "Database not available"
            }
            
    except Exception as e:
        return {"status": "error", "message": str(e)}

async def stream_agent_outputs_realtime(orchestrator: OrchestratorAgent, input_data: Dict[str, Any], user_id: int = None):
    """Stream agent outputs in real-time with database integration."""
    try:
        # Create database session at start with user_id
        input_data_with_user = input_data.copy()
        if user_id:
            input_data_with_user['user_id'] = user_id
        orchestrator._create_analysis_session(input_data_with_user)
        
        # Cumulative input data for subsequent agents
        cumulative_input_data = input_data.copy()
        
        # Agent names mapping
        agent_names_map = {
            "Problem Explorer": "problem_explorer",
            "Best Practices": "best_practices", 
            "Horizon Scanning": "horizon_scanning",
            "Scenario Planning": "scenario_planning",
            "Research Synthesis": "research_synthesis",
            "Strategic Action": "strategic_action",
            "High Impact": "high_impact",
            "Backcasting": "backcasting"
        }
        
        # Helper function to process agent and return result
        async def process_agent(agent_name: str, current_input_data: Dict[str, Any]):
            agent_instance = orchestrator.agents[agent_name]
            result = await orchestrator.rate_limited_process(agent_instance, current_input_data.copy(), agent_name)
            return result
        
        # Stage 1: Problem Explorer
        result = await process_agent("Problem Explorer", cumulative_input_data)
        cumulative_input_data[agent_names_map["Problem Explorer"]] = result
        # Ensure session_id and agent_result_id are included in the response
        if orchestrator.current_session_id and 'session_id' not in result:
            result['session_id'] = orchestrator.current_session_id
        yield safe_json_dumps({"Problem Explorer": result}) + "\n"
        
        # Stage 2: Parallel agents (Best Practices, Horizon Scanning, Scenario Planning)
        parallel_agents = ["Best Practices", "Horizon Scanning", "Scenario Planning"]
        
        # Create tasks with proper mapping
        agent_tasks = {}
        for agent_name in parallel_agents:
            task = asyncio.create_task(process_agent(agent_name, cumulative_input_data))
            agent_tasks[agent_name] = task
        
        # Process parallel agents and yield results as they complete
        remaining_agents = set(parallel_agents)
        
        while remaining_agents:
            # Wait for any task to complete
            completed_tasks, pending_tasks = await asyncio.wait(
                [agent_tasks[agent_name] for agent_name in remaining_agents],
                return_when=asyncio.FIRST_COMPLETED
            )
            
            # Process completed tasks
            for completed_task in completed_tasks:
                # Find which agent this task belongs to
                completed_agent = None
                for agent_name in remaining_agents:
                    if agent_tasks[agent_name] == completed_task:
                        completed_agent = agent_name
                        break
                
                if completed_agent:
                    try:
                        result = await completed_task
                        
                        # Update cumulative data
                        agent_key = agent_names_map[completed_agent]
                        cumulative_input_data[agent_key] = result
                        
                        # Ensure session_id and agent_result_id are included in the response
                        if orchestrator.current_session_id and 'session_id' not in result:
                            result['session_id'] = orchestrator.current_session_id
                        
                        # Yield result with correct agent name
                        yield safe_json_dumps({completed_agent: result}) + "\n"
                        
                        # Remove from remaining agents
                        remaining_agents.remove(completed_agent)
                        
                    except Exception as task_error:
                        # Handle individual task errors
                        yield safe_json_dumps({completed_agent: f"Error: {str(task_error)}"}) + "\n"
                        remaining_agents.remove(completed_agent)
        
        # Stage 3: Research Synthesis
        result = await process_agent("Research Synthesis", cumulative_input_data)
        cumulative_input_data[agent_names_map["Research Synthesis"]] = result
        # Ensure session_id and agent_result_id are included in the response
        if orchestrator.current_session_id and 'session_id' not in result:
            result['session_id'] = orchestrator.current_session_id
        yield safe_json_dumps({"Research Synthesis": result}) + "\n"
        
        # Stage 4: Strategic Action
        result = await process_agent("Strategic Action", cumulative_input_data)
        cumulative_input_data[agent_names_map["Strategic Action"]] = result
        # Ensure session_id and agent_result_id are included in the response
        if orchestrator.current_session_id and 'session_id' not in result:
            result['session_id'] = orchestrator.current_session_id
        yield safe_json_dumps({"Strategic Action": result}) + "\n"
        
        # Stage 5: High Impact
        result = await process_agent("High Impact", cumulative_input_data)
        cumulative_input_data[agent_names_map["High Impact"]] = result
        # Ensure session_id and agent_result_id are included in the response
        if orchestrator.current_session_id and 'session_id' not in result:
            result['session_id'] = orchestrator.current_session_id
        yield safe_json_dumps({"High Impact": result}) + "\n"
        
        # Stage 6: Backcasting
        result = await process_agent("Backcasting", cumulative_input_data)
        cumulative_input_data[agent_names_map["Backcasting"]] = result
        # Ensure session_id and agent_result_id are included in the response
        if orchestrator.current_session_id and 'session_id' not in result:
            result['session_id'] = orchestrator.current_session_id
        yield safe_json_dumps({"Backcasting": result}) + "\n"
        
        # Update session completion status
        orchestrator._update_session_completion("completed")
        
        # Yield session info
        if orchestrator.current_session_id:
            yield safe_json_dumps({
                "session_info": {
                    "session_id": orchestrator.current_session_id,
                    "status": "completed"
                }
            }) + "\n"
            
    except Exception as e:
        # Update session as failed
        orchestrator._update_session_completion("failed")
        yield safe_json_dumps({"error": str(e)}) + "\n"

@app.post("/analyze-batch")
async def analyze_batch(request: AnalysisRequest):
    """Process analysis and return all agent results at once (for home page)"""
    try:
        # Initialize orchestrator
        orchestrator = OrchestratorAgent()
        
        # Convert request to dict
        input_data = request.dict()
        
        # Process all agents and return complete results
        results = await orchestrator.process(input_data, architecture=request.architecture)
        
        # Return the complete analysis results
        return {
            "status": "success",
            "results": results,
            "session_id": orchestrator.current_session_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-pdf")
async def generate_pdf(request: PDFRequest):
    """Generate PDF report from analysis data"""
    try:
        # Create a BytesIO buffer to hold the PDF
        buffer = io.BytesIO()
        
        # Create the PDF document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # Get the default stylesheet
        styles = getSampleStyleSheet()
        
        # Custom styles for better formatting
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontSize=28,
            spaceAfter=30,
            spaceBefore=20,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#1f2937'),
            fontName='Helvetica-Bold'
        )
        
        agent_heading_style = ParagraphStyle(
            'AgentHeading',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=16,
            spaceBefore=24,
            textColor=colors.HexColor('#3730a3'),
            fontName='Helvetica-Bold',
            borderWidth=1,
            borderColor=colors.HexColor('#e5e7eb'),
            borderPadding=8,
            backColor=colors.HexColor('#f8fafc')
        )
        
        section_heading_style = ParagraphStyle(
            'SectionHeading',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            spaceBefore=16,
            textColor=colors.HexColor('#1e40af'),
            fontName='Helvetica-Bold'
        )
        
        subsection_heading_style = ParagraphStyle(
            'SubsectionHeading',
            parent=styles['Heading3'],
            fontSize=12,
            spaceAfter=8,
            spaceBefore=12,
            textColor=colors.HexColor('#3730a3'),
            fontName='Helvetica-Bold'
        )
        
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=8,
            spaceBefore=4,
            alignment=TA_JUSTIFY,
            textColor=colors.HexColor('#374151'),
            leading=14
        )
        
        bullet_style = ParagraphStyle(
            'BulletStyle',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=4,
            spaceBefore=2,
            leftIndent=20,
            bulletIndent=10,
            textColor=colors.HexColor('#374151'),
            leading=13
        )
        
        summary_style = ParagraphStyle(
            'SummaryStyle',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            alignment=TA_JUSTIFY,
            textColor=colors.HexColor('#4b5563'),
            leading=14
        )
        
        # Build the story (content)
        story = []
        
        # Title page
        story.append(Paragraph("Strategic Intelligence Analysis Report", title_style))
        story.append(Spacer(1, 0.5*inch))
        
        # Executive summary section
        story.append(Paragraph("Executive Summary", section_heading_style))
        
        # Analysis details
        analysis_details = [
            f"<b>Strategic Question:</b> {request.strategic_question}",
            f"<b>Time Frame:</b> {request.time_frame.replace('_', ' ').title()}",
            f"<b>Region:</b> {request.region.replace('_', ' ').title()}",
            f"<b>Generated:</b> {datetime.now().strftime('%B %d, %Y at %H:%M')}"
        ]
        
        for detail in analysis_details:
            story.append(Paragraph(detail, summary_style))
            
        story.append(Spacer(1, 0.4*inch))
        story.append(PageBreak())
        
        # Process each agent's output
        agent_order = [
            'Problem Explorer',
            'Best Practices', 
            'Horizon Scanning',
            'Scenario Planning',
            'Research Synthesis',
            'Strategic Action',
            'High Impact',
            'Backcasting'
        ]
        
        for i, agent_name in enumerate(agent_order, 1):
            agent_key = agent_name.lower().replace(' ', '_')
            
            if agent_key in request.analysis_data:
                agent_data = request.analysis_data[agent_key]
                
                # Add agent section header
                story.append(Paragraph(f"{i}. {agent_name}", agent_heading_style))
                story.append(Spacer(1, 0.15*inch))
                
                # Process the agent's data
                content = extract_agent_content(agent_data)
                
                if content:
                    # Parse and format the content
                    formatted_paragraphs = parse_agent_content_for_pdf(content)
                    
                    for paragraph_data in formatted_paragraphs:
                        if paragraph_data['type'] == 'heading':
                            story.append(Paragraph(paragraph_data['content'], section_heading_style))
                        elif paragraph_data['type'] == 'subheading':
                            story.append(Paragraph(paragraph_data['content'], subsection_heading_style))
                        elif paragraph_data['type'] == 'bullet':
                            story.append(Paragraph(f"• {paragraph_data['content']}", bullet_style))
                        elif paragraph_data['type'] == 'numbered':
                            story.append(Paragraph(f"{paragraph_data['number']}. {paragraph_data['content']}", bullet_style))
                        elif paragraph_data['type'] == 'bold':
                            story.append(Paragraph(f"<b>{paragraph_data['content']}</b>", body_style))
                        else:  # regular paragraph
                            if paragraph_data['content'].strip():
                                story.append(Paragraph(paragraph_data['content'], body_style))
                
                story.append(Spacer(1, 0.25*inch))
                
                # Add page break after every 2 agents (except the last one)
                if i % 2 == 0 and i < len(agent_order):
                    story.append(PageBreak())
        
        # Build the PDF
        doc.build(story)
        
        # Get the PDF data
        buffer.seek(0)
        pdf_data = buffer.getvalue()
        buffer.close()
        
        # Return as download response
        filename = f"strategic_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        return StreamingResponse(
            io.BytesIO(pdf_data),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")

def extract_agent_content(agent_data):
    """Extract content from agent data structure"""
    if isinstance(agent_data, dict):
        if 'data' in agent_data and isinstance(agent_data['data'], dict):
            data = agent_data['data']
            if 'formatted_output' in data:
                return data['formatted_output']
            elif 'raw_response' in data:
                return data['raw_response']
            else:
                # Try to concatenate all string values
                content_parts = []
                for key, value in data.items():
                    if isinstance(value, str) and key not in ['raw_response', 'formatted_output']:
                        content_parts.append(f"**{key.replace('_', ' ').title()}**\n{value}")
                return '\n\n'.join(content_parts)
        else:
            return str(agent_data)
    else:
        return str(agent_data)

def parse_agent_content_for_pdf(content: str):
    """Parse agent content and return structured paragraphs for PDF formatting"""
    if not content:
        return []
    
    paragraphs = []
    lines = content.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Detect headings (markdown style)
        if line.startswith('###'):
            paragraphs.append({
                'type': 'subheading',
                'content': clean_text_for_pdf(line.replace('###', '').strip())
            })
        elif line.startswith('##'):
            paragraphs.append({
                'type': 'heading',
                'content': clean_text_for_pdf(line.replace('##', '').strip())
            })
        elif line.startswith('#'):
            paragraphs.append({
                'type': 'heading',
                'content': clean_text_for_pdf(line.replace('#', '').strip())
            })
        # Detect bullet points
        elif line.startswith('- ') or line.startswith('* ') or line.startswith('• '):
            content_text = line[2:].strip()
            formatted_content = format_inline_text(content_text)
            paragraphs.append({
                'type': 'bullet',
                'content': formatted_content
            })
        # Detect numbered lists
        elif re.match(r'^\d+\.\s+', line):
            match = re.match(r'^(\d+)\.\s+(.+)', line)
            if match:
                formatted_content = format_inline_text(match.group(2))
                paragraphs.append({
                    'type': 'numbered',
                    'number': match.group(1),
                    'content': formatted_content
                })
        # Detect bold text (entire line)
        elif line.startswith('**') and line.endswith('**') and len(line) > 4:
            paragraphs.append({
                'type': 'bold',
                'content': clean_text_for_pdf(line[2:-2])
            })
        # Regular paragraph
        else:
            # Handle inline formatting FIRST, then clean
            formatted_content = format_inline_text(line)
            if formatted_content.strip():
                paragraphs.append({
                    'type': 'paragraph',
                    'content': formatted_content
                })
    
    return paragraphs

def format_inline_text(text: str) -> str:
    """Format inline text with bold, italic, etc."""
    if not text:
        return ""
    
    # Convert **bold** to <b>bold</b> (non-greedy matching)
    text = re.sub(r'\*\*([^*]+?)\*\*', r'<b>\1</b>', text)
    
    # Convert *italic* to <i>italic</i> (but not ** patterns)
    text = re.sub(r'(?<!\*)\*([^*]+?)\*(?!\*)', r'<i>\1</i>', text)
    
    # Convert _italic_ to <i>italic</i>
    text = re.sub(r'_([^_]+?)_', r'<i>\1</i>', text)
    
    # Clean up any remaining ** that weren't matched
    text = text.replace('**', '')
    
    return clean_text_for_pdf(text)

def clean_text_for_pdf(text: str) -> str:
    """Clean and escape text for PDF display"""
    if not text:
        return ""
    
    # Convert to string and handle None
    text = str(text) if text is not None else ""
    
    # First, preserve our HTML formatting tags
    text = text.replace('<b>', '|||BOLD_START|||')
    text = text.replace('</b>', '|||BOLD_END|||')
    text = text.replace('<i>', '|||ITALIC_START|||')
    text = text.replace('</i>', '|||ITALIC_END|||')
    
    # Escape special characters for ReportLab
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;').replace('>', '&gt;')
    
    # Restore our formatting tags
    text = text.replace('|||BOLD_START|||', '<b>')
    text = text.replace('|||BOLD_END|||', '</b>')
    text = text.replace('|||ITALIC_START|||', '<i>')
    text = text.replace('|||ITALIC_END|||', '</i>')
    
    return text

# 🚀 SMART TEMPLATE GENERATION & USER HISTORY ENDPOINTS

@app.post("/api/track-query-pattern")
async def track_query_pattern(request: Request):
    """Track user query patterns for AI template generation"""
    try:
        data = await request.json()
        
        result = DatabaseService.track_user_query_pattern(
            strategic_question=data.get('strategic_question', ''),
            time_frame=data.get('time_frame', ''),
            region=data.get('region', ''),
            additional_instructions=data.get('additional_instructions'),
            user_id=data.get('user_id', 'anonymous')
        )
        
        return JSONResponse({
            "success": result,
            "message": "Query pattern tracked successfully" if result else "Failed to track pattern"
        })
        
    except Exception as e:
        logging.error(f"Error tracking query pattern: {e}")
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)

@app.get("/api/ai-template-suggestions/{user_id}")
async def get_ai_template_suggestions(user_id: str = 'anonymous', limit: int = 3):
    """Get AI-powered template suggestions based on user history"""
    try:
        suggestions = DatabaseService.generate_ai_template_suggestions(user_id, limit)
        
        return JSONResponse({
            "success": True,
            "suggestions": suggestions,
            "count": len(suggestions)
        })
        
    except Exception as e:
        logging.error(f"Error getting AI template suggestions: {e}")
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)

@app.post("/api/get-template-recommendations")
async def get_template_recommendations(request: Request):
    """Get template recommendations based on current question and user history"""
    try:
        data = await request.json()
        strategic_question = data.get('strategic_question', '')
        user_id = data.get('user_id', 'anonymous')
        
        if not strategic_question:
            return JSONResponse({"success": False, "error": "Strategic question is required"}, status_code=400)
        
        recommendations = DatabaseService.get_template_recommendations_for_user(
            strategic_question, user_id
        )
        
        return JSONResponse({
            "success": True,
            "recommendations": recommendations,
            "count": len(recommendations)
        })
        
    except Exception as e:
        logging.error(f"Error getting template recommendations: {e}")
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)

@app.post("/api/save-analysis-as-template")
async def save_analysis_as_template(request: Request):
    """Save a completed analysis as a reusable template"""
    try:
        data = await request.json()
        
        session_id = data.get('session_id')
        template_name = data.get('template_name', '').strip()
        template_description = data.get('template_description', '').strip()
        category = data.get('category', 'User Generated').strip()
        user_id = data.get('user_id', 'anonymous')
        
        if not all([session_id, template_name, template_description]):
            return JSONResponse({
                "success": False, 
                "error": "Session ID, template name, and description are required"
            }, status_code=400)
        
        template_id = DatabaseService.save_analysis_as_template(
            session_id=session_id,
            template_name=template_name,
            template_description=template_description,
            category=category,
            user_id=user_id
        )
        
        if template_id:
            return JSONResponse({
                "success": True,
                "template_id": template_id,
                "message": f"Template '{template_name}' saved successfully!"
            })
        else:
            return JSONResponse({
                "success": False,
                "error": "Failed to save template. Analysis session may not exist."
            }, status_code=400)
        
    except Exception as e:
        logging.error(f"Error saving analysis as template: {e}")
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)

@app.get("/api/popular-query-patterns")
async def get_popular_query_patterns(limit: int = 10):
    """Get popular query patterns for auto-template generation"""
    try:
        patterns = DatabaseService.get_popular_query_patterns(limit)
        
        return JSONResponse({
            "success": True,
            "patterns": patterns,
            "count": len(patterns)
        })
        
    except Exception as e:
        logging.error(f"Error getting popular query patterns: {e}")
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)

@app.post("/api/generate-smart-template")
async def generate_smart_template(request: Request):
    """Generate a smart template based on AI analysis of user patterns"""
    try:
        data = await request.json()
        user_id = data.get('user_id', 'anonymous')
        domain = data.get('domain')
        intent = data.get('intent')
        
        # Get user patterns for analysis
        patterns = DatabaseService.get_popular_query_patterns(20)
        
        # Find matching patterns
        matching_patterns = []
        for pattern in patterns:
            if (domain and pattern.get('domain') == domain) or \
               (intent and pattern.get('intent') == intent):
                matching_patterns.append(pattern)
        
        if not matching_patterns:
            return JSONResponse({
                "success": False,
                "error": "No matching patterns found for smart template generation"
            }, status_code=404)
        
        # Generate smart template based on patterns
        best_pattern = max(matching_patterns, key=lambda x: x.get('frequency', 0))
        
        # Create AI-generated template
        template_name = f"Smart {best_pattern['domain'].title()} {best_pattern['intent'].replace('_', ' ').title()}"
        template_description = f"AI-generated template based on popular {best_pattern['domain']} analysis patterns with {best_pattern['intent'].replace('_', ' ')} focus."
        
        # Generate strategic question template
        strategic_question = DatabaseService._generate_smart_question_template(
            best_pattern['domain'], 
            best_pattern['intent'], 
            best_pattern.get('keywords', '')
        )
        
        # Create the template
        template_id = DatabaseService.create_template(
            name=template_name,
            description=template_description,
            category='AI Generated',
            strategic_question=strategic_question,
            default_time_frame=best_pattern.get('time_frame', 'Next 12 months'),
            default_region=best_pattern.get('region', 'Global'),
            additional_instructions=f"This template was automatically generated based on analysis of {best_pattern['frequency']} similar queries.",
            tags=[best_pattern['domain'], best_pattern['intent'], 'ai-generated', 'smart-template'],
            is_public=True,
            created_by='ai-system'
        )
        
        return JSONResponse({
            "success": True,
            "template_id": template_id,
            "template_name": template_name,
            "message": "Smart template generated successfully!",
            "pattern_data": best_pattern
        })
        
    except Exception as e:
        logging.error(f"Error generating smart template: {e}")
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)

@app.get("/api/user-analytics/{user_id}")
async def get_user_analytics(user_id: str):
    """Get user analytics for personalized template suggestions"""
    try:
        # Get user query patterns using the existing database service methods
        from data.database_config import get_db_connection
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Domain distribution
            cursor.execute("""
                SELECT extracted_domain, COUNT(*) as count
                FROM user_query_patterns 
                WHERE user_id = %s AND created_at >= NOW() - INTERVAL '30 days'
                GROUP BY extracted_domain
                ORDER BY count DESC
            """, (user_id,))
            
            domain_stats = [{"domain": row[0], "count": row[1]} for row in cursor.fetchall()]
            
            # Intent distribution
            cursor.execute("""
                SELECT extracted_intent, COUNT(*) as count
                FROM user_query_patterns 
                WHERE user_id = %s AND created_at >= NOW() - INTERVAL '30 days'
                GROUP BY extracted_intent
                ORDER BY count DESC
            """, (user_id,))
            
            intent_stats = [{"intent": row[0], "count": row[1]} for row in cursor.fetchall()]
            
            # Recent activity
            cursor.execute("""
                SELECT strategic_question, extracted_domain, extracted_intent, created_at
                FROM user_query_patterns 
                WHERE user_id = %s 
                ORDER BY created_at DESC
                LIMIT 10
            """, (user_id,))
            
            recent_activity = []
            for row in cursor.fetchall():
                recent_activity.append({
                    "question": row[0],
                    "domain": row[1],
                    "intent": row[2],
                    "created_at": row[3].isoformat() if row[3] else None
                })
        
        return JSONResponse({
            "success": True,
            "analytics": {
                "domain_distribution": domain_stats,
                "intent_distribution": intent_stats,
                "recent_activity": recent_activity,
                "total_queries": len(recent_activity)
            }
        })
        
    except Exception as e:
        logging.error(f"Error getting user analytics: {e}")
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)

@app.get("/api/analysis-session/{session_id}")
async def get_analysis_session(session_id: int):
    try:
        # Add database imports for this endpoint
        import sys
        import os
        from pathlib import Path
        
        # Get the project root directory
        current_file = Path(__file__).resolve()
        project_root = current_file.parent.parent
        data_path = project_root / 'data'
        
        # Add data directory to Python path
        sys.path.insert(0, str(data_path))
        
        try:
            from database_service import DatabaseService
            
            # Get analysis session with all agent results
            session = DatabaseService.get_analysis_session(session_id)
            
            if not session:
                return JSONResponse({
                    "status": "error",
                    "message": "Session not found"
                }, status_code=404)
            
            return {
                "status": "success",
                "data": session
            }
            
        except ImportError:
            return JSONResponse({
                "status": "error",
                "message": "Database not available"
            }, status_code=500)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch session details: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True) 