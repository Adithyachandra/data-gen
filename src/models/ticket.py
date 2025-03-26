from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime

class TicketType(str, Enum):
    EPIC = "Epic"
    STORY = "Story"
    TASK = "Task"
    SUBTASK = "Sub-task"
    BUG = "Bug"

class TicketStatus(str, Enum):
    TO_DO = "To Do"
    IN_PROGRESS = "In Progress"
    IN_REVIEW = "In Review"
    BLOCKED = "Blocked"
    DONE = "Done"

class TicketPriority(str, Enum):
    HIGHEST = "Highest"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    LOWEST = "Lowest"

class Component(str, Enum):
    FRONTEND = "Frontend"
    BACKEND = "Backend"
    DATABASE = "Database"
    INFRASTRUCTURE = "Infrastructure"
    SECURITY = "Security"
    TESTING = "Testing"

class SprintStatus(str, Enum):
    PLANNED = "Planned"
    ACTIVE = "Active"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"

class Sprint(BaseModel):
    id: str = Field(..., description="Unique identifier for the sprint")
    name: str = Field(..., description="Sprint name (e.g., 'Sprint 23')")
    goal: str = Field(..., description="Sprint goal")
    start_date: datetime = Field(..., description="Sprint start date")
    end_date: datetime = Field(..., description="Sprint end date")
    status: SprintStatus = Field(default=SprintStatus.PLANNED, description="Current sprint status")
    tickets: List[str] = Field(default_factory=list, description="IDs of tickets in the sprint")
    story_points_committed: int = Field(default=0, description="Story points committed for the sprint")
    story_points_completed: int = Field(default=0, description="Story points completed in the sprint")
    team_id: str = Field(..., description="ID of the team running this sprint")
    retrospective_notes: Optional[str] = Field(None, description="Notes from sprint retrospective")
    demo_date: Optional[datetime] = Field(None, description="Date of sprint demo")
    planning_notes: Optional[str] = Field(None, description="Notes from sprint planning")
    velocity: Optional[float] = Field(None, description="Actual velocity achieved in the sprint")

class Comment(BaseModel):
    id: str = Field(..., description="Unique identifier for the comment")
    author_id: str = Field(..., description="ID of the team member who wrote the comment")
    content: str = Field(..., description="Content of the comment")
    created_at: datetime = Field(..., description="When the comment was created")
    updated_at: Optional[datetime] = Field(None, description="When the comment was last updated")
    reactions: Dict[str, List[str]] = Field(default_factory=dict, description="Reactions to the comment (emoji: [user_ids])")

class FixVersion(BaseModel):
    id: str = Field(..., description="Unique identifier for the version")
    name: str = Field(..., description="Version name (e.g., 'v1.2.3')")
    description: Optional[str] = Field(None, description="Version description")
    release_date: Optional[datetime] = Field(None, description="Planned release date")
    released: bool = Field(False, description="Whether this version has been released")

class TicketRelationType(str, Enum):
    BLOCKS = "blocks"
    BLOCKED_BY = "blocked by"
    CLONES = "clones"
    CLONED_BY = "cloned by"
    DUPLICATES = "duplicates"
    DUPLICATED_BY = "duplicated by"
    RELATES_TO = "relates to"
    IMPLEMENTS = "implements"
    IMPLEMENTED_BY = "implemented by"
    DEPENDS_ON = "depends on"
    REQUIRED_FOR = "required for"

