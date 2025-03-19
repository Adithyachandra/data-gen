from typing import Dict, List, Optional
from datetime import datetime, timedelta
import random

from src.models.team import (
    TeamMember, Team, BusinessUnit, Department,
    Role, Skill, SeniorityLevel
)
from src.models.ticket import Component
from src.generators.utils import (
    generate_id, generate_email, random_date_between,
    random_subset, generate_name
)
from src.config.sample_company import (
    INNOVATECH_CONFIG,
    DEPARTMENT_STRUCTURE,
    BUSINESS_UNITS,
    ROLE_SKILL_REQUIREMENTS,
    DEPARTMENT_CERTIFICATIONS,
    OFFICE_LOCATIONS
)

class TeamGenerator:
    def __init__(self, config=INNOVATECH_CONFIG):
        self.config = config
        self.members: Dict[str, TeamMember] = {}
        self.teams: Dict[str, Team] = {}
        self.business_units: Dict[str, BusinessUnit] = {}
        self.company_start_date = datetime(2020, 1, 1)  # Company founded date

    def generate_organization(self) -> Dict[str, BusinessUnit]:
        """Generate the entire organizational structure."""
        # Generate C-level executives first
        self._generate_executive_team()
        
        # Generate business units and their departments
        for bu_config in BUSINESS_UNITS:
            self._generate_business_unit(bu_config)
        
        return self.business_units

    def _generate_executive_team(self):
        """Generate C-level executives."""
        # Create CEO
        ceo_first, ceo_last = generate_name()
        ceo = TeamMember(
            id=generate_id("EMP"),
            name=f"{ceo_first} {ceo_last}",
            email=generate_email(ceo_first, ceo_last, self.config.email_domain),
            department=Department.OPERATIONS,
            role=Role.COO,  # Using COO as placeholder since we don't have CEO in enum
            seniority=SeniorityLevel.C_LEVEL,
            skills=[Skill.TEAM_LEADERSHIP, Skill.COMMUNICATION],
            join_date=self.company_start_date + timedelta(days=1),
            office_location=OFFICE_LOCATIONS["headquarters"]
        )
        self.members[ceo.id] = ceo

    def _generate_business_unit(self, bu_config: Dict):
        """Generate a business unit and its departments."""
        bu_id = generate_id("BU")
        bu = BusinessUnit(
            id=bu_id,
            name=bu_config["name"],
            description=f"Business unit responsible for {bu_config['name']}",
            head_id="",  # Will be set when we create department heads
            departments=[Department(d) for d in bu_config["departments"]],
            budget=bu_config["budget"],
            headcount=sum(
                sum(team["size"] for team in DEPARTMENT_STRUCTURE[dept]["teams"])
                for dept in bu_config["departments"]
                if dept in DEPARTMENT_STRUCTURE
            ),
            location=bu_config["location"]
        )
        
        # Generate departments
        for dept_name in bu_config["departments"]:
            if dept_name in DEPARTMENT_STRUCTURE:
                self._generate_department(dept_name, bu)
        
        self.business_units[bu_id] = bu

    def _generate_department(self, dept_name: str, business_unit: BusinessUnit):
        """Generate a department's structure."""
        dept_config = DEPARTMENT_STRUCTURE[dept_name]
        
        # Generate department head and required roles
        for role_name in dept_config["required_roles"]:
            member = self._generate_team_member(
                department=Department(dept_name),
                role=Role[role_name],
                seniority=SeniorityLevel.VP if "VP" in role_name else SeniorityLevel.DIRECTOR,
                location=business_unit.location
            )
            if role_name.startswith("C"):  # C-level executive
                business_unit.head_id = member.id
        
        # Generate teams
        for team_config in dept_config["teams"]:
            self._generate_team(team_config, dept_name, business_unit)

    def _generate_team(self, team_config: Dict, dept_name: str, business_unit: BusinessUnit):
        """Generate a team and its members."""
        team_id = generate_id("TEAM")
        
        # Generate team members
        team_members = []
        required_roles = self.config.required_roles_per_team.copy()
        
        # Add team lead first
        lead = self._generate_team_member(
            department=Department(dept_name),
            role=Role.TECH_LEAD,
            seniority=SeniorityLevel.SENIOR,
            location=business_unit.location
        )
        team_members.append(lead)
        self.members[lead.id] = lead
        
        # Generate other team members
        remaining_count = team_config["size"] - 1
        while remaining_count > 0:
            # Determine role based on requirements
            role_name = next(
                (role for role, count in required_roles.items() if count > 0),
                "Software Engineer"
            )
            required_roles[role_name] = required_roles.get(role_name, 0) - 1
            
            # Map role names to Role enum values
            role_mapping = {
                "Senior Software Engineer": Role.SENIOR_ENGINEER,
                "Software Engineer": Role.SOFTWARE_ENGINEER,
                "Junior Software Engineer": Role.JUNIOR_ENGINEER
            }
            
            role = role_mapping.get(role_name, Role.SOFTWARE_ENGINEER)
            
            member = self._generate_team_member(
                department=Department(dept_name),
                role=role,
                seniority=SeniorityLevel.MID,
                location=business_unit.location
            )
            team_members.append(member)
            self.members[member.id] = member
            remaining_count -= 1
        
        # Create team
        # Map team name to component
        component_mapping = {
            "Backend Core": Component.BACKEND,
            "Frontend Experience": Component.FRONTEND,
            "Platform Infrastructure": Component.INFRASTRUCTURE,
            "Data Engineering": Component.DATABASE,
            "Technical Support": Component.TESTING,
            "UX/UI Design": Component.FRONTEND,
            "Product Strategy": Component.FRONTEND,  # Default to frontend for product teams
            "Enterprise Sales": Component.FRONTEND,  # Default to frontend for sales teams
            "Sales Operations": Component.FRONTEND,  # Default to frontend for sales teams
            "Customer Success": Component.FRONTEND,  # Default to frontend for support teams
            "Financial Planning": Component.FRONTEND,  # Default to frontend for finance teams
            "Talent Acquisition": Component.FRONTEND,  # Default to frontend for HR teams
            "Growth Marketing": Component.FRONTEND,  # Default to frontend for marketing teams
            "Content & Communications": Component.FRONTEND  # Default to frontend for marketing teams
        }
        
        # Create team
        team = Team(
            id=team_id,
            name=team_config["name"],
            department=Department(dept_name),
            description=f"Team responsible for {team_config['name']}",
            manager_id=lead.id,
            members=team_members,  # Store TeamMember objects directly
            tech_stack=[Skill(skill) for skill in team_config["tech_stack"]],
            created_date=random_date_between(
                self.company_start_date,
                datetime.now() - timedelta(days=90)
            ),
            timezone=self.config.meeting_timezone,
            is_virtual=random.random() < OFFICE_LOCATIONS["remote_percentage"],
            components=[component_mapping.get(team_config["name"], Component.FRONTEND)]  # Map team name to component
        )
        
        self.teams[team_id] = team
        business_unit.teams.append(team)

    def _generate_team_member(
        self,
        department: Department,
        role: Role,
        seniority: SeniorityLevel,
        location: str
    ) -> TeamMember:
        """Generate a team member with appropriate attributes."""
        first_name, last_name = generate_name()
        
        # Determine skills based on role
        base_skills = ROLE_SKILL_REQUIREMENTS.get(role.value, [])
        skills = [Skill(skill) for skill in base_skills]
        
        # Add random certifications based on department
        certifications = []
        if department.value in DEPARTMENT_CERTIFICATIONS:
            cert_count = random.randint(0, 2)
            if cert_count > 0:
                certifications = random.sample(
                    DEPARTMENT_CERTIFICATIONS[department.value],
                    cert_count
                )
        
        # Determine if remote based on company policy
        is_remote = random.random() < OFFICE_LOCATIONS["remote_percentage"]
        
        member = TeamMember(
            id=generate_id("EMP"),
            name=f"{first_name} {last_name}",
            email=generate_email(first_name, last_name, self.config.email_domain),
            department=department,
            role=role,
            seniority=seniority,
            skills=skills,
            join_date=random_date_between(
                self.company_start_date,
                datetime.now() - timedelta(days=30)
            ),
            certifications=certifications,
            languages=["English"],
            office_location=None if is_remote else location,
            is_remote=is_remote
        )
        
        self.members[member.id] = member
        return member

    def get_all_members(self) -> Dict[str, TeamMember]:
        """Return all generated team members."""
        return self.members

    def get_all_teams(self) -> Dict[str, Team]:
        """Return all generated teams."""
        return self.teams

    def get_member_by_id(self, member_id: str) -> Optional[TeamMember]:
        """Get a team member by their ID."""
        return self.members.get(member_id) 