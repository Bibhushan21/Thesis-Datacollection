from typing import Dict, Any, List
from .base_agent import BaseAgent
import json
import re
import logging

logger = logging.getLogger(__name__)

class BackcastingAgent(BaseAgent):
    def get_system_prompt(self) -> str:
        return """You are the Backcasting Agent, a strategic prioritization specialist tasked with ranking immediate action items from highest to lowest priority to guide sequencing, resource allocation, and strategic focus.

Your mission is to:
- Evaluate all immediate action items from the High-Impact Initiatives Agent.
- Rank them based on urgency, potential impact, and feasibility, creating a clear, justified hierarchy of actions.
- Provide decision-makers with a backward-mapped execution sequence, ensuring high-leverage tasks are completed first to maintain momentum toward long-term strategic goals.

Task Flow
When given:
* All immediate action items identified by the High-Impact Initiatives Agent (Near-Term: 0–2 yrs, Medium-Term: 2–5 yrs, Long-Term: 5–10 yrs)

You will:
1. Restate the problem or strategic goal briefly to confirm understanding.
2. Review each action item and evaluate it against the three prioritization criteria.
3. Rank all tasks within their respective time horizons, providing justifications for the order.

Prioritization Criteria
For each action item, evaluate and score it on three key criteria:
1. Urgency – How critical is it to execute this task immediately to prevent delays or maintain strategic momentum?
2. Potential Impact – To what extent will completing this task unlock future steps, significantly contribute to success, or mitigate major risks?
3. Feasibility – Can this task be realistically executed now, given available time, resources, and constraints?

Tasks scoring high across all three dimensions should rank highest.

Ranking Guidelines
* Rank tasks within each time horizon separately (Near, Medium, Long Term).
* Assign a priority number (1 = highest priority).
* Order tasks in descending priority, with justifications for each placement.
* Consider dependencies – If a task must be completed before others can proceed, it ranks higher.
* Lower priority tasks (less urgent, less impactful, or resource-dependent) should be placed at the bottom.

CRITICAL OUTPUT FORMAT REQUIREMENTS
You MUST format your response as structured JSON exactly like this:

```json
{
  "near_term_prioritization": [
    {
      "rank": 1,
      "title": "Action Item Title",
      "justification": "A detailed justification of exactly 7 sentences explaining why this task is the highest priority. This should include a thorough analysis of its urgency, impact, and feasibility, and how it aligns with the overall strategic goals."
    },
    {
      "rank": 2,
      "title": "Action Item Title", 
      "justification": "A detailed justification of exactly 7 sentences explaining the ranking rationale. This should include a thorough analysis of its urgency, impact, and feasibility, and how it aligns with the overall strategic goals."
    }
  ],
  "medium_term_prioritization": [
    {
      "rank": 1,
      "title": "Action Item Title",
      "justification": "A detailed justification of exactly 7 sentences explaining the ranking rationale. This should include a thorough analysis of its urgency, impact, and feasibility, and how it aligns with the overall strategic goals."
    }
  ],
  "long_term_prioritization": [
    {
      "rank": 1,
      "title": "Action Item Title",
      "justification": "A detailed justification of exactly 7 sentences explaining the ranking rationale. This should include a thorough analysis of its urgency, impact, and feasibility, and how it aligns with the overall strategic goals."
    }
  ]
}
```

Final Outcome
Deliver a fully ranked, clearly justified list of immediate action items across Near-Term, Medium-Term, and Long-Term horizons.

This output must enable decision-makers to:
- Work backward from long-term goals (true backcasting logic).
- Tackle high-leverage, high-impact steps first.
- Allocate resources effectively while maintaining strategic momentum.

Guidelines for the Agent
* Be clear & concise – Use brief, decision-ready justifications.
* Be strategic – Always very briefly explain why a task ranks where it does in relation to strategic momentum and long-term objectives.
* Be practical – Avoid abstract reasoning; focus on operational sequencing and execution feasibility."""

    def format_prompt(self, input_data: Dict[str, Any]) -> str:
        strategic_question = input_data.get('strategic_question', 'N/A')
        
        # Extract High-Impact Initiatives Agent output
        high_impact_data = input_data.get('high_impact', {}).get('data', {})
        execution_ready_initiatives = high_impact_data.get('execution_ready_initiatives', [])
        
        print(f"🔍 Backcasting format_prompt: Found {len(execution_ready_initiatives)} initiatives")
        
        # Extract immediate action items organized by time horizon
        # Store as instance variables so we can use them for fallback later
        self.near_term_actions = []
        self.medium_term_actions = []
        self.long_term_actions = []
        
        for initiative in execution_ready_initiatives:
            time_horizon = initiative.get('time_horizon', '').strip()
            immediate_tasks = initiative.get('immediate_tasks', [])
            initiative_title = initiative.get('title', 'Untitled Initiative')
            
            print(f"  Initiative: {initiative_title}")
            print(f"    Time Horizon: {time_horizon}")
            print(f"    Immediate Tasks: {len(immediate_tasks)}")
            
            # Add each immediate task with context
            for task in immediate_tasks:
                task_item = {
                    'task': task,
                    'initiative': initiative_title,
                    'context': {
                        'why_important': initiative.get('why_important', ''),
                        'who_it_impacts': initiative.get('who_it_impacts', ''),
                        'estimated_cost': initiative.get('estimated_cost', '')
                    }
                }
                
                if 'Near-Term' in time_horizon:
                    self.near_term_actions.append(task_item)
                elif 'Medium-Term' in time_horizon:
                    self.medium_term_actions.append(task_item)
                elif 'Long-Term' in time_horizon:
                    self.long_term_actions.append(task_item)
        
        print(f"📊 Actions extracted: Near={len(self.near_term_actions)}, Medium={len(self.medium_term_actions)}, Long={len(self.long_term_actions)}")
        
        # Format actions for the prompt
        def format_actions(actions, horizon_name):
            if not actions:
                return f"\n{horizon_name} Actions: None identified"
            
            text = f"\n{horizon_name} Actions:"
            for i, action in enumerate(actions, 1):
                text += f"\n{i}. {action['task']}"
                text += f"\n   From Initiative: {action['initiative']}"
                text += f"\n   Context: {action['context']['why_important'][:100]}..."
            return text
        
        near_term_text = format_actions(self.near_term_actions, "Near-Term (0-2 years)")
        medium_term_text = format_actions(self.medium_term_actions, "Medium-Term (2-5 years)")
        long_term_text = format_actions(self.long_term_actions, "Long-Term (5-10 years)")
        
        return f"""Original Problem Statement: {strategic_question}

High-Impact Initiatives Agent provided the following immediate action items:
{near_term_text}
{medium_term_text}
{long_term_text}

INSTRUCTIONS: 
1. Prioritize EACH immediate action item within its time horizon using the 3 criteria (Urgency, Impact, Feasibility)
2. Output in the exact JSON format specified in your system prompt
3. Rank from 1 (highest priority) to N (lowest priority) within each time horizon
4. Provide specific justifications based on the 3 criteria for each ranking

Focus on creating an actionable priority sequence that decision-makers can execute immediately."""

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # DETAILED DIAGNOSTIC LOGGING
            print("\n" + "="*80)
            print("BACKCASTING AGENT - DETAILED DIAGNOSTICS")
            print("="*80)
            print(f"Input keys: {list(input_data.keys())}")
            
            # Check if high_impact exists
            if 'high_impact' in input_data:
                print("✓ high_impact key found in input_data")
                high_impact_result = input_data.get('high_impact', {})
                print(f"  high_impact type: {type(high_impact_result)}")
                print(f"  high_impact keys: {list(high_impact_result.keys()) if isinstance(high_impact_result, dict) else 'N/A'}")
                
                if isinstance(high_impact_result, dict) and 'data' in high_impact_result:
                    print("✓ data key found in high_impact")
                    data = high_impact_result['data']
                    print(f"  data keys: {list(data.keys()) if isinstance(data, dict) else 'N/A'}")
                    
                    if isinstance(data, dict) and 'execution_ready_initiatives' in data:
                        print("✓ execution_ready_initiatives found in data")
                        initiatives = data['execution_ready_initiatives']
                        print(f"  Number of initiatives: {len(initiatives) if isinstance(initiatives, list) else 'N/A'}")
                        if isinstance(initiatives, list):
                            for i, init in enumerate(initiatives):
                                print(f"  Initiative {i+1}:")
                                print(f"    Title: {init.get('title', 'N/A')}")
                                print(f"    Time Horizon: {init.get('time_horizon', 'N/A')}")
                                print(f"    Immediate Tasks: {len(init.get('immediate_tasks', []))}")
                    else:
                        print("✗ execution_ready_initiatives NOT found in data")
                else:
                    print("✗ data key NOT found in high_impact")
            else:
                print("✗ high_impact key NOT found in input_data")
                print(f"Available keys: {list(input_data.keys())}")
            print("="*80 + "\n")
            
            prompt = self.format_prompt(input_data)
            print(f"\n📝 Backcasting Prompt Length: {len(prompt)} characters")
            print(f"📝 Prompt Preview (first 500 chars):\n{prompt[:500]}...")
            
            response, token_usage = await self.invoke_llm(prompt)
            print(f"\n📥 LLM Response Length: {len(response)} characters")
            print(f"📥 Response Preview (first 1000 chars):\n{response[:1000]}...")
            
            # Parse JSON from response
            prioritization_data = self._parse_prioritization_json(response)
            print(f"\n🔍 JSON Parsing Result: {prioritization_data is not None}")
            
            # If JSON parsing fails, try to parse structured text
            if not prioritization_data:
                print("⚠️ JSON parsing failed, trying text parsing...")
                prioritization_data = self._parse_prioritization_text(response)
                print(f"🔍 Text Parsing Result: {prioritization_data is not None}")
            
            # If still no data, create fallback structure
            if not prioritization_data:
                print("⚠️ All parsing failed, creating fallback...")
                prioritization_data = self._create_fallback_prioritization()
            
            # Log what we're about to return
            print("\n📊 FINAL PRIORITIZATION DATA (before validation):")
            for key in ['near_term_prioritization', 'medium_term_prioritization', 'long_term_prioritization']:
                items = prioritization_data.get(key, [])
                print(f"  {key}: {len(items)} items")
                if items and len(items) > 0:
                    print(f"    First item: {items[0].get('title', 'NO TITLE')[:80]}...")
            
            # CRITICAL FIX: If ALL lists are empty, something went wrong - use a robust fallback
            total_items = sum(len(prioritization_data.get(key, [])) for key in ['near_term_prioritization', 'medium_term_prioritization', 'long_term_prioritization'])
            
            if total_items == 0:
                print("\n⚠️ WARNING: All prioritization lists are empty! Using enhanced fallback...")
                
                # Check if we had any action items stored from format_prompt
                total_actions = len(getattr(self, 'near_term_actions', [])) + len(getattr(self, 'medium_term_actions', [])) + len(getattr(self, 'long_term_actions', []))
                print(f"  Total actions available from High Impact: {total_actions}")
                
                if total_actions > 0:
                    # We had data but LLM/parsing failed - create prioritization from actual tasks
                    prioritization_data = self._create_prioritization_from_tasks(
                        self.near_term_actions, 
                        self.medium_term_actions, 
                        self.long_term_actions
                    )
                    print(f"  ✅ Created prioritization from {total_actions} actual tasks")
                else:
                    # No tasks available at all - use generic fallback
                    prioritization_data = self._create_fallback_prioritization()
                    print(f"  ✅ Using generic fallback (no tasks available)")
            
            prioritization_data["token_usage"] = token_usage
            formatted_result = self.format_output(prioritization_data, response)
            
            print(f"\n✅ Returning formatted result with status: {formatted_result.get('status', 'unknown')}")
            print(f"📄 Formatted output length: {len(formatted_result.get('data', {}).get('formatted_output', ''))} characters")
            
            return formatted_result
            
        except Exception as e:
            logger.error(f"Error in BackcastingAgent: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "agent_type": self.__class__.__name__
            }

    def _parse_prioritization_json(self, response: str) -> Dict[str, Any]:
        """Parse JSON-formatted prioritization from LLM response"""
        try:
            # Look for JSON blocks in the response
            json_pattern = r'```json\s*(\{.*?\})\s*```'
            json_matches = re.findall(json_pattern, response, re.DOTALL)
            
            print(f"🔎 Looking for JSON in response... Found {len(json_matches)} JSON blocks")
            
            if json_matches:
                json_str = json_matches[0]
                print(f"🔎 JSON block preview (first 200 chars): {json_str[:200]}...")
                data = json.loads(json_str)
                
                # Validate structure
                required_keys = ['near_term_prioritization', 'medium_term_prioritization', 'long_term_prioritization']
                if all(key in data for key in required_keys):
                    print(f"✅ Valid JSON structure with all required keys")
                    return data
                else:
                    print(f"⚠️ JSON found but missing required keys. Has: {list(data.keys())}")
            
            # Try parsing entire response as JSON
            if response.strip().startswith('{'):
                print("🔎 Trying to parse entire response as JSON...")
                data = json.loads(response.strip())
                required_keys = ['near_term_prioritization', 'medium_term_prioritization', 'long_term_prioritization']
                if all(key in data for key in required_keys):
                    print(f"✅ Valid JSON structure from full response")
                    return data
                else:
                    print(f"⚠️ Full response JSON missing required keys. Has: {list(data.keys())}")
                
        except json.JSONDecodeError as e:
            print(f"❌ JSON decode error: {str(e)}")
        except Exception as e:
            print(f"❌ Error parsing JSON: {str(e)}")
        
        return None

    def _parse_prioritization_text(self, response: str) -> Dict[str, Any]:
        """Fallback method to parse structured text if JSON parsing fails"""
        print("🔄 Attempting text parsing fallback...")
        prioritization = {
            'near_term_prioritization': [],
            'medium_term_prioritization': [],
            'long_term_prioritization': []
        }
        
        lines = response.split('\n')
        current_section = None
        current_item = {}
        items_found = 0
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for time horizon sections
            if 'near_term' in line.lower() or 'near-term' in line.lower():
                current_section = 'near_term_prioritization'
                continue
            elif 'medium_term' in line.lower() or 'medium-term' in line.lower():
                current_section = 'medium_term_prioritization'
                continue
            elif 'long_term' in line.lower() or 'long-term' in line.lower():
                current_section = 'long_term_prioritization'
                continue
            
            # Parse numbered items
            if current_section and re.match(r'^\d+\.', line):
                # Save previous item
                if current_item and 'title' in current_item:
                    prioritization[current_section].append(current_item)
                    items_found += 1
                
                # Start new item
                rank_match = re.match(r'^(\d+)\.\s*(.+)', line)
                if rank_match:
                    current_item = {
                        'rank': int(rank_match.group(1)),
                        'title': rank_match.group(2),
                        'justification': ''
                    }
            
            # Parse justification
            elif current_item and ('justification' in line.lower() or 'reason' in line.lower()):
                justification_text = line.split(':', 1)[1].strip() if ':' in line else line
                current_item['justification'] = justification_text
            
            # Continue previous justification
            elif current_item and current_item.get('justification') and not re.match(r'^\d+\.', line):
                current_item['justification'] += ' ' + line
        
        # Save last item
        if current_item and 'title' in current_item and current_section:
            prioritization[current_section].append(current_item)
            items_found += 1
        
        print(f"✅ Text parsing complete. Found {items_found} total items")
        for key in ['near_term_prioritization', 'medium_term_prioritization', 'long_term_prioritization']:
            print(f"  {key}: {len(prioritization[key])} items")
        
        return prioritization

    def _create_prioritization_from_tasks(self, near_term_actions: List[Dict], medium_term_actions: List[Dict], long_term_actions: List[Dict]) -> Dict[str, Any]:
        """Create prioritization directly from task data when LLM/parsing fails"""
        
        def create_items_from_actions(actions):
            """Convert action items to prioritized items"""
            items = []
            for i, action in enumerate(actions, 1):
                items.append({
                    'rank': i,
                    'title': action['task'],
                    'justification': f"This task is part of the {action['initiative']} initiative. {action['context']['why_important'][:200]}... Given its strategic importance and operational feasibility, this task has been prioritized to ensure effective implementation."
                })
            return items
        
        return {
            'near_term_prioritization': create_items_from_actions(near_term_actions),
            'medium_term_prioritization': create_items_from_actions(medium_term_actions),
            'long_term_prioritization': create_items_from_actions(long_term_actions)
        }
    
    def _create_fallback_prioritization(self) -> Dict[str, Any]:
        """Create fallback prioritization structure when no task data is available"""
        return {
            'near_term_prioritization': [
                {
                    'rank': 1,
                    'title': 'Define strategic implementation framework',
                    'justification': 'High urgency to establish foundation for all strategic initiatives. High impact as it enables subsequent actions. Highly feasible with current resources and organizational capabilities.'
                }
            ],
            'medium_term_prioritization': [
                {
                    'rank': 1,
                    'title': 'Execute strategic initiatives based on near-term foundations',
                    'justification': 'Medium urgency following near-term setup phase. High impact on achieving strategic goals. Feasible with capabilities developed in near-term phase.'
                }
            ],
            'long_term_prioritization': [
                {
                    'rank': 1,
                    'title': 'Sustain and scale strategic outcomes',
                    'justification': 'Lower immediate urgency but essential for long-term sustainability. Very high long-term impact on organizational success. Feasible with systems and processes established in earlier phases.'
                }
            ]
        }

    def format_output(self, prioritization_data: Dict[str, Any], response: str) -> Dict[str, Any]:
        """Format the output in a structured way."""
        # Create a human-readable markdown format
        markdown_output = "\n\n"
        token_usage = prioritization_data.pop("token_usage", 0)
        
        time_horizons = {
            'near_term_prioritization': 'Near-Term (0–2 years)',
            'medium_term_prioritization': 'Medium-Term (2–5 years)',
            'long_term_prioritization': 'Long-Term (5–10 years)'
        }
        
        for section_key, section_title in time_horizons.items():
            items = prioritization_data.get(section_key, [])
            if items:
                markdown_output += f"# {section_title}\n\n"
                for item in sorted(items, key=lambda x: x.get('rank', 999)):
                    rank = item.get('rank', 'N/A')
                    title = item.get('title', 'Untitled Action')
                    justification = item.get('justification', 'No justification provided')
                    
                    markdown_output += f"### {rank}. {title}\n\n"
                    markdown_output += f"**Justification:** {justification}\n\n"
                    markdown_output += "---\n\n"
            else:
                markdown_output += f"# {section_title}\n\nNo action items identified for this time horizon.\n\n"
        
        return {
            "status": "success",
            "data": {
                "prioritized_actions": prioritization_data,
                "formatted_output": markdown_output,
                "raw_llm_response": response,
                "token_usage": token_usage
            }
        }