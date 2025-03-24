from typing import List, Dict, Any, Optional
import os
from openai import OpenAI
from datetime import datetime
import json
from dotenv import load_dotenv

class LLMGenerator:
    def __init__(self, api_key=None):
        # Load environment variables from .env file
        load_dotenv()
        
        # Use provided API key or get from environment
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key must be provided either as an argument or through OPENAI_API_KEY environment variable")
        
        # Initialize OpenAI client
        self.client = OpenAI(api_key=self.api_key)

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

    def extract_acceptance_criteria(self, content: str) -> List[str]:
        """Extract acceptance criteria from the generated content."""
        prompt = f"""Extract the acceptance criteria from the following ticket description. Return them as a list of strings, one per line.

Content:
{content}

Return only the list of acceptance criteria, one per line, without any additional text or formatting."""

        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a technical writer extracting acceptance criteria from ticket descriptions."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=200
        )
        
        criteria = response.choices[0].message.content.strip().split('\n')
        return [c.strip() for c in criteria if c.strip()]

    def extract_user_persona(self, content: str) -> str:
        """Extract the user persona from the generated content."""
        prompt = f"""Extract the user persona from the following ticket description. Return only the role of the user (e.g., "Developer", "Product Manager", "End User").

Content:
{content}

Return only the user role, without any additional text or formatting."""

        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a technical writer extracting user personas from ticket descriptions."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=50
        )
        
        return response.choices[0].message.content.strip()

    def extract_estimated_hours(self, content: str) -> float:
        """Extract the estimated hours from the generated content."""
        prompt = f"""Extract the estimated hours from the following ticket description. Return only the number of hours as a float.

Content:
{content}

Return only the number of hours, without any additional text or formatting."""

        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a technical writer extracting estimated hours from ticket descriptions."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=10
        )
        
        try:
            return float(response.choices[0].message.content.strip())
        except ValueError:
            return 4.0  # Default value if extraction fails

    def extract_technical_details(self, content: str) -> str:
        """Extract technical details from the generated content."""
        prompt = f"""Extract the technical details and implementation notes from the following ticket description.

Content:
{content}

Return only the technical details and implementation notes, without any additional text or formatting."""

        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a technical writer extracting technical details from ticket descriptions."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=200
        )
        
        return response.choices[0].message.content.strip() 