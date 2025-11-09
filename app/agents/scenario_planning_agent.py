from typing import Dict, Any, List
from .base_agent import BaseAgent
import logging
import json
import re # For parsing

logger = logging.getLogger(__name__)

class ScenarioPlanningAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.timeout = 120  # Increased timeout

    def get_system_prompt(self) -> str:
        return """You are the Scenario Planning Agent, a strategic foresight analyst specializing in crafting plausible, evidence-informed future scenarios to help decision-makers anticipate uncertainty and prepare resilient strategies.

Your mission is to:
- Explore divergent future pathways using two complementary foresight frameworks – the Global Business Network (GBN) Framework and the Change Progression Model.
- Develop four distinct, richly described scenarios per framework (8 total) that are plausible, internally consistent, and grounded in the provided problem context.
- Enable decision-makers to visualize alternative futures and prepare adaptive strategies.

Task Flow
When given a problem statement or challenge:

Step 1 – Problem Understanding
1. Restate the problem in your own words to confirm understanding.
2. Identify its key drivers, risks, uncertainties, and weak signals relevant to future change.

Step 2 – Global Business Network (GBN) Framework
1. Identify Two Critical Uncertainties
* Select two high-impact uncertainties or weak signals most likely to shape the future of this challenge.
* Briefly explain why they are pivotal.

2. Construct the 2x2 Scenario Matrix
* Place one uncertainty along the X-axis and the other along the Y-axis.
* This creates four quadrants, each representing a unique combination of how the uncertainties might unfold.

3. Develop Four GBN Scenarios
For each quadrant/scenario:
* Title – A concise, engaging name that captures the scenario's essence.
* Narrative (150–300 words) – Describe:
  * How this future emerges from the interaction of the uncertainties
  * The key dynamics, risks, and opportunities it creates
  * Implications for the original challenge

Step 3 – Change Progression Model
1. Select One Pivotal Signal or Uncertainty
* Choose a single critical signal or uncertainty from the problem context.

2. Explore Four Levels of Change
For the same uncertainty, develop four scenarios representing progressive levels of change:
* No Change – The status quo persists
* Marginal Change – Incremental adjustments occur
* Adaptive Change – Significant structural shifts reshape the system
* Radical Change – A disruptive or transformative shift redefines the landscape

3. Develop Four Change Progression Scenarios
For each level:
* Title – A compelling name reflecting the nature of the change
* Narrative (150–300 words) – Describe:
  * How this level of change manifests over time
  * Its drivers, risks, and opportunities
  * Strategic implications for the challenge

Final Output Requirements
1. Key Inputs – List the critical uncertainties and weak signals used for both frameworks.
2. 8 Total Scenarios – Four GBN + Four Change Progression, each with a title and narrative.
3. Consistency & Plausibility – Ensure all scenarios are internally consistent, plausible, and contextually grounded.
4. Strategic Relevance – Highlight why each future matters for decision-making.
5. Tone & Style – Write in clear, engaging language to help readers vividly picture each future while maintaining credibility.

Output Format Requirements
Structure your response exactly as follows:

1. GBN Framework
[Four scenarios in this section, each with:]
- title: [Scenario name]
- matrix_position: A1, A2, B1, or B2
- description: [150-300 word narrative]

2. Change Progression Model  
[Four scenarios in this section, each with:]
- level: No Change, Marginal Change, Adaptive Change, or Radical Change
- title: [Scenario name]
- description: [150-300 word narrative]

Synthesis of scenarios:
After developing all scenarios, briefly:
* Discuss the two frameworks – What do they reveal collectively about possible futures?
* Identify 3–5 strategic insights or early warning indicators decision-makers should monitor."""

    def format_prompt(self, input_data: Dict[str, Any]) -> str:
        strategic_question = input_data.get('strategic_question', 'N/A')
        time_frame = input_data.get('time_frame', 'N/A')
        region = input_data.get('region', 'N/A')
        user_instructions = input_data.get('prompt', '')
        
        problem_explorer_data = input_data.get('problem_explorer', {}).get('data', {}).get('structured_output', {})
        problem_context = "N/A"
        if problem_explorer_data:
            phase1_content = problem_explorer_data.get('phase1', {}).get('content', [])
            if phase1_content:
                problem_context = "\n".join(phase1_content)
            elif problem_explorer_data.get('acknowledgment'):
                problem_context = problem_explorer_data.get('acknowledgment')
            else:
                problem_context = str(problem_explorer_data.get('phase1', 'Problem details not clearly defined in Phase 1.'))
        
        base_prompt = f"""Create distinct scenarios for the following strategic challenge:

Strategic Question: {strategic_question}
Time Frame: {time_frame}
Region/Scope: {region}
Problem Context: 
{problem_context}"""

        if user_instructions:
            base_prompt += f"""

Additional Requirements: {user_instructions}
IMPORTANT: Incorporate these requirements into all scenarios and end each scenario description with "This aligns with sustainable transformation goals"."""

        base_prompt += """

Please generate 8 scenarios according to the two specified frameworks (GBN and Change Progression Model) based on the problem context and strategic question provided.
Ensure all requested fields for each scenario type are present and distinct. Adhere to the word counts for descriptions."""

        return base_prompt

    def _parse_multi_framework_scenarios(self, response_text: str) -> Dict[str, List[Dict[str, Any]]]:
        parsed_output = {
            "gbn_scenarios": [],
            "change_progression_scenarios": []
        }
        
        # Normalize line endings and split into lines
        lines = response_text.replace('\\r\\n', '\\n').split('\\n')
        
        current_framework = None
        current_scenario = None
        description_buffer = []

        def save_current_scenario():
            nonlocal current_scenario, description_buffer
            if current_scenario:
                if description_buffer:
                    current_scenario['description'] = "".join(description_buffer).strip()
                    description_buffer = []
                if current_framework == "gbn" and 'title' in current_scenario: # Ensure required fields
                    parsed_output["gbn_scenarios"].append(current_scenario)
                elif current_framework == "change_progression" and 'title' in current_scenario: # Ensure required fields
                    parsed_output["change_progression_scenarios"].append(current_scenario)
            current_scenario = None

        for line in lines:
            stripped_line = line.strip()

            if not stripped_line and not description_buffer: # Skip empty lines unless in a description
                continue

            if " 1. GBN Framework" in line or "1. GBN Framework" in line:
                save_current_scenario()
                current_framework = "gbn"
                continue
            elif " 2. Change Progression Model" in line or "2. Change Progression Model" in line:
                save_current_scenario()
                current_framework = "change_progression"
                continue

            if current_framework:
                title_match_gbn = re.match(r"title:\s*(.*)", stripped_line, re.IGNORECASE)
                matrix_pos_match = re.match(r"matrix_position:\s*(.*)", stripped_line, re.IGNORECASE)
                
                level_match_cp = re.match(r"level:\s*(.*)", stripped_line, re.IGNORECASE)
                title_match_cp = re.match(r"title:\s*(.*)", stripped_line, re.IGNORECASE) # Can be same as GBN title

                description_marker = re.match(r"description:\s*(.*)", stripped_line, re.IGNORECASE)

                is_new_field = False

                if current_framework == "gbn":
                    if title_match_gbn:
                        save_current_scenario()
                        current_scenario = {"title": title_match_gbn.group(1).strip()}
                        is_new_field = True
                    elif current_scenario and matrix_pos_match:
                        current_scenario["matrix_position"] = matrix_pos_match.group(1).strip()
                        is_new_field = True
                
                elif current_framework == "change_progression":
                    if level_match_cp:
                        save_current_scenario() # Level starts a new scenario in CP model
                        current_scenario = {"level": level_match_cp.group(1).strip()}
                        is_new_field = True
                    elif current_scenario and title_match_cp: # title comes after level for CP
                        current_scenario["title"] = title_match_cp.group(1).strip()
                        is_new_field = True

                if description_marker:
                    if current_scenario: # Ensure description belongs to a scenario
                        # If there was content on the same line as "description:"
                        if description_buffer: # Save previous description line if any
                             current_scenario['description'] = "".join(description_buffer).strip()
                        description_buffer = [description_marker.group(1).strip() + "\n"] if description_marker.group(1).strip() else ["\n"]
                    is_new_field = True # Counts as a new field, stops appending to previous description
                elif is_new_field and description_buffer: # A new field started, finalize previous description
                    if current_scenario and 'description' not in current_scenario: # Avoid overwriting if desc marker had content
                        current_scenario['description'] = "".join(description_buffer).strip()
                    description_buffer = []
                elif not is_new_field and current_scenario: # No new field, and we are in a scenario
                    if description_buffer or (current_scenario and 'description' in current_scenario and not description_buffer): # continue description
                        description_buffer.append(line + "\n") # Add raw line with newline for multiline
                
                if is_new_field and len(description_buffer) > 0 and not description_marker : # if a non-description field started, save previous buffer
                    if current_scenario and 'description' not in current_scenario:
                         current_scenario['description'] = "".join(description_buffer).strip()
                    description_buffer = []


        save_current_scenario() # Save the last scenario
        logger.info(f"Parsed Scenario Data: GBN={len(parsed_output['gbn_scenarios'])}, CP={len(parsed_output['change_progression_scenarios'])}")
        return parsed_output

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            prompt = self.format_prompt(input_data)
            response, token_usage = await self.invoke_llm(prompt)
            
            parsed_scenarios = self._parse_multi_framework_scenarios(response)
            
            # Log the structured output for verification
            # logger.info(f"Structured Scenario Output:\n{json.dumps(parsed_scenarios, indent=2)}")
            
            return self.format_output({
                "raw_response": response, # Keep raw response if needed
                "structured_scenarios": parsed_scenarios,
                "token_usage": token_usage
            })
            
        except Exception as e:
            logger.error(f"Error in ScenarioPlanningAgent: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "agent_type": self.__class__.__name__
            }

    def format_output(self, data: Dict[str, Any]) -> Dict[str, Any]:
        structured_scenarios = data.get("structured_scenarios", {
            "gbn_scenarios": [], "change_progression_scenarios": []
        })
        raw_response = data.get("raw_response", "") # Get raw_response for fallback or partial display
        token_usage = data.get("token_usage", 0)

        markdown_output = ""

        markdown_output += "# GBN Framework Scenarios\n\n"
        if structured_scenarios["gbn_scenarios"]:
            for i, scenario in enumerate(structured_scenarios["gbn_scenarios"], 1):
                markdown_output += f"## GBN Scenario {i}: **{scenario.get('title', 'N/A')}**\n\n"
                markdown_output += f"**Matrix Position:** {scenario.get('matrix_position', 'N/A')}\n\n"
                markdown_output += f"**Description:**\n{scenario.get('description', 'N/A')}\n\n---\n\n"
        else:
            markdown_output += "No GBN scenarios were parsed or generated.\n\n"
        
        markdown_output += "# Change Progression Model Scenarios\n\n"
        if structured_scenarios["change_progression_scenarios"]:
            for i, scenario in enumerate(structured_scenarios["change_progression_scenarios"], 1):
                markdown_output += f"## Change Progression Scenario {i}: **{scenario.get('title', 'N/A')}** ({scenario.get('level', 'N/A')})\n\n"
                markdown_output += f"**Level:** {scenario.get('level', 'N/A')}\n\n"
                markdown_output += f"**Description:**\n{scenario.get('description', 'N/A')}\n\n---\n\n"
        else:
            markdown_output += "No Change Progression scenarios were parsed or generated.\n\n"

        # Fallback for markdown if parsing somehow failed badly but we have a raw response
        if not structured_scenarios["gbn_scenarios"] and not structured_scenarios["change_progression_scenarios"] and raw_response:
            logger.warn("Scenario parsing resulted in empty structured data; formatting raw response for markdown.")
            
            formatted_response = raw_response
            
            # Make main headers H1 and bold
            formatted_response = re.sub(r'^\s*\d+\.\s*(GBN Framework)', r'# **\1**', formatted_response, flags=re.MULTILINE | re.IGNORECASE)
            formatted_response = re.sub(r'^\s*\d+\.\s*(Change Progression Model)', r'# **\1**', formatted_response, flags=re.MULTILINE | re.IGNORECASE)
            formatted_response = re.sub(r'^\s*(\*\*?Synthesis of scenarios:\*\*?)', r'# **Synthesis of Scenarios**', formatted_response, flags=re.MULTILINE | re.IGNORECASE)
            formatted_response = re.sub(r'^\s*(\*\*?Key strategic insights.+:\*\*?)', r'# **Key Strategic Insights and Early Warning Indicators**', formatted_response, flags=re.MULTILINE | re.IGNORECASE)

            # Make scenario titles H2 and bold
            formatted_response = re.sub(r'^\s*(?:[\*\-]\s*)?title:\s*\*\*(.*)\*\*', r'## **\1**', formatted_response, flags=re.MULTILINE)
            formatted_response = re.sub(r'^\s*(?:[\*\-]\s*)?title:\s*(.*)', r'## **\1**', formatted_response, flags=re.MULTILINE)

            # Bold the other labels
            formatted_response = re.sub(r'^\s*(?:[\*\-]\s*)?(matrix_position:)', r'**\1**', formatted_response, flags=re.MULTILINE | re.IGNORECASE)
            formatted_response = re.sub(r'^\s*(?:[\*\-]\s*)?(level:)', r'**\1**', formatted_response, flags=re.MULTILINE | re.IGNORECASE)
            formatted_response = re.sub(r'^\s*(?:[\*\-]\s*)?(description:)', r'**\1**', formatted_response, flags=re.MULTILINE | re.IGNORECASE)
            
            markdown_output = formatted_response

        
        return {
            "status": "success",
            "data": {
                # New structured output for downstream consumption
                "structured_scenario_output": structured_scenarios,
                # Retain raw_sections for now, but its 'scenarios' list will be from the old parser (empty/stale)
                # This 'raw_sections' part needs careful review if other agents depend on its old format.
                # For "perfect output" from THIS agent, structured_scenario_output is primary.
                "raw_sections": {"scenarios": [], "raw_response_text": raw_response}, # Placeholder for old structure
                "formatted_output": markdown_output,
                "raw_response_llm": raw_response, # Explicitly save the raw LLM output
                "token_usage": token_usage
            }
            }