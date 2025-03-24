from typing import Dict, List, Optional
from datetime import datetime, timedelta
import random

from src.models.communication import (
    Message, Thread, Channel, Meeting,
    CommunicationType, MessagePriority, CommunicationChannel, MeetingType, MeetingStatus,
    Email, EmailPriority, EmailStatus
)
from src.models.team import TeamMember, Team
from src.models.ticket import Ticket, TicketStatus, TicketType, Sprint
from src.generators.utils import (
    generate_id, generate_paragraph, random_date_between,
    weighted_choice
)
from src.config.sample_company import INNOVATECH_CONFIG, MEETING_SCENARIOS, EMAIL_TEMPLATES
from src.generators.llm_generator import LLMGenerator

class CommunicationGenerator:
    def __init__(
        self,
        team_members: Dict[str, TeamMember],
        teams: Dict[str, Team],
        tickets: Dict[str, Ticket] = None,
        sprints: Dict[str, Sprint] = None,
        config=INNOVATECH_CONFIG
    ):
        self.config = config
        self.team_members = team_members
        self.teams = teams
        self.tickets = tickets or {}
        self.sprints = sprints or {}
        self.channels: Dict[str, Channel] = {}
        self.messages: Dict[str, Message] = {}
        self.threads: Dict[str, Thread] = {}
        self.meetings: Dict[str, Meeting] = {}
        self.emails: Dict[str, Email] = {}
        self.llm = LLMGenerator()
        
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

    def generate_meeting(
        self,
        organizer: TeamMember,
        attendees: List[TeamMember],
        meeting_type: str,
        context: dict = None,
        is_adhoc: bool = False
    ) -> Meeting:
        """Generate a meeting with context from tickets and templates."""
        meeting_id = generate_id("MTG")
        
        # Get meeting template
        template = MEETING_SCENARIOS.get('adhoc' if is_adhoc else 'standard', {}).get(meeting_type, {})
        
        # Generate meeting title and description
        if context and context.get('ticket'):
            ticket = context['ticket']
            title = f"{meeting_type}: {ticket.summary}"
            
            # Generate description using LLM with ticket context
            description = self.llm.generate_meeting_description(
                meeting_type=meeting_type,
                organizer_name=organizer.name,
                attendee_names=[a.name for a in attendees],
                context={
                    "template": template,
                    "ticket": ticket,
                    "sprint": self.sprints.get(ticket.sprint_id) if ticket.sprint_id else None,
                    "is_adhoc": is_adhoc
                }
            )
        else:
            title = f"{meeting_type} Meeting"
            description = self.llm.generate_meeting_description(
                meeting_type=meeting_type,
                organizer_name=organizer.name,
                attendee_names=[a.name for a in attendees],
                context={"template": template, "is_adhoc": is_adhoc}
            )

        # Create meeting object
        meeting = Meeting(
            id=meeting_id,
            title=title,
            description=description,
            organizer_id=organizer.id,
            attendee_ids=[a.id for a in attendees],
            attendees=[a.id for a in attendees],  # Required field
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(minutes=template.get('duration_minutes', 60)),
            type=MeetingType(meeting_type),  # Required field
            team_id=organizer.team_id,  # Required field
            status=MeetingStatus.SCHEDULED,  # Required field with correct enum value
            location="Virtual Meeting Room",
            agenda=template.get('agenda_template', []),
            notes=None  # Notes will be generated after the meeting
        )
        
        self.meetings[meeting_id] = meeting
        return meeting

    def generate_sprint_communications(self, sprint: Sprint, team: Team) -> Dict[str, List]:
        """Generate all communications for a sprint."""
        result = {
            "emails": [],
            "meetings": [],
            "adhoc_meetings": []
        }
        
        # Get sprint tickets
        sprint_tickets = [t for t in self.tickets.values() if t.sprint_id == sprint.id]
        
        # Generate standard sprint meetings
        for meeting_type in ["Sprint Planning", "Sprint Review"]:
            meeting = self.generate_meeting(
                organizer=team.get_tech_lead(),
                attendees=team.get_all_members(),
                meeting_type=meeting_type,
                context={"sprint": sprint, "tickets": sprint_tickets}
            )
            result["meetings"].append(meeting)
        
        # Generate daily standups
        for day in range(sprint.duration_days):
            if day % 7 < 5:  # Weekdays only
                standup = self.generate_meeting(
                    organizer=team.get_tech_lead(),
                    attendees=team.get_all_members(),
                    meeting_type="Daily Standup",
                    context={"sprint": sprint, "day": day}
                )
                result["meetings"].append(standup)
        
        # Generate ticket-based communications
        for ticket in sprint_tickets:
            # Generate status update emails
            if ticket.status in [TicketStatus.IN_PROGRESS, TicketStatus.DONE]:
                email = self.generate_email(
                    sender=self.team_members[ticket.assignee_id],
                    recipients=[self.team_members[ticket.reporter_id]],
                    email_type="ticket_status_update",
                    context={"ticket": ticket}
                )
                result["emails"].append(email)
            
            # Generate ad-hoc meetings based on ticket context
            adhoc_meeting = self.generate_adhoc_meeting_for_ticket(ticket, team)
            if adhoc_meeting:
                result["adhoc_meetings"].append(adhoc_meeting)
            
            # Generate code review emails
            if ticket.status == TicketStatus.IN_REVIEW:
                email = self.generate_email(
                    sender=self.team_members[ticket.assignee_id],
                    recipients=[r for r in team.get_senior_engineers()],
                    email_type="code_review_request",
                    context={"ticket": ticket}
                )
                result["emails"].append(email)
            
            # Generate blocking issue alerts
            if ticket.status == TicketStatus.BLOCKED:
                email = self.generate_email(
                    sender=self.team_members[ticket.assignee_id],
                    recipients=[team.get_tech_lead()],
                    email_type="blocking_issue_alert",
                    context={"ticket": ticket}
                )
                result["emails"].append(email)
        
        return result

    def generate_email(
        self,
        sender: TeamMember,
        recipients: List[TeamMember],
        subject: str = None,
        context: dict = None,
        email_type: str = None
    ) -> Email:
        """Generate an email with context from tickets and templates."""
        email_id = generate_id("EMAIL")
        
        if context and context.get('ticket'):
            ticket = context['ticket']
            template = EMAIL_TEMPLATES.get(email_type or 'ticket_status_update')
            
            if not subject and template:
                subject = template['subject_template'].format(
                    ticket_id=ticket.id,
                    ticket_title=ticket.title
                )
            
            content = self.llm.generate_email_content(
                sender_name=sender.name,
                recipient_names=[r.name for r in recipients],
                subject=subject,
                context={
                    "template": template,
                    "ticket": ticket,
                    "sprint": self.sprints.get(ticket.sprint_id) if ticket.sprint_id else None
                }
            )
        else:
            # Generic email without ticket context
            content = self.llm.generate_email_content(
                sender_name=sender.name,
                recipient_names=[r.name for r in recipients],
                subject=subject,
                context=context
            )

        email = Email(
            id=email_id,
            subject=subject,
            content=content,
            sender_id=sender.id,
            recipient_ids=[r.id for r in recipients],
            timestamp=datetime.now(),
            thread_id=generate_id("THREAD"),
            status="sent"
        )
        
        self.emails[email_id] = email
        return email

    def generate_adhoc_meeting_for_ticket(
        self,
        ticket: Ticket,
        team: Team
    ) -> Optional[Meeting]:
        """Generate an ad-hoc meeting based on ticket context."""
        # Determine appropriate ad-hoc meeting type based on ticket
        meeting_type = None
        if ticket.status == TicketStatus.BLOCKED:
            meeting_type = "Blocking Issue Resolution"
        elif ticket.type == "BUG" and ticket.priority == "HIGH":
            meeting_type = "Bug Triage"
        elif ticket.type == "EPIC" or "design" in ticket.summary.lower():
            meeting_type = "Technical Design Review"
        elif "review" in ticket.summary.lower() or ticket.type == "CODE_REVIEW":
            meeting_type = "Code Review Sync"
        
        if not meeting_type:
            return None
            
        # Get meeting template
        template = MEETING_SCENARIOS['adhoc'][meeting_type]
        
        # Select attendees based on required and optional roles
        required_attendees = []
        optional_attendees = []
        
        for member in team.members:
            if member.role in template['required_roles']:
                required_attendees.append(self.team_members[member.id])
            elif template.get('optional_roles') and member.role in template['optional_roles']:
                optional_attendees.append(self.team_members[member.id])
        
        # Ensure we have required attendees
        if not required_attendees:
            return None
            
        # Add some optional attendees
        attendees = required_attendees + random.sample(
            optional_attendees,
            min(2, len(optional_attendees))
        )
        
        # Generate the meeting
        return self.generate_meeting(
            organizer=required_attendees[0],  # First required attendee organizes
            attendees=attendees,
            meeting_type=meeting_type,
            context={"ticket": ticket},
            is_adhoc=True
        )

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