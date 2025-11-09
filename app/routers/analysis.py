from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from typing import Dict, Any
import json
import os
from app.agents.orchestrator_agent import OrchestratorAgent
from pydantic import BaseModel
from typing import Optional
import asyncio


router = APIRouter(prefix="/analysis", tags=["analysis"])
templates = Jinja2Templates(directory="app/templates")

# Ensure analysis directory exists
os.makedirs("data/analysis", exist_ok=True)

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


@router.get("/", response_class=HTMLResponse)
async def list_analyses(request: Request):
    """List all analyses"""
    analyses = []
    for filename in os.listdir("data/analysis"):
        if filename.endswith(".json"):
            with open(f"data/analysis/{filename}", "r") as f:
                analyses.append(json.load(f))
    return templates.TemplateResponse(
        "analysis.html",
        {"request": request, "analyses": analyses}
    )

@router.post("/")
async def create_analysis(analysis: Dict[str, Any]):
    """Create a new analysis"""
    analysis_id = analysis.get("id")
    if not analysis_id:
        raise HTTPException(status_code=400, detail="Analysis ID is required")
    
    filepath = f"data/analysis/{analysis_id}.json"
    if os.path.exists(filepath):
        raise HTTPException(status_code=400, detail="Analysis already exists")
    
    with open(filepath, "w") as f:
        json.dump(analysis, f, indent=2)
    
    return {"status": "success", "message": "Analysis created successfully"}

@router.get("/{analysis_id}")
async def get_analysis(analysis_id: str):
    """Get a specific analysis"""
    filepath = f"data/analysis/{analysis_id}.json"
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    with open(filepath, "r") as f:
        return json.load(f)

@router.put("/{analysis_id}")
async def update_analysis(analysis_id: str, analysis: Dict[str, Any]):
    """Update an analysis"""
    filepath = f"data/analysis/{analysis_id}.json"
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    with open(filepath, "w") as f:
        json.dump(analysis, f, indent=2)
    
    return {"status": "success", "message": "Analysis updated successfully"}

@router.delete("/{analysis_id}")
async def delete_analysis(analysis_id: str):
    """Delete an analysis"""
    filepath = f"data/analysis/{analysis_id}.json"
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    os.remove(filepath)
    return {"status": "success", "message": "Analysis deleted successfully"} 


class AnalysisRequest(BaseModel):
    strategic_question: str
    time_frame: str
    region: str
    architecture: Optional[str] = None
    prompt: Optional[str] = None


@router.post("/analyze-batch")
async def analyze_batch(request: AnalysisRequest):
    """Process analysis and return all agent results at once (for home page)"""
    try:
        # Initialize orchestrator
        orchestrator = OrchestratorAgent()
        
        # Convert request to dict
        input_data = request.dict()
        
        # Process all agents and return complete results
        results = await orchestrator.process(input_data)
        
        # Return the complete analysis results
        return {
            "status": "success",
            "results": results,
            "session_id": orchestrator.current_session_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 


@router.post("/analyze")
async def analyze(request: AnalysisRequest):
    try:
        # Initialize orchestrator
        orchestrator = OrchestratorAgent()
        
        # Convert request to dict
        input_data = request.dict()
        
        # Return real-time streaming response without user information
        return StreamingResponse(
            stream_agent_outputs_realtime(orchestrator, input_data),
            media_type="application/x-ndjson"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 