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
    
    # Get company domain or use a default
    company_name = config.get('company', {}).get('name', 'company').lower().replace(' ', '')
    company_domain = config.get('company', {}).get('domain', f"{company_name}.com")
    
    # Default skills for team members based on role
    default_skills = {
        'Developer': ['Python', 'Java', 'SQL', 'Git'],
        'QA': ['Testing', 'Automation', 'Python', 'SQL'],
        'DevOps': ['Docker', 'Kubernetes', 'AWS', 'CI/CD'],
        'Product Manager': ['Agile', 'JIRA', 'Product Management', 'Stakeholder Management'],
        'Designer': ['UI/UX', 'Figma', 'Adobe Creative Suite', 'Design Systems']
    }
    
    # Valid seniority levels
    seniority_levels = ['Junior', 'Mid-level', 'Senior', 'Lead', 'Principal']
    
    for bu in config['business_units']:
        for team_data in bu['teams']:
            team_id = team_data.get('id', generate_id())
            
            # Create team members first
            team_members_list = []
            for member_data in team_data['team_members']:
                member_id = member_data.get('id', generate_id())
                role = member_data.get('role', 'Developer')
                
                member = TeamMember(
                    id=member_id,
                    name=member_data['name'],
                    role=role,
                    team_id=team_id,
                    email=f"{member_data['name'].lower().replace(' ', '.')}@{company_domain}",
                    department=bu['name'],
                    seniority='Mid-level',  # Using a valid enum value
                    skills=default_skills.get(role, default_skills['Developer']),
                    join_date=datetime.now() - timedelta(days=random.randint(30, 730))
                )
                team_members[member_id] = member
                team_members_list.append(member)
            
            # Select a manager from the team members
            manager = random.choice(team_members_list) if team_members_list else None
            
            team = Team(
                id=team_id,
                name=team_data['name'],
                description=f"Team {team_data['name']} in {bu['name']}",
                business_unit=bu['name'],
                department=bu['name'],  # Using business unit as department
                manager_id=manager.id if manager else None,
                members=team_members_list,
                created_date=datetime.now() - timedelta(days=random.randint(30, 365))
            )
            teams[team_id] = team
    
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
        # Create ticket generator with team members and teams
        ticket_generator = TicketGenerator(team_members=team_members, teams=teams, config=config)
        
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