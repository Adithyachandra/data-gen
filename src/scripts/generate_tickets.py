from datetime import datetime, timedelta
import json
from pathlib import Path

from src.config.sample_company import INNOVATECH_CONFIG
from src.generators.ticket_generator import TicketGenerator
from src.scripts.generate_teams import generate_teams

def generate_tickets(teams=None, team_members=None, output_dir: str = "generated_data", num_sprints: int = 3):
    """Generate tickets and sprints for all teams."""
    print("Starting ticket data generation...")
    
    # If teams and members not provided, generate them
    if teams is None or team_members is None:
        teams, team_members = generate_teams(output_dir)
    
    # Initialize generator
    generator = TicketGenerator(team_members, teams, INNOVATECH_CONFIG)
    
    # Storage for generated data
    tickets = {}
    sprints = {}
    
    # Generate tickets for each team
    for team in teams.values():
        print(f"Generating tickets and sprints for team {team.name}...")
        
        # Generate sprints
        team_sprints = []
        sprint_start = datetime.now() - timedelta(days=90)  # Start from 90 days ago
        
        for i in range(num_sprints):
            sprint = generator.generate_sprint(
                team.id,
                start_date=sprint_start + timedelta(days=i * 14)
            )
            team_sprints.append(sprint)
            sprints[sprint.id] = sprint
        
        # Generate tickets for each sprint
        for sprint in team_sprints:
            component = team.components[0] if team.components else "FRONTEND"
            sprint_tickets = generator.generate_sprint_tickets(sprint, component)
            
            # Store tickets
            for ticket_type, ticket_list in sprint_tickets.items():
                for ticket in ticket_list:
                    tickets[ticket.id] = ticket
    
    # Create output directory
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    # Helper function to convert objects to dict
    def to_dict(obj):
        if hasattr(obj, "model_dump"):  # Use pydantic v2 method
            return obj.model_dump()
        return obj
    
    # Save ticket data
    data_mapping = {
        "tickets": tickets,
        "sprints": sprints
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
    
    print("\nTicket Generation Summary:")
    print(f"Sprints: {len(sprints)}")
    print(f"Tickets: {len(tickets)}")
    print(f"\nData saved to {output_dir}")
    
    return tickets, sprints

if __name__ == "__main__":
    generate_tickets() 