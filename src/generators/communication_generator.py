from typing import Dict, List, Optional
from datetime import datetime, timedelta
import random

from src.models.communication import (
    Message, Thread, Channel, Meeting,
    CommunicationType, MessagePriority, CommunicationChannel, MeetingType
)
from src.models.team import TeamMember, Team
from src.models.ticket import Ticket, TicketStatus, TicketType, Sprint
from src.generators.utils import (
    generate_id, generate_paragraph, random_date_between,
    weighted_choice
)
from src.config.sample_company import INNOVATECH_CONFIG

class CommunicationGenerator:
    def __init__(self, team_members: Dict[str, TeamMember], teams: Dict[str, Team], config=INNOVATECH_CONFIG):
        self.config = config
        self.team_members = team_members
        self.teams = teams
        self.channels: Dict[str, Channel] = {}
        self.messages: Dict[str, Message] = {}
        self.threads: Dict[str, Thread] = {}
        self.meetings: Dict[str, Meeting] = {}
        
        # Communication patterns
        self.message_frequency = {
            CommunicationType.CHAT: 0.5,    # 50% of messages are chat
            CommunicationType.EMAIL: 0.2,    # 20% are emails
            CommunicationType.COMMENT: 0.2,  # 20% are comments
            CommunicationType.MENTION: 0.1   # 10% are mentions
        }
        
        self.channel_activity = {
            CommunicationChannel.TEAM_CHAT: 0.3,
            CommunicationChannel.PROJECT_CHAT: 0.25,
            CommunicationChannel.GENERAL: 0.2,
            CommunicationChannel.TECHNICAL: 0.15,
            CommunicationChannel.ANNOUNCEMENTS: 0.05,
            CommunicationChannel.INCIDENTS: 0.05
        }

    def generate_channels_for_team(self, team: Team) -> List[Channel]:
        """Generate communication channels for a team."""
        channels = []
        
        # Create general team channel
        general_channel = Channel(
            id=generate_id("CHN"),
            name=f"{team.name.lower().replace(' ', '-')}-general",
            type=CommunicationChannel.TEAM_CHAT,
            description=f"General discussion channel for {team.name}",
            created_at=team.created_date,
            team_id=team.id,
            members=[member.id for member in team.members],
            is_private=False
        )
        self.channels[general_channel.id] = general_channel
        channels.append(general_channel)
        
        # Create project-specific channel
        project_channel = Channel(
            id=generate_id("CHN"),
            name=f"{team.name.lower().replace(' ', '-')}-projects",
            type=CommunicationChannel.PROJECT_CHAT,
            description=f"Project discussions for {team.name}",
            created_at=team.created_date,
            team_id=team.id,
            members=[member.id for member in team.members],
            is_private=False
        )
        self.channels[project_channel.id] = project_channel
        channels.append(project_channel)
        
        # Create technical channel
        tech_channel = Channel(
            id=generate_id("CHN"),
            name=f"{team.name.lower().replace(' ', '-')}-tech",
            type=CommunicationChannel.TECHNICAL,
            description=f"Technical discussions for {team.name}",
            created_at=team.created_date,
            team_id=team.id,
            members=[member.id for member in team.members],
            is_private=False
        )
        self.channels[tech_channel.id] = tech_channel
        channels.append(tech_channel)
        
        return channels

    def generate_thread(self, channel: Channel, ticket: Optional[Ticket] = None) -> Thread:
        """Generate a discussion thread in a channel."""
        thread_id = generate_id("THR")
        
        thread = Thread(
            id=thread_id,
            channel_id=channel.id,
            title=f"Discussion: {ticket.summary}" if ticket else None,
            created_at=datetime.now() - timedelta(days=random.randint(1, 30)),
            last_activity=datetime.now() - timedelta(hours=random.randint(1, 24)),
            participants=random.sample(channel.members, random.randint(2, len(channel.members))),
            ticket_id=ticket.id if ticket else None,
            resolved=random.random() > 0.3
        )
        
        self.threads[thread_id] = thread
        channel.threads.append(thread_id)
        return thread

    def generate_message(
        self,
        sender: TeamMember,
        thread: Optional[Thread] = None,
        ticket: Optional[Ticket] = None,
        msg_type: Optional[CommunicationType] = None
    ) -> Message:
        """Generate a message from a team member."""
        if not msg_type:
            msg_type = weighted_choice(self.message_frequency)
        
        # Determine channel and thread
        channel_id = None
        if thread:
            channel_id = thread.channel_id
        elif sender.team_id and random.random() > 0.3:  # 70% chance of team channel
            team_channels = [c for c in self.channels.values() if c.team_id == sender.team_id]
            if team_channels:
                channel = random.choice(team_channels)
                channel_id = channel.id
        
        # Generate message content
        technical = msg_type in [CommunicationType.COMMENT, CommunicationType.MENTION]
        content = generate_paragraph(
            min_words=5,
            max_words=30,
            technical=technical
        )
        
        # Add mentions
        mentions = []
        if random.random() < 0.3:  # 30% chance of mentions
            potential_mentions = [m.id for m in self.team_members.values() 
                               if m.id != sender.id]
            num_mentions = random.randint(1, min(3, len(potential_mentions)))
            mentions = random.sample(potential_mentions, num_mentions)
            for mention in mentions:
                content = f"@{mention} {content}"
        
        message = Message(
            id=generate_id("MSG"),
            type=msg_type,
            sender_id=sender.id,
            content=content,
            created_at=datetime.now() - timedelta(minutes=random.randint(1, 1440)),
            priority=MessagePriority.HIGH if random.random() < 0.1 else MessagePriority.NORMAL,
            channel_id=channel_id,
            thread_id=thread.id if thread else None,
            ticket_id=ticket.id if ticket else None,
            mentions=mentions
        )
        
        # Add reactions (30% chance)
        if random.random() < 0.3:
            reactions = ["👍", "❤️", "🎉", "🚀", "💯"]
            num_reactions = random.randint(1, 3)
            for _ in range(num_reactions):
                reaction = random.choice(reactions)
                reactors = random.sample(list(self.team_members.keys()), 
                                      random.randint(1, 3))
                message.reactions[reaction] = reactors
        
        self.messages[message.id] = message
        if thread:
            thread.messages.append(message.id)
            thread.last_activity = max(thread.last_activity, message.created_at)
        
        return message

    def generate_meeting(self, team: Team, meeting_type: MeetingType) -> Meeting:
        """Generate a team meeting."""
        # Get team members
        team_members = team.members
        
        # Select meeting organizer (prefer team manager)
        organizer = next(
            (member for member in team_members if member.id == team.manager_id),
            random.choice(team_members)
        )
        
        # Determine meeting duration based on type
        duration_minutes = {
            MeetingType.STANDUP: 15,
            MeetingType.SPRINT_PLANNING: 120,
            MeetingType.SPRINT_REVIEW: 60,
            MeetingType.SPRINT_RETRO: 60,
            MeetingType.TECHNICAL_DISCUSSION: 60,
            MeetingType.TEAM_SYNC: 30,
            MeetingType.INCIDENT_REVIEW: 45
        }.get(meeting_type, 30)
        
        # Set meeting time during working hours
        start_time = datetime.now() - timedelta(days=random.randint(1, 30))
        start_time = start_time.replace(
            hour=random.randint(9, 16),
            minute=random.choice([0, 15, 30, 45]),
            second=0,
            microsecond=0
        )
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        # Select attendees (everyone for important meetings, subset for others)
        if meeting_type in [MeetingType.SPRINT_PLANNING, MeetingType.SPRINT_REVIEW, MeetingType.SPRINT_RETRO]:
            attendees = [member.id for member in team_members]
            optional_attendees = []
        else:
            # Select 50-80% of team members as required attendees
            num_required = max(2, int(len(team_members) * random.uniform(0.5, 0.8)))
            attendees = [member.id for member in random.sample(team_members, num_required)]
            # Rest are optional
            optional_attendees = [
                member.id for member in team_members
                if member.id not in attendees
            ]
        
        # Generate meeting
        meeting = Meeting(
            id=generate_id("MTG"),
            type=meeting_type,
            title=self._generate_meeting_title(meeting_type, team.name),
            description=self._generate_meeting_description(meeting_type),
            start_time=start_time,
            end_time=end_time,
            organizer_id=organizer.id,
            attendees=attendees,
            optional_attendees=optional_attendees,
            team_id=team.id,
            recurring=meeting_type in [MeetingType.STANDUP, MeetingType.TEAM_SYNC],
            status="completed" if end_time < datetime.now() else "scheduled"
        )
        
        return meeting

    def generate_sprint_meetings(self, team: Team, sprint: Sprint) -> List[Meeting]:
        """Generate all meetings for a sprint."""
        meetings = []
        
        # Sprint Planning
        planning = self.generate_meeting(team, MeetingType.SPRINT_PLANNING, sprint)
        meetings.append(planning)
        
        # Daily Standups (one per day)
        sprint_days = (sprint.end_date - sprint.start_date).days
        for day in range(sprint_days):
            if day % 7 not in [5, 6]:  # Skip weekends
                standup = self.generate_meeting(team, MeetingType.STANDUP, sprint)
                meetings.append(standup)
        
        # Sprint Review and Retro (if sprint is completed)
        if sprint.status == "completed":
            review = self.generate_meeting(team, MeetingType.SPRINT_REVIEW, sprint)
            retro = self.generate_meeting(team, MeetingType.SPRINT_RETRO, sprint)
            meetings.extend([review, retro])
        
        return meetings

    def generate_ticket_communication(self, ticket: Ticket) -> Dict[str, List[Message]]:
        """Generate communication around a ticket."""
        messages = []
        
        # Find the team for the ticket's assignee
        team = None
        for t in self.teams.values():
            if any(member.id == ticket.assignee_id for member in t.members):
                team = t
                break
        
        if team is None:
            # If we can't find the team, skip generating communication
            return {"messages": []}
        
        # Generate initial discussion
        channel = self.get_or_create_team_channel(team)
        
        # Create a thread about the ticket
        thread_id = generate_id("THR")
        
        # Initial message about ticket creation
        initial_message = Message(
            id=generate_id("MSG"),
            channel_id=channel.id,
            thread_id=thread_id,
            sender_id=ticket.reporter_id,
            content=f"Created ticket {ticket.id}: {ticket.summary}",
            type=CommunicationType.CHAT,
            created_at=ticket.created_at,
            updated_at=ticket.created_at,
            mentions=[ticket.assignee_id] if ticket.assignee_id else [],
            reactions={},
            attachments=[],
            metadata={
                "ticket_id": ticket.id,
                "ticket_type": ticket.type.value,
                "ticket_status": ticket.status.value
            }
        )
        messages.append(initial_message)
        
        # Generate some follow-up discussion
        num_replies = random.randint(1, 4)
        current_time = ticket.created_at
        
        for _ in range(num_replies):
            current_time += timedelta(hours=random.randint(1, 8))
            
            # Select a random participant from the team
            sender = random.choice(team.members)
            
            # Generate message content based on ticket type and status
            content = self._generate_ticket_discussion_message(ticket)
            
            reply = Message(
                id=generate_id("MSG"),
                channel_id=channel.id,
                thread_id=thread_id,
                sender_id=sender.id,
                content=content,
                type=CommunicationType.CHAT,
                created_at=current_time,
                updated_at=current_time,
                mentions=[],
                reactions={},
                attachments=[],
                metadata={
                    "ticket_id": ticket.id,
                    "ticket_type": ticket.type.value,
                    "ticket_status": ticket.status.value
                }
            )
            messages.append(reply)
            
            # Randomly add some reactions
            if random.random() < 0.3:
                reactors = random.sample(
                    team.members,
                    k=random.randint(1, min(3, len(team.members)))
                )
                reaction = random.choice(["👍", "🎉", "💯", "✅"])
                reply.reactions[reaction] = [r.id for r in reactors]
        
        return {"messages": messages}

    def get_channel_activity(self, channel_id: str, time_period: timedelta = timedelta(days=7)) -> Dict:
        """Get activity statistics for a channel."""
        channel = self.channels.get(channel_id)
        if not channel:
            return {}
        
        start_time = datetime.now() - time_period
        
        # Get messages in the time period
        channel_messages = [m for m in self.messages.values()
                          if m.channel_id == channel_id and
                          m.created_at >= start_time]
        
        return {
            "total_messages": len(channel_messages),
            "active_threads": len(set(m.thread_id for m in channel_messages if m.thread_id)),
            "unique_participants": len(set(m.sender_id for m in channel_messages)),
            "reactions": sum(len(m.reactions) for m in channel_messages),
            "mentions": sum(len(m.mentions) for m in channel_messages)
        }

    def get_team_communication_stats(self, team_id: str, time_period: timedelta = timedelta(days=30)) -> Dict:
        """Get communication statistics for a team."""
        team_channels = [c for c in self.channels.values() if c.team_id == team_id]
        team_meetings = [m for m in self.meetings.values() if m.team_id == team_id]
        
        start_time = datetime.now() - time_period
        
        stats = {
            "channels": len(team_channels),
            "active_channels": 0,
            "total_messages": 0,
            "total_threads": 0,
            "meetings": len([m for m in team_meetings 
                           if m.start_time >= start_time]),
            "meeting_hours": sum(
                (m.end_time - m.start_time).total_seconds() / 3600
                for m in team_meetings
                if m.start_time >= start_time
            )
        }
        
        for channel in team_channels:
            activity = self.get_channel_activity(channel.id, time_period)
            if activity["total_messages"] > 0:
                stats["active_channels"] += 1
                stats["total_messages"] += activity["total_messages"]
                stats["total_threads"] += activity["active_threads"]
        
        return stats 

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
            description=f"General discussion channel for {team.name}",
            type=CommunicationChannel.PROJECT_CHAT,
            team_id=team.id,
            created_at=team.created_date,
            members=[member.id for member in team.members],
            is_private=False,
            is_archived=False
        )
        
        self.channels[channel.id] = channel
        return channel 

    def _generate_ticket_discussion_message(self, ticket: Ticket) -> str:
        """Generate a discussion message about a ticket."""
        # Different message templates based on ticket type and status
        status_messages = {
            TicketStatus.TO_DO: [
                "When do we plan to start working on this?",
                "I can pick this up next sprint.",
                "Let's discuss this in our next planning.",
                "Any prerequisites we need to handle first?"
            ],
            TicketStatus.IN_PROGRESS: [
                "Making good progress on this.",
                "Hit a small snag, but working through it.",
                "Should be done with this soon.",
                "Need some clarification on the requirements."
            ],
            TicketStatus.IN_REVIEW: [
                "PR is ready for review.",
                "Made the suggested changes.",
                "Can someone take a look at this?",
                "Tests are passing now."
            ],
            TicketStatus.BLOCKED: [
                "Blocked by dependency issues.",
                "Waiting on the API changes.",
                "Need input from product team.",
                "Environment issues are blocking progress."
            ],
            TicketStatus.DONE: [
                "All done! Please verify.",
                "Completed and deployed.",
                "Ready for QA testing.",
                "Merged and ready for release."
            ]
        }
        
        type_specific_messages = {
            TicketType.BUG: [
                "Can reproduce this in staging.",
                "Fixed in latest commit.",
                "Added regression tests.",
                "Similar issue was fixed before."
            ],
            TicketType.STORY: [
                "Updated acceptance criteria.",
                "Need product review.",
                "User flow looks good.",
                "Added new test cases."
            ],
            TicketType.TASK: [
                "Implementation details updated.",
                "Code cleanup done.",
                "Documentation updated.",
                "Performance looks good."
            ],
            TicketType.SUBTASK: [
                "Part of the larger task.",
                "Dependencies handled.",
                "Small update needed.",
                "Quick fix applied."
            ],
            TicketType.EPIC: [
                "Good progress on child stories.",
                "Timeline looks realistic.",
                "Dependencies mapped.",
                "Scope well defined."
            ]
        }
        
        # Combine status and type-specific messages
        messages = status_messages.get(ticket.status, []) + type_specific_messages.get(ticket.type, [])
        return random.choice(messages) 

    def _generate_meeting_title(self, meeting_type: MeetingType, team_name: str) -> str:
        """Generate a title for a meeting."""
        type_titles = {
            MeetingType.STANDUP: "Daily Standup",
            MeetingType.SPRINT_PLANNING: "Sprint Planning",
            MeetingType.SPRINT_REVIEW: "Sprint Review",
            MeetingType.SPRINT_RETRO: "Sprint Retrospective",
            MeetingType.TECHNICAL_DISCUSSION: "Technical Discussion",
            MeetingType.TEAM_SYNC: "Team Sync",
            MeetingType.INCIDENT_REVIEW: "Incident Review"
        }
        
        return f"{team_name} - {type_titles.get(meeting_type, meeting_type.value)}"

    def _generate_meeting_description(self, meeting_type: MeetingType) -> str:
        """Generate a description for a meeting."""
        descriptions = {
            MeetingType.STANDUP: "Daily team sync to discuss progress, blockers, and plans.",
            MeetingType.SPRINT_PLANNING: "Plan and estimate work for the upcoming sprint.",
            MeetingType.SPRINT_REVIEW: "Review completed work and demonstrate achievements.",
            MeetingType.SPRINT_RETRO: "Reflect on the sprint and identify improvements.",
            MeetingType.TECHNICAL_DISCUSSION: "Discuss technical challenges and solutions.",
            MeetingType.TEAM_SYNC: "Sync on team initiatives and share updates.",
            MeetingType.INCIDENT_REVIEW: "Review and analyze recent incidents."
        }
        
        base_description = descriptions.get(
            meeting_type,
            "Team meeting to discuss ongoing work and initiatives."
        )
        
        # Add some random agenda items
        agenda_items = [
            "Review action items from previous meeting",
            "Team updates and announcements",
            "Open discussion and questions",
            "Next steps and action items"
        ]
        
        return f"{base_description}\n\nAgenda:\n- " + "\n- ".join(agenda_items) 