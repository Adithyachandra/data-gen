from datetime import datetime, time
from src.config.company_config import (
    CompanyConfig,
    CompanySize,
    Industry,
    DevelopmentMethodology
)

# Detailed product scenarios and features
PRODUCT_SCENARIOS = {
    "Enterprise Workflow Automation": {
        "description": """
        InnovaTech's core product is an AI-powered workflow automation platform that helps enterprises 
        streamline their business processes. The platform includes:
        - Smart document processing with OCR and NLP
        - Automated approval workflows with role-based access
        - Integration with major enterprise systems (SAP, Salesforce, etc.)
        - Real-time analytics and process monitoring
        - Compliance and audit trail features
        """,
        "key_features": [
            "Document Intelligence Engine",
            "Workflow Designer",
            "Integration Hub",
            "Analytics Dashboard",
            "Compliance Manager"
        ],
        "user_personas": [
            {
                "role": "Process Manager",
                "needs": [
                    "Design and optimize workflows",
                    "Monitor process performance",
                    "Generate compliance reports"
                ]
            },
            {
                "role": "Department Head",
                "needs": [
                    "Approve/reject requests",
                    "View department analytics",
                    "Manage team permissions"
                ]
            },
            {
                "role": "End User",
                "needs": [
                    "Submit requests",
                    "Track request status",
                    "Complete assigned tasks"
                ]
            }
        ],
        "current_challenges": [
            "Scale OCR processing for high-volume documents",
            "Improve ML model accuracy for document classification",
            "Reduce workflow bottlenecks in approval processes",
            "Enhance real-time monitoring capabilities",
            "Strengthen security measures for sensitive data"
        ]
    }
}

# Epic themes and initiatives
PRODUCT_INITIATIVES = {
    "AI Enhancement": {
        "description": "Improve AI capabilities across the platform",
        "objectives": [
            "Enhance document classification accuracy by 20%",
            "Implement automated anomaly detection",
            "Add intelligent workflow recommendations"
        ],
        "success_metrics": [
            "ML model accuracy",
            "Processing time reduction",
            "User adoption of AI features"
        ]
    },
    "Platform Scalability": {
        "description": "Scale platform to handle enterprise workloads",
        "objectives": [
            "Support 10x increase in document processing",
            "Reduce system latency by 40%",
            "Implement multi-region deployment"
        ],
        "success_metrics": [
            "System throughput",
            "Response time",
            "Error rates under load"
        ]
    },
    "User Experience": {
        "description": "Enhance platform usability and accessibility",
        "objectives": [
            "Redesign workflow designer interface",
            "Implement advanced search capabilities",
            "Add customizable dashboards"
        ],
        "success_metrics": [
            "User satisfaction score",
            "Time to complete common tasks",
            "Support ticket reduction"
        ]
    }
}

# Story templates for different components
STORY_TEMPLATES = {
    "FRONTEND": {
        "features": [
            "Implement drag-and-drop workflow designer",
            "Add real-time collaboration features",
            "Create customizable dashboard widgets",
            "Enhance document preview functionality",
            "Improve mobile responsiveness"
        ],
        "improvements": [
            "Optimize component load time",
            "Enhance error handling and feedback",
            "Implement progressive loading",
            "Add offline support capabilities"
        ]
    },
    "BACKEND": {
        "features": [
            "Implement document processing pipeline",
            "Create workflow execution engine",
            "Build real-time notification system",
            "Develop audit logging service",
            "Add multi-tenant support"
        ],
        "improvements": [
            "Optimize database queries",
            "Implement caching layer",
            "Enhance error handling and recovery",
            "Add performance monitoring"
        ]
    },
    "DATABASE": {
        "features": [
            "Design workflow state storage",
            "Implement document metadata indexing",
            "Create analytics data model",
            "Add audit trail storage",
            "Design caching structure"
        ],
        "improvements": [
            "Optimize query performance",
            "Implement data partitioning",
            "Add data archival process",
            "Enhance backup procedures"
        ]
    },
    "INFRASTRUCTURE": {
        "features": [
            "Set up auto-scaling configuration",
            "Implement blue-green deployment",
            "Add disaster recovery system",
            "Configure monitoring and alerts",
            "Set up CI/CD pipeline"
        ],
        "improvements": [
            "Optimize resource utilization",
            "Enhance security measures",
            "Improve deployment process",
            "Add performance monitoring"
        ]
    }
}

