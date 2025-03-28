import os
import sys
from pathlib import Path

# Add the project root directory to Python path
project_root = str(Path(__file__).parent.parent.parent)
sys.path.insert(0, project_root)

from datetime import datetime, timedelta
import json
import argparse
import random
import uuid

from src.scripts.generate_teams import generate_teams
from src.scripts.generate_tickets import generate_tickets, extract_teams_and_members
from src.scripts.generate_communication import generate_communication
from src.models.fix_version import FixVersion
from src.models.ticket import Sprint, SprintStatus
from src.generators.utils import generate_id

def load_company_config(config_file: str) -> dict:
    """Load company configuration from JSON file."""
    with open(config_file, 'r') as f:
        return json.load(f)

def create_default_sprint_and_release(teams, output_dir):
    """Create a default sprint and release for the generated tickets."""
    # Create a default release
    current_date = datetime.now()
    release_date = current_date + timedelta(days=30)
    fix_version = FixVersion(
        id=f"REL{generate_id()}",
        name="Release 1.0",
        description="Initial release with core features",
        release_date=release_date,
        released=False,
        archived=False
    )
    
    # Create a default sprint
    sprint_start = current_date - timedelta(days=14)  # Start from 2 weeks ago
    sprint = Sprint(
        id=f"SPR{uuid.uuid4().hex[:8]}",
        name="Sprint 1",
        goal="Complete initial set of features",
        description="Initial sprint for core features",
        start_date=sprint_start,
        end_date=sprint_start + timedelta(days=14),
        status=SprintStatus.ACTIVE,
        team_id=next(iter(teams.values())).id,  # Use the first team's ID
        story_points_committed=0,
        story_points_completed=0,
        velocity=0,
        retrospective_notes="",
        tickets=[]
    )
    
    # Save the sprint and release
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    with open(os.path.join(output_dir, "sprints.json"), "w") as f:
        json.dump({sprint.id: sprint.model_dump()}, f, indent=2, default=str)
    
    with open(os.path.join(output_dir, "fix_versions.json"), "w") as f:
        json.dump({fix_version.id: fix_version.model_dump()}, f, indent=2, default=str)
    
    return sprint, fix_version

def main():
    """Main function to generate data."""
    parser = argparse.ArgumentParser(description='Generate data for JIRA')
    parser.add_argument('--config-file', required=True, help='Path to company configuration JSON file')
    parser.add_argument('--batch', choices=['teams', 'tickets', 'all'], default='all', help='What data to generate')
    parser.add_argument('--output-dir', default='generated_data', help='Directory to save generated data')
    parser.add_argument('--num-sprints', type=int, default=1, help='Number of sprints to generate per team')
    parser.add_argument('--tickets-per-sprint', type=int, default=5, help='Target number of tickets to generate per sprint')
    parser.add_argument('--team-name', help='Name of specific team to generate tickets for')
    parser.add_argument('--product-initiative', help='Name of product initiative to focus on')
    parser.add_argument('--team-id', help='ID of specific team to generate tickets for')
    parser.add_argument('--initiative-id', help='ID of specific initiative to focus on')
    args = parser.parse_args()
    
    # Load company configuration
    print("\n=== Loading Company Configuration ===")
    with open(args.config_file, 'r') as f:
        company_config = json.load(f)
    print(f"Loaded configuration for {company_config['company']['name']}")
    
    # Generate team data
    if args.batch in ['teams', 'all']:
        print("\n=== Generating Team Data ===")
        print("Starting team data generation...")
        teams, team_members = generate_teams(args.config_file, args.output_dir)
        print(f"\nTeam Generation Summary:")
        print(f"Business Units: {len(company_config['business_units'])}")
        print(f"Teams: {len(teams)}")
        print(f"Team Members: {len(team_members)}")
        print(f"\nData saved to {args.output_dir}")
    
    # Generate ticket data
    if args.batch in ['tickets', 'all']:
        print("\n=== Generating Ticket Data ===")
        print("Starting ticket data generation...")
        
        # Load or create teams and team members
        if args.batch == 'tickets':
            teams, team_members = extract_teams_and_members(company_config)
        
        # Filter teams if team_id is specified
        if args.team_id:
            if args.team_id not in teams:
                print(f"Error: Team ID {args.team_id} not found")
                return
            teams = {args.team_id: teams[args.team_id]}
            print(f"Generating tickets for specific team: {teams[args.team_id].name}")
        
        # Create default sprint and release if they don't exist
        output_dir = Path(args.output_dir)
        output_dir.mkdir(exist_ok=True)
        
        # Load existing fix versions or create a new one
        fix_versions_file = output_dir / "fix_versions.json"
        if fix_versions_file.exists():
            with open(fix_versions_file, 'r') as f:
                fix_versions = json.load(f)
        else:
            sprint, fix_version = create_default_sprint_and_release(teams, args.output_dir)
            fix_versions = {fix_version.id: fix_version.model_dump()}
        
        # Initialize lists for all generated data
        all_tickets = []
        all_sprints = []
        
        # Filter teams based on team_name or team_id
        teams_to_process = teams
        if args.team_name:
            teams_to_process = {t.id: t for t in teams.values() if t.name == args.team_name}
            if not teams_to_process:
                print(f"Error: Team name '{args.team_name}' not found")
                return
            print(f"Generating tickets for team: {args.team_name}")
        
        # Filter team members to only include members of the selected team(s)
        filtered_team_members = {
            member_id: member 
            for member_id, member in team_members.items() 
            for team in teams_to_process.values()
            if any(m.id == member.id for m in team.members)
        }
        
        for team in teams_to_process.values():
            print(f"\nGenerating tickets for team: {team.name}")
            tickets, sprints = generate_tickets(
                team_members=filtered_team_members,
                teams={team.id: team},
                config=company_config,
                num_sprints=args.num_sprints,
                tickets_per_sprint=args.tickets_per_sprint,
                team_name=team.name,
                product_initiative=args.product_initiative,
                initiative_id=args.initiative_id
            )
            
            # Assign fix versions to tickets
            for ticket in tickets:
                # Randomly assign to a fix version
                fix_version_id = random.choice(list(fix_versions.keys()))
                ticket.fix_versions = [fix_version_id]
            
            all_tickets.extend(tickets)
            all_sprints.extend(sprints)
        
        # Save generated data
        print("\nSaving generated data...")
        
        # Save tickets
        tickets_file = output_dir / "tickets.json"
        with open(tickets_file, 'w') as f:
            json.dump({ticket.id: ticket.model_dump() for ticket in all_tickets}, f, indent=2, default=str)
        
        # Save sprints
        sprints_file = output_dir / "sprints.json"
        with open(sprints_file, 'w') as f:
            json.dump({sprint.id: sprint.model_dump() for sprint in all_sprints}, f, indent=2, default=str)
        
        print(f"\nTicket Generation Summary:")
        print(f"Total Tickets: {len(all_tickets)}")
        print(f"Total Sprints: {len(all_sprints)}")
        print(f"Fix Versions: {len(fix_versions)}")
        print(f"\nData saved to {args.output_dir}")
    
    # Generate communication data
    if args.batch in ['all']:
        print("\n=== Generating Communication Data ===")
        print("Starting communication data generation...")
        generate_communication(company_config, args.output_dir)
        print(f"Communication data saved to {args.output_dir}")
    
    print("\n=== Data Generation Complete ===")

if __name__ == "__main__":
    main() 