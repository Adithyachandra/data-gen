import os
import sys
from pathlib import Path

# Add the project root directory to Python path
project_root = str(Path(__file__).parent.parent.parent)
sys.path.insert(0, project_root)

from datetime import datetime, timedelta
import json
import random
import uuid

from src.generators.ticket_generator import TicketGenerator
from src.models.ticket import Component
from src.models.fix_version import FixVersion
from src.models.team import Team, TeamMember

def generate_id(prefix: str = None):
    """Generate a unique ID with an optional prefix."""
    id = uuid.uuid4().hex[:8]
    return f"{prefix}-{id}" if prefix else id

def find_team_by_name(config, team_name):
    """Find a team by name in the config."""
    for bu in config['business_units']:
        for team in bu['teams']:
            if team['name'] == team_name:
                return team
    return None

def extract_teams_and_members(config):
    """Extract teams and team members from config."""
    teams = {}
    team_members = {}
    
    for bu in config['business_units']:
        for team_data in bu['teams']:
            team_id = team_data.get('id', generate_id())
            team = Team(
                id=team_id,
                name=team_data['name'],
                description=f"Team {team_data['name']} in {bu['name']}",
                business_unit=bu['name']
            )
            teams[team_id] = team
            
            for member_data in team_data['team_members']:
                member_id = member_data.get('id', generate_id())
                member = TeamMember(
                    id=member_id,
                    name=member_data['name'],
                    role=member_data.get('role', 'Developer'),
                    team_id=team_id,
                    email=f"{member_data['name'].lower().replace(' ', '.')}@{config['company']['domain']}"
                )
                team_members[member_id] = member
    
    return teams, team_members

def get_component_for_team(team_name: str) -> Component:
    """Get an appropriate component based on team name."""
    team_name_lower = team_name.lower()
    if 'frontend' in team_name_lower or 'ui' in team_name_lower:
        return Component.FRONTEND
    elif 'backend' in team_name_lower or 'api' in team_name_lower:
        return Component.BACKEND
    elif 'database' in team_name_lower or 'data' in team_name_lower:
        return Component.DATABASE
    elif 'infrastructure' in team_name_lower or 'devops' in team_name_lower:
        return Component.INFRASTRUCTURE
    elif 'security' in team_name_lower:
        return Component.SECURITY
    elif 'test' in team_name_lower or 'qa' in team_name_lower:
        return Component.TESTING
    else:
        # Default to backend if no specific match
        return Component.BACKEND