class Ticket(BaseModel):
    id: str = Field(..., description="Unique identifier for the ticket")
    type: TicketType = Field(..., description="Type of the ticket")
    summary: str = Field(..., description="Brief summary/title of the ticket")
    description: str = Field(..., description="Detailed description of the ticket")
    status: TicketStatus = Field(default=TicketStatus.TO_DO, description="Current status")
    priority: TicketPriority = Field(default=TicketPriority.MEDIUM, description="Ticket priority")
    
    # Relationships
    epic_link: Optional[str] = Field(None, description="ID of parent epic")
    parent_ticket: Optional[str] = Field(None, description="ID of parent ticket (for sub-tasks)")
    subtasks: List[str] = Field(default_factory=list, description="IDs of subtasks")
    related_tickets: List[str] = Field(default_factory=list, description="IDs of related tickets")
    sprint_id: Optional[str] = Field(None, description="ID of the sprint this ticket is part of")
    
    # Dependencies and Relationships
    blocks: List[str] = Field(default_factory=list, description="IDs of tickets that this ticket blocks")
    blocked_by: List[str] = Field(default_factory=list, description="IDs of tickets that block this ticket")
    depends_on: List[str] = Field(default_factory=list, description="IDs of tickets this ticket depends on")
    required_for: List[str] = Field(default_factory=list, description="IDs of tickets that require this ticket")
    clones: List[str] = Field(default_factory=list, description="IDs of tickets that this ticket clones")
    cloned_by: List[str] = Field(default_factory=list, description="IDs of tickets that clone this ticket")
    duplicates: List[str] = Field(default_factory=list, description="IDs of tickets that this ticket duplicates")
    duplicated_by: List[str] = Field(default_factory=list, description="IDs of tickets that duplicate this ticket")
    implements: List[str] = Field(default_factory=list, description="IDs of tickets that this ticket implements")
    implemented_by: List[str] = Field(default_factory=list, description="IDs of tickets that implement this ticket")
    blocking_reason: Optional[str] = Field(None, description="Reason why the ticket is blocked (if status is BLOCKED)")
    relationship_notes: Dict[str, Dict[str, str]] = Field(
        default_factory=dict,
        description="Notes explaining the relationships (e.g., {'duplicates': {'TICK-123': 'Exact same issue in mobile app'}}"
    )
    
    # Assignment and tracking
    reporter_id: str = Field(..., description="ID of team member who created the ticket")
    assignee_id: Optional[str] = Field(None, description="ID of team member assigned to the ticket")
    watchers: List[str] = Field(default_factory=list, description="IDs of team members watching the ticket")
    
    # Components and versions
    components: List[Component] = Field(default_factory=list, description="Components affected by this ticket")
    fix_versions: List[str] = Field(default_factory=list, description="IDs of versions where this will be fixed")
    affected_versions: List[str] = Field(default_factory=list, description="IDs of versions affected by this issue")
    
    # Dates and time tracking
    created_at: datetime = Field(..., description="When the ticket was created")
    updated_at: datetime = Field(..., description="When the ticket was last updated")
    resolved_at: Optional[datetime] = Field(None, description="When the ticket was resolved")
    due_date: Optional[datetime] = Field(None, description="When the ticket is due")
    estimated_hours: Optional[float] = Field(None, description="Estimated hours of work")
    spent_hours: float = Field(default=0, description="Actual hours spent")
    blocked_since: Optional[datetime] = Field(None, description="When the ticket became blocked")
    
    # Additional fields
    labels: List[str] = Field(default_factory=list, description="Labels/tags attached to the ticket")
    comments: List[Comment] = Field(default_factory=list, description="Comments on the ticket")
    story_points: Optional[int] = Field(None, description="Story points (for stories and epics)")
    environment: Optional[str] = Field(None, description="Environment where issue occurs (for bugs)")
    acceptance_criteria: Optional[List[str]] = Field(None, description="Acceptance criteria (for stories)")

class Epic(Ticket):
    type: TicketType = TicketType.EPIC
    child_stories: List[str] = Field(default_factory=list, description="IDs of stories in this epic")
    target_start: Optional[datetime] = Field(None, description="Target start date for the epic")
    target_end: Optional[datetime] = Field(None, description="Target end date for the epic")

class Story(Ticket):
    type: TicketType = TicketType.STORY
    user_persona: Optional[str] = Field(None, description="User persona this story relates to")
    business_value: Optional[str] = Field(None, description="Description of business value")

class Task(Ticket):
    type: TicketType = TicketType.TASK
    technical_details: Optional[str] = Field(None, description="Technical implementation details")
    story_points: Optional[int] = Field(None, description="Story points for the task")
    estimated_hours: Optional[float] = None  # Keep for backward compatibility but mark as deprecated

class Subtask(Ticket):
    type: TicketType = TicketType.SUBTASK
    parent_ticket: str = Field(..., description="ID of parent ticket (required for subtasks)")
    story_points: Optional[int] = Field(None, description="Story points for the subtask")

class Bug(Ticket):
    type: TicketType = TicketType.BUG
    severity: TicketPriority = Field(..., description="Severity of the bug")
    steps_to_reproduce: List[str] = Field(..., description="Steps to reproduce the bug")
    actual_behavior: str = Field(..., description="What actually happens")
    expected_behavior: str = Field(..., description="What should happen")
    workaround: Optional[str] = Field(None, description="Temporary workaround if available") 