# Meeting scenarios and templates
MEETING_SCENARIOS = {
    "standard": {
        "Daily Standup": {
            "duration_minutes": 15,
            "required_roles": ["Tech Lead", "Senior Software Engineer", "Software Engineer", "QA Engineer"],
            "agenda_template": [
                "What did you complete yesterday?",
                "What are you working on today?",
                "Any blockers or impediments?"
            ]
        },
        "Sprint Planning": {
            "duration_minutes": 120,
            "required_roles": ["Tech Lead", "Senior Software Engineer", "Software Engineer", "QA Engineer"],
            "agenda_template": [
                "Sprint Goal Review",
                "Capacity Planning",
                "Backlog Refinement",
                "Story Point Estimation",
                "Sprint Commitment"
            ]
        },
        "Sprint Review": {
            "duration_minutes": 60,
            "required_roles": ["Tech Lead", "Senior Software Engineer", "Software Engineer", "QA Engineer"],
            "agenda_template": [
                "Sprint Goal Achievement",
                "Demo of Completed Work",
                "Stakeholder Feedback",
                "Next Steps"
            ]
        }
    },
    "adhoc": {
        "Technical Design Review": {
            "triggers": [
                "New epic creation",
                "Complex story implementation",
                "Architecture changes"
            ],
            "duration_minutes": 60,
            "required_roles": ["Tech Lead", "Senior Software Engineer"],
            "optional_roles": ["Software Engineer"],
            "agenda_template": [
                "Design Overview",
                "Technical Requirements",
                "Architecture Considerations",
                "Implementation Approach",
                "Risk Assessment"
            ]
        },
        "Bug Triage": {
            "triggers": [
                "Critical bug reported",
                "Multiple related bugs",
                "Production incident"
            ],
            "duration_minutes": 30,
            "required_roles": ["Tech Lead", "QA Engineer"],
            "optional_roles": ["Senior Software Engineer", "Software Engineer"],
            "agenda_template": [
                "Issue Overview",
                "Impact Assessment",
                "Root Cause Analysis",
                "Action Items"
            ]
        },
        "Code Review Sync": {
            "triggers": [
                "Large PR pending review",
                "Complex implementation discussion",
                "Technical debt resolution"
            ],
            "duration_minutes": 45,
            "required_roles": ["Senior Software Engineer"],
            "optional_roles": ["Tech Lead", "Software Engineer"],
            "agenda_template": [
                "Code Walkthrough",
                "Design Decisions",
                "Implementation Details",
                "Testing Approach"
            ]
        },
        "Blocking Issue Resolution": {
            "triggers": [
                "Sprint blocker identified",
                "Cross-team dependency",
                "Technical impediment"
            ],
            "duration_minutes": 30,
            "required_roles": ["Tech Lead"],
            "optional_roles": ["Senior Software Engineer", "Software Engineer"],
            "agenda_template": [
                "Blocker Overview",
                "Impact Assessment",
                "Solution Options",
                "Action Plan"
            ]
        }
    }
}

# Email templates based on ticket events
EMAIL_TEMPLATES = {
    "ticket_status_update": {
        "subject_template": "[{ticket_id}] Status Update: {ticket_title}",
        "content_sections": [
            "Status Change Summary",
            "Current Progress",
            "Next Steps",
            "Required Actions"
        ]
    },
    "code_review_request": {
        "subject_template": "[{ticket_id}] Code Review Request: {ticket_title}",
        "content_sections": [
            "Implementation Overview",
            "Key Changes",
            "Testing Details",
            "Review Instructions"
        ]
    },
    "blocking_issue_alert": {
        "subject_template": "[{ticket_id}] Blocking Issue Alert: {ticket_title}",
        "content_sections": [
            "Blocker Description",
            "Business Impact",
            "Required Support",
            "Proposed Solutions"
        ]
    },
    "sprint_status_update": {
        "subject_template": "Sprint {sprint_number} Status Update",
        "content_sections": [
            "Sprint Goal Progress",
            "Key Accomplishments",
            "Risks and Blockers",
            "Action Items"
        ]
    }
}

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
    adhoc_meetings=[
        "Technical Design Review",
        "Bug Triage",
        "Code Review Sync",
        "Blocking Issue Resolution"
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
                "tech_stack": ["Python", "AWS", "Database"],
                "focus_areas": [
                    "Document processing pipeline",
                    "Workflow execution engine",
                    "Integration framework"
                ]
            },
            {
                "name": "Frontend Experience",
                "size": 6,
                "tech_stack": ["React", "TypeScript", "Node.js"],
                "focus_areas": [
                    "Workflow designer UI",
                    "Analytics dashboard",
                    "Document viewer"
                ]
            },
            {
                "name": "Platform Infrastructure",
                "size": 5,
                "tech_stack": ["AWS", "DevOps", "Security"],
                "focus_areas": [
                    "Cloud infrastructure",
                    "Security compliance",
                    "Performance optimization"
                ]
            },
            {
                "name": "Data Engineering",
                "size": 6,
                "tech_stack": ["Python", "Database", "AWS"],
                "focus_areas": [
                    "Data pipelines",
                    "Analytics backend",
                    "ML model deployment"
                ]
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