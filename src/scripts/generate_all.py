from datetime import datetime
import json
from pathlib import Path
import argparse

from src.scripts.generate_teams import generate_teams
from src.scripts.generate_tickets import generate_tickets
from src.scripts.generate_communication import generate_communication

def main():
    """Main function to orchestrate data generation."""
    parser = argparse.ArgumentParser(description="Generate company data in batches.")
    parser.add_argument("--output-dir", default="generated_data", help="Output directory for generated data")
    parser.add_argument("--num-sprints", type=int, default=3, help="Number of sprints to generate per team")
    parser.add_argument("--batch", choices=["teams", "tickets", "communication", "all"], 
                       default="all", help="Which batch of data to generate")
    args = parser.parse_args()
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)
    
    teams = None
    team_members = None
    tickets = None
    
    # Load existing data if available
    if args.batch != "teams":
        try:
            with open(output_dir / "teams.json") as f:
                teams = json.load(f)
            with open(output_dir / "team_members.json") as f:
                team_members = json.load(f)
        except FileNotFoundError:
            print("No existing team data found. Will generate teams first.")
    
    if args.batch == "communication":
        try:
            with open(output_dir / "tickets.json") as f:
                tickets = json.load(f)
        except FileNotFoundError:
            print("No existing ticket data found. Will generate tickets first.")
    
    # Generate data based on batch selection
    if args.batch in ["teams", "all"]:
        print("\n=== Generating Team Data ===")
        teams, team_members = generate_teams(args.output_dir)
    
    if args.batch in ["tickets", "all"]:
        print("\n=== Generating Ticket Data ===")
        tickets, _ = generate_tickets(teams, team_members, args.output_dir, args.num_sprints)
    
    if args.batch in ["communication", "all"]:
        print("\n=== Generating Communication Data ===")
        generate_communication(teams, team_members, tickets, args.output_dir)
    
    print("\nData generation complete!")

if __name__ == "__main__":
    main() 