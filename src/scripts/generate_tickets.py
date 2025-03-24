from datetime import datetime, timedelta
import json
from pathlib import Path

from src.config.sample_company import INNOVATECH_CONFIG
from src.generators.ticket_generator import TicketGenerator
from src.scripts.generate_teams import generate_teams
from src.models.ticket import Component

def generate_tickets(teams=None, team_members=None, output_dir: str = "generated_data", num_sprints: int = 1, tickets_per_sprint: int = None, team_name: str = None, product_initiative: str = None):
    """Generate tickets and sprints for all teams.
    
    Args:
        teams: Dictionary of teams
        team_members: Dictionary of team members
        output_dir: Directory to save generated data
        num_sprints: Number of sprints to generate per team (default: 1)
        tickets_per_sprint: Target number of tickets to generate per sprint. If None, uses default generation logic.
        team_name: Name of the team to generate tickets for. If None, generates for all teams.
        product_initiative: Name of the product initiative to focus on. If None, uses random initiatives.
    """
    print("Starting ticket data generation...")
    
    # If teams and members not provided, generate them
    if teams is None or team_members is None:
        teams, team_members = generate_teams(output_dir)
    
    # Initialize generator
    generator = TicketGenerator(team_members, teams, INNOVATECH_CONFIG)
    
    # Set product initiative if specified
    if product_initiative:
        generator.set_product_initiative(product_initiative)
    
    # Storage for generated data
    tickets = {}
    sprints = {}
    
    # Filter teams if team_name is specified
    target_teams = {name: team for name, team in teams.items() if team.name == team_name} if team_name else teams
    
    if not target_teams:
        print(f"No team found with name: {team_name}")
        return tickets, sprints
    
    # Generate tickets for each team
    for team in target_teams.values():
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
            # Convert component string to enum value
            component_str = team.components[0] if team.components else "FRONTEND"
            component = Component[component_str.upper()]  # Convert string to enum value
            
            # If tickets_per_sprint is specified, adjust the generator's parameters
            if tickets_per_sprint is not None:
                # Calculate number of stories based on tickets_per_sprint
                # Assuming 2-4 tasks per story and 1-3 subtasks per task
                num_stories = max(1, tickets_per_sprint // 8)  # Rough estimate
                generator.stories_per_sprint = num_stories
                generator.tasks_per_story = max(1, tickets_per_sprint // (num_stories * 3))
                generator.subtasks_per_task = max(1, tickets_per_sprint // (num_stories * generator.tasks_per_story * 2))
            
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
    print(f"Total Tickets: {len(tickets)}")
    print(f"Total Sprints: {len(sprints)}")
    if product_initiative:
        print(f"Product Initiative: {product_initiative}")
    print(f"\nData saved to {output_dir}")
    
    return tickets, sprints

if __name__ == "__main__":
    generate_tickets() 