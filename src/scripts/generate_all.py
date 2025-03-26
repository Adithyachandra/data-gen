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
from src.scripts.generate_tickets import generate_tickets
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
    """Main function to orchestrate data generation."""
    parser = argparse.ArgumentParser(description="Generate sample company data")
    parser.add_argument("--batch", choices=["teams", "tickets", "communication", "all"], default="all",
                      help="Which data to generate")
    parser.add_argument("--output-dir", default="generated_data",
                      help="Directory to save generated data")
    parser.add_argument("--num-sprints", type=int, default=1,
                      help="Number of sprints to generate per team (default: 1)")
    parser.add_argument("--tickets-per-sprint", type=int, default=None,
                      help="Target number of tickets to generate per sprint. If not specified, uses default generation logic.")
    parser.add_argument("--team-name", type=str, default=None,
                      help="Name of the team to generate tickets for. If not specified, generates for all teams.")
    parser.add_argument("--product-initiative", type=str, default=None,
                      help="Name of the product initiative to focus on. If not specified, uses random initiatives.")
    parser.add_argument("--config-file", type=str, required=True,
                      help="Path to the company configuration JSON file")
    
    args = parser.parse_args()
    
    # Load company configuration
    print("\n=== Loading Company Configuration ===")
    company_config = load_company_config(args.config_file)
    print(f"Loaded configuration for {company_config['company']['name']}")
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)
    
    # Generate teams and members first if needed
    teams = None
    team_members = None
    if args.batch in ["teams", "tickets", "communication", "all"]:
        print("\n=== Generating Team Data ===")
        teams, team_members = generate_teams(args.config_file, args.output_dir)
    
    if args.batch in ["tickets", "all"]:
        print("\n=== Generating Ticket Data ===")
        # Create default sprint and release first
        sprint, fix_version = create_default_sprint_and_release(teams, args.output_dir)
        print(f"Created default sprint {sprint.id} and release {fix_version.id}")
        
        # Generate tickets with the default sprint and release
        tickets, _ = generate_tickets(
            teams, 
            team_members, 
            args.output_dir, 
            args.num_sprints, 
            args.tickets_per_sprint, 
            args.team_name, 
            args.product_initiative,
            company_config
        )
    
    if args.batch in ["communication", "all"]:
        print("\n=== Generating Communication Data ===")
        generate_communication(teams, team_members, tickets, args.output_dir, company_config)
    
    print("\nData generation complete!")

if __name__ == "__main__":
    main() 