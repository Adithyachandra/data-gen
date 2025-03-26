import os
import sys
from pathlib import Path

# Add the project root directory to Python path
project_root = str(Path(__file__).parent.parent.parent)
sys.path.insert(0, project_root)

from datetime import datetime
import json

from src.generators.team_generator import TeamGenerator

def generate_teams(config_file: str, output_dir: str = "generated_data"):
    """Generate organizational structure including teams and members.
    
    Args:
        config_file: Path to the company configuration JSON file
        output_dir: Directory to save generated data
    """
    print("Starting team data generation...")
    
    # Load company configuration
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    # Initialize generator
    generator = TeamGenerator(config)
    
    # Generate organization structure
    business_units = generator.generate_organization()
    team_members = generator.get_all_members()
    teams = generator.get_all_teams()
    
    # Create output directory
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    # Helper function to convert objects to dict
    def to_dict(obj):
        if hasattr(obj, "model_dump"):  # Use pydantic v2 method
            return obj.model_dump()
        return obj
    
    # Save team data
    data_mapping = {
        "business_units": business_units,
        "team_members": team_members,
        "teams": teams
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
    
    print("\nTeam Generation Summary:")
    print(f"Business Units: {len(business_units)}")
    print(f"Teams: {len(teams)}")
    print(f"Team Members: {len(team_members)}")
    print(f"\nData saved to {output_dir}")
    
    return teams, team_members

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Generate team data from company configuration')
    parser.add_argument('--config-file', required=True, help='Path to company configuration JSON file')
    parser.add_argument('--output-dir', default='generated_data', help='Directory to save generated data')
    args = parser.parse_args()
    
    generate_teams(args.config_file, args.output_dir) 