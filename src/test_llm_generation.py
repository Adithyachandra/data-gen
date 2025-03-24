import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from src.models.team import Team, TeamMember, Role, Department, Seniority, Skill
from src.models.ticket import Component, TicketType
from src.models.communication import MeetingType
from src.generators.llm_generator import LLMGenerator
from src.generators.team_generator import TeamGenerator
from src.generators.ticket_generator import TicketGenerator
from src.generators.communication_generator import CommunicationGenerator
from src.generators.activity_generator import ActivityGenerator
import json

def test_llm_generation():
    """Test LLM-enhanced data generation."""
    print("\n=== Testing LLM-Enhanced Data Generation ===\n")
    
    # Initialize generators
    team_generator = TeamGenerator()
    team_generator.generate_organization()  # Generate the organization structure
    team_members = team_generator.get_all_members()
    teams = team_generator.get_all_teams()

    # Find a team that has a tech lead
    selected_team = None
    selected_team_members = []
    tech_lead = None
    
    for team in teams.values():
        team_members_list = [m for m in team_members.values() if m.team_id == team.id]
        tech_lead_candidates = [m for m in team_members_list if m.role == Role.TECH_LEAD]
        if tech_lead_candidates:
            selected_team = team
            selected_team_members = team_members_list
            tech_lead = tech_lead_candidates[0]
            break
    
    if not selected_team:
        raise ValueError("No team with a tech lead found. Please check team generation.")

    # Initialize other generators
    ticket_generator = TicketGenerator(team_members, teams)
    communication_generator = CommunicationGenerator(team_members, teams)

    # Generate a sample ticket
    sprint = ticket_generator.generate_sprint(selected_team.id)
    component_str = selected_team.components[0]
    component = Component[component_str.upper()]  # Convert string to enum value
    sprint_tickets = ticket_generator.generate_sprint_tickets(sprint, component)
    sample_ticket = next(iter(sprint_tickets["stories"]))  # Get first story ticket

    # Find senior engineers
    senior_engineers = [m for m in selected_team_members if m.role == Role.SENIOR_ENGINEER]

    # Generate a technical discussion meeting
    tech_discussion = communication_generator.generate_meeting(
        organizer=tech_lead,
        attendees=selected_team_members,
        meeting_type="Technical Discussion",
        context={"ticket": sample_ticket}
    )
    print("\nGenerated Technical Discussion Meeting:")
    print(json.dumps(tech_discussion.dict(), indent=2, default=str))

    # Generate a code review activity
    code_review = ticket_generator.llm.generate_code_review_comment(
        code_snippet="def process_data(data):\n    result = []\n    for item in data:\n        if item > 0:\n            result.append(item * 2)\n    return result",
        context=f"Code review by {tech_lead.name} for performance optimization"
    )
    print("\nGenerated Code Review Comment:")
    print(code_review)

    # Generate an email
    email_content = ticket_generator.llm.generate_email_content(
        sender_name=tech_lead.name,
        recipient_names=[m.name for m in selected_team_members[:2]],  # First two team members
        subject="Sprint Planning Follow-up",
        context={"ticket": sample_ticket, "sprint": sprint}
    )
    print("\nGenerated Email Content:")
    print(email_content)

    # Generate a sprint planning meeting
    sprint_planning = communication_generator.generate_meeting(
        organizer=tech_lead,
        attendees=selected_team_members,
        meeting_type="Sprint Planning",
        context={"sprint": sprint, "tickets": sprint_tickets}
    )
    print("\nGenerated Sprint Planning Meeting:")
    print(json.dumps(sprint_planning.dict(), indent=2, default=str))

if __name__ == "__main__":
    test_llm_generation() 