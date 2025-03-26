from datetime import datetime, timedelta
import json
from pathlib import Path
import random
import uuid

from src.config.sample_company import INNOVATECH_CONFIG
from src.generators.ticket_generator import TicketGenerator
from src.scripts.generate_teams import generate_teams
from src.models.ticket import Component
from src.models.fix_version import FixVersion

def generate_id():
    return uuid.uuid4().hex[:8]

def generate_tickets(teams=None, team_members=None, output_dir: str = "generated_data", num_sprints: int = 1, tickets_per_sprint: int = None, team_name: str = None, product_initiative: str = None):
    """Generate tickets and sprints for all teams.
    
    Args:
        teams: Dictionary of teams to generate tickets for. If None, uses all teams from config.
        team_members: Dictionary of team members. If None, uses all team members from config.
        output_dir: Directory to save generated data.
        num_sprints: Number of sprints to generate per team.
        tickets_per_sprint: Number of tickets to generate per sprint. If None, uses default values.
        team_name: Name of specific team to generate tickets for.
        product_initiative: Name of product initiative to focus on.
    """
    # Load configuration
    config = INNOVATECH_CONFIG
    
    # Initialize generators
    generator = TicketGenerator(team_members or config.team_members, teams or config.teams)
    
    # Set product initiative if specified
    if product_initiative:
        generator.current_initiative = product_initiative
    
    # Initialize storage
    tickets = {}
    sprints = {}
    fix_versions = {}
    
    # Generate fix versions (releases)
    current_date = datetime.now()
    for i in range(3):  # Generate 3 releases
        release_date = current_date + timedelta(days=30 * (i + 1))
        fix_version = FixVersion(
            id=f"REL{generate_id()}",
            name=f"Release {i + 1}.0",
            description=f"Release {i + 1}.0 with new features and improvements",
            release_date=release_date,
            released=False,
            archived=False
        )
        fix_versions[fix_version.id] = fix_version
    
    # Filter teams if team_name is specified
    target_teams = {}
    if team_name:
        for team_id, team in (teams or config.teams).items():
            if team.name == team_name:
                target_teams[team_id] = team
    else:
        target_teams = teams or config.teams
    
    # Generate tickets for each team
    for team in target_teams.values():
        print(f"Generating tickets and sprints for team {team.name}...")
        
        # Generate sprints
        team_sprints = []
        sprint_start = datetime.now() - timedelta(days=90)  # Start from 90 days ago
        
        # Ensure at least one sprint is generated
        num_sprints = max(1, num_sprints)
        
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
            
            # Store tickets and assign to fix versions
            for ticket_type, ticket_list in sprint_tickets.items():
                for ticket in ticket_list:
                    tickets[ticket.id] = ticket
                    # Randomly assign tickets to fix versions
                    if random.random() < 0.7:  # 70% chance of being assigned to a release
                        ticket.fix_versions = [random.choice(list(fix_versions.keys()))]
    
    # Create output directory
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    # Save generated data
    with open(output_dir / "tickets.json", "w") as f:
        json.dump({k: v.model_dump() for k, v in tickets.items()}, f, indent=2, default=str)
    
    with open(output_dir / "sprints.json", "w") as f:
        json.dump({k: v.model_dump() for k, v in sprints.items()}, f, indent=2, default=str)
    
    with open(output_dir / "fix_versions.json", "w") as f:
        json.dump({k: v.model_dump() for k, v in fix_versions.items()}, f, indent=2, default=str)
    
    print(f"\nGenerated {len(tickets)} tickets, {len(sprints)} sprints, and {len(fix_versions)} releases")
    print(f"Data saved to {output_dir}")
    
    return tickets, sprints

if __name__ == "__main__":
    generate_tickets() 