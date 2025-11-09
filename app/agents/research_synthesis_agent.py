from typing import Dict, Any, List
from .base_agent import BaseAgent
import logging
import json
import re


logger = logging.getLogger(__name__)


class ResearchSynthesisAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.timeout = 120  # Increased timeout

    def get_system_prompt(self) -> str:
        return """You are the Research Synthesis Agent, a strategic foresight integrator responsible for extracting, prioritizing, and translating research findings into actionable, high-leverage insights.

Your mission is to:
- Synthesize—not just summarize—the outputs of prior research agents (Problem Explorer, Best Practices, Horizon Scanning, and Scenario Planning).
- Identify opportunity spaces, risks, and innovation pathways with strategic relevance.
- Provide decision-makers with clear, actionable insights and a roadmap that balances quick wins with long-term strategies.

Task Flow
When given a problem statement or challenge along with all research outputs:
1. Restate the challenge in your own words to confirm understanding.
2. Analyze all inputs holistically, focusing on interconnections, implications, and strategic meaning rather than repeating raw findings.
3. Structure your synthesis into five action-oriented sections.
4. For every major section, identify identical subheadings, consolidate the text from them, and rewrite the grouped points into a single, cohesive paragraph. Use connecting words and phrases to ensure a logical flow. DO NOT use bullet points or numbered lists in the final output.

The Five-Section Research Synthesis Framework

Section 1 – Key Insights (Critical Takeaways for Action)
Purpose: Extract only the most high-impact, decision-relevant findings. Avoid restating obvious or descriptive points.
For each key insight:
1. State the Insight – What is the most critical finding across all research inputs?
2. Actionable Implication – How does this insight directly inform strategy or intervention?
3. Strategic Translation – What concrete action or policy does this suggest?
Deliverable: 3-4 complete insight blocks, each with its own Insight, Actionable Implication, and Strategic Translation sections, which will then be consolidated into paragraphs.

Section 2 – Opportunity Spaces (Where to Act or Innovate)
Purpose: Identify high-leverage domains for action or innovation based on research and scenario exploration.
For each opportunity space:
1. Define the Opportunity – Where is there greatest potential for high-impact intervention?
2. Rationale – What research or scenario insights highlight this as a priority?
3. Potential Impact – What tangible benefits or transformative effects could result?
Deliverable: 3–5 clearly defined opportunity areas with brief justifications.

Section 3 – Risk and Resilience (Anticipating Challenges & Building Robustness)
Purpose: Identify risks and outline practical resilience strategies to remain adaptable under uncertainty.
For each risk:
1. Risk Description – What uncertainty or vulnerability emerged from research or scenarios?
2. Resilience Strategy – What action can mitigate this risk or increase adaptability?
3. Futureproofing – How can the strategy work under multiple future scenarios?
Deliverable: A two-column list mapping risks → resilience strategies.

Section 4 – Innovation Pathways (Transformative Solutions, Not Incremental Fixes)
Purpose: Highlight breakthrough opportunities by challenging outdated approaches.
For each pathway:
1. Gap in Current Approach – Where are existing methods failing or insufficient?
2. Emerging Innovation – What new idea, model, or technology could drive transformative change?
3. Strategic Fit – How does this directly advance the challenge solution?
Deliverable: A list of innovation opportunities mapped to specific gaps.

Section 5 – Quick Wins vs. Long-Term Strategies (Balanced Roadmap)
Purpose: Provide a two-tier action plan balancing urgent needs with sustainable success.
1. Quick Wins – Immediate, high-impact actions feasible within weeks or months.
2. Long-Term Strategies – Foundational initiatives to build resilience and transformation over 3–10 years.
3. Balance Consideration – How quick wins can lay the groundwork for long-term success.
Deliverable: A two-part roadmap (Quick Wins | Long-Term Strategies).

CRITICAL OUTPUT FORMAT REQUIREMENTS
You MUST format your response using exactly this structure, with each subheading followed by a single, consolidated paragraph. DO NOT use bullet points.

Here is an example for "Key Insights":

**Section 1: Key Insights**

**Insight:**
AI-powered tools offer significant productivity gains but require careful management of associated risks, as European businesses increasingly adopt them for efficiency while concerns around data privacy and job displacement persist. Simultaneously, a growing consumer demand for sustainability and ethical practices necessitates a shift in business strategy, given that European consumers prioritize these values and companies failing to adapt face reputational damage.

**Actionable Implication:**
To address these insights, businesses must strategically adopt AI tools while mitigating negative consequences, prioritizing those that enhance productivity without causing significant job displacement and implementing robust data governance. It is also essential to integrate sustainability and ethical considerations into core operations by developing transparent supply chains and implementing measurable sustainability targets.

**Strategic Translation:**
Long-term success requires developing a phased AI integration plan with clear ethical guidelines, including piloting tools in specific departments and establishing an ethics committee. In parallel, sustainability must be embedded into product development, marketing, and corporate governance, which involves designing eco-friendly products and transparently communicating these efforts to consumers.

---

Apply the same paragraph-based consolidation to all other sections:

**Section 2: Opportunity Spaces**

**Opportunity:**
[A single paragraph consolidating all "Opportunity" points]

**Rationale:**
[A single paragraph consolidating all "Rationale" points]

**Potential Impact:**
[A single paragraph consolidating all "Potential Impact" points]

**Section 3: Risk & Resilience**

**Risk:**
[A single paragraph consolidating all "Risk" points]

**Resilience Strategy:**
[A single paragraph consolidating all "Resilience Strategy" points]

**Futureproofing:**
[A single paragraph consolidating all "Futureproofing" points]

**Section 4: Innovation Pathways**

**Gap:**
[A single paragraph consolidating all "Gap" points]

**Emerging Innovation:**
[A single paragraph consolidating all "Emerging Innovation" points]

**Strategic Fit:**
[A single paragraph consolidating all "Strategic Fit" points]

**Section 5: Quick Wins vs Long-Term Strategies**

**Quick Wins:**
[A single paragraph consolidating all "Quick Wins" points]

**Long-Term Strategies:**
[A single paragraph consolidating all "Long-Term Strategies" points]

**Balance Consideration:**
[A single paragraph for the "Balance Consideration" section]

Guidelines for the Agent
* Synthesize, don't duplicate – Focus on meaning and implications, not raw data.
* Be action-oriented – Every insight should have clear strategic relevance.
* Use concise, decision-ready language – Prioritize strategic clarity, feasibility, and transformative potential.
* Ground all insights in the research and scenario context – Avoid generic statements."""


    def format_prompt(self, input_data: Dict[str, Any]) -> str:
        problem_explorer_data = input_data.get('problem_explorer', {}).get('data', {}).get('structured_output', {})
        problem_definition_text = "N/A"
        if problem_explorer_data:
            phase1_content = problem_explorer_data.get('phase1', {}).get('content', [])
            if phase1_content:
                problem_definition_text = "\n".join(phase1_content)
            elif problem_explorer_data.get('acknowledgment'):
                problem_definition_text = problem_explorer_data.get('acknowledgment')

        best_practices_data = input_data.get('best_practices', {}).get('data', {})
        best_practices_list = best_practices_data.get('structured_practices', []) 

        # Horizon scanning data - current structure is likely raw text due to user revert
        horizon_scan_raw_data = input_data.get('horizon_scanning', {}).get('data', {}).get('raw_sections', {})
        horizon_scan_text = "N/A"
        if isinstance(horizon_scan_raw_data, dict) and 'raw_response' in horizon_scan_raw_data: # Assuming old structure post-revert
            horizon_scan_text = horizon_scan_raw_data.get('raw_response', 'Horizon scan data not available or in unexpected format.')
        elif isinstance(horizon_scan_raw_data, str): # If raw_sections became just the string itself
             horizon_scan_text = horizon_scan_raw_data
        elif horizon_scan_raw_data: # If it's some other dict, try to stringify for now
            horizon_scan_text = json.dumps(horizon_scan_raw_data, indent=2)


        # Scenario Planning data - access the new detailed structure
        scenario_planning_output = input_data.get('scenario_planning', {}).get('data', {}).get('structured_scenario_output', {})
        gbn_scenarios = scenario_planning_output.get('gbn_scenarios', [])
        change_progression_scenarios = scenario_planning_output.get('change_progression_scenarios', [])

        scenarios_summary_text = "Scenario summaries not available or not parsed."
        if gbn_scenarios or change_progression_scenarios:
            scenarios_summary_text = "Key Scenarios Identified:\n"
            if gbn_scenarios:
                scenarios_summary_text += "\nGBN Framework Scenarios:\n"
                for s in gbn_scenarios[:2]: # Summarize first 2 GBN
                    scenarios_summary_text += f"- Title: {s.get('title', 'N/A')} (Position: {s.get('matrix_position', 'N/A')})\n  Description (brief): {s.get('description', 'N/A')[:100]}...\n"
            if change_progression_scenarios:
                scenarios_summary_text += "\nChange Progression Model Scenarios:\n"
                for s in change_progression_scenarios[:2]: # Summarize first 2 CP
                    scenarios_summary_text += f"- Title: {s.get('title', 'N/A')} (Level: {s.get('level', 'N/A')})\n  Description (brief): {s.get('description', 'N/A')[:100]}...\n"

        # Format best practices
        best_practices_text = "\n".join([f"- {p.get('title','N/A')}: {p.get('description','N/A')}" for p in best_practices_list[:2]]) if best_practices_list else "N/A"

        return f"""Synthesize the following research findings for the strategic question: {input_data.get('strategic_question', 'N/A')}

Problem Definition Context:
{problem_definition_text}

Key Best Practices Identified:
{best_practices_text}

Horizon Scanning Insights (Raw, as available):
{horizon_scan_text}

{scenarios_summary_text}

Additional Instructions from user: {input_data.get('prompt', 'N/A')}

Please provide a comprehensive synthesis following the 5-section structure outlined in your system prompt (Key Insights, Opportunity Spaces, Risk & Resilience, Innovation Pathways, Quick Wins vs Long-Term Strategies).
Ensure all insights are grounded in the provided research and scenarios.
"""


    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            prompt = self.format_prompt(input_data)
            response, token_usage = await self.invoke_llm(prompt)
           
            # New parsing logic for the 5 sections
            parsed_data = {
                "key_insights": [],
                "opportunity_spaces": [],
                "risk_and_resilience": [],
                "innovation_pathways": [],
                "quick_wins_vs_long_term": []
            }
           
            current_section_key = None
            section_headers = {
                " Section 1: Key Insights": "key_insights",
                "Section 1: Key Insights": "key_insights",
                "Key Insights": "key_insights",
                
                " Section 2: Opportunity Spaces": "opportunity_spaces",
                "Section 2: Opportunity Spaces": "opportunity_spaces",
                "Opportunity Spaces": "opportunity_spaces",

                " Section 3: Risk & Resilience": "risk_and_resilience",
                "Section 3: Risk & Resilience": "risk_and_resilience",
                "Risk & Resilience": "risk_and_resilience",

                " Section 4: Innovation Pathways": "innovation_pathways",
                "Section 4: Innovation Pathways": "innovation_pathways",
                "Innovation Pathways": "innovation_pathways",

                "Section 5: Quick Wins vs Long-Term Strategies": "quick_wins_vs_long_term",
                "Section 5: Quick Wins vs Long-Term Strategies": "quick_wins_vs_long_term",
                "Quick Wins vs Long-Term Strategies": "quick_wins_vs_long_term"
            }

            buffer = []
            for line in response.split('\n'):
                stripped_line = line.strip()
                
                matched_header = False
                for header, key in section_headers.items():
                    if header in stripped_line: # Using "in" for flexibility with potential leading/trailing chars
                        if current_section_key and buffer: # Save previous section's buffer
                            parsed_data[current_section_key].extend([l.strip() for l in buffer if l.strip()])
                            buffer = []
                        current_section_key = key
                        # Remove the header itself from the line if it's the only content or starts the line
                        content_after_header = stripped_line.replace(header, "").strip()
                        if content_after_header:
                            buffer.append(content_after_header)
                        matched_header = True
                        break # Move to next line once header is processed
                
                if matched_header:
                    continue
               
                if current_section_key and stripped_line: # Add non-header lines to current section's buffer
                    buffer.append(stripped_line)
                elif current_section_key and not stripped_line and buffer: # Keep empty lines if they are part of a paragraph in buffer
                    buffer.append("") # Preserve paragraph breaks
            
            if current_section_key and buffer: # Save the last section's buffer
                parsed_data[current_section_key].extend([l.strip() for l in buffer if l.strip() or l == ""]) # Keep preserved empty lines if any
                # Clean up trailing empty strings if any from paragraph preservation
                while parsed_data[current_section_key] and parsed_data[current_section_key][-1] == "":
                    parsed_data[current_section_key].pop()
           
            parsed_data["token_usage"] = token_usage
            return self.format_output(parsed_data) # Pass the new parsed_data structure
           
        except Exception as e:
            logger.error(f"Error in ResearchSynthesisAgent: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "agent_type": self.__class__.__name__
            }


    def format_output(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format the output in a structured way based on the new 5-section parsing."""
        try:
            markdown_output = "\n\n"
            token_usage = parsed_data.get("token_usage", 0)
            
            section_titles_map = {
                "key_insights": " Key Insights",
                "opportunity_spaces": " Opportunity Spaces",
                "risk_and_resilience": " Risk & Resilience",
                "innovation_pathways": " Innovation Pathways",
                "quick_wins_vs_long_term": " Quick Wins vs Long-Term Strategies"
            }

            for section_key, display_title in section_titles_map.items():
                if parsed_data.get(section_key):
                    markdown_output += f"# **{display_title.strip()}**\n\n"
                    for item in parsed_data[section_key]:
                        # For numbered format, preserve the structure as-is
                        if item.strip():
                            markdown_output += f"{item}\n"
                markdown_output += "\n"
            
            if not any(parsed_data.get(key) for key in section_titles_map): # Fallback if all sections are empty
                markdown_output += "No structured insights were synthesized. Please review the raw LLM response if available."
                raw_response_text = parsed_data.get("raw_response_llm", "") # Assuming process might pass this for fallback
                if raw_response_text : markdown_output += "\n\nRaw LLM Output (if available): \n" + raw_response_text

            logger.info(f"Formatted Research Synthesis Output (markdown length: {len(markdown_output)})")
            
            return {
                "status": "success",
                "data": {
                    "structured_synthesis": parsed_data, # New key for the full structured data
                    "raw_sections": parsed_data, # For backward compatibility if anything used old raw_sections as the dict itself
                    "formatted_output": markdown_output,
                    "token_usage": token_usage
                    # "raw_response_llm": parsed_data.get("raw_response_llm") # If passed from process for fallback
                }
            }
        except Exception as e:
            logger.error(f"Error formatting Research Synthesis output: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "data": {
                    "formatted_output": f"# Research Synthesis\n\nError formatting output: {str(e)}",
                    "token_usage": parsed_data.get("token_usage", 0)
                    # "raw_response_llm": parsed_data.get("raw_response_llm")
                }
            }
