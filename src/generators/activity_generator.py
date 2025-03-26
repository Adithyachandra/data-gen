from typing import Dict, List, Optional
from datetime import datetime, timedelta
import random
from collections import defaultdict

from src.models.activity import (
    Activity, ActivityType, ActivityCategory,
    UserActivitySummary
)
from src.models.team import TeamMember, Team
from src.models.ticket import Ticket, Sprint, TicketStatus
from src.models.communication import Message, Meeting
from src.generators.utils import generate_id
from src.config.sample_company import INNOVATECH_CONFIG
from src.generators.llm_generator import LLMGenerator

class ActivityGenerator:
    def __init__(
        self,
        team_members: Dict[str, TeamMember],
        teams: Dict[str, Team],
        config: dict
    ):
        self.team_members = team_members
        self.teams = teams
        self.config = config
        self.activities: Dict[str, Activity] = {}
        self.llm = LLMGenerator(config=config)
        
        # Get company-specific settings from config
        self.company_name = config.get('company', {}).get('name', 'the company')
        self.industry = config.get('company', {}).get('industry', 'tech')
        self.work_hours = config.get('work_hours', {'start': '09:00', 'end': '17:00'})
        self.ticket_complexity_distribution = config.get('ticket_complexity_distribution', {
            'low': 0.3,
            'medium': 0.5,
            'high': 0.2
        })
        
        # Activity patterns
        self.activity_patterns = {
            ActivityCategory.TICKET: 0.4,      # 40% ticket activities
            ActivityCategory.COMMUNICATION: 0.3,# 30% communication
            ActivityCategory.MEETING: 0.15,     # 15% meetings
            ActivityCategory.SPRINT: 0.1,       # 10% sprint activities
            ActivityCategory.WORKFLOW: 0.05     # 5% workflow activities
        }
        
        # Working hours distribution (24-hour format)
        self.hour_weights = {
            9: 0.15,   # 9 AM: Peak
            10: 0.15,  # 10 AM: Peak
            11: 0.12,  # 11 AM: High
            12: 0.05,  # 12 PM: Lunch dip
            13: 0.08,  # 1 PM: Post-lunch
            14: 0.12,  # 2 PM: High
            15: 0.15,  # 3 PM: Peak
            16: 0.12,  # 4 PM: High
            17: 0.06   # 5 PM: End of day
        }

    def generate_ticket_activities(
        self,
        ticket: Ticket,
        user: TeamMember,
        timestamp: datetime
    ) -> List[Activity]:
        """Generate activities related to a ticket."""
        activities = []
        
        # Find the team for the user
        team_id = None
        for team in self.teams.values():
            if any(member.id == user.id for member in team.members):
                team_id = team.id
                break
        
        if team_id is None:
            # If we can't find the team, try to find it through the ticket's assignee
            for team in self.teams.values():
                if any(member.id == ticket.assignee_id for member in team.members):
                    team_id = team.id
                    break
        
        if team_id is None:
            # If we still can't find the team, use the first team's ID as a fallback
            team_id = next(iter(self.teams.values())).id
        
        # Ticket creation
        create_activity = Activity(
            id=generate_id("ACT"),
            type=ActivityType.TICKET_CREATE,
            category=ActivityCategory.TICKET,
            user_id=user.id,
            timestamp=timestamp,
            team_id=team_id,
            ticket_id=ticket.id,
            details={
                "ticket_type": ticket.type.value,
                "summary": ticket.summary,
                "priority": ticket.priority.value
            }
        )
        activities.append(create_activity)
        
        # Generate status changes
        if ticket.status != TicketStatus.TO_DO:
            # Track the previous status
            previous_status = TicketStatus.TO_DO
            
            # Define status progression
            status_progression = [
                (TicketStatus.IN_PROGRESS, timestamp + timedelta(hours=random.randint(1, 24))),
                (TicketStatus.IN_REVIEW, timestamp + timedelta(hours=random.randint(24, 48))),
                (TicketStatus.DONE, timestamp + timedelta(hours=random.randint(48, 72)))
            ]
            
            for status, status_time in status_progression:
                if ticket.status.value >= status.value:  # Compare string values
                    status_activity = Activity(
                        id=generate_id("ACT"),
                        type=ActivityType.TICKET_STATUS_CHANGE,
                        category=ActivityCategory.TICKET,
                        user_id=user.id,
                        timestamp=status_time,
                        team_id=team_id,
                        ticket_id=ticket.id,
                        details={
                            "old_status": previous_status.value,
                            "new_status": status.value,
                            "time_in_previous_status": random.randint(1, 24)
                        }
                    )
                    activities.append(status_activity)
                    previous_status = status
        
        return activities

    def generate_sprint_activities(
        self,
        sprint: Sprint,
        team: Team,
        timestamp: datetime
    ) -> List[Activity]:
        """Generate activities related to a sprint."""
        activities = []
        
        # Sprint creation
        create_activity = Activity(
            id=generate_id("ACT"),
            type=ActivityType.SPRINT_CREATE,
            category=ActivityCategory.SPRINT,
            user_id=team.manager_id,
            timestamp=timestamp,
            team_id=team.id,
            sprint_id=sprint.id,
            details={
                "sprint_name": sprint.name,
                "sprint_goal": sprint.goal,
                "planned_story_points": sprint.story_points_committed
            }
        )
        activities.append(create_activity)
        
        # Sprint updates (every few days)
        sprint_duration = (sprint.end_date - sprint.start_date).days
        for day in range(1, sprint_duration):
            if random.random() < 0.3:  # 30% chance of update each day
                update_time = timestamp + timedelta(days=day)
                update_activity = Activity(
                    id=generate_id("ACT"),
                    type=ActivityType.SPRINT_UPDATE,
                    category=ActivityCategory.SPRINT,
                    user_id=random.choice(list(self.team_members.keys())),
                    timestamp=update_time,
                    team_id=team.id,
                    sprint_id=sprint.id,
                    details={
                        "completed_story_points": random.randint(
                            0, sprint.story_points_committed
                        ),
                        "remaining_story_points": random.randint(
                            0, sprint.story_points_committed
                        )
                    }
                )
                activities.append(update_activity)
        
        # Sprint completion
        if sprint.status == "completed":
            complete_activity = Activity(
                id=generate_id("ACT"),
                type=ActivityType.SPRINT_COMPLETE,
                category=ActivityCategory.SPRINT,
                user_id=team.manager_id,
                timestamp=sprint.end_date,
                team_id=team.id,
                sprint_id=sprint.id,
                details={
                    "completed_story_points": sprint.story_points_completed,
                    "velocity": sprint.velocity,
                    "completion_percentage": round(
                        (sprint.story_points_completed / sprint.story_points_committed) * 100
                    )
                }
            )
            activities.append(complete_activity)
        
        return activities

    def generate_meeting_activities(
        self,
        meeting: Meeting,
        timestamp: datetime
    ) -> List[Activity]:
        """Generate activities related to a meeting."""
        activities = []
        
        # Meeting creation
        create_activity = Activity(
            id=generate_id("ACT"),
            type=ActivityType.MEETING_CREATE,
            category=ActivityCategory.MEETING,
            user_id=meeting.organizer_id,
            timestamp=timestamp,
            team_id=meeting.team_id,
            meeting_id=meeting.id,
            details={
                "meeting_type": meeting.type.value,
                "title": meeting.title,
                "duration_minutes": int(
                    (meeting.end_time - meeting.start_time).total_seconds() / 60
                )
            }
        )
        activities.append(create_activity)
        
        # Meeting attendance
        if meeting.status == "completed":
            for attendee_id in meeting.attendees:
                attend_activity = Activity(
                    id=generate_id("ACT"),
                    type=ActivityType.MEETING_ATTEND,
                    category=ActivityCategory.MEETING,
                    user_id=attendee_id,
                    timestamp=meeting.start_time,
                    team_id=meeting.team_id,
                    meeting_id=meeting.id,
                    details={
                        "duration_minutes": int(
                            (meeting.end_time - meeting.start_time).total_seconds() / 60
                        )
                    }
                )
                activities.append(attend_activity)
        
        return activities

    def generate_communication_activities(
        self,
        message: Message,
        timestamp: datetime
    ) -> List[Activity]:
        """Generate activities related to communication."""
        activities = []
        
        # Message sending
        send_activity = Activity(
            id=generate_id("ACT"),
            type=ActivityType.MESSAGE_SEND,
            category=ActivityCategory.COMMUNICATION,
            user_id=message.sender_id,
            timestamp=timestamp,
            channel_id=message.channel_id,
            message_id=message.id,
            details={
                "message_type": message.type.value,
                "has_attachments": bool(message.attachments)
            }
        )
        activities.append(send_activity)
        
        # Mentions
        for mentioned_id in message.mentions:
            mention_activity = Activity(
                id=generate_id("ACT"),
                type=ActivityType.MENTION,
                category=ActivityCategory.COMMUNICATION,
                user_id=mentioned_id,  # The person being mentioned
                timestamp=timestamp,
                channel_id=message.channel_id,
                message_id=message.id,
                details={
                    "mentioned_by": message.sender_id,
                    "context": "message"
                }
            )
            activities.append(mention_activity)
        
        # Reactions
        for reaction, reactors in message.reactions.items():
            for reactor_id in reactors:
                reaction_activity = Activity(
                    id=generate_id("ACT"),
                    type=ActivityType.REACTION_ADD,
                    category=ActivityCategory.COMMUNICATION,
                    user_id=reactor_id,
                    timestamp=timestamp + timedelta(minutes=random.randint(1, 60)),
                    channel_id=message.channel_id,
                    message_id=message.id,
                    details={
                        "reaction": reaction,
                        "message_author": message.sender_id
                    }
                )
                activities.append(reaction_activity)
        
        return activities

    def generate_user_activity_summary(
        self,
        user_id: str,
        start_time: datetime,
        end_time: datetime
    ) -> UserActivitySummary:
        """Generate a summary of a user's activities over a time period."""
        user_activities = [
            activity for activity in self.activities.values()
            if (activity.user_id == user_id and
                start_time <= activity.timestamp <= end_time)
        ]
        
        summary = UserActivitySummary(
            user_id=user_id,
            period_start=start_time,
            period_end=end_time,
            total_activities=len(user_activities)
        )
        
        # Count activities by type and category
        for activity in user_activities:
            summary.activities_by_type[activity.type] = (
                summary.activities_by_type.get(activity.type, 0) + 1
            )
            summary.activities_by_category[activity.category] = (
                summary.activities_by_category.get(activity.category, 0) + 1
            )
        
        # Calculate ticket metrics
        summary.tickets_created = sum(
            1 for a in user_activities
            if a.type == ActivityType.TICKET_CREATE
        )
        summary.tickets_resolved = sum(
            1 for a in user_activities
            if (a.type == ActivityType.TICKET_STATUS_CHANGE and
                a.details.get("new_status") == TicketStatus.DONE.value)
        )
        summary.tickets_commented = sum(
            1 for a in user_activities
            if a.type == ActivityType.TICKET_COMMENT
        )
        
        # Calculate communication metrics
        summary.messages_sent = sum(
            1 for a in user_activities
            if a.type == ActivityType.MESSAGE_SEND
        )
        summary.mentions_received = sum(
            1 for a in user_activities
            if a.type == ActivityType.MENTION
        )
        summary.reactions_received = sum(
            1 for a in self.activities.values()
            if (a.type == ActivityType.REACTION_ADD and
                a.details.get("message_author") == user_id)
        )
        summary.meetings_attended = sum(
            1 for a in user_activities
            if a.type == ActivityType.MEETING_ATTEND
        )
        
        # Calculate collaboration metrics
        collaborators = set()
        for activity in user_activities:
            if activity.type == ActivityType.MESSAGE_SEND:
                # Add people who reacted or were mentioned
                msg_activities = [
                    a for a in self.activities.values()
                    if a.message_id == activity.message_id
                ]
                for msg_activity in msg_activities:
                    if msg_activity.type in [ActivityType.REACTION_ADD, ActivityType.MENTION]:
                        collaborators.add(msg_activity.user_id)
            elif activity.type == ActivityType.MEETING_ATTEND:
                # Add other meeting attendees
                meeting_activities = [
                    a for a in self.activities.values()
                    if (a.meeting_id == activity.meeting_id and
                        a.type == ActivityType.MEETING_ATTEND)
                ]
                for meet_activity in meeting_activities:
                    collaborators.add(meet_activity.user_id)
        
        summary.unique_collaborators = len(collaborators)
        
        # Calculate time distribution
        for activity in user_activities:
            hour = activity.timestamp.hour
            day = activity.timestamp.strftime("%A")
            summary.activity_by_hour[hour] = (
                summary.activity_by_hour.get(hour, 0) + 1
            )
            summary.activity_by_day[day] = (
                summary.activity_by_day.get(day, 0) + 1
            )
        
        return summary

    def get_team_activity_summary(
        self,
        team_id: str,
        time_period: timedelta = timedelta(days=30)
    ) -> Dict:
        """Get activity summary for a team."""
        end_time = datetime.now()
        start_time = end_time - time_period
        
        team_activities = [
            activity for activity in self.activities.values()
            if (activity.team_id == team_id and
                start_time <= activity.timestamp <= end_time)
        ]
        
        summary = {
            "total_activities": len(team_activities),
            "activities_by_category": defaultdict(int),
            "activities_by_type": defaultdict(int),
            "active_users": set(),
            "tickets": {
                "created": 0,
                "resolved": 0,
                "average_resolution_time": 0
            },
            "communication": {
                "messages": 0,
                "meetings": 0,
                "meeting_hours": 0
            }
        }
        
        resolution_times = []
        
        for activity in team_activities:
            summary["activities_by_category"][activity.category] += 1
            summary["activities_by_type"][activity.type] += 1
            summary["active_users"].add(activity.user_id)
            
            if activity.type == ActivityType.TICKET_CREATE:
                summary["tickets"]["created"] += 1
            elif (activity.type == ActivityType.TICKET_STATUS_CHANGE and
                  activity.details.get("new_status") == TicketStatus.DONE.value):
                summary["tickets"]["resolved"] += 1
                if "time_in_previous_status" in activity.details:
                    resolution_times.append(activity.details["time_in_previous_status"])
            elif activity.type == ActivityType.MESSAGE_SEND:
                summary["communication"]["messages"] += 1
            elif activity.type == ActivityType.MEETING_ATTEND:
                summary["communication"]["meetings"] += 1
                if "duration_minutes" in activity.details:
                    summary["communication"]["meeting_hours"] += (
                        activity.details["duration_minutes"] / 60
                    )
        
        if resolution_times:
            summary["tickets"]["average_resolution_time"] = (
                sum(resolution_times) / len(resolution_times)
            )
        
        summary["active_users"] = len(summary["active_users"])
        
        return summary

    def generate_code_review_activity(self, ticket: Ticket, reviewer_id: str) -> Activity:
        """Generate a code review activity with realistic comments."""
        activity_id = generate_id()
        
        # Get the first component from the ticket's components list
        component = ticket.components[0] if ticket.components else "unknown"
        
        # Simulate code snippet based on ticket type and component
        code_snippet = f"def implement_{component.lower()}():\n    # Implementation\n    pass"
        
        comment = self.llm.generate_code_review_comment(
            code_snippet=code_snippet,
            context=f"Code review for {ticket.type.value} ticket related to {component}"
        )
        
        activity = Activity(
            id=activity_id,
            type=ActivityType.CODE_REVIEW,
            category=ActivityCategory.TICKET,
            ticket_id=ticket.id,
            user_id=reviewer_id,
            timestamp=datetime.now(),
            details={
                "comment": comment,
                "code_snippet": code_snippet,
                "component": component
            }
        )
        
        self.activities[activity_id] = activity
        return activity 