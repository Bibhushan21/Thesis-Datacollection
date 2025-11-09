from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import logging
import sys
import os
from pathlib import Path

# Database imports - Fixed path handling
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent.parent  # Go up from routers -> app -> project root
data_path = project_root / 'data'

# Add data directory to Python path
sys.path.insert(0, str(data_path))

try:
    from database_service import DatabaseService
    DATABASE_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Database modules not available: {e}")
    DATABASE_AVAILABLE = False

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ratings", tags=["ratings"])

# Pydantic models for request validation
class RatingSubmission(BaseModel):
    session_id: int
    agent_result_id: int
    agent_name: str
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5 stars")
    review_text: Optional[str] = None
    helpful_aspects: Optional[List[str]] = None
    improvement_suggestions: Optional[str] = None
    would_recommend: bool = True
    user_id: Optional[int] = None

class RatingQuery(BaseModel):
    agent_name: Optional[str] = None
    session_id: Optional[int] = None
    limit: int = Field(50, ge=1, le=100)
    offset: int = Field(0, ge=0)

@router.post("/submit")
async def submit_rating(rating_data: RatingSubmission) -> JSONResponse:
    """Submit a rating for an agent result"""
    if not DATABASE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        # Log the incoming data for debugging
        logger.info(f"Received rating submission: {rating_data.dict()}")
        
        # Validate that session and agent result exist
        session = DatabaseService.get_analysis_session(rating_data.session_id)
        if not session:
            logger.warning(f"Invalid session_id {rating_data.session_id} in rating submission")
            raise HTTPException(status_code=400, detail=f"Session {rating_data.session_id} not found")
        
        # Check if agent result exists (you'll need to add this method to DatabaseService)
        agent_result = DatabaseService.get_agent_result_by_id(rating_data.agent_result_id)
        if not agent_result:
            logger.warning(f"Invalid agent_result_id {rating_data.agent_result_id} in rating submission")
            raise HTTPException(status_code=400, detail=f"Agent result {rating_data.agent_result_id} not found")
        
        # Validate that the agent result belongs to the session
        if agent_result['session_id'] != rating_data.session_id:
            logger.warning(f"Agent result {rating_data.agent_result_id} does not belong to session {rating_data.session_id}")
            raise HTTPException(status_code=400, detail="Agent result does not belong to the specified session")
        
        # Validate that the agent name matches
        if agent_result['agent_name'] != rating_data.agent_name:
            logger.warning(f"Agent name mismatch: expected {agent_result['agent_name']}, got {rating_data.agent_name}")
            raise HTTPException(status_code=400, detail="Agent name does not match the agent result")
        
        # Check if user has already rated this agent result
        existing_rating = DatabaseService.get_user_rating_for_result(rating_data.agent_result_id, rating_data.user_id)
        if existing_rating:
            logger.info(f"User {rating_data.user_id} already rated agent result {rating_data.agent_result_id}")
            raise HTTPException(status_code=409, detail="You have already rated this agent result")
        
        rating_id = DatabaseService.submit_agent_rating(
            session_id=rating_data.session_id,
            agent_result_id=rating_data.agent_result_id,
            agent_name=rating_data.agent_name,
            rating=rating_data.rating,
            review_text=rating_data.review_text,
            helpful_aspects=rating_data.helpful_aspects,
            improvement_suggestions=rating_data.improvement_suggestions,
            would_recommend=rating_data.would_recommend,
            user_id=rating_data.user_id
        )
        
        if rating_id:
            logger.info(f"Successfully submitted rating {rating_id} for agent {rating_data.agent_name} in session {rating_data.session_id}")
            return JSONResponse(
                status_code=200,
                content={
                    "status": "success",
                    "message": "Rating submitted successfully",
                    "rating_id": rating_id,
                    "session_id": rating_data.session_id,
                    "agent_result_id": rating_data.agent_result_id
                }
            )
        else:
            logger.error(f"DatabaseService.submit_agent_rating returned None for data: {rating_data.dict()}")
            raise HTTPException(status_code=400, detail="Failed to submit rating - database operation returned None")
            
    except HTTPException:
        # Re-raise HTTP exceptions (like validation errors)
        raise
    except Exception as e:
        logger.error(f"Error submitting rating: {str(e)}")
        logger.error(f"Rating data was: {rating_data.dict()}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/agent/{agent_name}")
async def get_agent_ratings(agent_name: str, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
    """Get ratings for a specific agent"""
    if not DATABASE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        ratings = DatabaseService.get_agent_ratings(
            agent_name=agent_name,
            limit=limit,
            offset=offset
        )
        
        summary = DatabaseService.get_agent_rating_summary(agent_name)
        
        return {
            "agent_name": agent_name,
            "ratings": ratings,
            "summary": summary,
            "pagination": {
                "limit": limit,
                "offset": offset,
                "total": len(ratings)
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting agent ratings: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/session/{session_id}")
async def get_session_ratings(session_id: int) -> Dict[str, Any]:
    """Get all ratings for a specific analysis session"""
    if not DATABASE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        ratings = DatabaseService.get_agent_ratings(session_id=session_id)
        
        # Group ratings by agent
        agent_ratings = {}
        for rating in ratings:
            agent_name = rating['agent_name']
            if agent_name not in agent_ratings:
                agent_ratings[agent_name] = []
            agent_ratings[agent_name].append(rating)
        
        return {
            "session_id": session_id,
            "ratings_by_agent": agent_ratings,
            "total_ratings": len(ratings)
        }
        
    except Exception as e:
        logger.error(f"Error getting session ratings: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/user/{user_id}/result/{agent_result_id}")
async def get_user_rating(agent_result_id: int, user_id: str = "anonymous") -> Dict[str, Any]:
    """Get user's existing rating for a specific agent result"""
    if not DATABASE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        rating = DatabaseService.get_user_rating_for_result(agent_result_id, user_id)
        
        return {
            "user_rating": rating,
            "has_rated": rating is not None
        }
        
    except Exception as e:
        logger.error(f"Error getting user rating: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/summaries")
async def get_all_rating_summaries() -> Dict[str, Any]:
    """Get rating summaries for all agents"""
    if not DATABASE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        summaries = DatabaseService.get_all_agent_rating_summaries()
        
        return {
            "agent_summaries": summaries,
            "total_agents": len(summaries)
        }
        
    except Exception as e:
        logger.error(f"Error getting rating summaries: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/top-rated")
async def get_top_rated_agents(limit: int = 10) -> Dict[str, Any]:
    """Get top-rated agents"""
    if not DATABASE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        top_agents = DatabaseService.get_top_rated_agents(limit=limit)
        
        return {
            "top_rated_agents": top_agents,
            "limit": limit
        }
        
    except Exception as e:
        logger.error(f"Error getting top rated agents: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/analytics")
async def get_rating_analytics(days_back: int = 30) -> Dict[str, Any]:
    """Get rating analytics for dashboard"""
    if not DATABASE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        analytics = DatabaseService.get_rating_analytics(days_back=days_back)
        
        return {
            "analytics": analytics,
            "period": f"Last {days_back} days"
        }
        
    except Exception as e:
        logger.error(f"Error getting rating analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.delete("/result/{agent_result_id}/user/{user_id}")
async def delete_rating(agent_result_id: int, user_id: str = "anonymous") -> JSONResponse:
    """Delete a user's rating (for testing purposes)"""
    if not DATABASE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Database not available")
    
    # This would typically require admin privileges in production
    try:
        # Implementation would go here - for now just return success
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "message": "Rating deletion functionality not implemented yet"
            }
        )
        
    except Exception as e:
        logger.error(f"Error deleting rating: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") 