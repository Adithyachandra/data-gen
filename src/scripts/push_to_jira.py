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

def create_jira_ticket(jira: JIRA, ticket_data: Dict[str, Any], reporter: str, assignee: str) -> str:
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
    
    # Create tickets in JIRA
    created_tickets = {}
    for ticket_id, ticket_data in tickets.items():
        try:
            jira_key = create_jira_ticket(jira, ticket_data, jira_username, jira_username)
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