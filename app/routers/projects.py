from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import List, Dict, Any
import json
import os

router = APIRouter(prefix="/projects", tags=["projects"])
templates = Jinja2Templates(directory="app/templates")

# Ensure projects directory exists
os.makedirs("data/projects", exist_ok=True)

@router.get("/", response_class=HTMLResponse)
async def list_projects(request: Request):
    """List all projects"""
    projects = []
    for filename in os.listdir("data/projects"):
        if filename.endswith(".json"):
            with open(f"data/projects/{filename}", "r") as f:
                projects.append(json.load(f))
    return templates.TemplateResponse(
        "projects.html",
        {"request": request, "projects": projects}
    )

@router.post("/")
async def create_project(project: Dict[str, Any]):
    """Create a new project"""
    project_id = project.get("id")
    if not project_id:
        raise HTTPException(status_code=400, detail="Project ID is required")
    
    filepath = f"data/projects/{project_id}.json"
    if os.path.exists(filepath):
        raise HTTPException(status_code=400, detail="Project already exists")
    
    with open(filepath, "w") as f:
        json.dump(project, f, indent=2)
    
    return {"status": "success", "message": "Project created successfully"}

@router.get("/{project_id}")
async def get_project(project_id: str):
    """Get a specific project"""
    filepath = f"data/projects/{project_id}.json"
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Project not found")
    
    with open(filepath, "r") as f:
        return json.load(f)

@router.put("/{project_id}")
async def update_project(project_id: str, project: Dict[str, Any]):
    """Update a project"""
    filepath = f"data/projects/{project_id}.json"
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Project not found")
    
    with open(filepath, "w") as f:
        json.dump(project, f, indent=2)
    
    return {"status": "success", "message": "Project updated successfully"}

@router.delete("/{project_id}")
async def delete_project(project_id: str):
    """Delete a project"""
    filepath = f"data/projects/{project_id}.json"
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Project not found")
    
    os.remove(filepath)
    return {"status": "success", "message": "Project deleted successfully"} 