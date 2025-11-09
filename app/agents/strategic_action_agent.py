from typing import Dict, Any, List
from .base_agent import BaseAgent
import json
import re
import logging

logger = logging.getLogger(__name__)

class StrategicActionAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.timeout = 90  # Increased timeout for this complex agent

    def get_system_prompt(self) -> str:
        return """You are the Strategic Action Planning Agent, a strategy-to-execution specialist responsible for turning foresight insights into a practical, time-bound roadmap for implementation.

Your mission is to:
- Translate the synthesized findings from the Research Synthesis Agent into clear, prioritized, and time-sequenced strategic actions.
- Provide a balanced mix of quick wins, medium-term initiatives, and long-term systemic strategies to ensure early momentum while building toward transformational change.
- Deliver a structured, operationally ready action plan that can guide immediate execution and long-term strategic alignment.

Task Flow
When given a problem statement and context, along with the Research Synthesis Agent's output (Key Insights, Opportunity Spaces, Risks & Resilience, Innovation Pathways, Quick Wins vs. Long-Term Strategies):
1. Restate the challenge in your own words to confirm understanding.
2. Develop strategic ideas and action plans across three time horizons.
3. Ensure all actions are realistic, clearly defined, and directly aligned with the challenge context and synthesized insights.

The Three-Tier Strategic Action Framework

1. Near-Term (0–2 Years) – Quick Wins & Urgent Needs
Purpose: Deliver immediate, visible impact with minimal investment and high feasibility.
For each Strategic Idea:
* Title – A concise, action-oriented name.
* Summary (≤100 words) – What it aims to achieve and why it matters now.
* Action Plan (5 Specific Steps) – Each step must be operationally ready.
* Format: [Action Item] – Priority: High / Medium / Low
* Priority Guidance – Highlight which actions unlock immediate value or reduce key risks.

2. Medium-Term (2–5 Years) – Strategic Build-Out
Purpose: Implement initiatives requiring moderate planning, resource allocation, or stakeholder coordination.
For each Strategic Idea:
* Title & Summary (≤100 words) – What medium-term goal it advances.
* Action Plan (5 Steps) – Focus on sequencing, resource mobilization, and cross-stakeholder collaboration.
* Priority Levels – Indicate which actions are foundational vs. enabling.

3. Long-Term (5–10 Years) – Visionary & Transformational Strategies
Purpose: Build toward systemic change, institutional reform, or breakthrough innovation aligned with broader strategic goals.
For each Strategic Idea:
* Title & Summary (≤100 words) – Articulate the long-term vision and transformative potential.
* Action Plan (5 Steps) – Steps may include policy shifts, institutional redesign, major R&D initiatives, or cultural change programs.
* Priority Levels – Highlight early groundwork actions essential for long-term success.

CRITICAL OUTPUT FORMAT REQUIREMENTS
You MUST format your response using exactly this markdown structure:

### Near-Term (0–2 Years) – Quick Wins & Urgent Needs

#### Strategic Idea 1: [Title]
**Summary:** [What this idea aims to achieve, strategic relevance – ≤100 words]

**Action Items:**
1. **[Action Name]** - [Detailed description] -- **Priority:** [High/Medium/Low]
2. **[Action Name]** - [Detailed description] -- **Priority:** [High/Medium/Low]
3. **[Action Name]** - [Detailed description] -- **Priority:** [High/Medium/Low]
4. **[Action Name]** - [Detailed description] -- **Priority:** [High/Medium/Low]
5. **[Action Name]** - [Detailed description] -- **Priority:** [High/Medium/Low]

#### Strategic Idea 2: [Title]
**Summary:** [What this idea aims to achieve, strategic relevance – ≤100 words]

**Action Items:**
1. **[Action Name]** - [Detailed description] -- **Priority:** [High/Medium/Low]
2. **[Action Name]** - [Detailed description] -- **Priority:** [High/Medium/Low]
3. **[Action Name]** - [Detailed description] -- **Priority:** [High/Medium/Low]

### Medium-Term (2–5 Years) – Strategic Build-Out

#### Strategic Idea 1: [Title]
**Summary:** [What this idea aims to achieve, strategic relevance – ≤100 words]

**Action Items:**
1. **[Action Name]** - [Detailed description] -- **Priority:** [High/Medium/Low]
2. **[Action Name]** - [Detailed description] -- **Priority:** [High/Medium/Low]
3. **[Action Name]** - [Detailed description] -- **Priority:** [High/Medium/Low]
4. **[Action Name]** - [Detailed description] -- **Priority:** [High/Medium/Low]
5. **[Action Name]** - [Detailed description] -- **Priority:** [High/Medium/Low]

#### Strategic Idea 2: [Title]
**Summary:** [What this idea aims to achieve, strategic relevance – ≤100 words]

**Action Items:**
1. **[Action Name]** - [Detailed description] -- **Priority:** [High/Medium/Low]
2. **[Action Name]** - [Detailed description] -- **Priority:** [High/Medium/Low]
3. **[Action Name]** - [Detailed description] -- **Priority:** [High/Medium/Low]

### Long-Term (5–10 Years) – Visionary & Transformational Strategies

#### Strategic Idea 1: [Title]
**Summary:** [What this idea aims to achieve, strategic relevance – ≤100 words]

**Action Items:**
1. **[Action Name]** - [Detailed description] -- **Priority:** [High/Medium/Low]
2. **[Action Name]** - [Detailed description] -- **Priority:** [High/Medium/Low]
3. **[Action Name]** - [Detailed description] -- **Priority:** [High/Medium/Low]
4. **[Action Name]** - [Detailed description] -- **Priority:** [High/Medium/Low]
5. **[Action Name]** - [Detailed description] -- **Priority:** [High/Medium/Low]

#### Strategic Idea 2: [Title]
**Summary:** [What this idea aims to achieve, strategic relevance – ≤100 words]

**Action Items:**
1. **[Action Name]** - [Detailed description] -- **Priority:** [High/Medium/Low]
2. **[Action Name]** - [Detailed description] -- **Priority:** [High/Medium/Low]
3. **[Action Name]** - [Detailed description] -- **Priority:** [High/Medium/Low]

Guidelines for the Agent
* Be action-oriented – Avoid vague recommendations; every step must be ready for operationalization.
* Ensure alignment – Each action should trace back to Key Insights, Opportunity Spaces, or Innovation Pathways from prior research.
* Prioritize strategically – Consider impact, urgency, feasibility, and sequencing.
* Balance horizons – Quick wins should create momentum, while long-term strategies should lay foundations for transformation.
* Keep language clear & concise – Write for decision-makers who need immediate clarity on what to do, when, and why."""

    def _convert_list_to_string_for_prompt(self, items: List[str]) -> str:
        if not items:
            return "N/A"
        return "\n- " + "\n- ".join(items)

    def format_prompt(self, input_data: Dict[str, Any]) -> str:
        strategic_question = input_data.get('strategic_question', 'N/A')
        contextual_constraints = input_data.get('prompt', 'None provided')

        synthesis_data = input_data.get('research_synthesis', {}).get('data', {}).get('structured_synthesis', {})
        
        synthesis_sections_text = "\n\nResearch Synthesis Agent Output:\n"
        
        section_titles_map = {
            "key_insights": "📌 Key Insights",
            "opportunity_spaces": "🚀 Opportunity Spaces",
            "risk_and_resilience": "⚠️ Risk & Resilience",
            "innovation_pathways": "💡 Innovation Pathways",
            "quick_wins_vs_long_term": "📆 Quick Wins vs Long-Term Strategies"
        }

        for key, title in section_titles_map.items():
            items = synthesis_data.get(key, [])
            if items:
                synthesis_sections_text += f"\n--- {title} ---\n"
                for item in items:
                    if isinstance(item, dict):
                         synthesis_sections_text += f"- {item.get('content', json.dumps(item))}\n"
                    else:
                         synthesis_sections_text += f"- {str(item)}\n"
            else:
                synthesis_sections_text += f"\n--- {title} ---\nNo specific points provided by Research Synthesis Agent for this section.\n"

        return f"""Original Problem Statement: {strategic_question}

Contextual Constraints (if any): {contextual_constraints}
{synthesis_sections_text}

Based on all the above information (Original Problem, Constraints, and the detailed Research Synthesis output), please generate strategic ideas and their specific action items according to the three time horizons (Near-Term, Medium-Term, Long-Term) and prioritization criteria outlined in your system instructions.
Focus on creating a practical and actionable roadmap.
"""

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        prompt = self.format_prompt(input_data)
        
        try:
            # Call the LLM
            response, token_usage = await self.invoke_llm(prompt)
            
            # Log the raw response for debugging
            logger.info(f"Raw LLM response (first 500 chars): {response[:500]}...")
            logger.info(f"Full LLM response length: {len(response)} characters")
            
            # Log the response instead of saving to file
            logger.debug(f"Full LLM response: {response}")
            
            # Parse the response with multiple strategies
            parsed_action_plan = self._parse_structured_response(response)
            
            # Check if parsing was successful
            total_ideas = sum(len(ideas) for ideas in parsed_action_plan.values())
            logger.info(f"Main parsing result: {total_ideas} ideas found")
            for key, ideas in parsed_action_plan.items():
                if ideas:
                    logger.info(f"  {key}: {len(ideas)} ideas")
                    for i, idea in enumerate(ideas):
                        logger.info(f"    {i+1}. '{idea.get('idea_title', 'NO TITLE')[:50]}...'")
            
            if total_ideas == 0:
                logger.warning("Main parsing failed, trying fallback parsing")
                parsed_action_plan = self._fallback_parse_response(response)
                
                total_ideas = sum(len(ideas) for ideas in parsed_action_plan.values())
                logger.info(f"Fallback parsing result: {total_ideas} ideas found")
                
                if total_ideas == 0:
                    logger.warning("Fallback parsing failed, creating basic structure")
                    parsed_action_plan = self._create_basic_structure(response)
                    total_ideas = sum(len(ideas) for ideas in parsed_action_plan.values())
                    logger.info(f"Basic structure result: {total_ideas} ideas found")
            
            # Format the output
            formatted_output = self.format_output(parsed_action_plan, response, token_usage)
            
            logger.info(f"Final output contains {total_ideas} strategic ideas")
            
            return {
                "status": "success",
                "data": formatted_output["data"],  # Extract the data dict from format_output
                "metadata": {
                    "prompt_length": len(prompt),
                    "response_length": len(response),
                    "ideas_parsed": total_ideas,
                    "parsing_strategy": "structured" if total_ideas > 0 else "fallback",
                    "token_usage": token_usage
                }
            }
            
        except Exception as e:
            logger.error(f"Error in Strategic Action Agent: {str(e)}")
            error_output = {
                "markdown": f"# Strategic Action Plan\n\n**Error:** Unable to generate strategic action plan due to processing error: {str(e)}\n\nPlease try again or contact support if the issue persists.",
                "structured_data": {
                    "near_term_ideas": [],
                    "medium_term_ideas": [],
                    "long_term_ideas": []
                }
            }
            
            return {
                "status": "error",
                "error": str(e),
                "data": error_output,
                "metadata": {
                    "error": str(e),
                    "prompt_length": len(prompt) if 'prompt' in locals() else 0
                }
            }

    def _parse_structured_response(self, response: str) -> Dict[str, Any]:
        """Main parsing logic for structured LLM responses"""
        parsed_action_plan = {
            "near_term_ideas": [],
            "medium_term_ideas": [],
            "long_term_ideas": []
        }
        
        current_time_horizon_key = None
        current_strategic_idea = None
        action_item_buffer = []

        lines = response.split('\n')
        logger.info(f"Parsing response with {len(lines)} lines")

        def save_current_strategic_idea():
            nonlocal current_strategic_idea, current_time_horizon_key, action_item_buffer
            if current_strategic_idea and current_strategic_idea.get('idea_title') and action_item_buffer:
                current_strategic_idea['action_items'] = [item for item in action_item_buffer if isinstance(item, dict)]
            
            if current_strategic_idea and current_strategic_idea.get('idea_title') and current_strategic_idea.get('action_items'):
                if current_time_horizon_key:
                    parsed_action_plan[current_time_horizon_key].append(current_strategic_idea)
                    logger.debug(f"Saved idea: {current_strategic_idea['idea_title']} with {len(current_strategic_idea['action_items'])} actions")
                else:
                    logger.warning(f"Strategic idea '{current_strategic_idea.get('idea_title')}' found without a time horizon.")
            current_strategic_idea = None
            action_item_buffer = []
        
        for i, line in enumerate(lines):
            stripped_line = line.strip()
            if not stripped_line:
                continue
            
            # 1. Time Horizon Detection (enhanced for markdown format)
            time_horizon_match = None
            if re.search(r"^#{1,3}\s*.*(?:near.?term|0.?2\s*years|short.?term)", stripped_line, re.IGNORECASE):
                if current_strategic_idea: save_current_strategic_idea()
                current_time_horizon_key = "near_term_ideas"
                logger.debug(f"Found near-term section at line {i}: {stripped_line}")
                continue
            elif re.search(r"^#{1,3}\s*.*(?:medium.?term|2.?5\s*years)", stripped_line, re.IGNORECASE):
                if current_strategic_idea: save_current_strategic_idea()
                current_time_horizon_key = "medium_term_ideas"
                logger.debug(f"Found medium-term section at line {i}: {stripped_line}")
                continue
            elif re.search(r"^#{1,3}\s*.*(?:long.?term|5.?10\s*years)", stripped_line, re.IGNORECASE):
                if current_strategic_idea: save_current_strategic_idea()
                current_time_horizon_key = "long_term_ideas"
                logger.debug(f"Found long-term section at line {i}: {stripped_line}")
                continue
            
            # Skip if not under a time horizon
            if not current_time_horizon_key:
                continue
            
            # 2. Strategic Idea Detection (enhanced for markdown format)
            title_patterns = [
                # Match: "#### Idea 1: Title" or "#### Strategic Idea 1: Title"
                r"^#{3,4}\s*(?:strategic\s+)?idea\s*\d*:\s*(.+)",
                # Match: "Strategic Idea: Title" or "Idea: Title"
                r"(?:strategic\s+idea|idea|title):\s*(.+)",
                # Match: "1. Strategic Title" or "• Strategic Title" 
                r"^(?:\d+\.|\*|-|•)\s*(.+?)(?:\s*\(|$)",
                # Match any line that looks like a title (not starting with action words)
                r"^([A-Z][^.!?]*(?:Strategy|Plan|Initiative|Approach|Framework|Capabilities|Enhancement|Development|Implementation|Integration|Optimization)[^.!?]*)$",
                # Match: "Development of..." or "Implementation of..." etc.
                r"^((?:Development|Implementation|Creation|Establishment|Enhancement|Optimization|Integration)\s+of\s+.+)",
                # Match lines that don't start with action words but seem like titles
                r"^([A-Z][^.!?]{15,60})(?:\s*$|:)",
            ]
            
            title_match = None
            for pattern in title_patterns:
                title_match = re.match(pattern, stripped_line, re.IGNORECASE)
                if title_match:
                    potential_title = title_match.group(1).strip()
                    # Filter out obvious non-titles including time horizons
                    if (not re.match(r"timeline|priority|action|summary|detail|action\s+items|priority:", potential_title, re.IGNORECASE) and
                        not re.search(r"(?:near|medium|long).?term|(?:0.?2|2.?5|5.?10)\s*years", potential_title, re.IGNORECASE) and
                        not potential_title.startswith('*')):  # Avoid **Summary:** etc.
                        break
                    else:
                        title_match = None
            
            if title_match:
                if current_strategic_idea: save_current_strategic_idea()
                title = title_match.group(1).strip()
                logger.debug(f"Found strategic idea title at line {i}: {title}")
                
                current_strategic_idea = {
                    "idea_title": title,
                    "idea_summary": "",
                    "action_items": []
                }
                action_item_buffer = []
                
                # Look for summary in next few lines
                summary_buffer = []
                for j in range(1, min(8, len(lines) - i)):
                    if i + j >= len(lines):
                        break
                    next_line = lines[i+j].strip()
                    if not next_line:
                        continue
                    
                    # Check if this line is a summary
                    if next_line.startswith('**Summary:**'):
                        summary_text = next_line.replace('**Summary:**', '').strip()
                        if summary_text:
                            summary_buffer.append(summary_text)
                        # Continue reading until we hit action items or another section
                        for k in range(j+1, min(j+4, len(lines) - i)):
                            if i + k >= len(lines):
                                break
                            follow_line = lines[i+k].strip()
                            if not follow_line:
                                continue
                            if (re.match(r"^\*\*action\s+items?:\*\*", follow_line, re.IGNORECASE) or
                                re.match(r"^#{2,4}", follow_line) or
                                re.match(r"^\d+\.", follow_line)):
                                break
                            summary_buffer.append(follow_line)
                        break
                    
                    # Stop if we hit action items or another title
                    if (re.match(r"^\*\*action\s+items?:\*\*", next_line, re.IGNORECASE) or
                        re.match(r"^#{2,4}", next_line) or
                        re.match(r"^\d+\.", next_line)):
                        break
                
                if summary_buffer:
                    current_strategic_idea["idea_summary"] = " ".join(summary_buffer)
                    logger.debug(f"Found summary: {current_strategic_idea['idea_summary'][:50]}...")
                else:
                    current_strategic_idea["idea_summary"] = "Strategic initiative for organizational improvement"
                continue

            # 3. Action Item Detection (enhanced for markdown format)
            if current_strategic_idea:
                # Skip header lines like "**Action Items:**" or "**Summary:**"
                if re.match(r"^\*\*(?:Action Items?|Summary):\*\*\s*$", stripped_line, re.IGNORECASE):
                    continue
                
                # Improved pattern to match the actual LLM output format
                # Format: "1. **Action Name** - Description -- **Priority:** High"
                action_pattern = r"^(\d+\.)\s*\*\*([^*]+)\*\*\s*-\s*([^-]+?)\s*--\s*\*\*Priority:\*\*\s*(High|Medium|Low)\s*$"
                action_match = re.match(action_pattern, stripped_line, re.IGNORECASE)
                
                if action_match:
                    action_name = action_match.group(2).strip()
                    action_description = action_match.group(3).strip()
                    priority = action_match.group(4).title()
                    
                    # Combine name and description for full action text
                    action_text = f"{action_name} - {action_description}"
                    
                    current_action = {
                        "action": action_text,
                        "priority": priority
                    }
                    action_item_buffer.append(current_action)
                    logger.debug(f"Found action: {action_text[:50]}... Priority: {priority}")
                    continue
                
                # Fallback pattern for simpler formats without description
                simple_pattern = r"^(\d+\.)\s*\*\*([^*]+)\*\*.*?--\s*\*\*Priority:\*\*\s*(High|Medium|Low)"
                simple_match = re.match(simple_pattern, stripped_line, re.IGNORECASE)
                
                if simple_match:
                    action_text = simple_match.group(2).strip()
                    priority = simple_match.group(3).title()
                    
                    current_action = {
                        "action": action_text,
                        "priority": priority
                    }
                    action_item_buffer.append(current_action)
                    logger.debug(f"Found action (simple): {action_text[:50]}... Priority: {priority}")
                    continue

        # Save any remaining idea
        if current_strategic_idea:
            save_current_strategic_idea()
        
        logger.info(f"Parsed {sum(len(ideas) for ideas in parsed_action_plan.values())} strategic ideas")
        return parsed_action_plan

    def _fallback_parse_response(self, response: str) -> Dict[str, Any]:
        """Fallback parsing for less structured responses"""
        parsed_action_plan = {
            "near_term_ideas": [],
            "medium_term_ideas": [],
            "long_term_ideas": []
        }
        
        # Split by common section indicators
        sections = re.split(r'\n(?=(?:near|medium|long|short).?term|\d+\.\s*(?:near|medium|long))', response, flags=re.IGNORECASE)
        
        for section in sections:
            section = section.strip()
            if not section:
                continue
                
            # Determine time horizon
            time_key = None
            if re.search(r"near.?term|short.?term|0.?2\s*years", section, re.IGNORECASE):
                time_key = "near_term_ideas"
            elif re.search(r"medium.?term|2.?5\s*years", section, re.IGNORECASE):
                time_key = "medium_term_ideas"
            elif re.search(r"long.?term|5.?10\s*years", section, re.IGNORECASE):
                time_key = "long_term_ideas"
            
            if not time_key:
                continue
            
            # Extract ideas from this section
            lines = section.split('\n')
            current_idea = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Look for idea titles (anything that looks like a heading)
                if re.match(r"(?:\d+\.|\*|-|#{1,3})\s*([^(]+)", line) and len(line) > 10:
                    if current_idea and current_idea.get('action_items'):
                        parsed_action_plan[time_key].append(current_idea)
                    
                    current_idea = {
                        "idea_title": re.sub(r"^(?:\d+\.|\*|-|#{1,3})\s*", "", line).strip(),
                        "idea_summary": "Strategic initiative for implementation",
                        "action_items": []
                    }
                
                # Look for action items
                elif current_idea and (line.startswith('-') or line.startswith('•') or re.match(r'\d+\.', line)):
                    action_text = re.sub(r"^(?:\d+\.|-|•)\s*", "", line).strip()
                    if len(action_text) > 5:
                        current_idea['action_items'].append({
                            "action": action_text,
                            "priority": "Medium"
                        })
            
            # Save last idea
            if current_idea and current_idea.get('action_items'):
                parsed_action_plan[time_key].append(current_idea)
        
        return parsed_action_plan

    def _create_basic_structure(self, response: str) -> Dict[str, Any]:
        """Create basic structure when all parsing fails"""
        logger.warning("Creating basic structure from raw response")
        
        # Extract main points from response
        lines = [line.strip() for line in response.split('\n') if line.strip() and len(line.strip()) > 10]
        
        if not lines:
            logger.warning("No meaningful lines found in response")
            return {
                "near_term_ideas": [],
                "medium_term_ideas": [],
                "long_term_ideas": []
            }
        
        # Try to extract action-like statements from the response
        action_lines = []
        for line in lines[:15]:  # Look at first 15 meaningful lines
            # Clean up the line
            cleaned_line = re.sub(r"^(?:\d+\.|\*|-|#{1,4})\s*", "", line).strip()
            cleaned_line = re.sub(r"priority:\s*(high|medium|low)", "", cleaned_line, flags=re.IGNORECASE).strip()
            cleaned_line = re.sub(r"--\s*$", "", cleaned_line).strip()
            
            # Skip lines that are obviously not actions
            if (cleaned_line and 
                len(cleaned_line) > 15 and
                not cleaned_line.lower().startswith(('near-term', 'medium-term', 'long-term', 'summary:', 'action items:', 'strategic idea', 'phase', 'step')) and
                not re.match(r'^\d+\s*years?', cleaned_line.lower()) and
                not cleaned_line.startswith('**') and
                '=' not in cleaned_line):
                action_lines.append(cleaned_line)
        
        logger.info(f"Extracted {len(action_lines)} potential action items from response")
        
        if not action_lines:
            # If no good action lines found, create generic ones
            action_lines = [
                "Review and assess current capabilities and resources",
                "Develop implementation timeline and resource allocation plan", 
                "Establish key performance indicators and success metrics",
                "Create stakeholder communication and engagement strategy",
                "Begin pilot implementation with selected initiatives"
            ]
            logger.info("Using fallback generic action items")
        
        # Create a comprehensive strategic idea
        basic_idea = {
            "idea_title": "Strategic Implementation Framework",
            "idea_summary": "Comprehensive approach to implementing strategic initiatives based on analysis findings and organizational capabilities",
            "action_items": []
        }
        
        # Convert action lines to proper action items
        priorities = ["High", "Medium", "Low"]
        for i, action_line in enumerate(action_lines[:6]):  # Limit to 6 action items
            # Ensure action starts with a verb if it doesn't already
            if not re.match(r'^(Develop|Implement|Create|Establish|Build|Design|Launch|Execute|Conduct|Analyze|Evaluate|Monitor|Review|Optimize|Enhance|Integrate|Deploy|Train|Assess|Identify|Research|Plan|Organize|Coordinate|Manage)', action_line, re.IGNORECASE):
                if not action_line[0].isupper():
                    action_line = action_line.capitalize()
                # Add a verb if needed
                if not any(action_line.lower().startswith(verb.lower()) for verb in ['develop', 'implement', 'create', 'establish', 'build', 'design', 'launch', 'execute', 'conduct', 'analyze', 'evaluate', 'monitor', 'review', 'optimize', 'enhance', 'integrate', 'deploy', 'train', 'assess', 'identify', 'research', 'plan', 'organize', 'coordinate', 'manage']):
                    action_line = f"Implement {action_line.lower()}"
            
            basic_idea['action_items'].append({
                "action": action_line,
                "priority": priorities[i % 3]
            })
        
        result = {
            "near_term_ideas": [basic_idea],
            "medium_term_ideas": [],
            "long_term_ideas": []
        }
        
        logger.info(f"Created basic structure with {len(basic_idea['action_items'])} action items")
        return result

    def format_output(self, parsed_action_plan: Dict[str, Any], raw_response: str = "", token_usage: int = 0) -> Dict[str, Any]:
        markdown_output = "\n\n"
        time_horizon_map = {
            "near_term_ideas": "# Near-Term (0–2 years)",
            "medium_term_ideas": "# Medium-Term (2–5 years)",
            "long_term_ideas": "# Long-Term (5–10 years)"
        }

        any_ideas_found = False
        for key, title_markdown in time_horizon_map.items():
            ideas = parsed_action_plan.get(key, [])
            if ideas:
                any_ideas_found = True
                markdown_output += f"{title_markdown}\n\n"
                for i, idea in enumerate(ideas):
                    markdown_output += f"### Strategic Idea {i+1}: {idea.get('idea_title', 'N/A')}\n"
                    markdown_output += f"**Summary:** {idea.get('idea_summary', 'N/A')}\n\n"
                    markdown_output += "**Action Items:**\n"
                    action_items = idea.get('action_items', [])
                    if action_items:
                        for j, item in enumerate(action_items):
                            markdown_output += f"{j+1}. {item.get('action', 'N/A')} -- **Priority:** {item.get('priority', 'Medium')}\n"
                    else:
                        markdown_output += "- No specific action items identified for this idea.\n"
                    markdown_output += "\n"

        if not any_ideas_found:
            markdown_output += "## Analysis Results\n\n"
            markdown_output += "The analysis has been completed. Here are the key strategic insights:\n\n"
            
            # Try to extract at least some meaningful content from raw response
            if raw_response:
                # Extract meaningful lines from raw response
                meaningful_lines = []
                for line in raw_response.split('\n'):
                    line = line.strip()
                    if line and len(line) > 20 and not line.startswith('#'):
                        # Clean up common prefixes
                        cleaned_line = re.sub(r'^(?:\d+\.|\*|-|•)\s*', '', line)
                        if cleaned_line:
                            meaningful_lines.append(cleaned_line)
                
                if meaningful_lines:
                    markdown_output += "### Key Strategic Recommendations:\n\n"
                    for i, line in enumerate(meaningful_lines[:8], 1):  # Limit to 8 recommendations
                        markdown_output += f"{i}. {line}\n"
                    markdown_output += "\n"
                
                # Add a section for raw analysis if available
                if len(raw_response) > 100:
                    markdown_output += "### Detailed Analysis:\n\n"
                    # Clean and format the raw response
                    cleaned_response = re.sub(r'\n{3,}', '\n\n', raw_response.strip())
                    markdown_output += cleaned_response + "\n\n"
            
            markdown_output += "*Strategic recommendations have been generated based on the comprehensive analysis. "
            markdown_output += "Please review the detailed analysis above for implementation guidance.*\n"

        return {
            "status": "success",
            "data": {
                "structured_action_plan": parsed_action_plan,
                "raw_sections": parsed_action_plan,
                "formatted_output": markdown_output,
                "raw_llm_response": raw_response,  # Include for debugging
                "token_usage": token_usage
            }
        } 