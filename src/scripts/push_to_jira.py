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

def create_jira_ticket(jira: JIRA, ticket_data: Dict[str, Any], created_tickets: Dict[str, str], reporter: str, assignee: str) -> str:
    """Create a ticket in JIRA with the given data."""
    # Map ticket types to JIRA issue types
    issue_type_map = {
        "Epic": "Epic",
        "Story": "Story",
        "Task": "Task",
        "Bug": "Bug",
        "Subtask": "Subtask"
    }
    
    # Prepare the description with acceptance criteria if they exist
    description = ticket_data["description"]
    if ticket_data.get("acceptance_criteria"):
        description += "\n\n## Acceptance Criteria\n"
        for criterion in ticket_data["acceptance_criteria"]:
            description += f"* {criterion}\n"
    
    # Prepare the issue fields with only essential fields
    issue_fields = {
        "project": {"key": os.getenv("JIRA_PROJECT_KEY")},
        "summary": ticket_data["summary"],
        "description": description,
        "issuetype": {"name": issue_type_map.get(ticket_data["type"], "Task")},
        "labels": ticket_data["labels"]
    }
    
    # Add story points if they exist (for all ticket types)
    if ticket_data.get("story_points") is not None:
        issue_fields["customfield_10016"] = ticket_data["story_points"]  # Story Point Estimate field
    
    # Handle parent relationships
    if ticket_data.get("parent_ticket") and ticket_data.get("parent_ticket") in created_tickets:
        # For subtasks and tasks under stories
        parent_key = created_tickets[ticket_data["parent_ticket"]]
        issue_fields["parent"] = {"key": parent_key}
    elif ticket_data.get("epic_link") and ticket_data.get("epic_link") in created_tickets:
        # For stories under epics
        epic_key = created_tickets[ticket_data["epic_link"]]
        issue_fields["customfield_10014"] = epic_key  # Epic Link field
    
    # Create the issue
    try:
        issue = jira.create_issue(fields=issue_fields)
        print(f"Created {ticket_data['type']} {issue.key} from {ticket_data['id']}")
        
        # Create Relates link for Tasks to their parent Stories
        if ticket_data["type"] == "Task" and ticket_data.get("parent_ticket") and ticket_data.get("parent_ticket") in created_tickets:
            parent_key = created_tickets[ticket_data["parent_ticket"]]
            try:
                jira.create_issue_link(
                    type="Relates",
                    inwardIssue=issue.key,
                    outwardIssue=parent_key
                )
                print(f"Created Relates link: {issue.key} relates to {parent_key}")
            except Exception as e:
                print(f"Warning: Could not create Relates link between {issue.key} and {parent_key}: {str(e)}")
        
        # Update relationships after creation
        if ticket_data.get("depends_on"):
            for dep_id in ticket_data["depends_on"]:
                if dep_id in created_tickets:
                    dep_key = created_tickets[dep_id]
                    try:
                        jira.create_issue_link(
                            type="Depends",
                            inwardIssue=issue.key,
                            outwardIssue=dep_key
                        )
                        print(f"Created dependency link: {issue.key} depends on {dep_key}")
                    except Exception as e:
                        print(f"Warning: Could not create dependency link between {issue.key} and {dep_key}: {str(e)}")
        
        if ticket_data.get("blocks"):
            for block_id in ticket_data["blocks"]:
                if block_id in created_tickets:
                    block_key = created_tickets[block_id]
                    try:
                        jira.create_issue_link(
                            type="Blocks",
                            inwardIssue=issue.key,
                            outwardIssue=block_key
                        )
                        print(f"Created blocks link: {issue.key} blocks {block_key}")
                    except Exception as e:
                        print(f"Warning: Could not create blocks link between {issue.key} and {block_key}: {str(e)}")
        
        return issue.key
    except Exception as e:
        print(f"Error creating {ticket_data['type']} {ticket_data['id']}: {str(e)}")
        raise

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
    for ticket_data in tickets:
        if ticket_data["type"] == "Epic":
            try:
                jira_key = create_jira_ticket(jira, ticket_data, created_tickets, jira_username, jira_username)
                created_tickets[ticket_data["id"]] = jira_key
                print(f"Created Epic {jira_key} from {ticket_data['id']}")
            except Exception as e:
                print(f"Error creating Epic {ticket_data['id']}: {str(e)}")
    
    # Then create all other tickets
    for ticket_data in tickets:
        if ticket_data["type"] != "Epic":
            try:
                jira_key = create_jira_ticket(jira, ticket_data, created_tickets, jira_username, jira_username)
                created_tickets[ticket_data["id"]] = jira_key
                print(f"Created {ticket_data['type']} {jira_key} from {ticket_data['id']}")
                
                # Assign ticket to sprint if it has one
                if ticket_data.get("sprint_id") and ticket_data["sprint_id"] in created_sprints:
                    try:
                        jira.add_issues_to_sprint(created_sprints[ticket_data["sprint_id"]], [jira_key])
                        print(f"Added ticket {jira_key} to sprint {ticket_data['sprint_id']}")
                    except Exception as e:
                        print(f"Warning: Could not add ticket {jira_key} to sprint {ticket_data['sprint_id']}: {str(e)}")
                
                # Assign ticket to fix version if it has one
                if ticket_data.get("fix_versions"):
                    for version_id in ticket_data["fix_versions"]:
                        if version_id in created_versions:
                            try:
                                # Get the version object
                                version = jira.version(created_versions[version_id])
                                # Add the version to the issue's fix versions
                                issue = jira.issue(jira_key)
                                current_versions = issue.fields.fixVersions
                                current_versions.append({"id": version.id})
                                issue.update(fields={"fixVersions": current_versions})
                                print(f"Added ticket {jira_key} to fix version {version_id}")
                            except Exception as e:
                                print(f"Warning: Could not add ticket {jira_key} to fix version {version_id}: {str(e)}")
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