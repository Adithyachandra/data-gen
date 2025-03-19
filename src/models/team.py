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
    SENIOR = "Senior"
    LEAD = "Lead"
    PRINCIPAL = "Principal"

class TeamMember(BaseModel):
    id: str = Field(..., description="Unique identifier for the team member")
    name: str = Field(..., description="Full name of the team member")
    email: str = Field(..., description="Work email address")
    department: Department = Field(..., description="Department the member belongs to")
    role: Role = Field(..., description="Current role in the company")
    seniority: Seniority = Field(..., description="Seniority level")
    skills: List[Skill] = Field(default_factory=list, description="Professional skills")
    join_date: datetime = Field(..., description="Date when member joined the company")
    reports_to: Optional[str] = Field(None, description="ID of the manager/lead")
    direct_reports: List[str] = Field(default_factory=list, description="IDs of team members reporting to this person")
    certifications: List[str] = Field(default_factory=list, description="Professional certifications")
    languages: List[str] = Field(default_factory=list, description="Languages spoken")
    office_location: Optional[str] = Field(None, description="Primary office location")
    is_remote: bool = Field(default=False, description="Whether the member works remotely")
    team_id: str = Field(..., description="ID of the team the member belongs to")

class Team(BaseModel):
    id: str = Field(..., description="Unique identifier for the team")
    name: str = Field(..., description="Team name")
    department: Department = Field(..., description="Department this team belongs to")
    description: str = Field(..., description="Brief description of team's responsibilities")
    manager_id: str = Field(..., description="ID of the team manager")
    members: List[TeamMember] = Field(default_factory=list, description="List of team members")
    tech_stack: Optional[List[Skill]] = Field(default_factory=list, description="Technologies/skills used by the team")
    created_date: datetime = Field(..., description="Date when team was formed")
    mission: Optional[str] = Field(None, description="Team's mission statement")
    objectives: List[str] = Field(default_factory=list, description="Team's current objectives")
    timezone: str = Field(default="UTC", description="Primary timezone of the team")
    is_virtual: bool = Field(default=False, description="Whether the team is fully remote")
    components: List[str] = Field(default_factory=list, description="Components owned by the team")
    current_projects: List[str] = Field(default_factory=list, description="Current projects the team is working on")

class BusinessUnit(BaseModel):
    id: str = Field(..., description="Unique identifier for the business unit")
    name: str = Field(..., description="Business unit name")
    description: str = Field(..., description="Business unit description")
    head_id: str = Field(..., description="ID of business unit head")
    departments: List[Department] = Field(..., description="Departments in this business unit")
    teams: List[Team] = Field(default_factory=list, description="Teams in the business unit")
    budget: Optional[float] = Field(None, description="Annual budget allocation")
    headcount: int = Field(..., description="Total number of employees")
    location: Optional[str] = Field(None, description="Primary location of the business unit") 