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
        self.min_request_interval = 2.0  # Minimum time between requests in seconds
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
                results.append(f"{agent_type.replace('_', ' ').title()}: {input_data[agent_type].get('data', {})}")
        return '\n'.join(results) if results else 'No previous results available'

    def _create_analysis_session(self, input_data: Dict[str, Any], architecture: str) -> None:
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
                architecture=architecture
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
        self._create_analysis_session(initial_input_data, "sequential")
        
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
        Executes a pre-defined graph of agents with parallel steps.
        This was the original 'hybrid' implementation, now serving as the "Workshop" model.
        """
        self._create_analysis_session(initial_input_data, "parallel")
        
        results: Dict[str, Any] = {}
        cumulative_input_data = initial_input_data.copy()

        try:
            # --- Stage 1: Problem Explorer (Sequential) ---
            await self._run_agent("Problem Explorer", cumulative_input_data, results)

            # --- Stage 2: Best Practices, Horizon Scanning, Scenario Planning (Parallel) ---
            agent_bp_name = "Best Practices"
            agent_hs_name = "Horizon Scanning"
            agent_sp_name = "Scenario Planning"

            input_for_stage2 = cumulative_input_data.copy() 

            bp_task = self.rate_limited_process(self.agents[agent_bp_name], input_for_stage2, agent_bp_name)
            hs_task = self.rate_limited_process(self.agents[agent_hs_name], input_for_stage2, agent_hs_name)
            sp_task = self.rate_limited_process(self.agents[agent_sp_name], input_for_stage2, agent_sp_name)
            
            stage2_results_list = await asyncio.gather(bp_task, hs_task, sp_task, return_exceptions=True)
                
            parallel_agent_names = [agent_bp_name, agent_hs_name, agent_sp_name]
            for i, result_or_exc in enumerate(stage2_results_list):
                agent_name = parallel_agent_names[i]
                agent_key = self.agent_names_map[agent_name]

                if isinstance(result_or_exc, Exception):
                    print(f"Exception in parallel agent {agent_name}: {str(result_or_exc)}")
                    results[agent_name] = {"status": "error", "error": str(result_or_exc), "agent_type": agent_name}
                    self._update_session_completion("failed")
                    raise HTTPException(status_code=500, detail=f"Error in {agent_name} (parallel stage): {str(result_or_exc)}")
                
                result = result_or_exc
                if result.get("status") == "error":
                    print(f"Error in parallel agent {agent_name}: {result.get('error', 'Unknown error')}")
                    results[agent_name] = result
                    self._update_session_completion("failed")
                    raise HTTPException(status_code=500, detail=f"Error in {agent_name} (parallel stage): {result.get('error', 'Unknown error')}")

                results[agent_name] = result
                cumulative_input_data[agent_key] = result

            # --- Stage 3-6: Remaining agents (Sequential) ---
            await self._run_agent("Research Synthesis", cumulative_input_data, results)
            await self._run_agent("Strategic Action", cumulative_input_data, results)
            await self._run_agent("High Impact", cumulative_input_data, results)
            await self._run_agent("Backcasting", cumulative_input_data, results)

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
        Executes a dynamic, hierarchical process where the orchestrator analyzes
        intermediate results to decide the next steps. This is the "Managed Team" model.
        """
        self._create_analysis_session(initial_input_data, "hierarchical")

        results: Dict[str, Any] = {}
        cumulative_input_data = initial_input_data.copy()
        
        available_agents = list(self.agents.keys())

        try:
            # --- Stage 1: Always start with Problem Explorer ---
            await self._run_agent("Problem Explorer", cumulative_input_data, results)
            available_agents.remove("Problem Explorer")

            # --- Dynamic Loop ---
            while available_agents:
                # 1. Analyze current results and create a plan for the next step
                plan = await self._hierarchical_planning_step(cumulative_input_data, available_agents)
                next_steps = plan.get("next_steps", [])

                # 2. Check for termination condition
                if not next_steps or any(step.get("agent") == "complete" for step in next_steps):
                    print("Hierarchical planner decided to complete the analysis.")
                    break

                # 3. Execute the plan
                agent_names_in_step = [
                    step["agent"] for step in next_steps 
                    if step.get("agent") in self.agents and step.get("agent") in available_agents
                ]

                if not agent_names_in_step:
                    print(f"Planner returned no valid, available agents. Ending analysis. Plan was: {next_steps}")
                    break

                if len(agent_names_in_step) > 1: # Parallel execution
                    tasks = []
                    for step in next_steps:
                        agent_name = step.get("agent")
                        if agent_name not in agent_names_in_step:
                            continue
                        
                        step_input_data = cumulative_input_data.copy()
                        if "refined_prompt" in step:
                            step_input_data["prompt"] = step["refined_prompt"]
                        
                        tasks.append(self.rate_limited_process(self.agents[agent_name], step_input_data, agent_name))
                    
                    parallel_results = await asyncio.gather(*tasks, return_exceptions=True)

                    for i, result_or_exc in enumerate(parallel_results):
                        agent_name = agent_names_in_step[i]
                        agent_key = self.agent_names_map[agent_name]

                        if isinstance(result_or_exc, Exception):
                             print(f"Exception in hierarchical parallel agent {agent_name}: {result_or_exc}")
                             self._update_session_completion("failed")
                             raise HTTPException(status_code=500, detail=f"Error in hierarchical agent {agent_name}: {result_or_exc}")

                        result = result_or_exc
                        if result.get("status") == "error":
                            print(f"Error in hierarchical parallel agent {agent_name}: {result.get('error', 'Unknown error')}")
                            results[agent_name] = result
                            self._update_session_completion("failed")
                            raise HTTPException(status_code=500, detail=f"Error in hierarchical agent {agent_name}: {result.get('error', 'Unknown error')}")
                        
                        results[agent_name] = result
                        cumulative_input_data[agent_key] = result
                        available_agents.remove(agent_name)

                elif len(agent_names_in_step) == 1: # Sequential execution
                    agent_name = agent_names_in_step[0]
                    step = next((s for s in next_steps if s.get("agent") == agent_name), {})
                    
                    step_input_data = cumulative_input_data
                    if "refined_prompt" in step:
                        # Use a copy to avoid contaminating the main prompt for other agents
                        step_input_data = cumulative_input_data.copy()
                        step_input_data["prompt"] = step["refined_prompt"]
                    
                    await self._run_agent(agent_name, step_input_data, results)
                    available_agents.remove(agent_name)
            
            self._update_session_completion("completed")

        except HTTPException as he:
            print(f"Orchestrator caught HTTPException: {he.detail}")
            # Error logging and handling is already inside _run_agent or the parallel block
            return {"status": "error", "error_detail": he.detail, "completed_stages_results": results, "session_id": self.current_session_id}
        except Exception as e:
            print(f"Unexpected error in Hierarchical Orchestrator: {str(e)}")
            self._update_session_completion("failed")
            # Log generic error
            return {"status": "error", "error_detail": f"Orchestrator failed: {str(e)}", "completed_stages_results": results, "session_id": self.current_session_id}
        
        if self.current_session_id:
            results["session_id"] = self.current_session_id
            
        return results

    async def _hierarchical_planning_step(self, cumulative_input_data: Dict[str, Any], available_agents: List[str]) -> Dict[str, Any]:
        """
        Calls the LLM to analyze the current state and decide the next agent(s) to run.
        """
        previous_results_summary = self._format_previous_results(cumulative_input_data)

        planning_prompt = f"""
You are an expert project manager for a strategic intelligence analysis team.
Your goal is to dynamically plan the next steps of an analysis based on the results gathered so far.

The initial user request was:
- Strategic Question: {cumulative_input_data.get('strategic_question', 'N/A')}
- Time Frame: {cumulative_input_data.get('time_frame', 'N/A')}
- Region: {cumulative_input_data.get('region', 'N/A')}
- Additional Instructions: {cumulative_input_data.get('prompt', 'N/A')}

So far, the following agents have run and produced these results:
{previous_results_summary}

You have the following specialist agents still available to you:
{', '.join(available_agents)}

Based on the results so far, you must decide the next step. Your options are:
1.  Run a single agent next.
2.  Run a group of agents in parallel if they are not dependent on each other's immediate output.
3.  Conclude the analysis if you believe sufficient information has been gathered.

You can also refine the prompt for the next agent(s) to focus their analysis on specific findings.

Your response MUST be a JSON object with a single key "next_steps", which is a list of objects.
Each object in the list must have an "agent" key. It can optionally have a "refined_prompt" key.

- To run a single agent: `{{"next_steps": [{{"agent": "AgentName"}}]}}`
- To run agents in parallel: `{{"next_steps": [{{"agent": "Agent1"}}, {{"agent": "Agent2"}}]}}`
- To refine a prompt: `{{"next_steps": [{{"agent": "AgentName", "refined_prompt": "Focus on..."}}]}}`
- To finish: `{{"next_steps": [{{"agent": "complete"}}]}}`

Example:
If Problem Explorer's output mentioned "supply chain risks", a good next step might be:
`{{"next_steps": [{{"agent": "Best Practices", "refined_prompt": "Investigate best practices for mitigating supply chain risks."}}, {{"agent": "Horizon Scanning"}}]}}`
This would run Best Practices (with a refined prompt) and Horizon Scanning in parallel.

Now, provide your decision for the current analysis.
"""
        
        # Use the orchestrator's own system prompt for its "personality"
        response = await self.llm.invoke(self.get_system_prompt(), planning_prompt)
        response_text = response if isinstance(response, str) else response.content
        
        try:
            # The response might be inside a markdown code block
            match = re.search(r'```json\n(.*?)\n```', response_text, re.DOTALL)
            if match:
                json_str = match.group(1)
            else:
                json_str = response_text
            
            plan = json.loads(json_str)
            
            if "next_steps" not in plan or not isinstance(plan["next_steps"], list):
                raise ValueError("Invalid plan format: 'next_steps' key is missing or not a list.")
            
            print(f"Hierarchical planner generated plan: {plan}")
            return plan
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error parsing hierarchical plan: {e}. Defaulting to a sequential step with the first available agent.")
            return {"next_steps": [{"agent": available_agents[0]}]} 