def generate_tickets(teams=None, team_members=None, output_dir: str = "generated_data", num_sprints: int = 1, tickets_per_sprint: int = None, team_name: str = None, product_initiative: str = None, company_config: dict = None):
    """Generate tickets and sprints for all teams.
    
    Args:
        teams: Dictionary of teams to generate tickets for. If None, uses all teams from config.
        team_members: Dictionary of team members. If None, uses all team members from config.
        output_dir: Directory to save generated data.
        num_sprints: Number of sprints to generate per team.
        tickets_per_sprint: Number of tickets to generate per sprint. If None, uses default values.
        team_name: Name of specific team to generate tickets for.
        product_initiative: Name of product initiative to focus on.
        company_config: Company configuration dictionary containing products and initiatives.
    """
    # Initialize storage
    tickets = {}
    sprints = {}
    fix_versions = {}
    
    # Extract teams and members from config if not provided
    if teams is None or team_members is None:
        teams, team_members = extract_teams_and_members(company_config)
    
    # Initialize TicketGenerator with company config
    ticket_generator = TicketGenerator(team_members, teams, company_config)
    
    # Set the current initiative
    ticket_generator.current_initiative = product_initiative
    
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
    
    # Get target teams
    target_teams = []
    if team_name:
        team = find_team_by_name(company_config, team_name)
        if team:
            target_teams.append(team)
    else:
        for bu in company_config['business_units']:
            target_teams.extend(bu['teams'])
    
    # Generate tickets for each team
    for team in target_teams:
        print(f"Generating tickets and sprints for team {team['name']}...")
        
        # Get appropriate component for this team
        component = get_component_for_team(team['name'])
        
        # Generate sprints
        team_sprints = []
        sprint_start = datetime.now() - timedelta(days=90)  # Start from 90 days ago
        
        # Ensure at least one sprint is generated
        num_sprints = max(1, num_sprints)
        
        # Create a team ID if not present
        team_id = team.get('id', generate_id())
        
        for i in range(num_sprints):
            sprint = {
                'id': generate_id('SPR'),
                'name': f"Sprint {i + 1}",
                'goal': f"Complete planned work for sprint {i + 1}",
                'description': f"Sprint {i + 1} for team {team['name']}",
                'start_date': sprint_start + timedelta(days=i * 14),
                'end_date': sprint_start + timedelta(days=(i + 1) * 14),
                'status': 'ACTIVE',
                'team_id': team_id,
                'story_points_committed': 0,
                'story_points_completed': 0,
                'velocity': 0,
                'retrospective_notes': "",
                'tickets': []
            }
            team_sprints.append(sprint)
            sprints[sprint['id']] = sprint
        
        # Generate tickets for each sprint
        for sprint in team_sprints:
            # If tickets_per_sprint is specified, adjust the generator's parameters
            if tickets_per_sprint is not None:
                # Calculate number of stories based on tickets_per_sprint
                num_stories = max(1, tickets_per_sprint // 8)  # Rough estimate
                tasks_per_story = max(1, tickets_per_sprint // (num_stories * 3))
                subtasks_per_task = max(1, tickets_per_sprint // (num_stories * tasks_per_story * 2))
                
                # Generate epic for the sprint
                epic = ticket_generator.generate_epic(component=component)
                tickets[epic.id] = epic.model_dump()
                sprint['tickets'].append(epic.id)
                
                # Generate stories
                for i in range(num_stories):
                    story = ticket_generator.generate_story(epic=epic, component=component)
                    tickets[story.id] = story.model_dump()
                    sprint['tickets'].append(story.id)
                    
                    # Generate tasks for the story
                    for j in range(tasks_per_story):
                        task = ticket_generator.generate_task(story=story, component=component)
                        tickets[task.id] = task.model_dump()
                        sprint['tickets'].append(task.id)
                        
                        # Generate subtasks for the task
                        for k in range(subtasks_per_task):
                            subtask = ticket_generator.generate_subtask(task=task, component=component)
                            tickets[subtask.id] = subtask.model_dump()
                            sprint['tickets'].append(subtask.id)
                            
                            # Randomly assign tickets to fix versions
                            if random.random() < 0.7:  # 70% chance of being assigned to a release
                                subtask_data = tickets[subtask.id]
                                subtask_data['fix_versions'] = [random.choice(list(fix_versions.keys()))]
                                tickets[subtask.id] = subtask_data
    
    # Create output directory
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    # Save generated data
    with open(output_dir / "tickets.json", "w") as f:
        json.dump(tickets, f, indent=2, default=str)
    
    with open(output_dir / "sprints.json", "w") as f:
        json.dump(sprints, f, indent=2, default=str)
    
    with open(output_dir / "fix_versions.json", "w") as f:
        json.dump({k: v.model_dump() for k, v in fix_versions.items()}, f, indent=2, default=str)
    
    print(f"\nGenerated {len(tickets)} tickets, {len(sprints)} sprints, and {len(fix_versions)} releases")
    print(f"Data saved to {output_dir}")
    
    return tickets, sprints

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Generate ticket data from company configuration')
    parser.add_argument('--config-file', required=True, help='Path to company configuration JSON file')
    parser.add_argument('--output-dir', default='generated_data', help='Directory to save generated data')
    parser.add_argument('--num-sprints', type=int, default=1, help='Number of sprints to generate per team')
    parser.add_argument('--tickets-per-sprint', type=int, help='Target number of tickets to generate per sprint')
    parser.add_argument('--team-name', help='Name of specific team to generate tickets for')
    parser.add_argument('--product-initiative', help='Name of product initiative to focus on')
    args = parser.parse_args()
    
    # Load company configuration
    with open(args.config_file, 'r') as f:
        company_config = json.load(f)
    
    generate_tickets(
        output_dir=args.output_dir,
        num_sprints=args.num_sprints,
        tickets_per_sprint=args.tickets_per_sprint,
        team_name=args.team_name,
        product_initiative=args.product_initiative,
        company_config=company_config
    ) 