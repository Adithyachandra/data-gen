import os
import json
import argparse
from typing import Dict, Any, List
from datetime import datetime
from jira import JIRA
from dotenv import load_dotenv

def load_data(file_path: str) -> Dict[str, Any]:
    """Load data from a JSON file."""
    with open(file_path, 'r') as f:
        return json.load(f)

def create_fix_version(jira: JIRA, version_data: Dict[str, Any]) -> str:
    """Create a fix version in JIRA."""
    try:
        # Check if version already exists
        project_versions = jira.project_versions(os.getenv("JIRA_PROJECT_KEY"))
        for version in project_versions:
            if version.name == version_data["name"]:
                print(f"Fix version {version.name} already exists, using existing version")
                return version.id

        # Create new version
        version = jira.create_version(
            name=version_data["name"],
            project=os.getenv("JIRA_PROJECT_KEY"),
            description=version_data["description"],
            releaseDate=version_data["release_date"].split()[0],  # Only use the date part
            released=version_data["released"],
            archived=version_data["archived"]
        )
        print(f"Created fix version {version.name}")
        return version.id
    except Exception as e:
        print(f"Error creating fix version {version_data['name']}: {str(e)}")
        raise

def create_sprint(jira: JIRA, sprint_data: Dict[str, Any]) -> str:
    """Create a sprint in JIRA."""
    try:
        # Format dates in ISO 8601 format (YYYY-MM-DD)
        start_date = sprint_data["start_date"].split()[0]
        end_date = sprint_data["end_date"].split()[0]

        # Create sprint using Agile API
        sprint = jira.create_sprint(
            name=sprint_data["name"],
            board_id=os.getenv("JIRA_BOARD_ID"),
            startDate=start_date,
            endDate=end_date
        )
        print(f"Created sprint {sprint.name}")
        return sprint.id
    except Exception as e:
        print(f"Error creating sprint {sprint_data['name']}: {str(e)}")
        raise

