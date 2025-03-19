from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime

class ActivityType(str, Enum):
    TICKET_CREATE = "ticket_create"
    TICKET_UPDATE = "ticket_update"
    TICKET_COMMENT = "ticket_comment"
    TICKET_STATUS_CHANGE = "ticket_status_change"
    TICKET_ASSIGN = "ticket_assign"
    SPRINT_CREATE = "sprint_create"
    SPRINT_UPDATE = "sprint_update"
    SPRINT_COMPLETE = "sprint_complete"
    MEETING_CREATE = "meeting_create"
    MEETING_ATTEND = "meeting_attend"
    CHANNEL_CREATE = "channel_create"
    CHANNEL_JOIN = "channel_join"
    MESSAGE_SEND = "message_send"
    MENTION = "mention"
    REACTION_ADD = "reaction_add"
    CODE_REVIEW = "code_review"

class ActivityCategory(str, Enum):
    TICKET = "ticket"
    SPRINT = "sprint"
    MEETING = "meeting"
    COMMUNICATION = "communication"
    WORKFLOW = "workflow"

class Activity(BaseModel):
    id: str = Field(..., description="Unique identifier for the activity")
    type: ActivityType = Field(..., description="Type of activity")
    category: ActivityCategory = Field(..., description="Category of activity")
    user_id: str = Field(..., description="ID of the user who performed the activity")
    timestamp: datetime = Field(..., description="When the activity occurred")
    
    # Context
    team_id: Optional[str] = Field(None, description="ID of the team involved")
    ticket_id: Optional[str] = Field(None, description="ID of the related ticket")
    sprint_id: Optional[str] = Field(None, description="ID of the related sprint")
    meeting_id: Optional[str] = Field(None, description="ID of the related meeting")
    channel_id: Optional[str] = Field(None, description="ID of the related channel")
    message_id: Optional[str] = Field(None, description="ID of the related message")
    
    # Details
    details: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional details about the activity"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata about the activity"
    )

class UserActivitySummary(BaseModel):
    user_id: str = Field(..., description="ID of the user")
    period_start: datetime = Field(..., description="Start of the summary period")
    period_end: datetime = Field(..., description="End of the summary period")
    
    # Activity counts
    total_activities: int = Field(default=0, description="Total number of activities")
    activities_by_type: Dict[ActivityType, int] = Field(
        default_factory=dict,
        description="Count of activities by type"
    )
    activities_by_category: Dict[ActivityCategory, int] = Field(
        default_factory=dict,
        description="Count of activities by category"
    )
    
    # Ticket metrics
    tickets_created: int = Field(default=0, description="Number of tickets created")
    tickets_resolved: int = Field(default=0, description="Number of tickets resolved")
    tickets_commented: int = Field(default=0, description="Number of tickets commented on")
    average_ticket_resolution_time: Optional[float] = Field(
        None,
        description="Average time to resolve tickets (hours)"
    )
    
    # Communication metrics
    messages_sent: int = Field(default=0, description="Number of messages sent")
    mentions_received: int = Field(default=0, description="Number of times mentioned")
    reactions_received: int = Field(default=0, description="Number of reactions received")
    meetings_attended: int = Field(default=0, description="Number of meetings attended")
    
    # Collaboration metrics
    unique_collaborators: int = Field(default=0, description="Number of unique people interacted with")
    teams_collaborated_with: List[str] = Field(
        default_factory=list,
        description="IDs of teams collaborated with"
    )
    most_active_channels: List[str] = Field(
        default_factory=list,
        description="IDs of channels most active in"
    )
    
    # Time distribution
    time_in_meetings: float = Field(
        default=0.0,
        description="Total hours spent in meetings"
    )
    activity_by_hour: Dict[int, int] = Field(
        default_factory=dict,
        description="Distribution of activities by hour of day"
    )
    activity_by_day: Dict[str, int] = Field(
        default_factory=dict,
        description="Distribution of activities by day of week"
    ) 