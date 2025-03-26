from datetime import datetime, timedelta
import json
from pathlib import Path
import random
from typing import Dict, List

from src.config.sample_company import INNOVATECH_CONFIG
from src.generators.team_generator import TeamGenerator
from src.generators.ticket_generator import TicketGenerator
from src.generators.communication_generator import CommunicationGenerator
from src.generators.activity_generator import ActivityGenerator
from src.models.team import TeamMember, Team
from src.models.ticket import Ticket, Sprint, Component
from src.models.communication import Message, Channel, Meeting
from src.models.activity import Activity

class CompanyDataGenerator:
    def __init__(self, config: dict):
        self.config = config
        self.output_dir = Path("generated_data")
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize generators with company config
        self.team_generator = TeamGenerator(config)
        self.team_members = {}
        self.teams = {}
        
        self.ticket_generator = None
        self.communication_generator = None
        self.activity_generator = None
        
        # Storage for generated data
        self.tickets: Dict[str, Ticket] = {}
        self.sprints: Dict[str, Sprint] = {}
        self.channels: Dict[str, Channel] = {}
        self.messages: Dict[str, Message] = {}
        self.meetings: Dict[str, Meeting] = {}
        self.activities: Dict[str, Activity] = {}

    def generate_organization_structure(self):
        """Generate the organizational structure including teams and members."""
        print("Generating organizational structure...")
        
        # Generate teams and members
        self.business_units = self.team_generator.generate_organization()
        self.team_members = self.team_generator.get_all_members()
        self.teams = self.team_generator.get_all_teams()
        
        # Initialize other generators with team data
        self.ticket_generator = TicketGenerator(self.team_members, self.teams)
        self.communication_generator = CommunicationGenerator(self.team_members, self.teams)
        self.activity_generator = ActivityGenerator(self.team_members, self.teams)

    def generate_team_tickets_and_sprints(self, team: Team, num_sprints: int = 3):
        """Generate tickets and sprints for a team."""
        print(f"Generating tickets and sprints for team {team.name}...")
        
        # Generate sprints
        team_sprints = []
        sprint_start = datetime.now() - timedelta(days=90)  # Start from 90 days ago
        
        for i in range(num_sprints):
            sprint = self.ticket_generator.generate_sprint(
                team.id,  # Pass team ID instead of team object
                start_date=sprint_start + timedelta(days=i * 14)
            )
            team_sprints.append(sprint)
            self.sprints[sprint.id] = sprint
            
            # Generate sprint activities
            activities = self.activity_generator.generate_sprint_activities(
                sprint, team, sprint.start_date
            )
            for activity in activities:
                self.activities[activity.id] = activity
        
        # Generate tickets for each sprint
        for sprint in team_sprints:
            # Convert component string to enum value
            component_str = team.components[0]
            component = Component[component_str.upper()]  # Convert string to enum value
            
            sprint_tickets = self.ticket_generator.generate_sprint_tickets(
                sprint,
                component
            )
            
            # Store tickets
            for ticket_type, tickets in sprint_tickets.items():
                for ticket in tickets:
                    self.tickets[ticket.id] = ticket
                    
                    # Generate ticket activities
                    assignee = self.team_members[ticket.assignee_id]
                    activities = self.activity_generator.generate_ticket_activities(
                        ticket, assignee, ticket.created_at
                    )
                    for activity in activities:
                        self.activities[activity.id] = activity
                    
                    # Generate communication around ticket
                    comms = self.communication_generator.generate_ticket_communication(ticket)
                    for message in comms["messages"]:
                        self.messages[message.id] = message
                        # Generate communication activities
                        activities = self.activity_generator.generate_communication_activities(
                            message, message.created_at
                        )
                        for activity in activities:
                            self.activities[activity.id] = activity

    def generate_team_communication(self, team: Team):
        """Generate communication channels and patterns for a team."""
        print(f"Generating communication for team {team.name}...")
        
        # Generate channels
        team_channels = self.communication_generator.generate_channels_for_team(team)
        for channel in team_channels:
            self.channels[channel.id] = channel
            
            # Generate some general discussion threads
            num_threads = len(team.members) // 2  # Roughly half as many threads as members
            for _ in range(num_threads):
                thread = self.communication_generator.generate_thread(channel)
                
                # Generate some messages in the thread
                num_messages = random.randint(3, 8)
                participants = random.sample(channel.members, min(num_messages, len(channel.members)))
                for participant in participants:
                    message = self.communication_generator.generate_message(
                        self.team_members[participant],
                        thread
                    )
                    self.messages[message.id] = message
                    
                    # Generate message activities
                    activities = self.activity_generator.generate_communication_activities(
                        message, message.created_at
                    )
                    for activity in activities:
                        self.activities[activity.id] = activity
        
        # Generate team meetings
        num_meetings = random.randint(3, 6)  # Some regular team meetings
        for _ in range(num_meetings):
            meeting = self.communication_generator.generate_meeting(
                team,
                random.choice([
                    MeetingType.TEAM_SYNC,
                    MeetingType.TECHNICAL_DISCUSSION
                ])
            )
            self.meetings[meeting.id] = meeting
            
            # Generate meeting activities
            activities = self.activity_generator.generate_meeting_activities(
                meeting, meeting.start_time
            )
            for activity in activities:
                self.activities[activity.id] = activity

    def save_generated_data(self):
        """Save all generated data to JSON files."""
        print("Saving generated data...")
        
        # Helper function to convert objects to dict
        def to_dict(obj):
            if hasattr(obj, "dict"):
                return obj.dict()
            return obj
        
        # Save each data type to separate files
        data_mapping = {
            "teams": self.teams,
            "team_members": self.team_members,
            "tickets": self.tickets,
            "sprints": self.sprints,
            "channels": self.channels,
            "messages": self.messages,
            "meetings": self.meetings,
            "activities": self.activities
        }
        
        for name, data in data_mapping.items():
            output_file = self.output_dir / f"{name}.json"
            with open(output_file, "w") as f:
                json.dump(
                    {k: to_dict(v) for k, v in data.items()},
                    f,
                    indent=2,
                    default=str  # Handle datetime objects
                )

    def generate_all(self):
        """Generate all company data."""
        print("Starting data generation for", self.config.name)
        
        # Generate organizational structure
        self.generate_organization_structure()
        
        # Generate data for each team
        for team in self.teams.values():
            self.generate_team_tickets_and_sprints(team)
            self.generate_team_communication(team)
        
        # Save all generated data
        self.save_generated_data()
        
        print("Data generation complete!")
        print(f"Generated data saved to {self.output_dir}")
        
        # Print summary statistics
        print("\nGeneration Summary:")
        print(f"Teams: {len(self.teams)}")
        print(f"Team Members: {len(self.team_members)}")
        print(f"Tickets: {len(self.tickets)}")
        print(f"Sprints: {len(self.sprints)}")
        print(f"Channels: {len(self.channels)}")
        print(f"Messages: {len(self.messages)}")
        print(f"Meetings: {len(self.meetings)}")
        print(f"Activities: {len(self.activities)}")

if __name__ == "__main__":
    from src.models.communication import MeetingType
    
    # Set random seed for reproducibility
    random.seed(42)
    
    # Generate company data
    generator = CompanyDataGenerator()
    generator.generate_all() 