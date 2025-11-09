from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent
from .problem_explorer_agent import ProblemExplorerAgent
from .best_practices_agent import BestPracticesAgent
from .horizon_scanning_agent import HorizonScanningAgent
from .scenario_planning_agent import ScenarioPlanningAgent
from .research_synthesis_agent import ResearchSynthesisAgent
from .strategic_action_agent import StrategicActionAgent
from .high_impact_agent import HighImpactAgent
from .backcasting_agent import BackcastingAgent
import asyncio
import time
from fastapi import HTTPException
import random
import logging
import json
import re # Added for hierarchical planning

# Database imports - Fixed path handling
import sys
import os
from pathlib import Path

# Get the project root directory (Strategic Intelligence App)
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent.parent  # Go up from agents -> app -> project root
data_path = project_root / 'data'

# Add data directory to Python path
sys.path.insert(0, str(data_path))

# Database imports
try:
    from database_service import DatabaseService
    from database_config import test_connection
    DATABASE_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Database modules not available: {e}")
    DATABASE_AVAILABLE = False

logger = logging.getLogger(__name__)

class OrchestratorAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        # Initialize agents in the desired order
        self.agents = {
            "Problem Explorer": ProblemExplorerAgent(),
            "Best Practices": BestPracticesAgent(),
            "Horizon Scanning": HorizonScanningAgent(),
            "Scenario Planning": ScenarioPlanningAgent(),
            "Research Synthesis": ResearchSynthesisAgent(),
            "Strategic Action": StrategicActionAgent(),
            "High Impact": HighImpactAgent(),
            "Backcasting": BackcastingAgent()
        }
        self.last_request_time = 0
        self.min_request_interval = 7.0  # Minimum time between requests (adjusted for 10 RPM API limit)
        self.max_retries = 3
        self.base_delay = 1.0  # Base delay for exponential backoff
        
        # Database session tracking
        self.current_session_id = None
        self.session_start_time = None
        self.db_enabled = self._test_database_connection()

        # Map agent display names to the keys used for their results in data dictionaries
        self.agent_names_map = {
            "Problem Explorer": "problem_explorer",
            "Best Practices": "best_practices",
            "Horizon Scanning": "horizon_scanning",
            "Scenario Planning": "scenario_planning",
            "Research Synthesis": "research_synthesis",
            "Strategic Action": "strategic_action",
            "High Impact": "high_impact",
            "Backcasting": "backcasting"
        }

    def _test_database_connection(self) -> bool:
        """Test if database is available."""
        if not DATABASE_AVAILABLE:
            logger.warning("Database modules not available - running without database storage")
            return False
            
        try:
            if test_connection():
                logger.info("Database connection successful - enabling database features")
                return True
            else:
                logger.warning("Database connection failed - running without database storage")
                return False
        except Exception as e:
            logger.warning(f"Database connection test failed: {str(e)} - running without database storage")
            return False

    def get_system_prompt(self) -> str:
        return """You are the Orchestrator Agent. Your mission is to coordinate and manage the strategic intelligence analysis process. Focus on:

1. Task Coordination: Manage the flow of analysis between agents
2. Data Integration: Combine insights from different agents
3. Quality Control: Ensure analysis quality and consistency
4. Progress Tracking: Monitor analysis progress
5. Result Synthesis: Integrate final results

Your role is to ensure a smooth and effective analysis process."""

    def format_prompt(self, input_data: Dict[str, Any]) -> str:
        return f"""Coordinate the analysis of the following strategic challenge:

Strategic Question: {input_data.get('strategic_question', 'N/A')}
Time Frame: {input_data.get('time_frame', 'N/A')}
Region: {input_data.get('region', 'N/A')}
Additional Instructions: {input_data.get('prompt', 'N/A')}

Previous Analysis Results:
{self._format_previous_results(input_data)}

Provide a coordinated analysis plan and execution strategy."""

    def _format_previous_results(self, input_data: Dict[str, Any]) -> str:
        """Format previous analysis results for the prompt"""
        results = []
        for agent_type in ['problem_explorer', 'best_practices', 'horizon_scanning', 
                          'scenario_planning', 'research_synthesis', 'strategic_action', 'high_impact']:
            if agent_type in input_data:
                agent_result = input_data[agent_type]
                
                # Handle different result structures robustly
                if isinstance(agent_result, str):
                    # If it's a string, try to parse it as JSON first
                    try:
                        agent_result = json.loads(agent_result)
                    except json.JSONDecodeError:
                        # If parsing fails, use the string directly
                        results.append(f"{agent_type.replace('_', ' ').title()}: {agent_result[:200]}...")
                        continue
                
                # Now we know it's a dictionary
                if isinstance(agent_result, dict):
                    # Try to get formatted_output first, then data, then convert whole dict to string
                    if 'data' in agent_result and isinstance(agent_result['data'], dict):
                        if 'formatted_output' in agent_result['data']:
                            content = agent_result['data']['formatted_output'][:500]
                        elif 'analysis' in agent_result['data']:
                            content = agent_result['data']['analysis'][:500]
                        else:
                            content = str(agent_result['data'])[:500]
                    else:
                        content = str(agent_result)[:500]
                    results.append(f"{agent_type.replace('_', ' ').title()}: {content}")
                else:
                    # Fallback for any other type
                    results.append(f"{agent_type.replace('_', ' ').title()}: {str(agent_result)[:200]}")
                    
        return '\n'.join(results) if results else 'No previous results available'

    def _create_analysis_session(self, input_data: Dict[str, Any]) -> None:
        """Create database session for the analysis."""
        if not self.db_enabled or not DATABASE_AVAILABLE:
            return
            
        try:
            self.current_session_id = DatabaseService.create_analysis_session(
                strategic_question=input_data.get('strategic_question', ''),
                time_frame=input_data.get('time_frame', ''),
                region=input_data.get('region', ''),
                additional_instructions=input_data.get('prompt', ''),
                user_id=input_data.get('user_id'),
                architecture=input_data.get('architecture', 'unknown')
            )
            self.session_start_time = time.time()
            
            if self.current_session_id:
                # Minimal logging - just session creation
                print(f"Created database session {self.current_session_id}")
                # Log session creation
                DatabaseService.log_system_event(
                    log_level="INFO",
                    component="orchestrator",
                    message=f"Analysis session {self.current_session_id} started",
                    session_id=self.current_session_id,
                    details={
                        "strategic_question": input_data.get('strategic_question', ''),
                        "time_frame": input_data.get('time_frame', ''),
                        "region": input_data.get('region', '')
                    }
                )
            else:
                print("Failed to create database session")
                
        except Exception as e:
            print(f"Error creating database session: {str(e)}")
            self.current_session_id = None

    def _save_agent_result(self, agent_name: str, result: Dict[str, Any], processing_time: float) -> Optional[int]:
        """Save individual agent result to database and return the result ID."""
        if not self.db_enabled or not self.current_session_id or not DATABASE_AVAILABLE:
            return None
            
        try:
            # Handle cases where the result might be a string instead of a dictionary
            if isinstance(result, str):
                result = {"data": result}

            # Extract different data formats from result
            raw_response = ""
            formatted_output = ""
            structured_data = {}
            token_usage = 0
            
            if isinstance(result.get('data'), dict):
                # Get raw response (could be the full data or a specific field)
                raw_response = json.dumps(result['data'], indent=2)
                token_usage = result['data'].get('token_usage', 0)
                
                # Get formatted output (markdown content)
                if 'formatted_output' in result['data']:
                    formatted_output = result['data']['formatted_output']
                elif 'analysis' in result['data']:
                    formatted_output = result['data']['analysis']
                else:
                    formatted_output = str(result['data'])
                
                # Store structured data
                structured_data = result['data']
            else:
                raw_response = str(result.get('data', ''))
                formatted_output = raw_response
                structured_data = result
                token_usage = result.get('token_usage', 0)
            
            # Determine agent type
            agent_type_map = {
                "Problem Explorer": "analysis",
                "Best Practices": "research", 
                "Horizon Scanning": "scanning",
                "Scenario Planning": "planning",
                "Research Synthesis": "synthesis",
                "Strategic Action": "strategy",
                "High Impact": "impact",
                "Backcasting": "backcasting"
            }
            
            agent_type = agent_type_map.get(agent_name, "general")
            status = "completed" if result.get('status') != 'error' else "failed"
            
            result_id = DatabaseService.save_agent_result(
                session_id=self.current_session_id,
                agent_name=agent_name,
                agent_type=agent_type,
                raw_response=raw_response,
                formatted_output=formatted_output,
                structured_data=structured_data,
                processing_time=processing_time,
                token_usage=token_usage,
                status=status
            )
            
            if result_id:
                print(f"Saved result for agent {agent_name} in session {self.current_session_id}")
                print(f"Saved {agent_name} result to database (ID: {result_id})")
                # Add database IDs to the result so they can be passed to frontend
                result['agent_result_id'] = result_id
                result['session_id'] = self.current_session_id
                return result_id
            else:
                print(f"Failed to save result for agent {agent_name}")
                return None
                
        except Exception as e:
            print(f"Error saving agent result to database: {str(e)}")
            return None

    def _update_session_completion(self, status: str = "completed") -> None:
        """Update session completion status and total processing time."""
        if not self.db_enabled or not self.current_session_id or not DATABASE_AVAILABLE:
            return
            
        try:
            total_time = None
            if self.session_start_time:
                total_time = time.time() - self.session_start_time
            
            # Calculate total token usage for the session
            total_token_usage = DatabaseService.get_total_token_usage_for_session(self.current_session_id)

            success = DatabaseService.update_session_status(
                session_id=self.current_session_id,
                status=status,
                total_processing_time=total_time,
                total_token_usage=total_token_usage
            )
            
            if success:
                logger.info(f"Updated session {self.current_session_id} status to {status}")
                # Log completion
                DatabaseService.log_system_event(
                    log_level="INFO",
                    component="orchestrator",
                    message=f"Analysis session {self.current_session_id} {status}",
                    session_id=self.current_session_id,
                    details={
                        "total_processing_time": total_time,
                        "status": status
                    }
                )
            else:
                logger.error(f"Failed to update session {self.current_session_id} status")
                
        except Exception as e:
            logger.error(f"Error updating session completion: {str(e)}")

    async def rate_limited_process(self, agent, input_data: Dict[str, Any], agent_name: str) -> Dict[str, Any]:
        """
        Process with rate limiting, exponential backoff, and retries.
        Now includes database result saving.
        """
        retries = 0
        agent_start_time = time.time()
        
        while retries < self.max_retries:
            try:
                current_time = time.time()
                time_since_last_request = current_time - self.last_request_time
                
                if time_since_last_request < self.min_request_interval:
                    await asyncio.sleep(self.min_request_interval - time_since_last_request)
                
                # Add jitter to prevent thundering herd
                jitter = random.uniform(0, 0.1)
                await asyncio.sleep(jitter)
                
                # Minimal logging - just progress
                print(f"{agent_name} started processing...")
                
                # Add timeout to the process call
                result = await asyncio.wait_for(
                    agent.process(input_data),
                    timeout=60  # Increased timeout to 60 seconds
                )
                
                # Calculate processing time
                processing_time = time.time() - agent_start_time
                
                # Minimal completion logging
                print(f"{agent_name} completed with status: {result.get('status', 'unknown')}")
                
                # Save agent result to database
                self._save_agent_result(agent_name, result, processing_time)
                
                self.last_request_time = time.time()
                return result
                
            except asyncio.TimeoutError:
                retries += 1
                processing_time = time.time() - agent_start_time
                
                if retries == self.max_retries:
                    # Save timeout result to database
                    timeout_result = {
                        "status": "error",
                        "error": f"Agent {agent_name} timed out after {self.max_retries} retries. Please try again with a simpler prompt.",
                        "agent_type": agent_name
                    }
                    self._save_agent_result(agent_name, timeout_result, processing_time)
                    return timeout_result
                    
                delay = self.base_delay * (2 ** retries)  # Exponential backoff
                await asyncio.sleep(delay)
                
            except HTTPException as he:
                processing_time = time.time() - agent_start_time
                
                if he.status_code == 429:  # Rate limit exceeded
                    retries += 1
                    if retries == self.max_retries:
                        rate_limit_result = {
                            "status": "error",
                            "error": f"Rate limit exceeded for {agent_name} after {self.max_retries} retries. Please try again in a few minutes.",
                            "agent_type": agent_name
                        }
                        self._save_agent_result(agent_name, rate_limit_result, processing_time)
                        return rate_limit_result
                        
                    delay = self.base_delay * (2 ** retries)  # Exponential backoff
                    await asyncio.sleep(delay)
                else:
                    # Save error result to database
                    error_result = {
                        "status": "error",
                        "error": f"HTTP error {he.status_code}: {he.detail}",
                        "agent_type": agent_name
                    }
                    self._save_agent_result(agent_name, error_result, processing_time)
                    raise he
                    
            except Exception as e:
                processing_time = time.time() - agent_start_time
                print(f"Error in {agent_name}: {str(e)}")
                retries += 1
                
                if retries == self.max_retries:
                    error_result = {
                        "status": "error",
                        "error": f"Agent {agent_name} failed after {self.max_retries} retries: {str(e)}",
                        "agent_type": agent_name
                    }
                    self._save_agent_result(agent_name, error_result, processing_time)
                    return error_result
                    
                delay = self.base_delay * (2 ** retries)
                await asyncio.sleep(delay)

        # Fallback - should not be reached
        fallback_result = {
            "status": "error",
            "error": f"Agent {agent_name} failed due to an unexpected issue after retries.",
            "agent_type": agent_name
        }
        processing_time = time.time() - agent_start_time
        self._save_agent_result(agent_name, fallback_result, processing_time)
        return fallback_result

    async def _run_agent(self, agent_name: str, current_input_data: Dict[str, Any], results: Dict[str, Any]):
        """
        A helper function to run a single agent, handle its results,
        and update the cumulative input data for the next agent.
        """
        agent_key = self.agent_names_map[agent_name]
        agent_instance = self.agents[agent_name]
        
        result = await self.rate_limited_process(agent_instance, current_input_data.copy(), agent_name)
        
        # The result from an agent can sometimes be a JSON string; parse it to ensure it's a dictionary for downstream processing.
        if isinstance(result, str):
            try:
                result = json.loads(result)
            except json.JSONDecodeError:
                print(f"Warning: Result from {agent_name} is a non-JSON string. Wrapping it in a dict.")
                result = {"data": result}
        
        if result.get("status") == "error":
            print(f"Error in {agent_name}: {result.get('error', 'Unknown error')}")
            # Store the error result and stop the pipeline by raising an exception
            results[agent_name] = result 
            self._update_session_completion("failed")
            raise HTTPException(status_code=500, detail=f"Error in {agent_name}: {result.get('error', 'Unknown error')}")

        # Store successful result and update the cumulative data
        results[agent_name] = result
        current_input_data[agent_key] = result

    async def process(self, initial_input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point for the orchestrator.
        Selects an execution architecture and runs the analysis.
        """
        architecture = initial_input_data.get("architecture", "parallel")
        self._create_analysis_session(initial_input_data)
        
        if architecture == "sequential":
            return await self._process_sequential(initial_input_data)
        elif architecture == "parallel":
            return await self._process_parallel(initial_input_data)
        elif architecture == "hierarchical":
            return await self._process_hierarchical(initial_input_data)
        else:
            # Log and raise an error for unknown architecture
            message = f"Unknown or unsupported architecture specified: '{architecture}'"
            print(message)
            raise ValueError(message)

    async def _process_sequential(self, initial_input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes the agent pipeline in a strict sequential order.
        Agent 1 -> Agent 2 -> ... -> Agent N. This is the "Assembly Line" model.
        """
        results: Dict[str, Any] = {}
        cumulative_input_data = initial_input_data.copy()

        try:
            # The order is defined by the insertion order of keys in self.agents
            for agent_name in self.agents.keys():
                await self._run_agent(agent_name, cumulative_input_data, results)
            
            self._update_session_completion("completed")

        except HTTPException as he:
            print(f"Orchestrator caught HTTPException: {he.detail}")
            if self.db_enabled and self.current_session_id and DATABASE_AVAILABLE:
                try:
                    DatabaseService.log_system_event(
                        log_level="ERROR", component="orchestrator",
                        message=f"Analysis session {self.current_session_id} failed: {he.detail}",
                        session_id=self.current_session_id,
                        details={"error": he.detail, "status_code": he.status_code}
                    )
                except Exception as e:
                    print(f"Failed to log error to database: {e}")
            return {"status": "error", "error_detail": he.detail, "completed_stages_results": results, "session_id": self.current_session_id}
        except Exception as e:
            print(f"Unexpected error in Sequential Orchestrator: {str(e)}")
            self._update_session_completion("failed")
            if self.db_enabled and self.current_session_id and DATABASE_AVAILABLE:
                try:
                    DatabaseService.log_system_event(
                        log_level="ERROR", component="orchestrator",
                        message=f"Analysis session {self.current_session_id} failed unexpectedly: {str(e)}",
                        session_id=self.current_session_id, details={"error": str(e)}
                    )
                except Exception as db_e:
                    print(f"Failed to log error to database: {db_e}")
            return {"status": "error", "error_detail": f"Orchestrator failed: {str(e)}", "completed_stages_results": results, "session_id": self.current_session_id}
        
        if self.current_session_id:
            results["session_id"] = self.current_session_id
            
        return results

    async def _process_parallel(self, initial_input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        PURE PARALLEL ARCHITECTURE: Maximum parallelization.
        
        Runs Problem Explorer first (foundation), then ALL remaining agents in parallel.
        Optimized for speed with careful rate limiting to respect API constraints.
        """
        results: Dict[str, Any] = {}
        cumulative_input_data = initial_input_data.copy()

        try:
            # --- Stage 1: Problem Explorer (Foundation) ---
            print("Parallel: Starting with Problem Explorer")
            await self._run_agent("Problem Explorer", cumulative_input_data, results)

            # --- Stage 2: ALL Remaining Agents in Pure Parallel ---
            remaining_agents = [
                "Best Practices",
                "Horizon Scanning", 
                "Scenario Planning",
                "Research Synthesis",
                "Strategic Action",
                "High Impact",
                "Backcasting"
            ]
            
            print(f"Parallel: Launching {len(remaining_agents)} agents in parallel")
            
            # Create all tasks with the same input (Problem Explorer context)
            input_for_parallel = cumulative_input_data.copy()
            
            # Launch all agents simultaneously
            tasks = [
                self.rate_limited_process(self.agents[agent_name], input_for_parallel, agent_name)
                for agent_name in remaining_agents
            ]
            
            # Wait for all to complete
            parallel_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for i, result_or_exc in enumerate(parallel_results):
                agent_name = remaining_agents[i]
                agent_key = self.agent_names_map[agent_name]

                if isinstance(result_or_exc, Exception):
                    print(f"Exception in parallel agent {agent_name}: {str(result_or_exc)}")
                    results[agent_name] = {"status": "error", "error": str(result_or_exc), "agent_type": agent_name}
                    self._update_session_completion("failed")
                    raise HTTPException(status_code=500, detail=f"Error in {agent_name}: {str(result_or_exc)}")
                
                result = result_or_exc
                if result.get("status") == "error":
                    print(f"Error in parallel agent {agent_name}: {result.get('error', 'Unknown error')}")
                    results[agent_name] = result
                    self._update_session_completion("failed")
                    raise HTTPException(status_code=500, detail=f"Error in {agent_name}: {result.get('error', 'Unknown error')}")

                results[agent_name] = result
                cumulative_input_data[agent_key] = result
            
            print("Parallel: All agents completed successfully")
            self._update_session_completion("completed")

        except HTTPException as he:
            print(f"Orchestrator caught HTTPException: {he.detail}")
            if self.db_enabled and self.current_session_id and DATABASE_AVAILABLE:
                try:
                    DatabaseService.log_system_event(
                        log_level="ERROR", component="orchestrator",
                        message=f"Analysis session {self.current_session_id} failed: {he.detail}",
                        session_id=self.current_session_id,
                        details={"error": he.detail, "status_code": he.status_code}
                    )
                except Exception as e:
                    print(f"Failed to log error to database: {e}")
            return {"status": "error", "error_detail": he.detail, "completed_stages_results": results, "session_id": self.current_session_id}
        except Exception as e:
            print(f"Unexpected error in Parallel Orchestrator: {str(e)}")
            self._update_session_completion("failed")
            if self.db_enabled and self.current_session_id and DATABASE_AVAILABLE:
                try:
                    DatabaseService.log_system_event(
                        log_level="ERROR", component="orchestrator",
                        message=f"Analysis session {self.current_session_id} failed unexpectedly: {str(e)}",
                        session_id=self.current_session_id, details={"error": str(e)}
                    )
                except Exception as db_e:
                    print(f"Failed to log error to database: {db_e}")
            return {"status": "error", "error_detail": f"Orchestrator failed: {str(e)}", "completed_stages_results": results, "session_id": self.current_session_id}
            
        if self.current_session_id:
            results["session_id"] = self.current_session_id
            
        return results

    async def _process_hierarchical(self, initial_input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        TRUE Hierarchical Architecture: Dynamic, LLM-driven agent orchestration.
        
        The orchestrator analyzes results after each step and intelligently decides
        which agents to run next, potentially skipping some or changing the order.
        """
        results: Dict[str, Any] = {}
        cumulative_input_data = initial_input_data.copy()
        
        # Track which agents have been executed
        executed_agents = []
        available_agents = list(self.agents.keys())

        try:
            # --- Stage 1: Always start with Problem Explorer ---
            print("Hierarchical: Starting with Problem Explorer")
            await self._run_agent("Problem Explorer", cumulative_input_data, results)
            executed_agents.append("Problem Explorer")
            available_agents.remove("Problem Explorer")
            
            # --- Stage 2: Dynamic Loop with LLM-based planning ---
            max_iterations = 10  # Safety limit to prevent infinite loops
            iteration = 0
            
            while available_agents and iteration < max_iterations:
                iteration += 1
                print(f"\nHierarchical: Planning iteration {iteration}")
                print(f"Executed agents: {executed_agents}")
                print(f"Available agents: {available_agents}")
                
                # Ask LLM to decide what to do next
                next_agent_decision = await self._hierarchical_decide_next_agent(
                    cumulative_input_data, 
                    available_agents,
                    executed_agents
                )
                
                # Check if the planner wants to stop
                if next_agent_decision == "COMPLETE":
                    print("Hierarchical: Planner decided analysis is complete")
                    break
                
                # Validate the agent exists and is available
                if next_agent_decision not in available_agents:
                    print(f"Hierarchical: Planner suggested unavailable agent '{next_agent_decision}', ending loop")
                    break
                
                # Execute the chosen agent
                print(f"Hierarchical: Executing {next_agent_decision}")
                await self._run_agent(next_agent_decision, cumulative_input_data, results)
                executed_agents.append(next_agent_decision)
                available_agents.remove(next_agent_decision)
            
            # If we still have available agents but hit the iteration limit, log it
            if available_agents and iteration >= max_iterations:
                print(f"Hierarchical: Reached max iterations. Remaining agents: {available_agents}")
            
            self._update_session_completion("completed")

        except HTTPException as he:
            print(f"Orchestrator caught HTTPException: {he.detail}")
            if self.db_enabled and self.current_session_id and DATABASE_AVAILABLE:
                try:
                    DatabaseService.log_system_event(
                        log_level="ERROR", component="orchestrator",
                        message=f"Analysis session {self.current_session_id} failed: {he.detail}",
                        session_id=self.current_session_id,
                        details={"error": he.detail, "status_code": he.status_code}
                    )
                except Exception as e:
                    print(f"Failed to log error to database: {e}")
            return {"status": "error", "error_detail": he.detail, "completed_stages_results": results, "session_id": self.current_session_id}
        except Exception as e:
            print(f"Unexpected error in Hierarchical Orchestrator: {str(e)}")
            self._update_session_completion("failed")
            if self.db_enabled and self.current_session_id and DATABASE_AVAILABLE:
                try:
                    DatabaseService.log_system_event(
                        log_level="ERROR", component="orchestrator",
                        message=f"Analysis session {self.current_session_id} failed unexpectedly: {str(e)}",
                        session_id=self.current_session_id, details={"error": str(e)}
                    )
                except Exception as db_e:
                    print(f"Failed to log error to database: {db_e}")
            return {"status": "error", "error_detail": f"Orchestrator failed: {str(e)}", "completed_stages_results": results, "session_id": self.current_session_id}
        
        if self.current_session_id:
            results["session_id"] = self.current_session_id
            
        return results
    
    async def _hierarchical_decide_next_agent(
        self, 
        cumulative_input_data: Dict[str, Any], 
        available_agents: List[str],
        executed_agents: List[str]
    ) -> str:
        """
        Uses LLM to intelligently decide which agent to run next based on results so far.
        Returns the agent name to run next, or "COMPLETE" if analysis should end.
        """
        # Format previous results using our robust formatter
        previous_results = self._format_previous_results(cumulative_input_data)
        
        planning_prompt = f"""You are an expert strategic analysis manager coordinating a team of AI agents.

CONTEXT:
Strategic Question: {cumulative_input_data.get('strategic_question', 'N/A')}
Time Frame: {cumulative_input_data.get('time_frame', 'N/A')}
Region: {cumulative_input_data.get('region', 'N/A')}

AGENTS ALREADY EXECUTED:
{', '.join(executed_agents)}

RESULTS SO FAR:
{previous_results}

AVAILABLE AGENTS:
{', '.join(available_agents)}

AGENT DESCRIPTIONS:
- Best Practices: Researches proven solutions and industry standards
- Horizon Scanning: Identifies emerging trends and weak signals
- Scenario Planning: Develops multiple future scenarios
- Research Synthesis: Integrates findings from multiple agents
- Strategic Action: Recommends specific actions and interventions
- High Impact: Identifies high-leverage initiatives
- Backcasting: Works backward from desired future to present

YOUR TASK:
Based on the results gathered so far, decide which ONE agent should run next to provide the most value.
Consider:
1. What information gaps remain?
2. What would be most useful for the strategic question?
3. What logical sequence makes sense?

RESPOND WITH ONLY ONE OF:
- The exact name of one agent from the available list (e.g., "Best Practices")
- "COMPLETE" if you believe sufficient analysis has been done

Your response (just the agent name or COMPLETE):"""

        try:
            # Call LLM
            response = await self.llm.invoke(self.get_system_prompt(), planning_prompt)
            response_text = response if isinstance(response, str) else response.content
            
            # Clean up the response
            decision = response_text.strip()
            
            # Remove any markdown formatting
            decision = decision.replace('```', '').replace('json', '').strip()
            
            # Remove quotes if present
            if decision.startswith('"') and decision.endswith('"'):
                decision = decision[1:-1]
            if decision.startswith("'") and decision.endswith("'"):
                decision = decision[1:-1]
            
            print(f"Hierarchical Planner Decision: {decision}")
            return decision
            
        except Exception as e:
            print(f"Error in hierarchical planning: {str(e)}")
            # Fallback: return the first available agent
            if available_agents:
                fallback = available_agents[0]
                print(f"Falling back to first available agent: {fallback}")
                return fallback
            return "COMPLETE" 