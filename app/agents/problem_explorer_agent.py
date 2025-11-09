from typing import Dict, Any
from .base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)

class ProblemExplorerAgent(BaseAgent):
    def get_system_prompt(self) -> str:
        return """Role & Objective
You are the Problem Explorer Agent - a strategic analysis specialist trained to deconstruct complex challenges and establish a solid foundation for effective, context-aware solutions.
Your mission is to thoroughly understand the problem before suggesting any solutions, ensuring that the insights are evidence-based, logically structured, and strategically actionable.

Task Instructions
You will conduct a comprehensive five-section investigative analysis of the problem statement provided by the user.
Follow the sections sequentially, grounding each answer in specific, actionable insights rather than generic observations.
At the start, acknowledge the problem statement in your own words to confirm your understanding before proceeding.

The Problem Explorer's Checklist © - A Framework for Comprehensive Problem Analysis

**SECTION 1: DEFINING THE PROBLEM**
1. **What is the precise core challenge we are addressing?**
2. **Why is solving this issue strategically important to key stakeholders?**
3. **Who are the primary and secondary stakeholders, and how are they impacted?**
4. **What boundaries or exclusions must we set (what is NOT part of this problem)?**
5. **What is the current state or context regarding this challenge?**

**SECTION 2: BREAKING DOWN THE PROBLEM**
1. **What are the key components of this issue?**
2. **How do these components interconnect or influence one another?**
3. **What alternative perspectives could reveal hidden aspects or blind spots?**
4. **What root causes drive the visible symptoms?**
5. **Are there analogous problems or historical precedents that provide insights?**

**SECTION 3: INFORMATION ASSESSMENT AND GATHERING**
1. **What reliable data or intelligence do we already have?**
2. **What are the critical information gaps limiting our understanding?**
3. **What specific additional data would meaningfully improve our analysis?**
4. **What aspects remain uncertain or ambiguous?**
5. **What methods or sources should we use to gather the missing intelligence?**

**SECTION 4: SOLUTION EXPLORATION AND INNOVATION**
1. **Should we aim for a comprehensive solution or incremental fixes?**
2. **What diverse pathways or approaches deserve exploration?**
3. **How have similar challenges been solved elsewhere successfully?**
4. **What would an innovative, ideal solution look like if constraints were removed?**
5. **What tangible, measurable outcomes would define success?**

**SECTION 5: IMPLEMENTING THE SOLUTION**
1. **What are the critical steps in the implementation roadmap?**
2. **Which stakeholders must be engaged or aligned for success?**
3. **What is a realistic timeline for effective execution?**
4. **What resources (financial, human, technological) will be required?**
5. **How will we define and measure success (specific metrics)?**

CRITICAL OUTPUT FORMAT REQUIREMENTS
You MUST format your response using exactly this structure:

**Step 1:** [Acknowledge the problem statement in your own words to confirm understanding]

**SECTION 1: DEFINING THE PROBLEM**
- **What is the core problem?**: [Answer]
- **Why is addressing this problem important?**: [Answer]
- **Who are the key stakeholders for this problem?**: [Answer]
- **What is not the problem**: [Answer]
- **What is the current situation related to the problem?**: [Answer]

**SECTION 2: BREAKING DOWN THE PROBLEM**
- **What are the different parts of the problem?**: [Answer]
- **What are the relationships between different parts of the problem?**: [Answer]
- **In what ways can you reframe the problem?**: [Answer]
- **What are the underlying causes of this problem?**: [Answer]
- **Have you come across similar problems that could be considered to solve the problem?**: [Answer]

**SECTION 3: INFORMATION ASSESSMENT AND GATHERING**
- **What information do you have on the problem?**: [Answer]
- **Is the information sufficient to solve the problem?**: [Answer]
- **What further information do you require to solve the problem?**: [Answer]
- **What are you not yet understanding about the problem?**: [Answer]
- **How do you plan to gather more information to address gaps in information/understanding of the problem?**: [Answer]

**SECTION 4: SOLUTION EXPLORATION AND INNOVATION**
- **Can you solve the whole problem or part of the problem?**: [Answer]
- **Can you list out the different ways in which you can solve the problem?**: [Answer]
- **How have others solved the problem or similar problems?**: [Answer]
- **Can you describe what the final solution may look like and what innovation you could introduce?**: [Answer]
- **What may be the result of solving the problem?**: [Answer]

**SECTION 5: IMPLEMENTING THE SOLUTION**
- **What are key actions need to be taken to implement the solution?**: [Answer]
- **Who must be involved in the implementation of the solution?**: [Answer]
- **What is the timeline for implementation?**: [Answer]
- **What resources are required to implement the solution?**: [Answer]
- **What will success look like, and how will you measure it?**: [Answer]

**Key Takeaways**
- [Takeaway 1]
- [Takeaway 2]
- [Takeaway 3]
- [Takeaway 4]
- [Takeaway 5]

Output Guidelines
* Present your analysis in a clean, structured format with clear headings for each section.
* Highlight critical insights and blind spots (bold or bullet key points).
* Show connections between different sections (e.g., how root causes influence implementation challenges).
* Conclude with 3–5 key takeaways to guide final solution development.
* Be concise but deep - prioritize insight over length.
* For each question, provide a detailed answer that is 4-5 sentences long.
"""

    def format_prompt(self, input_data: Dict[str, Any]) -> str:
        strategic_question = input_data.get('strategic_question', 'N/A')
        time_frame = input_data.get('time_frame', 'N/A')
        region = input_data.get('region', 'N/A')
        prompt = input_data.get('prompt', '')
        
        return f"""Strategic Question: {strategic_question}
Time Frame: {time_frame}
Region/Scope: {region}
Additional Context: {prompt if prompt else 'None provided'}

Please analyze this strategic challenge using The Problem Explorer's Checklist © framework."""

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            prompt = self.format_prompt(input_data)
            response, token_usage = await self.invoke_llm(prompt)
            
            # Parse the response into structured format
            sections = {
                'acknowledgment': '',
                'section1': {'title': 'Defining the Problem', 'content': []},
                'section2': {'title': 'Breaking Down the Problem', 'content': []},
                'section3': {'title': 'Information Assessment and Gathering', 'content': []},
                'section4': {'title': 'Solution Exploration and Innovation', 'content': []},
                'section5': {'title': 'Implementing the Solution', 'content': []},
                'takeaways': []
            }
            
            current_section = None
            lines = response.split('\n')
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Check for acknowledgment
                if line.startswith('Step 1:') or line.startswith('I understand'):
                    sections['acknowledgment'] = line
                    continue
                
                # Check for section headers
                if 'SECTION 1:' in line or 'DEFINING THE PROBLEM' in line:
                    current_section = 'section1'
                    continue
                elif 'SECTION 2:' in line or 'BREAKING DOWN THE PROBLEM' in line:
                    current_section = 'section2'
                    continue
                elif 'SECTION 3:' in line or 'INFORMATION ASSESSMENT' in line:
                    current_section = 'section3'
                    continue
                elif 'SECTION 4:' in line or 'SOLUTION EXPLORATION' in line:
                    current_section = 'section4'
                    continue
                elif 'SECTION 5:' in line or 'IMPLEMENTING THE SOLUTION' in line:
                    current_section = 'section5'
                    continue
                elif 'Key Takeaways' in line:
                    current_section = 'takeaways'
                    continue
                
                # Add content to current section
                if current_section and current_section != 'acknowledgment':
                    if current_section == 'takeaways':
                        if line.startswith('-') or line.startswith('•'):
                            sections[current_section].append(line.lstrip('- ').lstrip('• '))
                    else:
                        # Only add bullet point if the line doesn't already have one
                        if line.startswith('-') or line.startswith('•'):
                            sections[current_section]['content'].append(line)
                        else:
                            sections[current_section]['content'].append(f"- {line}")
            
            return self.format_output({
                "raw_response": response,
                "structured_data": sections,
                "token_usage": token_usage
            })
            
        except Exception as e:
            logger.error(f"Error in ProblemExplorerAgent: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "agent_type": self.__class__.__name__
            }

    def format_output(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format the output in a structured way."""
        structured_data_from_process = data.get("structured_data", {})
        raw_response_from_process = data.get("raw_response", "")
        token_usage = data.get("token_usage", 0)
        
        # Create a human-readable markdown format
        markdown_output = "\n\n"
        
        # Add acknowledgment
        if structured_data_from_process.get('acknowledgment'):
            markdown_output += f"## Understanding\n{structured_data_from_process['acknowledgment']}\n\n"
        
        # Add each section
        for section in ['section1', 'section2', 'section3', 'section4', 'section5']:
            if section in structured_data_from_process:
                section_data = structured_data_from_process[section]
                markdown_output += f"# {section_data['title']}\n\n"
                for item in section_data['content']:
                    # Don't add bullet point if item already has one
                    if item.startswith('-') or item.startswith('•'):
                        markdown_output += f"{item}\n"
                    else:
                        markdown_output += f"- {item}\n"
                markdown_output += "\n"
        
        # Add takeaways
        if structured_data_from_process.get('takeaways'):
            markdown_output += "# Key Takeaways\n\n"
            for takeaway in structured_data_from_process['takeaways']:
                markdown_output += f"- {takeaway}\n"
        
        return {
            "status": "success",
            "data": {
                "structured_output": structured_data_from_process,
                "raw_response": raw_response_from_process,
                "formatted_output": markdown_output,
                "token_usage": token_usage
            }
        } 