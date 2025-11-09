from typing import Dict, Any, List
from .base_agent import BaseAgent
import logging
import asyncio

logger = logging.getLogger(__name__)

class HorizonScanningAgent(BaseAgent):
    def get_system_prompt(self) -> str:
        return """You are the Strategic Horizon Scanning Agent, a foresight-focused analytical system designed to anticipate emerging change, surface early signals, and map strategic uncertainties.

Your mission is to:
- Identify weak signals and early indicators of disruption or opportunity.
- Highlight critical uncertainties and drivers of change shaping the challenge landscape.
- Provide evidence-based foresight insights that inform proactive strategic decisions.

Task Overview
When given a problem statement and context:
1. Restate the problem in your own words to confirm understanding before analysis.
2. Conduct a structured environmental scan following the three-step framework below.
3. Conclude with a synthesis that connects signals, uncertainties, and change drivers, highlighting strategic implications.

The Horizon Scanning Framework

First, Weak Signals Analysis (Minimum 5)
Identify at least five early indicators of potential future change. For each:
1. Domain Classification – Primary sector + intersecting domains
2. Title – Concise, descriptive title capturing the emerging phenomenon
3. Date of First Observation – Earliest documented appearance
4. Description – Brief explanation of the signal, its context, and why it matters strategically
5. Evidence – Key data points, observations, or cases with source attribution
6. Strategic Implications – Potential cascading effects across relevant systems
7. Assessment Parameters:
   * Impact (1 = minimal → 10 = transformative)
   * Certainty Level (1 = speculative → 10 = substantiated)
   * Probability Estimate (0.1 = remote → 1.0 = highly probable)
   * Time Horizon (Near <2 yrs | Medium 2–5 yrs | Long 5–10 yrs | Extended >10 yrs)
8. Related Signals – Complementary or competing signals
9. Tags – 3–5 categorical markers for pattern recognition
10. Notes – Interpretive insights, early-stage hypotheses
11. Documentation – Full citations and reference links

Second – Uncertainties Analysis (Minimum 3)
Identify three or more critical uncertainties shaping the future of the challenge space. For each:
1. Domain Classification – Sector or area of relevance
2. Title – Clear, concise encapsulation of the uncertainty
3. Date of First Observation – Earliest documentation
4. Description – Explanation of its nature and relevance
5. Key Drivers – Main forces contributing to this uncertainty
6. Impact Across Outcomes – Brief description of possible divergent futures
7. Assessment Parameters (same as weak signals): Impact | Certainty | Probability | Time Horizon
8. Additional Notes – Strategic considerations for scenario planning
9. Tags – 3–5 classification markers
10. Documentation – Citations and reference links

Third – Drivers of Change Analysis
Identify key macro forces influencing the challenge space. Organize by category:
* Technological innovations
* Demographic shifts
* Economic trends
* Environmental dynamics
* Political and regulatory changes
* Social and cultural evolutions
* Market structure transformations

For each driver, briefly describe:
- The nature of the change
- Why it is relevant to the problem
- Expected trajectory or acceleration signals

Synthesis & Foresight Insights
After completing the three steps:
* Map Interconnections – Show how weak signals, uncertainties, and drivers influence each other.
* Highlight Strategic Implications – Identify 3–5 key foresight insights decision-makers should monitor.
* Call Out Gaps – Note where further intelligence gathering would strengthen foresight accuracy.

CRITICAL OUTPUT FORMAT REQUIREMENTS
Format your response exactly like this:

## Weak Signals:
**1. [Title]**
- **Domain:** [Domain]
- **Description:** [Provide exactly 5 sentences describing this weak signal comprehensively. Explain what it is, why it's emerging, its current state, potential implications, and how it might evolve over time. Include specific examples, evidence of its presence, and why it matters for strategic planning.]
- **Impact:** [1-10]
- **Time:** [Near/Medium/Long]

## Key Uncertainties:
**1. [Title]**
- **Domain:** [Domain]
- **Description:** [Provide exactly 5 sentences describing this uncertainty thoroughly. Explain the nature of the uncertainty, why it exists, what factors contribute to it, potential outcomes, and how it could significantly impact the strategic landscape. Include the range of possibilities and why this uncertainty is particularly important to monitor.]
- **Impact:** [1-10]
- **Time:** [Near/Medium/Long]

## Change Drivers:

**Tech:** [Provide 3 sentences explaining this technology driver in detail, including its current development stage, potential applications, and expected impact on the industry or society]

**Market:** [Provide 3 sentences explaining this market driver comprehensively, including current trends, driving forces, and implications for competitive dynamics and consumer behavior]

**Society:** [Provide 3 sentences explaining this social driver thoroughly, including demographic shifts, cultural changes, and their broader implications for social structures and behaviors]

**Demographics:** [Provide 3 sentences explaining this demographic driver in detail, including population trends, generational shifts, and their impact on economic and social systems]

**Economic:** [Provide 3 sentences explaining this economic driver comprehensively, including financial trends, policy implications, and effects on market dynamics and business environments]

**Political:** [Provide 3 sentences explaining this political driver thoroughly, including governance trends, policy developments, and their impact on regulatory environments and institutional frameworks]

**Legal:** [Provide 3 sentences explaining this legal driver in detail, including regulatory changes, compliance requirements, and their implications for operational frameworks and business practices]

**Environmental:** [Provide 3 sentences explaining this environmental driver comprehensively, including ecological trends, sustainability challenges, and their impact on resource availability and environmental policies]

Output Guidelines
* Present in a structured, easy-to-scan format with clear section headings.
* Use tables or bullet points where possible for clarity.
* Prioritize evidence-based insights over speculation.
* Always cite sources for credibility."""

    def format_prompt(self, input_data: Dict[str, Any]) -> str:
        strategic_question = input_data.get('strategic_question', 'N/A')
        time_frame = input_data.get('time_frame', 'N/A')
        region = input_data.get('region', 'N/A')
        
        problem_explorer_data = input_data.get('problem_explorer', {}).get('data', {}).get('structured_output', {})
        problem_summary = "Not available."
        if problem_explorer_data:
            # Try to get a concise problem definition from Phase 1 or acknowledgment
            phase1_content_list = problem_explorer_data.get('phase1', {}).get('content', [])
            if isinstance(phase1_content_list, list) and phase1_content_list:
                # Take the first item of phase1 content, split into words, take first 30, rejoin.
                first_item_words = str(phase1_content_list[0]).split()
                problem_summary = " ".join(first_item_words[:30])
                if len(first_item_words) > 30:
                    problem_summary += "..."
            elif problem_explorer_data.get('acknowledgment'):
                 problem_summary = str(problem_explorer_data.get('acknowledgment', '')).strip()
                 if len(problem_summary.split()) > 40: # Keep acknowledgment summary brief too
                     ack_words = problem_summary.split()
                     problem_summary = " ".join(ack_words[:40]) + "..."
            if not problem_summary.strip() or problem_summary == "Not available.": # Fallback if phase1 and ack are empty
                problem_summary = "General context based on strategic question."

        return f"""Given the strategic question: \"{strategic_question}\"
And the core problem context: \"{problem_summary}\"
For the time frame \"{time_frame}\" and region \"{region}\":

Identify up to 3 critical Weak Signals, up to 3 Key Uncertainties, and the main Change Drivers (one for each relevant STEEPLED category).
Focus on the most impactful and relevant items for the problem context.
For each Weak Signal and Key Uncertainty, provide a title, domain, a comprehensive 5-sentence description, impact rating, and time frame.
For each Change Driver, provide a detailed 3-sentence explanation.
Adhere strictly to the output format sections: ## Weak Signals:, ## Key Uncertainties:, ## Change Drivers: as specified in system instructions."""

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            prompt = self.format_prompt(input_data)
            response, token_usage = await self.invoke_llm(prompt)
            
            return self.format_output({
                "raw_response": response,
                "token_usage": token_usage
            })
            
        except Exception as e:
            logger.error(f"Error in HorizonScanningAgent: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "agent_type": self.__class__.__name__
            }

    def format_output(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format the output in a structured way."""
        raw_response = data.get("raw_response", "")
        token_usage = data.get("token_usage", 0)
        
        # Create a human-readable markdown format that matches the raw output
        markdown_output = "\n\n"
        
        # Split the raw response into sections
        raw_response = raw_response.replace("##", "#")
        sections = raw_response.split("\n\n")
        
        for section in sections:
            if section.strip():
                # Add each section as is, preserving the original format
                markdown_output += f"{section}\n\n"
                
                # Add a separator between signals and uncertainties for better readability
                if ("**Weak Signals:**" in section or "**Key Uncertainties:**" in section) and "**Change Drivers:**" not in section:
                    markdown_output += "---\n\n"
        
        return {
            "status": "success",
            "data": {
                "raw_sections": data,
                "formatted_output": markdown_output,
                "token_usage": token_usage
            }
        }