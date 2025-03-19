from typing import List, Dict, Any, Optional
import openai
from datetime import datetime
import os
import json

class LLMGenerator:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the LLM generator with OpenAI API key."""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key must be provided or set in OPENAI_API_KEY environment variable")
        openai.api_key = self.api_key

    def generate_ticket_description(self, title: str, ticket_type: str, component: str) -> str:
        """Generate a realistic ticket description based on the title and type."""
        prompt = f"""Generate a detailed, realistic ticket description for a software development task with the following details:
        Title: {title}
        Type: {ticket_type}
        Component: {component}
        
        The description should include:
        1. Background/Context
        2. Current Behavior (if applicable)
        3. Required Changes/Implementation Details
        4. Acceptance Criteria
        
        Format the response in markdown."""

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a technical writer creating detailed software development tickets."},
                {"role": "user", "content": prompt}
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

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
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

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a technical team member documenting meeting notes."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        return response.choices[0].message.content

    def generate_code_review_comment(self, code_snippet: str, context: str) -> str:
        """Generate realistic code review comments."""
        prompt = f"""Generate a constructive code review comment for the following code snippet:
        ```
        {code_snippet}
        ```
        Context: {context}
        
        The comment should be:
        1. Constructive and professional
        2. Specific to the code
        3. Include both positive feedback and improvement suggestions where applicable"""

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an experienced software developer reviewing code."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=200
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
        # Calculate number of segments based on duration
        num_segments = max(3, duration_minutes // 5)  # One segment every 5 minutes
        
        meeting_structure = {
            "Daily Standup": {
                "phases": ["Updates from each team member", "Blockers discussion", "Quick follow-ups"],
                "dynamics": ["Quick round-robin updates", "Brief blocker resolution", "Next-day planning"]
            },
            "Sprint Planning": {
                "phases": ["Sprint Goal Discussion", "Capacity Planning", "Backlog Review", "Story Point Estimation", "Sprint Commitment"],
                "dynamics": ["Goal clarification", "Detailed story discussions", "Technical feasibility debates", "Team commitment"]
            },
            "Sprint Review": {
                "phases": ["Sprint Goal Recap", "Demo Preparations", "Feature Demonstrations", "Feedback Collection", "Next Sprint Preview"],
                "dynamics": ["Demo presentations", "Stakeholder questions", "Technical explanations", "Future planning"]
            },
            "Sprint Retrospective": {
                "phases": ["Previous Action Items Review", "What Went Well", "What Needs Improvement", "Action Items Creation"],
                "dynamics": ["Open sharing", "Constructive criticism", "Solution brainstorming", "Commitment to change"]
            },
            "Technical Discussion": {
                "phases": ["Problem Statement", "Current Architecture Review", "Proposed Solutions", "Trade-offs Discussion", "Decision Making"],
                "dynamics": ["Technical deep-dives", "Architecture discussions", "Code review insights", "Best practices debate"]
            }
        }

        structure = meeting_structure.get(meeting_type, {
            "phases": ["Introduction", "Main Discussion", "Action Items"],
            "dynamics": ["General discussion", "Decision making", "Next steps"]
        })

        prompt = f"""Generate a detailed, realistic transcript for a {meeting_type} meeting with the following details:
        Duration: {duration_minutes} minutes
        Attendees: {', '.join(attendees)}
        Topics: {', '.join(topics)}
        
        Meeting Structure:
        - Phases: {', '.join(structure['phases'])}
        - Expected Dynamics: {', '.join(structure['dynamics'])}
        
        The transcript should include:
        1. Realistic meeting flow with:
           - Natural opening and closing segments
           - Transitions between topics
           - Side discussions and clarifications
           - Technical terminology appropriate for a software team
        
        2. Participant interactions showing:
           - Different communication styles
           - Technical discussions and debates
           - Question-answer exchanges
           - Agreement and disagreement patterns
           - Decision-making processes
        
        3. Time-based progression:
           - Regular timestamps (every 1 minute)
           - Realistic pacing of discussions
           - Time management indicators
           - Natural breaks and transitions
        
        4. Meeting-specific elements:
           - Role-appropriate contributions
           - Technical details and explanations
           - Action item assignments
           - Follow-up scheduling
        
        5. Realistic dialogue features:
           - Interruptions and overlapping discussions
           - Clarifying questions
           - Technical term explanations
           - References to code, systems, or documentation
           - Links to relevant resources or tickets
        
        Format the transcript in markdown with:
        - Clear timestamps
        - Speaker names in bold
        - Code snippets in code blocks
        - Important decisions or action items highlighted
        - Links to referenced materials"""

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
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