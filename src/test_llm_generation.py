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

def test_llm_generation():
    # Load environment variables
    load_dotenv()
    
    # Verify API key is set
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("Please set OPENAI_API_KEY in your .env file")

    # Create a sample team
    team = Team(
        id="team_1",
        name="Backend Infrastructure",
        description="Core backend infrastructure team responsible for authentication and API services",
        department=Department.ENGINEERING,
        manager_id="mgr_1",
        created_date=datetime.now() - timedelta(days=365),
        members=[
            TeamMember(
                id="mgr_1",
                name="Sarah Johnson",
                role=Role.ENGINEERING_MANAGER,
                email="sarah.j@company.com",
                team_id="team_1",
                department=Department.ENGINEERING,
                seniority=Seniority.SENIOR,
                join_date=datetime.now() - timedelta(days=365),
                skills=[Skill.PYTHON, Skill.AWS, Skill.TEAM_LEADERSHIP],
                reports_to=None,
                direct_reports=["dev_1", "dev_2"],
                certifications=["AWS Solutions Architect"],
                languages=["English", "Spanish"],
                is_remote=False
            ),
            TeamMember(
                id="dev_1",
                name="Alex Chen",
                role=Role.SENIOR_ENGINEER,
                email="alex.c@company.com",
                team_id="team_1",
                department=Department.ENGINEERING,
                seniority=Seniority.SENIOR,
                join_date=datetime.now() - timedelta(days=180),
                skills=[Skill.PYTHON, Skill.AWS, Skill.DATABASE],
                reports_to="mgr_1",
                direct_reports=[],
                certifications=["MongoDB Certified Developer"],
                languages=["English", "Mandarin"],
                is_remote=True
            ),
            TeamMember(
                id="dev_2",
                name="Maria Garcia",
                role=Role.SOFTWARE_ENGINEER,
                email="maria.g@company.com",
                team_id="team_1",
                department=Department.ENGINEERING,
                seniority=Seniority.MID,
                join_date=datetime.now() - timedelta(days=90),
                skills=[Skill.PYTHON, Skill.JAVASCRIPT, Skill.TESTING],
                reports_to="mgr_1",
                direct_reports=[],
                certifications=[],
                languages=["English", "Spanish"],
                is_remote=False
            )
        ],
        tech_stack=[Skill.PYTHON, Skill.AWS, Skill.DATABASE],
        mission="Build and maintain secure, scalable infrastructure components",
        objectives=["Migrate authentication service to new platform", "Implement API gateway"],
        timezone="UTC-8",
        is_virtual=False,
        components=[Component.BACKEND.value, Component.DATABASE.value],
        current_projects=["Authentication Service Migration", "API Gateway Implementation"]
    )

    print("\n=== Testing LLM-Enhanced Data Generation ===\n")

    # Create a dictionary of teams and team members for the generators
    teams = {team.id: team}
    team_members = {member.id: member for member in team.members}

    # Test ticket generation
    print("1. Generating a sample ticket...")
    ticket_gen = TicketGenerator(team_members=team_members, teams=teams)
    epic = ticket_gen.generate_epic(component=Component.BACKEND)
    print(f"Epic Summary: {epic.summary}")
    print(f"Epic Description:\n{epic.description}\n")

    # Test meeting generation
    print("2. Generating a technical discussion meeting...")
    comm_gen = CommunicationGenerator(team_members=team_members, teams=teams)
    meeting = comm_gen.generate_meeting(
        team=team,
        meeting_type=MeetingType.TECHNICAL_DISCUSSION
    )
    print(f"Meeting Title: {meeting.title}")
    print(f"Meeting Notes:\n{meeting.description}")
    if meeting.transcript:
        print(f"\nMeeting Transcript:\n{meeting.transcript}\n")

    # Test activity generation
    print("\n3. Generating code review activity...")
    activity_gen = ActivityGenerator(teams=teams, team_members=team_members)
    activity = activity_gen.generate_code_review_activity(
        ticket=epic,
        reviewer_id=team.members[1].id  # Alex as reviewer
    )
    print(f"Code Review Comment:\n{activity.details['comment']}\n")

if __name__ == "__main__":
    test_llm_generation() 