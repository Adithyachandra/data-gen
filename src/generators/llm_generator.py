from typing import List, Dict, Any, Optional, Tuple
import os
from openai import OpenAI
from datetime import datetime
import json
from dotenv import load_dotenv

class LLMGenerator:
    def __init__(self, api_key=None, config=None):
        # Load environment variables from .env file
        load_dotenv()
        
        # Use provided API key or get from environment
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key must be provided either as an argument or through OPENAI_API_KEY environment variable")
        
        # Initialize OpenAI client
        self.client = OpenAI(api_key=self.api_key)
        
        # Store config
        self.config = config or {}

    def generate_ticket_description(self, title: str, ticket_type: str, component: str, prompt: str = None) -> str:
        """Generate a realistic ticket description based on the title and type."""
        if prompt:
            system_prompt = "You are a technical writer creating detailed software development tickets."
            user_prompt = prompt
        else:
            system_prompt = "You are a technical writer creating detailed software development tickets."
            user_prompt = f"""Generate a detailed, realistic ticket description for a software development task with the following details:
            Title: {title}
            Type: {ticket_type}
            Component: {component}
            
            The description should include:
            1. Background/Context
            2. Current Behavior (if applicable)
            3. Required Changes/Implementation Details
            4. Acceptance Criteria
            
            Format the response in markdown."""

        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        return response.choices[0].message.content

    def generate_message_content(self, channel_name: str, context: Dict[str, Any]) -> str:
        """Generate realistic message content for team communications."""
        prompt = f"""Generate a realistic message for a {channel_name} channel in a software development team.
        Context:
        - Team: {context.get('team_name')}
        - Recent topics: {context.get('recent_topics', [])}
        - Message type: {context.get('message_type', 'general')}
        
        The message should sound natural and professional."""

        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a software development team member writing a message in a team chat."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=150
        )
        
        return response.choices[0].message.content

    def generate_meeting_notes(self, meeting_type: str, attendees: List[str], topics: List[str]) -> str:
        """Generate realistic meeting notes."""
        prompt = f"""Generate meeting notes for a {meeting_type} meeting with the following details:
        Attendees: {', '.join(attendees)}
        Topics: {', '.join(topics)}
        
        Include:
        1. Key Discussion Points
        2. Decisions Made
        3. Action Items
        4. Next Steps
        
        Format the response in markdown."""

        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a technical team member documenting meeting notes."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        return response.choices[0].message.content

    def generate_meeting_transcript(
        self,
        meeting_type: str,
        attendees: List[str],
        topics: List[str],
        duration_minutes: int
    ) -> str:
        """Generate a realistic meeting transcript."""
        prompt = f"""Generate a realistic transcript for a {meeting_type} meeting with the following details:
        Duration: {duration_minutes} minutes
        Attendees: {', '.join(attendees)}
        Topics: {', '.join(topics)}
        
        The transcript should:
        1. Show natural conversation flow
        2. Include technical discussions
        3. Show different speaking styles
        4. Include action items and decisions
        5. Be formatted as a conversation with timestamps
        
        Format the response in markdown."""

        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": """You are an AI transcribing a software development team meeting. Create realistic, natural dialogue that:
                    1. Uses technical terminology accurately
                    2. Shows realistic team dynamics and interactions
                    3. Includes specific technical details and code references
                    4. Demonstrates different personality types and communication styles
                    5. Captures the natural flow of a real meeting"""
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=2000  # Increased token limit for more detailed transcripts
        )
        
        return response.choices[0].message.content

    def generate_code_review_comment(self, code_snippet: str, context: str) -> str:
        """Generate a code review comment based on the code snippet and context."""
        prompt = f"""You are a senior software engineer reviewing code. Please provide a constructive code review comment for the following code snippet.
        
Context: {context}

Code:
```
{code_snippet}
```

