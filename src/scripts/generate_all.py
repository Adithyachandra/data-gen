from datetime import datetime
import json
from pathlib import Path
import argparse

from src.scripts.generate_teams import generate_teams
from src.scripts.generate_tickets import generate_tickets
from src.scripts.generate_communication import generate_communication

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
    
    args = parser.parse_args()
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)
    
    # Generate teams and members first if needed
    teams = None
    team_members = None
    if args.batch in ["teams", "tickets", "communication", "all"]:
        print("\n=== Generating Team Data ===")
        teams, team_members = generate_teams(args.output_dir)
    
    if args.batch in ["tickets", "all"]:
        print("\n=== Generating Ticket Data ===")
        tickets, _ = generate_tickets(teams, team_members, args.output_dir, args.num_sprints, args.tickets_per_sprint, args.team_name, args.product_initiative)
    
    if args.batch in ["communication", "all"]:
        print("\n=== Generating Communication Data ===")
        generate_communication(teams, team_members, tickets, args.output_dir)
    
    print("\nData generation complete!")

if __name__ == "__main__":
    main() 