def create_jira_ticket(ticket_data, jira, project_key, ticket_mapping, sprint_mapping, created_versions, fix_versions_data):
    """Create a JIRA ticket with proper relationships"""
    try:
        # Map ticket types to JIRA issue type names
        issue_type_map = {
            'Epic': 'Epic',
            'Story': 'Story',
            'Task': 'Task',
            'Sub-task': 'Subtask',  # Using the exact name from JIRA
            'Bug': 'Bug'
        }

        # Prepare issue fields
        issue_fields = {
            'project': project_key,
            'summary': ticket_data['summary'],
            'description': ticket_data['description'],
            'issuetype': {'name': issue_type_map[ticket_data['type']]}
        }

        # Add story points if available (excluding Epics)
        if 'story_points' in ticket_data and ticket_data['type'] != 'Epic':
            # The custom field ID for story points varies by JIRA instance
            # This is typically 'customfield_10026' but may need to be configured
            story_points_field = os.getenv('JIRA_STORY_POINTS_FIELD', 'customfield_10026')
            issue_fields[story_points_field] = ticket_data['story_points']

        # Add fix version if provided
        if ticket_data.get("fix_versions"):
            fix_versions = ticket_data["fix_versions"]
            if isinstance(fix_versions, str):
                fix_versions = [fix_versions]
            
            # Get the fix version name from fix_versions.json
            if fix_versions and fix_versions[0] in fix_versions_data:
                version_name = fix_versions_data[fix_versions[0]]["name"]
                issue_fields['fixVersions'] = [{'name': version_name}]
            else:
                print(f"Warning: Fix version {fix_versions[0] if fix_versions else 'None'} not found for {ticket_data['type']} {ticket_data['id']}")

        # Add sprint for Stories and Tasks only
        if ticket_data['type'] in ['Story', 'Task'] and ticket_data.get('sprint_id'):
            sprint_id = sprint_mapping.get(ticket_data['sprint_id'])
            if sprint_id:
                issue_fields['customfield_10020'] = int(sprint_id)
            else:
                print(f"Warning: Sprint {ticket_data['sprint_id']} not found for {ticket_data['type']} {ticket_data['id']}")

        # Handle parent-child relationships
        if ticket_data['type'] in ['Story', 'Task']:
            parent_id = ticket_data.get('epic_link')
            if parent_id and parent_id in ticket_mapping:
                issue_fields['parent'] = {'key': ticket_mapping[parent_id]}
        elif ticket_data['type'] == 'Sub-task':
            parent_id = ticket_data.get('parent_ticket')
            if parent_id and parent_id in ticket_mapping:
                issue_fields['parent'] = {'key': ticket_mapping[parent_id]}
            else:
                print(f"Warning: Parent ticket {parent_id} not found for {ticket_data['type']} {ticket_data['id']}")
                return None  # Skip creating the ticket if parent is not found

        # Create the issue
        new_issue = jira.create_issue(fields=issue_fields)
        print(f"Created {ticket_data['type']} {ticket_data['id']} as {new_issue.key}")

        # Create issue links for dependencies and blocks
        if ticket_data.get('depends_on'):
            for dependency in ticket_data['depends_on']:
                if dependency in ticket_mapping:
                    try:
                        jira.create_issue_link(
                            type='Depends',
                            inwardIssue=new_issue.key,
                            outwardIssue=ticket_mapping[dependency]
                        )
                    except Exception as e:
                        print(f"Error creating dependency link for {new_issue.key}: {str(e)}")

        if ticket_data.get('blocks'):
            for blocked in ticket_data['blocks']:
                if blocked in ticket_mapping:
                    try:
                        jira.create_issue_link(
                            type='Blocks',
                            inwardIssue=new_issue.key,
                            outwardIssue=ticket_mapping[blocked]
                        )
                    except Exception as e:
                        print(f"Error creating blocks link for {new_issue.key}: {str(e)}")

        return new_issue.key
    except Exception as e:
        print(f"Error creating {ticket_data['type']} {ticket_data['id']}: {str(e)}")
        return None

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Push generated data to JIRA')
    parser.add_argument('--input-dir', type=str, default='generated_data',
                      help='Directory containing the JSON files (default: generated_data)')
    args = parser.parse_args()

    # Load environment variables
    load_dotenv()
    
    # Get JIRA credentials from environment variables
    jira_url = os.getenv("JIRA_URL")
    jira_username = os.getenv("JIRA_USERNAME")
    jira_api_token = os.getenv("JIRA_API_TOKEN")
    
    if not all([jira_url, jira_username, jira_api_token]):
        raise ValueError("Missing required JIRA credentials in environment variables")
    
    # Initialize JIRA client
    jira = JIRA(server=jira_url, basic_auth=(jira_username, jira_api_token))
    
    # Load generated data from the specified directory
    tickets = load_data(os.path.join(args.input_dir, "tickets.json"))
    sprints = load_data(os.path.join(args.input_dir, "sprints.json"))
    fix_versions = load_data(os.path.join(args.input_dir, "fix_versions.json"))
    
    # Create fix versions first
    created_versions = {}
    for version_id, version_data in fix_versions.items():
        try:
            jira_version_id = create_fix_version(jira, version_data)
            created_versions[version_id] = jira_version_id
        except Exception as e:
            print(f"Error creating fix version {version_id}: {str(e)}")
    
    # Create sprints
    created_sprints = {}
    for sprint_id, sprint_data in sprints.items():
        try:
            jira_sprint_id = create_sprint(jira, sprint_data)
            created_sprints[sprint_id] = jira_sprint_id
        except Exception as e:
            print(f"Error creating sprint {sprint_id}: {str(e)}")
    
    # First, create all Epic tickets
    created_tickets = {}
    print("\nProcessing Epic tickets...")
    for ticket_id, ticket_data in tickets.items():
        if ticket_data["type"] == "Epic":
            try:
                jira_key = create_jira_ticket(ticket_data, jira, os.getenv("JIRA_PROJECT_KEY"), 
                                            created_tickets, created_sprints, created_versions, fix_versions)
                if jira_key:
                    created_tickets[ticket_data["id"]] = jira_key
                    print(f"Created Epic {jira_key} from {ticket_data['id']}")
            except Exception as e:
                print(f"Error creating Epic {ticket_data['id']}: {str(e)}")
    
    # Then create all Story and Task tickets
    print("\nProcessing Story and Task tickets...")
    for ticket_id, ticket_data in tickets.items():
        if ticket_data["type"] in ["Story", "Task"]:
            try:
                jira_key = create_jira_ticket(ticket_data, jira, os.getenv("JIRA_PROJECT_KEY"), 
                                            created_tickets, created_sprints, created_versions, fix_versions)
                if jira_key:
                    created_tickets[ticket_data["id"]] = jira_key
                    print(f"Created {ticket_data['type']} {jira_key} from {ticket_data['id']}")
            except Exception as e:
                print(f"Error creating ticket {ticket_data['id']}: {str(e)}")
    
    # Process Bug tickets
    print("\nProcessing Bug tickets...")
    for ticket_id, ticket_data in tickets.items():
        if ticket_data["type"] == "Bug":
            try:
                jira_key = create_jira_ticket(ticket_data, jira, os.getenv("JIRA_PROJECT_KEY"), 
                                            created_tickets, created_sprints, created_versions, fix_versions)
                if jira_key:
                    created_tickets[ticket_data["id"]] = jira_key
                    print(f"Created Bug {jira_key} from {ticket_data['id']}")
            except Exception as e:
                print(f"Error creating ticket {ticket_data['id']}: {str(e)}")
    
    # Finally, create all Subtask tickets
    print("\nProcessing Subtask tickets...")
    for ticket_id, ticket_data in tickets.items():
        if ticket_data["type"] == "Sub-task":
            print(f"Found subtask {ticket_data['id']} with parent {ticket_data.get('parent_ticket')}")
            try:
                jira_key = create_jira_ticket(ticket_data, jira, os.getenv("JIRA_PROJECT_KEY"), 
                                            created_tickets, created_sprints, created_versions, fix_versions)
                if jira_key:
                    created_tickets[ticket_data["id"]] = jira_key
                    print(f"Created Subtask {jira_key} from {ticket_data['id']}")
                else:
                    print(f"Failed to create subtask {ticket_data['id']}")
            except Exception as e:
                print(f"Error creating ticket {ticket_data['id']}: {str(e)}")
    
    # Save mapping of generated tickets to JIRA tickets
    mapping_file = os.path.join(args.input_dir, "jira_mapping.json")
    with open(mapping_file, "w") as f:
        json.dump({
            "tickets": created_tickets,
            "sprints": created_sprints,
            "fix_versions": created_versions
        }, f, indent=2)
    
    print(f"\nSuccessfully created {len(created_tickets)} tickets, {len(created_sprints)} sprints, and {len(created_versions)} fix versions in JIRA")
    print(f"Mapping saved to {mapping_file}")

if __name__ == "__main__":
    main() 