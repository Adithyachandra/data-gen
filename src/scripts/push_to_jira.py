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
    
    # Prepare the issue fields with only essential fields
    issue_fields = {
        "project": {"key": os.getenv("JIRA_PROJECT_KEY")},
        "summary": ticket_data["summary"],
        "description": description,
        "issuetype": {"name": issue_type_map.get(ticket_data["type"], "Task")},
        "labels": ticket_data["labels"]
    }
    
    # Add Epic-specific fields if this is an Epic
    if ticket_data["type"] == "Epic":
        # For Epics, we only need to set the issue type to "Epic"
        # The Epic fields will be handled by JIRA's default Epic configuration
        pass
    
    # Add Epic link if it exists and the Epic has already been created
    if ticket_data.get("epic_link") and ticket_data.get("epic_link") in created_tickets:
        epic_key = created_tickets[ticket_data["epic_link"]]
        # In JIRA Next-gen projects, Epics are set as parents
        issue_fields["parent"] = {"key": epic_key}
    # Add parent link if it exists and the parent has already been created
    elif ticket_data.get("parent_ticket") and ticket_data.get("parent_ticket") in created_tickets:
        parent_key = created_tickets[ticket_data["parent_ticket"]]
        issue_fields["parent"] = {"key": parent_key}
    
    # Create the issue
    issue = jira.create_issue(fields=issue_fields)
    
    return issue.key

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