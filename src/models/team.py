from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime

class Department(str, Enum):
    ENGINEERING = "Engineering"
    PRODUCT = "Product"
    DESIGN = "Design"
    QA = "Quality Assurance"
    SALES = "Sales"
    MARKETING = "Marketing"
    CUSTOMER_SUPPORT = "Customer Support"
    FINANCE = "Finance"
    HR = "HR"
    LEGAL = "Legal"
    OPERATIONS = "Operations"

class Role(str, Enum):
    # Engineering Roles
    CTO = "Chief Technology Officer"
    VP_ENGINEERING = "VP of Engineering"
    ENGINEERING_MANAGER = "Engineering Manager"
    TECH_LEAD = "Tech Lead"
    SENIOR_ENGINEER = "Senior Software Engineer"
    SOFTWARE_ENGINEER = "Software Engineer"
    JUNIOR_ENGINEER = "Junior Software Engineer"
    QA_ENGINEER = "QA Engineer"
    DEVOPS_ENGINEER = "DevOps Engineer"
    SECURITY_ENGINEER = "Security Engineer"
    
    # Product Roles
    CPO = "Chief Product Officer"
    VP_PRODUCT = "VP of Product"
    PRODUCT_MANAGER = "Product Manager"
    PRODUCT_OWNER = "Product Owner"
    UX_DESIGNER = "UX Designer"
    UI_DESIGNER = "UI Designer"
    PRODUCT_ANALYST = "Product Analyst"
    
    # Sales Roles
    CRO = "Chief Revenue Officer"
    VP_SALES = "VP of Sales"
    SALES_DIRECTOR = "Sales Director"
    ACCOUNT_EXECUTIVE = "Account Executive"
    SALES_ENGINEER = "Sales Engineer"
    SALES_OPS = "Sales Operations"
    
    # Customer Support Roles
    VP_SUPPORT = "VP of Customer Support"
    SUPPORT_MANAGER = "Support Manager"
    SENIOR_SUPPORT = "Senior Support Engineer"
    SUPPORT_ENGINEER = "Support Engineer"
    CUSTOMER_SUCCESS = "Customer Success Manager"
    
    # Finance Roles
    CFO = "Chief Financial Officer"
    VP_FINANCE = "VP of Finance"
    FINANCE_MANAGER = "Finance Manager"
    FINANCIAL_ANALYST = "Financial Analyst"
    ACCOUNTANT = "Accountant"
    
    # HR Roles
    CHRO = "Chief HR Officer"
    VP_HR = "VP of Human Resources"
    HR_MANAGER = "HR Manager"
    HR_SPECIALIST = "HR Specialist"
    RECRUITER = "Technical Recruiter"
    
    # Marketing Roles
    CMO = "Chief Marketing Officer"
    VP_MARKETING = "VP of Marketing"
    MARKETING_MANAGER = "Marketing Manager"
    CONTENT_MANAGER = "Content Manager"
    GROWTH_MARKETER = "Growth Marketing Specialist"
    
    # Operations Roles
    COO = "Chief Operating Officer"
    VP_OPS = "VP of Operations"
    OPERATIONS_MANAGER = "Operations Manager"
    PROJECT_MANAGER = "Project Manager"
    SCRUM_MASTER = "Scrum Master"

class Skill(str, Enum):
    # Technical Skills
    PYTHON = "Python"
    JAVA = "Java"
    JAVASCRIPT = "JavaScript"
    TYPESCRIPT = "TypeScript"
    REACT = "React"
    NODE = "Node.js"
    AWS = "AWS"
    DEVOPS = "DevOps"
    DATABASE = "Database"
    TESTING = "Testing"
    SECURITY = "Security"
    
    # Product Skills
    PRODUCT_MANAGEMENT = "Product Management"
    UX_DESIGN = "UX Design"
    UI_DESIGN = "UI Design"
    PRODUCT_ANALYTICS = "Product Analytics"
    AGILE = "Agile Methodologies"
    
    # Sales Skills
    SALES_METHODOLOGY = "Sales Methodology"
    CRM = "CRM Systems"
    NEGOTIATION = "Negotiation"
    SALES_ANALYTICS = "Sales Analytics"
    
    # Support Skills
    CUSTOMER_SERVICE = "Customer Service"
    TECHNICAL_SUPPORT = "Technical Support"
    TROUBLESHOOTING = "Troubleshooting"
    DOCUMENTATION = "Documentation"
    
    # Business Skills
    PROJECT_MANAGEMENT = "Project Management"
    TEAM_LEADERSHIP = "Team Leadership"
    COMMUNICATION = "Communication"
    PRESENTATION = "Presentation"
    ANALYTICS = "Data Analytics"
    
    # Domain Skills
    FINANCE = "Finance"
    ACCOUNTING = "Accounting"
    HR_MANAGEMENT = "HR Management"
    RECRUITMENT = "Recruitment"
    MARKETING = "Marketing"
    CONTENT_CREATION = "Content Creation"

class SeniorityLevel(str, Enum):
    C_LEVEL = "C-Level"
    VP = "Vice President"
    DIRECTOR = "Director"
    MANAGER = "Manager"
    SENIOR = "Senior"
    MID = "Mid-Level"
    JUNIOR = "Junior"
    ENTRY = "Entry Level"

class Seniority(str, Enum):
    JUNIOR = "Junior"
    MID = "Mid-level"
    MID_LEVEL = "Mid-level"  # Alias for MID
    SENIOR = "Senior"
    LEAD = "Lead"
    PRINCIPAL = "Principal"

class TeamMember(BaseModel):
    id: str = Field(..., description="JIRA account ID")
    name: str = Field(..., description="Display name from JIRA")
    email: Optional[str] = Field(None, description="Email address from JIRA")
    role: Optional[str] = Field(None, description="Role from JIRA")
    active: bool = Field(True, description="Whether the user is active in JIRA")
    timezone: Optional[str] = Field(None, description="Timezone from JIRA")
    locale: Optional[str] = Field(None, description="Locale from JIRA")

class Team(BaseModel):
    id: str = Field(..., description="JIRA team ID")
    name: str = Field(..., description="Team name from JIRA")
    description: Optional[str] = Field(None, description="Team description from JIRA")
    members: List[TeamMember] = Field(default_factory=list, description="Team members from JIRA")

class BusinessUnit(BaseModel):
    id: str
    name: str
    description: str
    head_id: str
    departments: List[str] = []
    teams: List[Team] = []
    budget: Optional[float] = None
    headcount: Optional[int] = None
    location: Optional[str] = None 