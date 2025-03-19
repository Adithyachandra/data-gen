from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime

class CommunicationType(str, Enum):
    CHAT = "chat"
    EMAIL = "email"
    COMMENT = "comment"
    MENTION = "mention"
    MEETING = "meeting"

class MessagePriority(str, Enum):
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"

class CommunicationChannel(str, Enum):
    TEAM_CHAT = "team_chat"
    PROJECT_CHAT = "project_chat"
    GENERAL = "general"
    TECHNICAL = "technical"
    ANNOUNCEMENTS = "announcements"
    INCIDENTS = "incidents"

class MeetingType(str, Enum):
    STANDUP = "standup"
    SPRINT_PLANNING = "sprint_planning"
    SPRINT_REVIEW = "sprint_review"
    SPRINT_RETRO = "sprint_retrospective"
    TECHNICAL_DISCUSSION = "technical_discussion"
    TEAM_SYNC = "team_sync"
    INCIDENT_REVIEW = "incident_review"

class Message(BaseModel):
    id: str = Field(..., description="Unique identifier for the message")
    type: CommunicationType = Field(..., description="Type of communication")
    sender_id: str = Field(..., description="ID of the team member who sent the message")
    content: str = Field(..., description="Content of the message")
    created_at: datetime = Field(..., description="When the message was sent")
    priority: MessagePriority = Field(default=MessagePriority.NORMAL, description="Priority of the message")
    channel_id: Optional[str] = Field(None, description="ID of the channel (if applicable)")
    thread_id: Optional[str] = Field(None, description="ID of the thread this message belongs to")
    ticket_id: Optional[str] = Field(None, description="ID of the related ticket (if applicable)")
    mentions: List[str] = Field(default_factory=list, description="IDs of team members mentioned")
    reactions: Dict[str, List[str]] = Field(default_factory=dict, description="Reactions to the message")
    attachments: List[str] = Field(default_factory=list, description="List of attachment URLs")

class Thread(BaseModel):
    id: str = Field(..., description="Unique identifier for the thread")
    channel_id: str = Field(..., description="ID of the channel this thread belongs to")
    title: Optional[str] = Field(None, description="Title/subject of the thread")
    created_at: datetime = Field(..., description="When the thread was created")
    last_activity: datetime = Field(..., description="When the last message was sent")
    participants: List[str] = Field(default_factory=list, description="IDs of team members in the thread")
    messages: List[str] = Field(default_factory=list, description="IDs of messages in the thread")
    ticket_id: Optional[str] = Field(None, description="ID of the related ticket (if applicable)")
    resolved: bool = Field(default=False, description="Whether the thread is resolved")

class Channel(BaseModel):
    id: str = Field(..., description="Unique identifier for the channel")
    name: str = Field(..., description="Name of the channel")
    type: CommunicationChannel = Field(..., description="Type of channel")
    description: str = Field(..., description="Description of the channel's purpose")
    created_at: datetime = Field(..., description="When the channel was created")
    team_id: Optional[str] = Field(None, description="ID of the team that owns this channel")
    members: List[str] = Field(default_factory=list, description="IDs of team members in the channel")
    threads: List[str] = Field(default_factory=list, description="IDs of threads in the channel")
    is_private: bool = Field(default=False, description="Whether the channel is private")
    pinned_messages: List[str] = Field(default_factory=list, description="IDs of pinned messages")

class Meeting(BaseModel):
    id: str = Field(..., description="Unique identifier for the meeting")
    type: MeetingType = Field(..., description="Type of meeting")
    title: str = Field(..., description="Title of the meeting")
    description: str = Field(..., description="Meeting description/agenda")
    start_time: datetime = Field(..., description="Meeting start time")
    end_time: datetime = Field(..., description="Meeting end time")
    organizer_id: str = Field(..., description="ID of the team member organizing the meeting")
    attendees: List[str] = Field(..., description="IDs of team members attending")
    optional_attendees: List[str] = Field(default_factory=list, description="IDs of optional attendees")
    sprint_id: Optional[str] = Field(None, description="ID of related sprint (if applicable)")
    team_id: str = Field(..., description="ID of the team having the meeting")
    notes: Optional[str] = Field(None, description="Meeting notes/minutes")
    action_items: List[Dict[str, str]] = Field(default_factory=list, description="List of action items")
    recurring: bool = Field(default=False, description="Whether this is a recurring meeting")
    status: str = Field(default="scheduled", description="Meeting status (scheduled, in_progress, completed, cancelled)") 