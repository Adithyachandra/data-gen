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
        teams, team_members = generate_teams(company_config)
        print(f"\nTeam Generation Summary:")
        print(f"Business Units: {len(company_config['business_units'])}")
        print(f"Teams: {len(teams)}")
        print(f"Team Members: {len(team_members)}")
        print(f"\nData saved to {args.output_dir}")
    
    # Generate ticket data
    if args.batch in ['tickets', 'all']:
        print("\n=== Generating Ticket Data ===")
        teams, team_members = extract_teams_and_members(company_config)
        tickets, _ = generate_tickets(
            team_members=team_members,
            teams=teams,
            config=company_config,
            num_sprints=args.num_sprints,
            tickets_per_sprint=args.tickets_per_sprint,
            team_name=args.team_name,
            product_initiative=args.product_initiative
        )
        
        # Save tickets to output directory
        output_dir = Path(args.output_dir)
        output_dir.mkdir(exist_ok=True)
        
        with open(output_dir / "tickets.json", "w") as f:
            json.dump([ticket.model_dump() for ticket in tickets], f, indent=2, default=str)
        
        print(f"\nGenerated {len(tickets)} tickets")
        print(f"Data saved to {args.output_dir}")

if __name__ == "__main__":
    main() 