Please provide a helpful and constructive review comment that:
1. Acknowledges what's good about the code
2. Suggests specific improvements
3. Maintains a positive and collaborative tone
"""

        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=200
        )
        
        return response.choices[0].message.content.strip()

    def generate_email_content(
        self,
        sender_name: str,
        recipient_names: List[str],
        subject: str,
        context: dict = None
    ) -> str:
        """Generate email content based on context and templates."""
        if context and context.get('ticket'):
            ticket = context['ticket']
            template = context.get('template', {})
            sprint = context.get('sprint')
            
            # Build email content based on template sections
            sections = []
            for section in template.get('content_sections', []):
                if section == "Status Change Summary":
                    sections.append(f"Status Change Summary:\n"
                                 f"The ticket {ticket.id} ({ticket.title}) has been updated to {ticket.status}.")
                
                elif section == "Current Progress":
                    sections.append(f"Current Progress:\n"
                                 f"- Implementation is {self._get_progress_percentage(ticket)}% complete\n"
                                 f"- Current focus: {ticket.current_focus if hasattr(ticket, 'current_focus') else 'Implementation'}\n"
                                 f"- Time spent: {ticket.time_spent if hasattr(ticket, 'time_spent') else 'Ongoing'}")
                
                elif section == "Implementation Overview":
                    sections.append(f"Implementation Overview:\n"
                                 f"I've completed the implementation for {ticket.title}. "
                                 f"The changes include:\n"
                                 f"- Core functionality implementation\n"
                                 f"- Unit tests with {ticket.test_coverage if hasattr(ticket, 'test_coverage') else '80%+'} coverage\n"
                                 f"- Documentation updates")
                
                elif section == "Blocker Description":
                    sections.append(f"Blocker Description:\n"
                                 f"The ticket is currently blocked due to: {ticket.blocking_reason if hasattr(ticket, 'blocking_reason') else 'technical dependencies'}.\n"
                                 f"Impact: This is affecting the sprint delivery timeline and needs immediate attention.")
            
            # Add sprint context if available
            if sprint:
                sections.append(f"\nSprint Context:\n"
                             f"Sprint: {sprint.name}\n"
                             f"Sprint Goal: {sprint.goal}\n"
                             f"Days Remaining: {(sprint.end_date - datetime.now()).days}")
            
            # Add call to action
            sections.append("\nNext Steps:\n"
                          "Please review and provide your feedback. "
                          "Let me know if you need any additional information.")
            
            return "\n\n".join(sections)
        
        else:
            # Generate generic email content
            return f"Dear {', '.join(recipient_names)},\n\n" + \
                   self._generate_generic_content(subject, context) + \
                   f"\n\nBest regards,\n{sender_name}"

    def generate_meeting_title(self, context: dict) -> str:
        """Generate a meeting title based on the context."""
        prompt = f"""Generate a concise and professional title for a {context['meeting_type']} meeting for the {context['team_name']} team.
        The meeting will last {context['duration_minutes']} minutes.
        
        Return only the title, no additional text."""
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=50
        )
        
        return response.choices[0].message.content.strip()

    def generate_meeting_description(
        self,
        meeting_type: str,
        organizer_name: str,
        attendee_names: List[str],
        context: dict = None
    ) -> str:
        """Generate meeting description based on context and templates."""
        if context and context.get('ticket'):
            ticket = context['ticket']
            template = context.get('template', {})
            sprint = context.get('sprint')
            is_adhoc = context.get('is_adhoc', False)
            
            # Build meeting description based on template
            sections = []
            
            # Meeting overview
            sections.append(f"Meeting Type: {meeting_type}\n"
                          f"Organizer: {organizer_name}\n"
                          f"Attendees: {', '.join(attendee_names)}\n"
                          f"Duration: {template.get('duration_minutes', 60)} minutes")
            
            # Add ticket context
            sections.append(f"\nTicket Context:\n"
                          f"ID: {ticket.id}\n"
                          f"Title: {ticket.summary}\n"
                          f"Status: {ticket.status}\n"
                          f"Priority: {ticket.priority}")
            
            # Add agenda based on meeting type
            if template and template.get('agenda_template'):
                sections.append("\nAgenda:")
                for item in template['agenda_template']:
                    sections.append(f"- {item}")
            
            # Add sprint context if available
            if sprint:
                sections.append(f"\nSprint Context:\n"
                             f"Sprint: {sprint.name}\n"
                             f"Sprint Goal: {sprint.goal}\n"
                             f"Days Remaining: {(sprint.end_date - datetime.now()).days}")
            
            # Add expected outcomes
            if is_adhoc:
                sections.append("\nExpected Outcomes:\n"
                              "1. Clear understanding of the current situation\n"
                              "2. Action plan with assigned owners\n"
                              "3. Timeline for resolution\n"
                              "4. Communication plan for stakeholders")
            
            return "\n".join(sections)
        
        else:
            # Generate generic meeting description
            return self._generate_generic_meeting_description(meeting_type, organizer_name, attendee_names)

    def _get_progress_percentage(self, ticket) -> int:
        """Estimate ticket progress based on status."""
        status_progress = {
            'TODO': 0,
            'IN_PROGRESS': 50,
            'IN_REVIEW': 80,
            'DONE': 100
        }
        return status_progress.get(str(ticket.status), 30)

    def _generate_generic_content(self, subject: str, context: dict = None) -> str:
        """Generate generic content when no specific template is available."""
        return f"I hope this email finds you well.\n\n" + \
               f"I wanted to touch base regarding {subject}.\n\n" + \
               f"Please let me know if you have any questions or need additional information."

    def _generate_generic_meeting_description(
        self,
        meeting_type: str,
        organizer_name: str,
        attendee_names: List[str]
    ) -> str:
        """Generate generic meeting description when no specific template is available."""
        return f"Meeting Type: {meeting_type}\n" + \
               f"Organizer: {organizer_name}\n" + \
               f"Attendees: {', '.join(attendee_names)}\n\n" + \
               f"Agenda:\n" + \
               f"1. Introduction and Updates\n" + \
               f"2. Discussion Points\n" + \
               f"3. Action Items and Next Steps"

    def generate_summary(self, description: str, ticket_type: str, component: str) -> str:
        """Generate a concise summary (less than 10 words) from a ticket description using GPT-4"""
        prompt = f"""Generate a concise summary (less than 10 words) for a {ticket_type} ticket in the {component} component.
        The summary should capture the essence of the following description:

        {description}

        Return ONLY the summary with no additional text, headers, or formatting. The summary must be less than 10 words."""
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a technical writer creating concise ticket summaries. Return ONLY the summary with no additional content."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=50
        )
        
        return response.choices[0].message.content.strip()

    def extract_acceptance_criteria(self, description: str) -> List[str]:
        """Extract acceptance criteria from a ticket description."""
        prompt = f"""Given the following ticket description, extract the acceptance criteria as a list of strings.
        If no explicit acceptance criteria are found, generate appropriate ones based on the description.
        
        Description:
        {description}
        
        Return the criteria as a JSON array of strings."""
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=200
        )
        
        try:
            return json.loads(response.choices[0].message.content)
        except json.JSONDecodeError:
            # Fallback to default criteria if parsing fails
            return [
                "Implementation matches requirements",
                "Code follows team standards",
                "Tests pass with adequate coverage",
                "Documentation is updated"
            ]

    def extract_user_persona(self, description: str) -> str:
        """Extract user persona information from a ticket description."""
        prompt = f"""Given the following ticket description, extract or generate a concise user persona description.
        The persona should be a brief description of the target user for this feature/story.
        
        Description:
        {description}
        
        Return only the user persona description as a single string, no additional text or JSON formatting."""
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=100
        )
        
        return response.choices[0].message.content.strip()

    def extract_estimated_hours(self, description: str) -> float:
        """Extract or estimate the number of hours needed for a task."""
        prompt = f"""Given the following task description, estimate the number of hours needed to complete it.
        Consider complexity, testing, and documentation time.
        
        Description:
        {description}
        
        Return only the number (decimal is fine), no additional text."""
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=10
        )
        
        try:
            return float(response.choices[0].message.content.strip())
        except ValueError:
            # Fallback to default estimate if parsing fails
            return 4.0

    def extract_technical_details(self, description: str) -> str:
        """Extract technical implementation details from a task description."""
        prompt = f"""Given the following task description, extract or generate a concise technical implementation plan.
        Include key technical considerations, potential challenges, and implementation approach.
        
        Description:
        {description}
        
        Return the technical details as a single string, focusing on implementation specifics."""
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=200
        )
        
        return response.choices[0].message.content.strip()

    def extract_steps_to_reproduce(self, description: str) -> List[str]:
        """Extract steps to reproduce from a bug description."""
        prompt = f"""Given the following bug description, extract the steps to reproduce the issue.
        If no explicit steps are found, generate realistic steps based on the description.
        
        Description:
        {description}
        
        Return the steps as a JSON array of strings."""
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=200
        )
        
        try:
            return json.loads(response.choices[0].message.content)
        except json.JSONDecodeError:
            # Fallback to default steps if parsing fails
            return [
                "Navigate to the feature",
                "Perform the action that triggers the issue",
                "Observe the unexpected behavior"
            ]

    def extract_expected_behavior(self, description: str) -> str:
        """Extract expected behavior from a bug description."""
        prompt = f"""Given the following bug description, extract or generate the expected behavior.
        If no explicit expected behavior is found, generate a realistic one based on the description.
        
        Description:
        {description}
        
        Return only the expected behavior as a single string, no additional text."""
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=100
        )
        
        return response.choices[0].message.content.strip()

    def extract_actual_behavior(self, description: str) -> str:
        """Extract actual behavior from a bug description."""
        prompt = f"""Given the following bug description, extract or generate the actual behavior.
        If no explicit actual behavior is found, generate a realistic one based on the description.
        
        Description:
        {description}
        
        Return only the actual behavior as a single string, no additional text."""
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=100
        )
        
        return response.choices[0].message.content.strip()

    def generate_story(self, component: str, parent_epic: str = None) -> Tuple[str, int]:
        """Generate a user story description using GPT-4"""
        company_name = self.config.get('company', {}).get('name', 'the company')
        industry = self.config.get('company', {}).get('industry', 'tech')
        
        prompt = f"""Generate a concise user story for a {component} component in the context of {company_name}, a {industry} company.
        The story should be part of the epic: {parent_epic}

        Return EXACTLY in this format with NO headers, NO additional content, and NO markdown formatting:

        As a [user type]
        I want to [action]
        So that [benefit]

        1. [First acceptance criterion]
        2. [Second acceptance criterion]
        3. [Third acceptance criterion]

        Do not include ANY other text, sections, or formatting. The output should be exactly as shown above, with real content replacing the bracketed placeholders.
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a product owner creating user stories. Return ONLY the exact format specified with no additional content, headers, or formatting."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=300
        )
        
        story_content = response.choices[0].message.content.strip()
        
        # Generate story points separately
        story_points_prompt = f"""Based on the following user story, determine appropriate story points (1, 2, 3, 5, 8, 13, or 21).
        Consider complexity, effort, and risk.
        
        Story:
        {story_content}
        
        Return ONLY the number, no additional text."""
        
        story_points_response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a product owner estimating story points. Return ONLY the number."},
                {"role": "user", "content": story_points_prompt}
            ],
            temperature=0.7,
            max_tokens=10
        )
        
        try:
            story_points = int(story_points_response.choices[0].message.content.strip())
            # Ensure story points is one of the standard values
            standard_points = [1, 2, 3, 5, 8, 13, 21]
            story_points = min(standard_points, key=lambda x: abs(x - story_points))
        except (ValueError, TypeError):
            story_points = 5  # Default to medium complexity
        
        return story_content, story_points

    def generate_task(self, component: str) -> Tuple[str, int]:
        """Generate a standalone task description using GPT-4"""
        company_name = self.config.get('company', {}).get('name', 'the company')
        industry = self.config.get('company', {}).get('industry', 'tech')
        
        prompt = f"""Generate a concise technical task description for a {component} component in the context of {company_name}, a {industry} company.

        Format the task exactly as follows:
        Task: [Brief task description]

        Technical Details:
        - [Key technical point 1]
        - [Key technical point 2]
        - [Key technical point 3]

        Keep the task description focused and technical.
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a technical lead creating development tasks. Keep tasks focused on technical implementation."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=300
        )
        
        task_content = response.choices[0].message.content.strip()
        
        # Generate story points separately
        story_points_prompt = f"""Based on the following technical task, determine appropriate story points (1, 2, 3, 5, 8, 13, or 21).
        Consider complexity, effort, and risk.
        
        Task:
        {task_content}
        
        Return ONLY the number, no additional text."""
        
        story_points_response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a technical lead estimating story points. Return ONLY the number."},
                {"role": "user", "content": story_points_prompt}
            ],
            temperature=0.7,
            max_tokens=10
        )
        
        try:
            story_points = int(story_points_response.choices[0].message.content.strip())
            # Ensure story points is one of the standard values
            standard_points = [1, 2, 3, 5, 8, 13, 21]
            story_points = min(standard_points, key=lambda x: abs(x - story_points))
        except (ValueError, TypeError):
            story_points = 3  # Default to small task
        
        return task_content, story_points

    def generate_subtask(self, task_description: str, task_id: str, parent_task: Dict[str, Any] = None) -> Tuple[str, int]:
        """Generate a subtask description and story points based on the parent task information."""
        company_name = self.config.get('company', {}).get('name', 'a tech company')
        industry = self.config.get('company', {}).get('industry', 'technology')
        
        # Get component from parent task
        component = parent_task.get('components', ['Backend'])[0] if parent_task else 'Backend'
        
        # Build context from parent task
        parent_context = ""
        if parent_task:
            parent_context = f"""
            Parent Task Context:
            - Summary: {parent_task.get('summary', 'Not provided')}
            - Description: {parent_task.get('description', 'Not provided')}
            - Technical Details: {parent_task.get('technical_details', 'Not provided')}
            - Components: {', '.join(parent_task.get('components', []))}
            - Story Points: {parent_task.get('story_points', 'Not provided')}
            """
        
        prompt = f"""You are a technical lead at {company_name} in the {industry} industry.
        Create a detailed technical subtask that contributes to the following task:
        
        Task Description: {task_description}
        
        {parent_context}
        
        The subtask should:
        1. Focus on a specific, well-defined portion of the parent task
        2. Include detailed technical implementation steps
        3. Specify exact testing requirements and acceptance criteria
        4. List specific dependencies on other components or services
        5. Include security considerations if relevant
        6. Define code review requirements and quality standards
        7. Be self-contained and independently implementable
        
        Format the response as a markdown document with the following sections:
        ## Technical Implementation
        [Detailed implementation steps]
        
        ## Testing Requirements
        [Specific test cases and acceptance criteria]
        
        ## Dependencies
        [List of specific dependencies]
        
        ## Security Considerations
        [Security-related requirements if applicable]
        
        ## Review Requirements
        [Code review and quality standards]
        
        Do not include time estimates in the description.
        """
        
        subtask_description = self.generate_ticket_description(
            title=f"Subtask for {task_id}",
            ticket_type="Subtask",
            component=component,
            prompt=prompt
        )
        
        # Generate story points for the subtask
        story_points_prompt = f"""Based on the following subtask description and its parent task context, estimate the story points (1, 2, 3, 5, 8, 13, or 21).
        Consider:
        1. The complexity of the specific implementation
        2. The effort required for testing and documentation
        3. The risk level of the changes
        4. The relationship to the parent task's story points
        
        Parent Task Story Points: {parent_task.get('story_points', 'Not provided') if parent_task else 'Not provided'}
        
        Subtask Description:
        {subtask_description}
        
        Respond with ONLY the number."""
        
        story_points_str = self.generate_ticket_description(
            title="Story Points Estimation",
            ticket_type="Subtask",
            component=component,
            prompt=story_points_prompt
        ).strip()
        
        try:
            story_points = int(story_points_str)
            if story_points not in [1, 2, 3, 5, 8, 13, 21]:
                story_points = 3  # Default to 3 if not a valid value
        except ValueError:
            story_points = 3  # Default to 3 if conversion fails
        
        return subtask_description, story_points 