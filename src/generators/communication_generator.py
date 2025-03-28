from typing import Dict, List, Optional
from datetime import datetime, timedelta
import random

from src.models.team import TeamMember, Team
from src.models.communication import (
    Channel, CommunicationChannel, Message, Thread,
    Meeting, MeetingType, Email, EmailPriority, EmailStatus
)
from src.models.ticket import Sprint
from src.generators.utils import generate_id

class CommunicationGenerator:
    def __init__(
        self,
        team_members: Dict[str, TeamMember],
        teams: Dict[str, Team],
        config: dict
    ):
        self.team_members = team_members
        self.teams = teams
        self.config = config
        self.channels: Dict[str, Channel] = {}
        self.threads: Dict[str, Thread] = {}
        self.messages: Dict[str, Message] = {}
        self.meetings: Dict[str, Meeting] = {}
        self.emails: Dict[str, Email] = {}

    def generate_channels_for_team(self, team: Team) -> List[Channel]:
        """Generate communication channels for a team."""
        channels = []
        
        # Create general team channel
        general_channel = Channel(
            id=generate_id("CHN"),
            name=f"{team.name.lower().replace(' ', '-')}-general",
            type=CommunicationChannel.TEAM_CHAT,
            description=f"General discussion channel for {team.name}",
            created_at=datetime.now(),
            team_id=team.id,
            members=[member.id for member in team.members]
        )
        channels.append(general_channel)
        self.channels[general_channel.id] = general_channel
        
        # Create project channel
        project_channel = Channel(
            id=generate_id("CHN"),
            name=f"{team.name.lower().replace(' ', '-')}-projects",
            type=CommunicationChannel.PROJECT_CHAT,
            description=f"Project discussions for {team.name}",
            created_at=datetime.now(),
            team_id=team.id,
            members=[member.id for member in team.members]
        )
        channels.append(project_channel)
        self.channels[project_channel.id] = project_channel
        
        return channels

    def generate_message(self, sender: TeamMember, content: str) -> Message:
        """Generate a message from a team member."""
        # Determine channel
        channel = None
        if random.random() > 0.3:  # 70% chance of team channel
            team_channels = [c for c in self.channels.values() if c.team_id == team.id]
            if team_channels:
                channel = random.choice(team_channels)
        
        if not channel:
            # Create a new channel if none exists
            channel = Channel(
                id=generate_id("CHN"),
                name=f"general-{generate_id()}",
                type=CommunicationChannel.GENERAL,
                description="General discussion channel",
                created_at=datetime.now(),
                members=[member.id for member in self.team_members.values()]
            )
            self.channels[channel.id] = channel
        
        # Generate potential mentions
        potential_mentions = [m.id for m in self.team_members.values() if m.id != sender.id]
        mentions = random.sample(potential_mentions, random.randint(0, 2))
        
        # Generate reactions
        reactors = random.sample(list(self.team_members.keys()),
                               random.randint(0, 3))
        reactions = {"👍": reactors} if reactors else {}
        
        message = Message(
            id=generate_id("MSG"),
            type=CommunicationChannel.TEAM_CHAT,
            sender_id=sender.id,
            content=content,
            created_at=datetime.now(),
            channel_id=channel.id,
            mentions=mentions,
            reactions=reactions
        )
        
        self.messages[message.id] = message
        return message

    def generate_meeting(self, organizer: TeamMember, attendees: List[TeamMember]) -> Meeting:
        """Generate a meeting with the specified organizer and attendees."""
        # Find the team for the organizer
        team = None
        for t in self.teams.values():
            if any(member.id == organizer.id for member in t.members):
                team = t
                break
        
        if not team:
            raise ValueError(f"No team found for organizer {organizer.id}")
        
        meeting = Meeting(
            id=generate_id("MTG"),
            type=MeetingType.TEAM_SYNC,
            title="Team Sync Meeting",
            description="Weekly team sync meeting",
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(hours=1),
            organizer_id=organizer.id,
            attendees=[member.id for member in attendees],
            team_id=team.id
        )
        
        self.meetings[meeting.id] = meeting
        return meeting

    def get_or_create_team_channel(self, team: Team) -> Channel:
        """Get or create a team's main channel."""
        # Look for existing team channel
        for channel in self.channels.values():
            if channel.team_id == team.id and channel.type == CommunicationChannel.PROJECT_CHAT:
                return channel
        
        # Create new channel if none exists
        channel = Channel(
            id=generate_id("CHN"),
            name=f"{team.name.lower().replace(' ', '-')}-general",
            type=CommunicationChannel.PROJECT_CHAT,
            description=f"General discussion channel for {team.name}",
            created_at=datetime.now(),
            team_id=team.id,
            members=[member.id for member in team.members]
        )
        
        self.channels[channel.id] = channel
        return channel 