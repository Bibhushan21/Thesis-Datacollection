from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Dict, Any
from app.agents.best_practices_agent import BestPracticesAgent
from app.agents.scenario_planning_agent import ScenarioPlanningAgent
from app.agents.horizon_scanning_agent import HorizonScanningAgent
from app.agents.research_synthesis_agent import ResearchSynthesisAgent
import json
import os
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agents", tags=["agents"])
templates = Jinja2Templates(directory="app/templates")

# Initialize agents
agents = {
    "best_practices": BestPracticesAgent(),
    "scenario_planning": ScenarioPlanningAgent(),
    "horizon_scan": HorizonScanningAgent(),
    "synthesis": ResearchSynthesisAgent()
}

@router.get("/", response_class=HTMLResponse)
async def list_agents(request: Request):
    """List all available agents"""
    return templates.TemplateResponse(
        "agents.html",
        {"request": request, "agents": list(agents.keys())}
    )

@router.post("/{agent_name}/process")
async def process_agent(agent_name: str, input_data: Dict[str, Any]):
    """Process input data with a specific agent"""
    if agent_name not in agents:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    try:
        # Log the incoming request
        logger.info(f"Processing request for agent: {agent_name}")
        logger.info(f"Input data: {json.dumps(input_data, indent=2)}")
        
        # Process the request
        result = await agents[agent_name].process(input_data)
        
        # Log the result
        logger.info(f"Agent {agent_name} processing completed")
        logger.info(f"Result: {json.dumps(result, indent=2)}")
        
        return result
    except HTTPException as he:
        logger.error(f"HTTP Exception in agent {agent_name}: {he.detail}")
        raise he
    except Exception as e:
        logger.error(f"Unexpected error in agent {agent_name}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )

@router.get("/{agent_name}/status")
async def get_agent_status(agent_name: str):
    """Get the status of a specific agent"""
    if agent_name not in agents:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    try:
        return {
            "status": "active",
            "agent_name": agent_name,
            "capabilities": agents[agent_name].get_system_prompt(),
            "required_fields": agents[agent_name].required_fields,
            "optional_fields": agents[agent_name].optional_fields
        }
    except Exception as e:
        logger.error(f"Error getting status for agent {agent_name}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting agent status: {str(e)}"
        ) 