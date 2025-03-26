import os
import json
from typing import Dict, Any
from datetime import datetime
from jira import JIRA
from dotenv import load_dotenv

def load_tickets(tickets_file: str) -> Dict[str, Any]:
    """Load tickets from the generated JSON file."""
    with open(tickets_file, 'r') as f:
        return json.load(f)

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
    
    # Add story points to description for now
    if ticket_data.get("story_points"):
        description += f"\n\n## Story Points\n{ticket_data['story_points']}"
    
    # Prepare the issue fields with only essential fields
    issue_fields = {
        "project": {"key": os.getenv("JIRA_PROJECT_KEY")},
        "summary": ticket_data["summary"],
        "description": description,
        "issuetype": {"name": issue_type_map.get(ticket_data["type"], "Task")},
        "labels": ticket_data["labels"]
    }
    
    # Handle parent relationships only for Stories under Epics
    if ticket_data["type"] == "Story" and ticket_data.get("epic_link") and ticket_data.get("epic_link") in created_tickets:
        # For Stories under Epics
        epic_key = created_tickets[ticket_data["epic_link"]]
        issue_fields["parent"] = {"key": epic_key}
    
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
    
    # Load generated tickets
    tickets = load_tickets("ticket-gen/tickets.json")
    
    # First, create all Epic tickets
    created_tickets = {}
    for ticket_id, ticket_data in tickets.items():
        if ticket_data["type"] == "Epic":
            try:
                jira_key = create_jira_ticket(jira, ticket_data, created_tickets, jira_username, jira_username)
                created_tickets[ticket_id] = jira_key
                print(f"Created Epic {jira_key} from {ticket_id}")
            except Exception as e:
                print(f"Error creating Epic {ticket_id}: {str(e)}")
    
    # Then create all other tickets
    for ticket_id, ticket_data in tickets.items():
        if ticket_data["type"] != "Epic":
            try:
                jira_key = create_jira_ticket(jira, ticket_data, created_tickets, jira_username, jira_username)
                created_tickets[ticket_id] = jira_key
                print(f"Created ticket {jira_key} from {ticket_id}")
            except Exception as e:
                print(f"Error creating ticket {ticket_id}: {str(e)}")
    
    # Save mapping of generated tickets to JIRA tickets
    with open("ticket-gen/jira_mapping.json", "w") as f:
        json.dump(created_tickets, f, indent=2)
    
    print(f"\nSuccessfully created {len(created_tickets)} tickets in JIRA")
    print("Mapping saved to ticket-gen/jira_mapping.json")

if __name__ == "__main__":
    main() 