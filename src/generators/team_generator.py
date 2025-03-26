from typing import Dict, List, Optional
from datetime import datetime, timedelta
import random

from src.models.team import (
    TeamMember, Team, BusinessUnit, Department,
    Role, Skill, Seniority, SeniorityLevel
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
    def __init__(self, config):
        self.config = config
        self.members: Dict[str, TeamMember] = {}
        self.teams: Dict[str, Team] = {}
        self.business_units: Dict[str, BusinessUnit] = {}
        self.company_start_date = datetime(2020, 1, 1)  # Company founded date
        
        # Get company-specific settings from config
        self.company_name = config.get('company', {}).get('name', 'Acme')
        self.industry = config.get('company', {}).get('industry', 'tech')
        self.email_domain = f"{self.company_name.lower().replace(' ', '')}.com"
        self.meeting_timezone = "UTC"  # Default to UTC for now

    def generate_organization(self) -> Dict[str, BusinessUnit]:
        """Generate the entire organizational structure."""
        # Generate business units from config
        for bu_config in self.config.get('business_units', []):
            self._generate_business_unit(bu_config)
        
        return self.business_units

    def _generate_business_unit(self, bu_config: dict):
        """Generate a business unit and its teams."""
        bu_id = f"BU{generate_id()}"
        bu_head = self._generate_team_member(
            name=bu_config.get('head_name', ''),
            role=bu_config.get('head_role', 'Business Unit Head'),
            department=bu_config.get('name', ''),
            seniority=Seniority.PRINCIPAL
        )
        
        business_unit = BusinessUnit(
            id=bu_id,
            name=bu_config.get('name', ''),
            description=bu_config.get('description', ''),
            head_id=bu_head.id,
            departments=bu_config.get('departments', []),
            teams=[]
        )
        
        # Generate teams for this business unit
        for team_config in bu_config.get('teams', []):
            team = self._generate_team(team_config, business_unit)
            business_unit.teams.append(team)
        
        self.business_units[bu_id] = business_unit

    def _generate_team(self, team_config: dict, business_unit: BusinessUnit) -> Team:
        """Generate a team and its members."""
        team_id = f"TEAM{generate_id()}"
        
        # Get department from team config or business unit
        department = team_config.get('department', business_unit.name)
        
        # Create team structure
        team = Team(
            id=team_id,
            name=team_config.get('name', ''),
            department=department,
            description=team_config.get('description', ''),
            manager_id='',  # Will be set after generating members
            members=[],
            tech_stack=team_config.get('tech_stack', []),
            created_date=self.company_start_date,
            mission=team_config.get('mission', ''),
            objectives=team_config.get('objectives', []),
            timezone=self.meeting_timezone,
            is_virtual=team_config.get('is_virtual', False),
            components=team_config.get('components', []),
            current_projects=team_config.get('current_projects', [])
        )
        
        # Generate team members from config
        configured_members = team_config.get('team_members', [])
        for member_config in configured_members:
            member = self._generate_team_member(
                name=member_config.get('name'),
                role=member_config.get('role'),
                department=department,
                seniority=self._determine_seniority(member_config.get('role', ''))
            )
            team.members.append(member)
            
            # Set the first member with a leadership role as team manager
            if not team.manager_id and self._is_leadership_role(member_config.get('role', '')):
                team.manager_id = member.id
        
        # If no manager was set, use the first member as manager
        if not team.manager_id and team.members:
            team.manager_id = team.members[0].id
        
        self.teams[team_id] = team
        return team

    def _determine_seniority(self, role: str) -> Seniority:
        """Determine seniority level based on role."""
        role_lower = role.lower()
        if any(title in role_lower for title in ['lead', 'senior', 'manager', 'head']):
            return Seniority.SENIOR
        elif 'junior' in role_lower:
            return Seniority.JUNIOR
        else:
            return Seniority.MID

    def _is_leadership_role(self, role: str) -> bool:
        """Check if the role is a leadership position."""
        role_lower = role.lower()
        return any(title in role_lower for title in ['lead', 'manager', 'head', 'director', 'vp', 'chief'])

    def _generate_team_member(self, name: str = None, role: str = None, department: str = None, seniority: Seniority = None) -> TeamMember:
        """Generate a team member with the given attributes."""
        member_id = f"EMP{generate_id()}"
        
        if name is None:
            first_name, last_name = generate_name()
            name = f"{first_name} {last_name}"
        
        if role is None:
            role = random.choice(['Software Engineer', 'Senior Software Engineer', 'Junior Software Engineer'])
        
        if department is None:
            department = random.choice(['Engineering', 'Product', 'Design', 'Marketing'])
        
        if seniority is None:
            seniority = random.choice([Seniority.JUNIOR, Seniority.MID_LEVEL, Seniority.SENIOR])
        
        # Generate skills based on role using GPT-4
        skills = self._generate_skills_for_role(role)
        
        member = TeamMember(
            id=member_id,
            name=name,
            email=f"{name.lower().replace(' ', '.')}@{self.email_domain}",
            department=department,
            role=role,
            seniority=seniority,
            skills=skills,
            join_date=random_date_between(self.company_start_date, datetime.now()),
            reports_to=None,
            direct_reports=[],
            certifications=self._generate_certifications_for_role(role),
            languages=['English'],
            office_location=random.choice(['New York, NY', 'San Francisco, CA', 'Remote']),
            is_remote=random.choice([True, False]),
            team_id=None  # Will be set by the team
        )
        
        self.members[member_id] = member
        return member

    def _generate_skills_for_role(self, role: str) -> List[str]:
        """Generate relevant skills for a given role using role context."""
        role_lower = role.lower()
        if 'backend' in role_lower or 'software engineer' in role_lower:
            return random_subset(['Python', 'JavaScript', 'AWS', 'Node.js', 'SQL', 'Docker', 'Kubernetes'])
        elif 'frontend' in role_lower:
            return random_subset(['JavaScript', 'React', 'TypeScript', 'HTML', 'CSS'])
        elif 'devops' in role_lower:
            return random_subset(['AWS', 'Docker', 'Kubernetes', 'Jenkins', 'Terraform'])
        elif 'qa' in role_lower or 'test' in role_lower:
            return random_subset(['Testing', 'Python', 'Selenium', 'Test Automation'])
        else:
            return random_subset(['Python', 'JavaScript', 'AWS', 'React', 'Node.js', 'SQL'])

    def _generate_certifications_for_role(self, role: str) -> List[str]:
        """Generate relevant certifications for a given role."""
        role_lower = role.lower()
        if 'backend' in role_lower or 'software engineer' in role_lower:
            return random_subset(['AWS Certified Solutions Architect', 'Certified Kubernetes Administrator'])
        elif 'devops' in role_lower:
            return random_subset(['AWS Certified DevOps Engineer', 'Certified Kubernetes Administrator'])
        elif 'scrum' in role_lower or 'manager' in role_lower:
            return random_subset(['Certified Scrum Master', 'Project Management Professional'])
        else:
            return random_subset(['AWS Certified Solutions Architect', 'Certified Kubernetes Administrator', 'Certified Scrum Master'])

    def get_all_members(self) -> Dict[str, TeamMember]:
        """Return all generated team members."""
        return self.members

    def get_all_teams(self) -> Dict[str, Team]:
        """Return all generated teams."""
        return self.teams

    def get_member_by_id(self, member_id: str) -> Optional[TeamMember]:
        """Get a team member by their ID."""
        return self.members.get(member_id) 