from datetime import datetime
import json
from pathlib import Path
import random

from src.config.sample_company import INNOVATECH_CONFIG
from src.generators.communication_generator import CommunicationGenerator
from src.models.communication import MeetingType
from src.scripts.generate_teams import generate_teams
from src.scripts.generate_tickets import generate_tickets

def generate_communication(teams=None, team_members=None, tickets=None, output_dir: str = "generated_data", company_config: dict = None):
    """Generate communication data including channels, messages, and meetings."""
    print("Starting communication data generation...")
    
    # If teams and members not provided, generate them
    if teams is None or team_members is None:
        teams, team_members = generate_teams(output_dir)
    
    # If tickets not provided, generate them
    if tickets is None:
        tickets, _ = generate_tickets(teams, team_members, output_dir)
    
    # Initialize generator with company config
    generator = CommunicationGenerator(team_members, teams, company_config)
    
    # Storage for generated data
    channels = {}
    messages = {}
    meetings = {}
    
    # Generate communication for each team
    for team in teams.values():
        print(f"Generating communication for team {team.name}...")
        
        # Generate channels
        team_channels = generator.generate_channels_for_team(team)
        for channel in team_channels:
            channels[channel.id] = channel
            
            # Generate some general discussion threads
            num_threads = len(team.members) // 2  # Roughly half as many threads as members
            for _ in range(num_threads):
                thread = generator.generate_thread(channel)
                
                # Generate some messages in the thread
                num_messages = random.randint(3, 8)
                participants = random.sample(
                    [m.id for m in team.members], 
                    min(num_messages, len(team.members))
                )
                for participant in participants:
                    message = generator.generate_message(
                        team_members[participant],
                        thread
                    )
                    messages[message.id] = message
        
        # Generate team meetings
        num_meetings = random.randint(3, 6)
        meeting_types = [
            MeetingType.TEAM_SYNC,
            MeetingType.TECHNICAL_DISCUSSION,
            MeetingType.SPRINT_PLANNING,
            MeetingType.SPRINT_REVIEW,
            MeetingType.SPRINT_RETRO
        ]
        for _ in range(num_meetings):
            meeting = generator.generate_meeting(team, random.choice(meeting_types))
            meetings[meeting.id] = meeting
        
        # Generate ticket-related communication
        team_tickets = [t for t in tickets.values() if any(m.team_id == team.id for m in team.members)]
        for ticket in team_tickets:
            comms = generator.generate_ticket_communication(ticket)
            for message in comms["messages"]:
                messages[message.id] = message
    
    # Create output directory
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    # Helper function to convert objects to dict
    def to_dict(obj):
        if hasattr(obj, "model_dump"):  # Use pydantic v2 method
            return obj.model_dump()
        return obj
    
    # Save communication data
    data_mapping = {
        "channels": channels,
        "messages": messages,
        "meetings": meetings
    }
    
    for name, data in data_mapping.items():
        output_file = output_dir / f"{name}.json"
        with open(output_file, "w") as f:
            json.dump(
                {k: to_dict(v) for k, v in data.items()},
                f,
                indent=2,
                default=str  # Handle datetime objects
            )
    
    print("\nCommunication Generation Summary:")
    print(f"Channels: {len(channels)}")
    print(f"Messages: {len(messages)}")
    print(f"Meetings: {len(meetings)}")
    print(f"\nData saved to {output_dir}")
    
    return channels, messages, meetings

if __name__ == "__main__":
    generate_communication() 