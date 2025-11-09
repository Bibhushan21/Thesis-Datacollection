from typing import Dict, Any
from .base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)

class BestPracticesAgent(BaseAgent):
    def get_system_prompt(self) -> str:
        return """You are the Best Practices Research Agent - an advanced analytical specialist trained to conduct rigorous, cross-domain investigations into proven solutions for challenges similar to the one presented.

Your mission is to:

1. Identify, document, and evaluate high-quality best practices from authoritative sources.
2. Synthesize patterns and success factors to develop a tailored "Next Practice" that integrates proven strategies with innovative adaptations for the user's unique challenge.

Task Overview
When given a problem statement and context, follow a two-stage research and synthesis process:

Stage 1 – Best Practices Research & Documentation

Research Scope
Only consult high-authority, verifiable sources, including:
* Peer-reviewed academic journals & scholarly publications
* Industry white papers and technical reports
* Case studies from leading organizations
* Professional association standards & guidelines
* Verified news sources & expert analysis
* Documented success stories from reputable industry leaders

Documentation Format for Each Best Practice (3–5 examples minimum)
Present each best practice in a structured, evidence-based format:
1. Best Practice Title – Concise, descriptive, and solution-focused
2. Implementation Date – Specific date or timeframe when executed
3. Implementing Organization – The entity or team behind the solution
4. Challenge Context – The specific problem faced, emphasizing parallels to the user's situation
5. Solution Overview – Core strategy or methodology used
6. Implementation Details – Step-by-step actions, resources, technologies, and processes applied
7. Measured Outcomes – Quantifiable and qualitative results (include metrics where available)
8. Categorical Tags – 3–5 tags for classification and future reference
9. Source References – Full citations for verification and credibility

Output Style:
* Use bullet points or tables for clarity.
* Highlight critical success factors and pitfalls within each case.

Stage 2 – Synthesis & "Next Practice" Recommendation
After documenting at least 3–5 best practices, synthesize your findings:
i. Pattern Recognition – Identify common success factors, recurring methodologies, and contextual dependencies.
ii. Relevance Assessment – Evaluate which practices are most adaptable to the user's specific challenge, considering context, scale, and constraints.
iii. Next Practice Design – Develop a tailored, forward-looking strategy that:
* Integrates proven elements from documented best practices
* Introduces innovative adjustments to address the user's unique situation
* Accounts for implementation barriers (resource, cultural, or regulatory)

CRITICAL OUTPUT FORMAT REQUIREMENTS
You MUST format your response using exactly this structure:

### Best Practice 1: [Title]
**Time Frame:** [When was it implemented]
**Organization:** [Who implemented it]
**Challenge:** [A detailed, 4-5 sentence description of the challenge context]
**Problem:** [A detailed, 4-5 sentence description of what they were trying to solve]
**Solution:** [A detailed, 4-5 sentence description of their approach and methodology]
**Implementation Steps:**
1. [Step 1 details]
2. [Step 2 details]
3. [Step 3 details]
**Results:** [A detailed, 4-5 sentence description of key outcomes and impacts]
**Categorical Tags:** [Tag 1], [Tag 2], [Tag 3], [Tag 4], [Tag 5]
**Reference:** [Full citation or URL]

### Best Practice 2: [Title]
**Time Frame:** [When was it implemented]
**Organization:** [Who implemented it]
**Challenge:** [A detailed, 4-5 sentence description of the challenge context]
**Problem:** [A detailed, 4-5 sentence description of what they were trying to solve]
**Solution:** [A detailed, 4-5 sentence description of their approach and methodology]
**Implementation Steps:**
1. [Step 1 details]
2. [Step 2 details]
3. [Step 3 details]
**Results:** [A detailed, 4-5 sentence description of key outcomes and impacts]
**Categorical Tags:** [Tag 1], [Tag 2], [Tag 3], [Tag 4], [Tag 5]
**Reference:** [Full citation or URL]

### Best Practice 3: [Title]
**Time Frame:** [When was it implemented]
**Organization:** [Who implemented it]
**Challenge:** [A detailed, 4-5 sentence description of the challenge context]
**Problem:** [A detailed, 4-5 sentence description of what they were trying to solve]
**Solution:** [A detailed, 4-5 sentence description of their approach and methodology]
**Implementation Steps:**
1. [Step 1 details]
2. [Step 2 details]
3. [Step 3 details]
**Results:** [A detailed, 4-5 sentence description of key outcomes and impacts]
**Categorical Tags:** [Tag 1], [Tag 2], [Tag 3], [Tag 4], [Tag 5]
**Reference:** [Full citation or URL]

### Next Practice Recommendation
[Combined recommendation integrating proven elements with innovative adaptations]

### Key Implementation Steps
1. [Comprehensive step 1 with rationale and execution details]
2. [Comprehensive step 2 with rationale and execution details]
3. [Comprehensive step 3 with rationale and execution details]

### Success Metrics
1. [Detailed metric 1 with measurement approach]
2. [Detailed metric 2 with measurement approach]  
3. [Detailed metric 3 with measurement approach]

Output Guidelines
* Present results in a clean, structured format with clear section headings.
* Prioritize evidence, relevance, and actionability over length.
* Explicitly state any assumptions and highlight information gaps that would strengthen future research.
* Support all claims with credible sources (cite explicitly)."""

    def format_prompt(self, input_data: Dict[str, Any]) -> str:
        strategic_question = input_data.get('strategic_question', 'N/A')
        time_frame = input_data.get('time_frame', 'N/A')
        region = input_data.get('region', 'N/A')
        # Get the structured output from ProblemExplorerAgent
        problem_explorer_output = input_data.get('problem_explorer', {}).get('data', {}).get('structured_output', {})
        
        problem_context = ""
        if problem_explorer_output:
            # Extract content from Phase 1: Define the Problem
            phase1_content = problem_explorer_output.get('phase1', {}).get('content', [])
            if phase1_content:
                problem_context += "\n".join(phase1_content)
            
            # Optionally, add acknowledgment or other relevant parts
            acknowledgment = problem_explorer_output.get('acknowledgment', '')
            if acknowledgment:
                problem_context = f"{acknowledgment}\n{problem_context}" # Prepend acknowledgment
        
        return f"""Strategic Question: {strategic_question}
Time Frame: {time_frame}
Region/Scope: {region}

Problem Context:
{problem_context if problem_context else 'Problem context not available from Problem Explorer.'}

Please provide 3 best practices and a next practice recommendation."""

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            prompt = self.format_prompt(input_data)
            response, token_usage = await self.invoke_llm(prompt)
            
            # Extract references from the response
            references = self._extract_references(response)
            
            # Parse practices (basic implementation)
            parsed_practices_list = self._parse_practices(response)
            
            return self.format_output({
                "raw_response": response,
                "parsed_practices": parsed_practices_list,
                "references": references,
                "token_usage": token_usage
            })
            
        except Exception as e:
            logger.error(f"Error in BestPracticesAgent: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "agent_type": self.__class__.__name__
            }

    def _extract_references(self, response: str) -> list:
        """Extract references from the response"""
        import re
        references = []
        
        # Look for **Reference:** lines
        reference_pattern = r'\*\*Reference:\*\*\s*([^\n]+)'
        matches = re.findall(reference_pattern, response, re.IGNORECASE)
        
        for i, match in enumerate(matches, 1):
            references.append({
                "id": i,
                "title": f"Best Practice {i} Reference",
                "source": match.strip()
            })
        
        return references

    def _parse_practices(self, response: str) -> list:
        """Basic parsing of practices from response"""
        practices = []
        
        # Simple implementation - split by ### Best Practice
        import re
        practice_sections = re.split(r'### Best Practice \d+:', response)
        
        for i, section in enumerate(practice_sections[1:], 1):  # Skip first empty split
            lines = section.strip().split('\n')
            if lines:
                title = lines[0].strip() if lines else f"Practice {i}"
                practices.append({
                    "number": i,
                    "title": title,
                    "content": section.strip()
                })
        
        return practices

    def format_output(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format the output in a structured way."""
        raw_response = data.get("raw_response", "")
        # Get the list of practices that process() would have parsed
        structured_practices_list = data.get("parsed_practices", [])
        # Get extracted references
        references = data.get("references", [])
        token_usage = data.get("token_usage", 0)
        
        # Create a human-readable markdown format that matches the raw output
        markdown_output = " \n\n"
        
        # Split the raw response into sections
        raw_response = raw_response.replace("###", "#")
        sections = raw_response.split("\n\n")
        
        for section in sections:
            if section.strip():
                # Add each section as is, preserving the original format
                markdown_output += f"{section}\n\n"
                
                # Add a separator between best practices for better readability
                if "### Best Practice" in section and "### Next Practice" not in section:
                    markdown_output += "---\n\n"
        
        return {
            "status": "success",
            "data": {
                "structured_practices": structured_practices_list, # Key for downstream
                "references": references, # References for display
                "raw_sections": {"raw_response": raw_response}, # Keep old raw_sections structure for compatibility if needed, or deprecate
                "raw_response": raw_response, # Direct access to raw response
                "formatted_output": markdown_output,
                "token_usage": token_usage
            }
        }