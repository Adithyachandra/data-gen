from datetime import datetime, time
from src.config.company_config import (
    CompanyConfig,
    CompanySize,
    Industry,
    DevelopmentMethodology
)

INNOVATECH_CONFIG = CompanyConfig(
    # Basic company information
    name="InnovaTech Solutions",
    industry=Industry.ENTERPRISE,
    size=CompanySize.MEDIUM,
    description="InnovaTech Solutions is a leading provider of enterprise workflow automation software, "
                "helping companies streamline their business processes through AI-powered solutions.",
    
    # Development methodology
    methodology=DevelopmentMethodology.SCRUM,
    sprint_duration_days=14,
    working_days=[0, 1, 2, 3, 4],  # Monday to Friday
    
    # Team structure
    min_team_size=5,
    max_team_size=8,
    required_roles_per_team={
        "Tech Lead": 1,
        "Senior Software Engineer": 2,
        "Software Engineer": 2,
        "QA Engineer": 1,
    },
    
    # Project configuration
    project_prefix="INNO",
    default_story_points=[1, 2, 3, 5, 8, 13, 21],
    
    # Communication patterns
    email_domain="innovatech.com",
    meeting_timezone="America/New_York",
    standard_meetings=[
        "Daily Standup",
        "Sprint Planning",
        "Sprint Review",
        "Sprint Retrospective",
        "Tech All-Hands",
        "Company Town Hall"
    ],
    
    # Work patterns
    work_hours={
        "start": "09:00",
        "end": "17:00"
    },
    
    # Data generation settings
    ticket_complexity_distribution={
        "low": 0.3,
        "medium": 0.5,
        "high": 0.2
    },
    communication_style={
        "formal": 0.2,
        "casual": 0.6,
        "technical": 0.2
    },
    bug_frequency=0.15
)

# Sample team distributions per department
DEPARTMENT_STRUCTURE = {
    "Engineering": {
        "teams": [
            {
                "name": "Backend Core",
                "size": 7,
                "tech_stack": ["Python", "AWS", "Database"]
            },
            {
                "name": "Frontend Experience",
                "size": 6,
                "tech_stack": ["React", "TypeScript", "Node.js"]
            },
            {
                "name": "Platform Infrastructure",
                "size": 5,
                "tech_stack": ["AWS", "DevOps", "Security"]
            },
            {
                "name": "Data Engineering",
                "size": 6,
                "tech_stack": ["Python", "Database", "AWS"]
            }
        ],
        "required_roles": ["CTO", "VP_ENGINEERING", "ENGINEERING_MANAGER"]
    },
    "Product": {
        "teams": [
            {
                "name": "Product Strategy",
                "size": 4,
                "tech_stack": ["Product Management", "Data Analytics"]
            },
            {
                "name": "UX/UI Design",
                "size": 5,
                "tech_stack": ["UX Design", "UI Design"]
            }
        ],
        "required_roles": ["CPO", "PRODUCT_MANAGER"]
    },
    "Sales": {
        "teams": [
            {
                "name": "Enterprise Sales",
                "size": 6,
                "tech_stack": ["Sales Methodology", "CRM Systems"]
            },
            {
                "name": "Sales Operations",
                "size": 4,
                "tech_stack": ["Sales Analytics", "CRM Systems"]
            }
        ],
        "required_roles": ["CRO", "VP_SALES", "SALES_DIRECTOR"]
    },
    "Customer Support": {
        "teams": [
            {
                "name": "Technical Support",
                "size": 8,
                "tech_stack": ["Technical Support", "Troubleshooting"]
            },
            {
                "name": "Customer Success",
                "size": 6,
                "tech_stack": ["Customer Service", "CRM Systems"]
            }
        ],
        "required_roles": ["VP_SUPPORT", "SUPPORT_MANAGER"]
    },
    "Finance": {
        "teams": [
            {
                "name": "Financial Planning",
                "size": 4,
                "tech_stack": ["Finance", "Data Analytics"]
            }
        ],
        "required_roles": ["CFO", "FINANCE_MANAGER"]
    },
    "HR": {
        "teams": [
            {
                "name": "Talent Acquisition",
                "size": 5,
                "tech_stack": ["Recruitment", "HR Management"]
            }
        ],
        "required_roles": ["CHRO", "HR_MANAGER"]
    },
    "Marketing": {
        "teams": [
            {
                "name": "Growth Marketing",
                "size": 5,
                "tech_stack": ["Marketing", "Data Analytics"]
            },
            {
                "name": "Content & Communications",
                "size": 4,
                "tech_stack": ["Content Creation", "Marketing"]
            }
        ],
        "required_roles": ["CMO", "MARKETING_MANAGER"]
    }
}

# Sample business units
BUSINESS_UNITS = [
    {
        "name": "Product & Engineering",
        "departments": ["Engineering", "Product"],
        "location": "New York, NY",
        "budget": 5000000
    },
    {
        "name": "Go-to-Market",
        "departments": ["Sales", "Marketing", "Customer Support"],
        "location": "San Francisco, CA",
        "budget": 3000000
    },
    {
        "name": "Operations",
        "departments": ["Finance", "HR", "Operations"],
        "location": "Chicago, IL",
        "budget": 2000000
    }
]

# Sample skill requirements per role
ROLE_SKILL_REQUIREMENTS = {
    "Tech Lead": ["Team Leadership", "Communication", "Python", "AWS"],
    "Senior Software Engineer": ["Python", "AWS", "Database"],
    "Software Engineer": ["Python", "JavaScript", "React"],
    "Product Manager": ["Product Management", "Communication", "Data Analytics"],
    "Sales Engineer": ["Technical Support", "Sales Methodology", "Communication"],
    "Customer Success Manager": ["Customer Service", "Communication", "CRM Systems"],
    "Financial Analyst": ["Finance", "Data Analytics", "Communication"],
    "HR Specialist": ["HR Management", "Recruitment", "Communication"]
}

# Sample certifications per department
DEPARTMENT_CERTIFICATIONS = {
    "Engineering": [
        "AWS Certified Solutions Architect",
        "Certified Kubernetes Administrator",
        "Certified Scrum Master"
    ],
    "Sales": [
        "Salesforce Certified Administrator",
        "Certified Sales Professional",
        "Solution Selling Certification"
    ],
    "Finance": [
        "CPA",
        "CFA",
        "Financial Risk Manager"
    ],
    "HR": [
        "PHR",
        "SHRM-CP",
        "Talent Management Certification"
    ]
}

# Office locations
OFFICE_LOCATIONS = {
    "headquarters": "New York, NY",
    "regional_offices": [
        "San Francisco, CA",
        "Chicago, IL",
        "Austin, TX",
        "London, UK"
    ],
    "remote_allowed": True,
    "remote_percentage": 0.3  # 30% of workforce is remote
} 