import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple

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
from src.models.team import Team, TeamMember, Department, Role, Seniority, Skill

def generate_id(prefix: str = None):
    """Generate a unique ID with an optional prefix."""
    id = uuid.uuid4().hex[:8]
    return f"{prefix}-{id}" if prefix else id

def find_team_by_name(config, team_name):
    """Find a team by name in the JIRA data."""
    teams_file = "user_data/jira_teams_20250328_104736.json"
    if os.path.exists(teams_file):
        with open(teams_file, 'r') as f:
            teams_data = json.load(f)
            for team_data in teams_data:
                if team_data['name'] == team_name:
                    return team_data
    return None

def extract_teams_and_members(config):
    """Extract teams and team members from JIRA data."""
    teams = {}
    team_members = {}
    
    # Load users data from JIRA first
    users_file = "user_data/jira_users_20250328_104736.json"
    if os.path.exists(users_file):
        with open(users_file, 'r') as f:
            users_data = json.load(f)
            for user_data in users_data:
                # Generate a valid email if none exists
                email = user_data.get('emailAddress')
                if not email:
                    email = f"{user_data['displayName'].lower().replace(' ', '.')}@company.com"
                
                member = TeamMember(
                    id=user_data['accountId'],
                    name=user_data['displayName'],
                    email=email,
                    role=Role.SOFTWARE_ENGINEER.value,
                    active=True
                )
                team_members[member.id] = member
    
    # Load teams data from JIRA
    teams_file = "user_data/jira_teams_20250328_104736.json"
    if os.path.exists(teams_file):
        with open(teams_file, 'r') as f:
            teams_data = json.load(f)
            for team_data in teams_data:
                # Get team members
                team_members_list = []
                for member_data in team_data.get('members', []):
                    member_id = member_data.get('accountId')
                    if member_id and member_id in team_members:
                        member = team_members[member_id]
                        team_members_list.append(member)
                
                team = Team(
                    id=team_data['id'],
                    name=team_data['name'],
                    description=team_data.get('description', ''),
                    members=team_members_list
                )
                teams[team.id] = team
    
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

def generate_tickets(
    team_members: Dict[str, TeamMember],
    teams: Dict[str, Team],
    config: dict,
    num_sprints: int = 3,
    tickets_per_sprint: int = 5,
    team_name: str = None,
    product_initiative: str = None,
    initiative_id: str = None
) -> Tuple[List[Dict], List[Dict]]:
    """Generate tickets for the specified team."""
    try:
        # Create ticket generator with config
        ticket_generator = TicketGenerator(config=config)
        
        if product_initiative:
            ticket_generator.set_product_initiative(product_initiative)
        
        # Generate sprints for the team
        team = next((t for t in teams.values() if t.name == team_name), None) if team_name else None
        if not team:
            team = random.choice(list(teams.values()))
        
        sprints = ticket_generator.generate_sprints_for_team(team.id, num_sprints)
        
        # Generate tickets for each sprint
        all_tickets = []
        all_sprints = []
        
        for sprint in sprints:
            try:
                # Generate exactly the requested number of tickets per sprint
                sprint_tickets = ticket_generator.generate_sprint_tickets(
                    sprint.id, 
                    team.id, 
                    tickets_per_sprint
                )
                all_tickets.extend(sprint_tickets)
                all_sprints.append(sprint)
                
                # Assign tickets to sprint
                for ticket in sprint_tickets:
                    ticket_generator.assign_ticket_to_sprint(ticket, sprint)
            except Exception as e:
                print(f"Error generating tickets for sprint {sprint.id}: {str(e)}")
                continue
        
        return all_tickets, all_sprints
    except Exception as e:
        print(f"Error in ticket generation: {str(e)}")
        return [], []

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
    
    teams, team_members = extract_teams_and_members(company_config)
    generate_tickets(
        team_members=team_members,
        teams=teams,
        config=company_config,
        num_sprints=args.num_sprints,
        tickets_per_sprint=args.tickets_per_sprint,
        team_name=args.team_name,
        product_initiative=args.product_initiative
    ) 