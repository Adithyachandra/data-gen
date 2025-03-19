from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from enum import Enum

class CompanySize(str, Enum):
    STARTUP = "Startup"  # < 50 employees
    SMALL = "Small"      # 50-200 employees
    MEDIUM = "Medium"    # 201-1000 employees
    LARGE = "Large"      # 1001-5000 employees
    ENTERPRISE = "Enterprise"  # > 5000 employees

class Industry(str, Enum):
    FINTECH = "Financial Technology"
    HEALTHTECH = "Healthcare Technology"
    ECOMMERCE = "E-Commerce"
    ENTERPRISE = "Enterprise Software"
    GAMING = "Gaming"
    EDTECH = "Educational Technology"
    CYBERSECURITY = "Cybersecurity"
    AI_ML = "AI/ML"
    BLOCKCHAIN = "Blockchain"
    OTHER = "Other"

class DevelopmentMethodology(str, Enum):
    SCRUM = "Scrum"
    KANBAN = "Kanban"
    SCRUMBAN = "Scrumban"
    WATERFALL = "Waterfall"
    CUSTOM = "Custom"

class CompanyConfig(BaseModel):
    # Basic company information
    name: str = Field(..., description="Company name")
    industry: Industry = Field(..., description="Primary industry")
    size: CompanySize = Field(..., description="Company size category")
    description: str = Field(..., description="Brief company description")
    
    # Development methodology
    methodology: DevelopmentMethodology = Field(..., description="Development methodology used")
    sprint_duration_days: Optional[int] = Field(14, description="Sprint duration in days (if applicable)")
    working_days: List[int] = Field(default=[0,1,2,3,4], description="Working days (0=Monday, 6=Sunday)")
    
    # Team structure
    min_team_size: int = Field(default=3, description="Minimum members per team")
    max_team_size: int = Field(default=8, description="Maximum members per team")
    required_roles_per_team: Dict[str, int] = Field(
        default={
            "Tech Lead": 1,
            "Senior Software Engineer": 1,
            "Software Engineer": 2,
        },
        description="Required roles and their count per team"
    )
    
    # Project configuration
    project_prefix: str = Field(..., description="Prefix for JIRA tickets (e.g., 'PROJ')")
    default_story_points: List[int] = Field(
        default=[1, 2, 3, 5, 8, 13, 21],
        description="Valid story point values"
    )
    
    # Communication patterns
    email_domain: str = Field(..., description="Company email domain")
    meeting_timezone: str = Field(default="UTC", description="Default timezone for meetings")
    standard_meetings: List[str] = Field(
        default=[
            "Daily Standup",
            "Sprint Planning",
            "Sprint Review",
            "Sprint Retrospective"
        ],
        description="Standard recurring meetings"
    )
    
    # Work patterns
    work_hours: Dict[str, str] = Field(
        default={
            "start": "09:00",
            "end": "17:00"
        },
        description="Standard work hours"
    )
    
    # Data generation settings
    ticket_complexity_distribution: Dict[str, float] = Field(
        default={
            "low": 0.3,
            "medium": 0.5,
            "high": 0.2
        },
        description="Distribution of ticket complexity"
    )
    communication_style: Dict[str, float] = Field(
        default={
            "formal": 0.3,
            "casual": 0.5,
            "technical": 0.2
        },
        description="Distribution of communication styles"
    )
    bug_frequency: float = Field(
        default=0.2,
        description="Frequency of bugs relative to features"
    )
    
    class Config:
        use_enum_values = True 