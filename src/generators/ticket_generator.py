from typing import Dict, List, Optional, Tuple, Union
from datetime import datetime, timedelta
import random
import uuid
import json
import os

from src.models.ticket import (
    Ticket, Epic, Story, Task, Subtask, Bug,
    TicketType, TicketStatus, TicketPriority, Component,
    Comment, FixVersion, Sprint, SprintStatus, TicketRelationType
)
from src.models.team import TeamMember, Team, Department, Role, Seniority, Skill
from src.generators.utils import (
    generate_id, generate_ticket_id, random_date_between,
    weighted_choice, generate_paragraph, random_subset
)
from src.config.sample_company import INNOVATECH_CONFIG, PRODUCT_INITIATIVES, PRODUCT_SCENARIOS, STORY_TEMPLATES
from src.generators.llm_generator import LLMGenerator

class TicketGenerator:
    def __init__(self, config: dict):
        self.config = config
        self.team_members: Dict[str, TeamMember] = {}
        self.teams: Dict[str, Team] = {}
        self.tickets: Dict[str, Ticket] = {}
        self.epics: Dict[str, Epic] = {}
        self.stories: Dict[str, Story] = {}
        self.tasks: Dict[str, Task] = {}
        self.subtasks: Dict[str, Subtask] = {}
        self.bugs: Dict[str, Bug] = {}
        self.sprints: Dict[str, Sprint] = {}
        self.ticket_counter = 1
        self.sprint_counter = 1
        self.fix_versions: Dict[str, FixVersion] = self._generate_fix_versions()
        
        # Default ticket generation parameters
        self.stories_per_sprint = random.randint(2, 4)
        self.tasks_per_story = random.randint(2, 4)
        self.subtasks_per_task = random.randint(1, 3)
        
        # Product initiative
        self.current_initiative = None
        
        # Relationship probabilities
        self.dependency_probability = 0.3  # 30% chance of dependencies between stories
        self.blocking_probability = 0.2    # 20% chance of blocked tickets
        self.clone_probability = 0.1       # 10% chance of cloned tickets
        self.duplicate_probability = 0.15  # 15% chance of duplicate tickets
        self.implements_probability = 0.2  # 20% chance of implementation relationships

        self.llm = LLMGenerator(config=config)

        self.sprint_duration_days = config.get('sprint_duration_days', 14)  # Default to 2 weeks
        
        # Load JIRA data
        self._load_jira_data()

    def _load_jira_data(self):
        """Load team and user data from JIRA JSON files."""
        # Load users data first
        users_file = "user_data/jira_users_20250328_104736.json"
        if os.path.exists(users_file):
            with open(users_file, 'r') as f:
                users_data = json.load(f)
                for user_data in users_data:
                    # Generate a valid email if none exists
                    email = user_data.get('emailAddress')
                    if not email:
                        email = f"{user_data['displayName'].lower().replace(' ', '.')}@company.com"
                    
                    team_member = TeamMember(
                        id=user_data['accountId'],
                        name=user_data['displayName'],
                        email=email,
                        role=user_data.get('role'),
                        active=user_data.get('active', True),
                        timezone=user_data.get('timeZone'),
                        locale=user_data.get('locale')
                    )
                    self.team_members[team_member.id] = team_member
        
        # Load teams data
        teams_file = "user_data/jira_teams_20250328_104736.json"
        if os.path.exists(teams_file):
            with open(teams_file, 'r') as f:
                teams_data = json.load(f)
                for team_data in teams_data:
                    # Get team members
                    team_members_list = []
                    for member_data in team_data.get('members', []):
                        member_id = member_data.get('accountId')
                        if member_id and member_id in self.team_members:
                            member = self.team_members[member_id]
                            team_members_list.append(member)
                    
                    team = Team(
                        id=team_data['id'],
                        name=team_data['name'],
                        description=team_data.get('description', ''),
                        team_type=team_data.get('teamType', 'MEMBER_INVITE'),
                        members=team_members_list
                    )
                    self.teams[team.id] = team

    def _generate_fix_versions(self) -> Dict[str, FixVersion]:
        """Generate fix versions for the project."""
        versions = {}
        current_date = datetime.now()
        
        # Generate past versions
        for i in range(1, 4):  # v1.0.0 to v1.2.0
            version_id = generate_id("VER")
            version = FixVersion(
                id=version_id,
                name=f"v1.{i-1}.0",
                description=f"Version 1.{i-1}.0 of the product",
                release_date=current_date - timedelta(days=90*i),
                released=True
            )
            versions[version_id] = version
        
        # Generate current version
        current_version_id = generate_id("VER")
        versions[current_version_id] = FixVersion(
            id=current_version_id,
            name="v1.3.0",
            description="Current development version",
            release_date=current_date + timedelta(days=30),
            released=False
        )
        
        # Generate future versions
        for i in range(4, 6):  # v1.4.0 to v1.5.0
            version_id = generate_id("VER")
            version = FixVersion(
                id=version_id,
                name=f"v1.{i}.0",
                description=f"Planned version 1.{i}.0",
                release_date=current_date + timedelta(days=90*(i-3)),
                released=False
            )
            versions[version_id] = version
        
        return versions

    def _assign_team_member(self) -> Tuple[str, str]:
        """Assign a random team member as reporter and assignee."""
        if not self.team_members:
            raise ValueError("No team members available for assignment")
        reporter = random.choice(list(self.team_members.values()))
        assignee = random.choice(list(self.team_members.values()))
        return reporter.id, assignee.id

    def generate_epic(self) -> Epic:
        """Generate an epic ticket."""
        epic_id = f"EPIC-{self.ticket_counter}"
        self.ticket_counter += 1
        reporter_id, assignee_id = self._assign_team_member()
        
        # Get team_id from the assignee
        team_id = None
        for team in self.teams.values():
            if any(member.id == assignee_id for member in team.members):
                team_id = team.id
                break
        
        # Generate epic description using LLM
        epic_description = self._generate_epic_description(
            self.current_initiative,
            PRODUCT_SCENARIOS
        )
        
        # Generate a concise summary using LLM
        summary = self.llm.generate_summary(epic_description, "Epic")
        
        epic = Epic(
            id=epic_id,
            summary=summary,
            description=epic_description,
            status=TicketStatus.IN_PROGRESS,
            priority=TicketPriority.HIGH,
            reporter_id=reporter_id,
            assignee_id=assignee_id,
            team_id=team_id,
            story_points=random.randint(8, 13),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.epics[epic_id] = epic
        return epic

    def generate_story(self, epic: Epic) -> Story:
        """Generate a story ticket."""
        story_id = f"STORY-{self.ticket_counter}"
        self.ticket_counter += 1
        reporter_id, assignee_id = self._assign_team_member()
        
        # Get team_id from the assignee
        team_id = None
        for team in self.teams.values():
            if any(member.id == assignee_id for member in team.members):
                team_id = team.id
                break
        
        # Generate story description using LLM with epic context
        story_description = self._generate_story_description(
            PRODUCT_SCENARIOS,
            self.current_initiative,
            epic.description if epic else None
        )
        
        # Generate a concise summary using LLM
        summary = self.llm.generate_summary(story_description, "Story")
        
        story = Story(
            id=story_id,
            summary=summary,
            description=story_description,
            status=TicketStatus.IN_PROGRESS,
            priority=TicketPriority.MEDIUM,
            reporter_id=reporter_id,
            assignee_id=assignee_id,
            team_id=team_id,
            epic_link=epic.id if epic else None,
            story_points=random.randint(3, 8),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.stories[story_id] = story
        return story

    def generate_task(self) -> Task:
        """Generate a task ticket."""
        task_id = f"TASK-{self.ticket_counter}"
        self.ticket_counter += 1
        reporter_id, assignee_id = self._assign_team_member()
        
        # Get team_id from the assignee
        team_id = None
        for team in self.teams.values():
            if any(member.id == assignee_id for member in team.members):
                team_id = team.id
                break
        
        # Generate task description using LLM
        task_description = self._generate_task_description(
            PRODUCT_SCENARIOS,
            self.current_initiative
        )
        
        # Generate a concise summary using LLM
        summary = self.llm.generate_summary(task_description, "Task")
        
        task = Task(
            id=task_id,
            summary=summary,
            description=task_description,
            status=TicketStatus.IN_PROGRESS,
            priority=TicketPriority.MEDIUM,
            reporter_id=reporter_id,
            assignee_id=assignee_id,
            team_id=team_id,
            story_points=random.randint(2, 5),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.tasks[task_id] = task
        return task

    def generate_subtask(self, task: Task) -> Subtask:
        """Generate a subtask within a task."""
        subtask_id = generate_ticket_id("SUBTASK", self.ticket_counter)
        self.ticket_counter += 1
        
        # Get parent task information
        parent_task_dict = task.dict() if task else None
        
        # Generate subtask content using GPT-4 with context
        subtask_description, story_points = self.llm.generate_subtask(
            task_description=task.description if task else "",
            task_id=task.id if task else "",
            parent_task=parent_task_dict
        )
        
        # Generate a concise summary using LLM
        summary = self.llm.generate_summary(subtask_description, "Subtask")
        
        # Assign team members
        reporter_id, assignee_id = self._assign_team_member()
        
        subtask = Subtask(
            id=subtask_id,
            summary=summary,
            description=subtask_description,
            status=TicketStatus.IN_PROGRESS,
            priority=TicketPriority.MEDIUM,
            parent_ticket=task.id if task else None,
            reporter_id=reporter_id,
            assignee_id=assignee_id,
            created_at=datetime.now() - timedelta(days=random.randint(1, 5)),
            updated_at=datetime.now() - timedelta(days=random.randint(1, 3)),
            story_points=story_points,
            technical_details=None
        )
        
        self.subtasks[subtask_id] = subtask
        return subtask

    def generate_bug(self, related_tickets: List[str] = None) -> Bug:
        """Generate a bug ticket."""
        bug_id = f"BUG-{self.ticket_counter}"
        self.ticket_counter += 1
        reporter_id, assignee_id = self._assign_team_member()
        
        # Get team_id from the assignee
        team_id = None
        for team in self.teams.values():
            if any(member.id == assignee_id for member in team.members):
                team_id = team.id
                break
        
        # Generate bug description using LLM
        bug_description = self._generate_bug_description(
            PRODUCT_SCENARIOS,
            self.current_initiative
        )
        
        # Generate a concise summary using LLM
        summary = self.llm.generate_summary(bug_description, "Bug")
        
        # Parse the bug description to extract steps, behaviors, etc.
        lines = bug_description.split('\n')
        steps_to_reproduce = []
        actual_behavior = ""
        expected_behavior = ""
        
        current_section = None
        for line in lines:
            if "Steps to Reproduce:" in line:
                current_section = "steps"
                continue
            elif "Current Behavior:" in line or "Actual Behavior:" in line:
                current_section = "actual"
                continue
            elif "Expected Behavior:" in line:
                current_section = "expected"
                continue
            
            if current_section == "steps" and line.strip():
                steps_to_reproduce.append(line.strip())
            elif current_section == "actual" and line.strip():
                actual_behavior += line.strip() + "\n"
            elif current_section == "expected" and line.strip():
                expected_behavior += line.strip() + "\n"
        
        # If any required fields are empty, provide default values
        if not steps_to_reproduce:
            steps_to_reproduce = ["1. Navigate to the feature", "2. Perform the action", "3. Observe the error"]
        if not actual_behavior:
            actual_behavior = "The system is not behaving as expected."
        if not expected_behavior:
            expected_behavior = "The system should work according to the specifications."
        
        bug = Bug(
            id=bug_id,
            summary=summary,
            description=bug_description,
            status=TicketStatus.IN_PROGRESS,
            priority=TicketPriority.HIGH,
            reporter_id=reporter_id,
            assignee_id=assignee_id,
            team_id=team_id,
            story_points=random.randint(1, 3),
            created_at=datetime.now(),
            updated_at=datetime.now(),
            severity=TicketPriority.HIGH,
            steps_to_reproduce=steps_to_reproduce,
            actual_behavior=actual_behavior.strip(),
            expected_behavior=expected_behavior.strip()
        )
        
        self.bugs[bug_id] = bug
        return bug

    def generate_comment(self, ticket: Ticket, author: TeamMember) -> Comment:
        """Generate a comment for a ticket."""
        return Comment(
            id=generate_id("CMT"),
            author_id=author.id,
            content="This is a sample comment.",
            created_at=datetime.now(),
            reactions={"👍": [random.choice(list(self.team_members.keys()))]}
        )

    def generate_sprints_for_team(self, team_id: str, num_sprints: int) -> List[Sprint]:
        """Generate sprints for a team."""
        sprints = []
        current_date = datetime.now()
        
        for i in range(num_sprints):
            sprint = Sprint(
                id=generate_id("SPR"),
                name=f"Sprint {i+1}",
                goal=f"Complete sprint {i+1} goals",
                start_date=current_date + timedelta(days=i*14),
                end_date=current_date + timedelta(days=(i+1)*14),
                status=SprintStatus.PLANNED,
                team_id=team_id
            )
            sprints.append(sprint)
            self.sprints[sprint.id] = sprint
        
        return sprints

    def assign_ticket_to_sprint(self, ticket: Ticket, sprint: Sprint):
        """Assign a ticket to a sprint."""
        if not isinstance(ticket, Epic):  # Don't assign epics to sprints
            ticket.sprint_id = sprint.id
            if sprint.id in self.sprints:
                self.sprints[sprint.id].tickets.append(ticket.id)

    def _create_dependencies(self, ticket: Ticket, available_tickets: List[Ticket]):
        """Create dependencies between tickets."""
        if not available_tickets:
            return

        # Randomly create dependencies
        if random.random() < self.dependency_probability:
            num_dependencies = random.randint(1, min(2, len(available_tickets)))
            dependencies = random.sample(available_tickets, num_dependencies)
            
            for dep in dependencies:
                # Avoid circular dependencies
                if ticket.id not in dep.depends_on:
                    ticket.depends_on.append(dep.id)
                    dep.blocks.append(ticket.id)

    def _create_blocking_issue(self, ticket: Ticket):
        """Create a blocking issue for a ticket."""
        if random.random() < self.blocking_probability:
            blocking_reasons = [
                "Waiting for external API documentation",
                "Pending security review",
                "Infrastructure upgrade required",
                "Dependent service not yet available",
                "Awaiting client feedback",
                "Technical debt needs to be addressed first",
                "Resource constraints"
            ]
            
            ticket.status = TicketStatus.BLOCKED
            ticket.blocking_reason = random.choice(blocking_reasons)
            ticket.blocked_since = datetime.now() - timedelta(days=random.randint(1, 5))

    def _create_relationship(
        self,
        source_ticket: Ticket,
        target_ticket: Ticket,
        relation_type: TicketRelationType,
        note: str = None
    ):
        """Create a relationship between two tickets."""
        # Get the corresponding reverse relationship
        reverse_relations = {
            TicketRelationType.BLOCKS: TicketRelationType.BLOCKED_BY,
            TicketRelationType.CLONES: TicketRelationType.CLONED_BY,
            TicketRelationType.DUPLICATES: TicketRelationType.DUPLICATED_BY,
            TicketRelationType.IMPLEMENTS: TicketRelationType.IMPLEMENTED_BY,
            TicketRelationType.DEPENDS_ON: TicketRelationType.REQUIRED_FOR
        }
        
        # Get the appropriate list attributes
        forward_attr = relation_type.value.replace(" ", "_")
        reverse_attr = reverse_relations[relation_type].value.replace(" ", "_")
        
        # Add the relationship
        getattr(source_ticket, forward_attr).append(target_ticket.id)
        getattr(target_ticket, reverse_attr).append(source_ticket.id)
        
        # Add relationship note if provided
        if note:
            if forward_attr not in source_ticket.relationship_notes:
                source_ticket.relationship_notes[forward_attr] = {}
            source_ticket.relationship_notes[forward_attr][target_ticket.id] = note

    def _handle_clones_and_duplicates(self, tickets: List[Ticket]):
        """Handle clone and duplicate relationships between tickets."""
        for ticket in tickets:
            # Handle clones (similar tickets in different components)
            if (random.random() < self.clone_probability and 
                len(ticket.components) == 1):  # Only clone single-component tickets
                
                # Find a ticket in a different component
                other_components = [c for c in Component if c not in ticket.components]
                if other_components and tickets:
                    clone_candidates = [t for t in tickets 
                                     if t.id != ticket.id and 
                                     any(c in other_components for c in t.components)]
                    if clone_candidates:
                        clone_ticket = random.choice(clone_candidates)
                        note = f"Similar functionality needed in {clone_ticket.components[0].value}"
                        self._create_relationship(ticket, clone_ticket, TicketRelationType.CLONES, note)
            
            # Handle duplicates (exactly same issue reported multiple times)
            if random.random() < self.duplicate_probability:
                duplicate_candidates = [t for t in tickets 
                                     if t.id != ticket.id and 
                                     t.type == ticket.type and
                                     set(t.components) == set(ticket.components)]
                if duplicate_candidates:
                    duplicate_ticket = random.choice(duplicate_candidates)
                    note = "Exact same issue reported separately"
                    self._create_relationship(ticket, duplicate_ticket, TicketRelationType.DUPLICATES, note)

    def _handle_implementations(self, stories: List[Story], tasks: List[Task]):
        """Handle implementation relationships between stories and tasks."""
        for story in stories:
            if random.random() < self.implements_probability:
                # Find tasks that could implement this story
                implement_candidates = [t for t in tasks 
                                     if t.id != story.id and 
                                     any(c in story.components for c in t.components)]
                if implement_candidates:
                    num_implementers = random.randint(1, min(3, len(implement_candidates)))
                    implementers = random.sample(implement_candidates, num_implementers)
                    for task in implementers:
                        note = f"Technical implementation of {story.summary}"
                        self._create_relationship(task, story, TicketRelationType.IMPLEMENTS, note)

    def generate_sprint_tickets(self, sprint_id: str, team_id: str, num_tickets: int) -> List[Ticket]:
        """Generate tickets for a sprint."""
        if sprint_id not in self.sprints:
            raise ValueError(f"Sprint {sprint_id} not found")
            
        if team_id not in self.teams:
            raise ValueError(f"Team {team_id} not found")
            
        sprint = self.sprints[sprint_id]
        team = self.teams[team_id]
        tickets = []
        
        # Calculate number of each ticket type
        num_stories = int(num_tickets * 0.4)  # 40% stories
        num_tasks = int(num_tickets * 0.3)    # 30% tasks
        num_subtasks = int(num_tickets * 0.2)  # 20% subtasks
        num_bugs = num_tickets - (num_stories + num_tasks + num_subtasks)  # Remaining as bugs
        
        # Generate epics first (1-2 per sprint)
        num_epics = random.randint(1, 2)
        for _ in range(num_epics):
            epic = self.generate_epic()
            self.assign_ticket_to_sprint(epic, sprint)
            tickets.append(epic)
        
        # Generate stories
        for _ in range(num_stories):
            if self.epics:
                epic = random.choice(list(self.epics.values()))
                story = self.generate_story(epic)
            else:
                story = self.generate_story(None)  # Default to backend for now
            self.assign_ticket_to_sprint(story, sprint)
            tickets.append(story)
        
        # Generate tasks
        for _ in range(num_tasks):
            task = self.generate_task()
            self.assign_ticket_to_sprint(task, sprint)
            tickets.append(task)
        
        # Generate subtasks
        for _ in range(num_subtasks):
            if self.tasks:
                parent_task = random.choice(list(self.tasks.values()))
                subtask = self.generate_subtask(parent_task)
                self.assign_ticket_to_sprint(subtask, sprint)
                tickets.append(subtask)
        
        # Generate bugs
        for _ in range(num_bugs):
            bug = self.generate_bug()
            self.assign_ticket_to_sprint(bug, sprint)
            tickets.append(bug)
        
        # Create dependencies between tickets
        self._create_dependencies(tickets[0], tickets[1:])
        
        # Handle clones and duplicates
        self._handle_clones_and_duplicates(tickets)
        
        # Handle implementations
        stories = [t for t in tickets if isinstance(t, Story)]
        tasks = [t for t in tickets if isinstance(t, Task)]
        self._handle_implementations(stories, tasks)
        
        return tickets

    def generate_ticket_hierarchy(self) -> Dict[str, List[Ticket]]:
        """Generate a complete ticket hierarchy with epics, stories, tasks, and bugs."""
        result = {
            "epics": [],
            "stories": [],
            "tasks": [],
            "subtasks": [],
            "bugs": []
        }
        
        # Generate epics for each component
        for component in Component:
            epic = self.generate_epic()
            result["epics"].append(epic)
            
            # Generate sprints for each team
            for team in self.teams.values():
                sprints = self.generate_sprints_for_team(team.id, self.stories_per_sprint)
                
                # Generate tickets for each sprint
                for sprint in sprints:
                    sprint_tickets = self.generate_sprint_tickets(sprint.id, team.id, len(sprint_tickets))
                    result["stories"].extend(sprint_tickets[1:])
                    result["tasks"].extend(sprint_tickets[2:])
                    result["subtasks"].extend(sprint_tickets[3:])
                    result["bugs"].extend([sprint_tickets[0] if isinstance(sprint_tickets[0], Bug) else None])
                    
                    # Link stories to epic
                    for story in sprint_tickets[1:]:
                        if isinstance(story, Story):
                            epic.child_stories.append(story.id)
        
        return result

    def get_all_tickets(self) -> Dict[str, Ticket]:
        """Return all generated tickets."""
        return {
            **self.epics,
            **self.stories,
            **self.tasks,
            **self.subtasks,
            **self.bugs
        }

    def get_ticket_by_id(self, ticket_id: str) -> Optional[Ticket]:
        """Get a ticket by its ID."""
        return self.get_all_tickets().get(ticket_id)

    def get_sprint_by_id(self, sprint_id: str) -> Optional[Sprint]:
        """Get a sprint by its ID."""
        return self.sprints.get(sprint_id)

    def get_team_sprints(self, team_id: str) -> List[Sprint]:
        """Get all sprints for a team."""
        return [sprint for sprint in self.sprints.values() if sprint.team_id == team_id]

    def get_sprint_tickets(self, sprint_id: str) -> List[Ticket]:
        """Get all tickets in a sprint."""
        sprint = self.get_sprint_by_id(sprint_id)
        if not sprint:
            return []
        return [ticket for ticket in self.get_all_tickets().values() 
                if ticket.sprint_id == sprint_id]

    def get_blocked_tickets(self, sprint_id: str = None) -> List[Ticket]:
        """Get all blocked tickets, optionally filtered by sprint."""
        all_tickets = self.get_all_tickets().values()
        blocked_tickets = [t for t in all_tickets if t.status == TicketStatus.BLOCKED]
        
        if sprint_id:
            return [t for t in blocked_tickets if t.sprint_id == sprint_id]
        return blocked_tickets

    def get_ticket_dependencies(self, ticket_id: str) -> Dict[str, List[str]]:
        """Get all dependencies for a ticket."""
        ticket = self.get_ticket_by_id(ticket_id)
        if not ticket:
            return {}
        
        return {
            "depends_on": ticket.depends_on,
            "blocked_by": ticket.blocked_by,
            "blocks": ticket.blocks
        }

    def get_sprint_dependencies(self, sprint_id: str) -> Dict[str, List[tuple[str, str]]]:
        """Get all dependencies between tickets in a sprint."""
        sprint_tickets = self.get_sprint_tickets(sprint_id)
        
        dependencies = {
            "blocking": [],  # List of (blocker_id, blocked_id) tuples
            "dependencies": []  # List of (dependent_id, dependency_id) tuples
        }
        
        for ticket in sprint_tickets:
            # Add blocking relationships
            for blocked_id in ticket.blocks:
                dependencies["blocking"].append((ticket.id, blocked_id))
            
            # Add dependencies
            for dep_id in ticket.depends_on:
                dependencies["dependencies"].append((ticket.id, dep_id))
        
        return dependencies

    def get_ticket_relationships(self, ticket_id: str) -> Dict[str, Dict[str, List[Tuple[str, Optional[str]]]]]:
        """Get all relationships for a ticket with their notes."""
        ticket = self.get_ticket_by_id(ticket_id)
        if not ticket:
            return {}
        
        relationships = {
            "outgoing": {},  # relationships where this ticket is the source
            "incoming": {}   # relationships where this ticket is the target
        }
        
        # Helper to add relationships to the result
        def add_relationship(rel_type: str, target_id: str, direction: str):
            if rel_type not in relationships[direction]:
                relationships[direction][rel_type] = []
            note = ticket.relationship_notes.get(rel_type, {}).get(target_id)
            relationships[direction][rel_type].append((target_id, note))
        
        # Add all relationship types
        for rel_type in TicketRelationType:
            attr_name = rel_type.value.replace(" ", "_")
            if hasattr(ticket, attr_name):
                related_ids = getattr(ticket, attr_name)
                for related_id in related_ids:
                    add_relationship(attr_name, related_id, "outgoing")

    def set_product_initiative(self, initiative_name: str):
        """Set the current product initiative."""
        self.current_initiative = initiative_name

    def generate_ticket(self, ticket_type: TicketType) -> Ticket:
        """Generate a ticket of the specified type."""
        reporter_id, assignee_id = self._assign_team_member()
        
        # Get team_id from the assignee's team
        team_id = None
        for team in self.teams.values():
            if any(member.id == assignee_id for member in team.members):
                team_id = team.id
                break

        ticket = Ticket(
            id=generate_id("TKT"),
            type=ticket_type,
            summary=f"Sample {ticket_type.value} ticket",
            description=f"This is a sample {ticket_type.value} ticket for testing purposes.",
            status=TicketStatus.TODO,
            priority="Medium",
            reporter_id=reporter_id,
            assignee_id=assignee_id,
            team_id=team_id,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.tickets[ticket.id] = ticket
        return ticket

    def _generate_epic_description(self, initiative, scenarios):
        """Generate a detailed epic description using GPT-4."""
        prompt = f"""Generate a detailed epic description for a software development project with the following context:

Initiative: {initiative if isinstance(initiative, str) else initiative.get('description', 'Not specified')}
Objectives: {', '.join(initiative['objectives']) if isinstance(initiative, dict) and 'objectives' in initiative else 'Not specified'}
Success Metrics: {', '.join(initiative['success_metrics']) if isinstance(initiative, dict) and 'success_metrics' in initiative else 'Not specified'}

Generate a comprehensive description that covers the initiative's goals, challenges, and implementation approach. Make it detailed, realistic, and specific to the initiative while keeping it generic enough to apply to any software project."""

        return self.llm.generate_ticket_description(
            title=f"Epic: {initiative.get('description', 'Initiative') if isinstance(initiative, dict) else initiative}",
            ticket_type="Epic",
            prompt=prompt
        )

    def _generate_story_description(self, scenarios, initiative=None, epic_description=None):
        """Generate a detailed story description using GPT-4."""
        prompt = f"""Generate a detailed story description for a software development project with the following context:

Initiative: {initiative['description'] if isinstance(initiative, dict) and 'description' in initiative else 'Not specified'}

Epic Description: {epic_description if epic_description else 'Not specified'}

Please follow the user story format:
As a [type of user], I want [goal] so that [benefit]

Then provide additional details about:
1. Acceptance criteria

Make the description detailed, realistic, and specific to the epic and initiative while keeping it generic enough to apply to any software project. If an epic description is provided, ensure the story aligns with the epic's goals and scope."""

        return self.llm.generate_ticket_description(
            title=f"Story: {initiative.get('description', 'Initiative') if isinstance(initiative, dict) else initiative}",
            ticket_type="Story",
            prompt=prompt
        )

    def _generate_bug_description(self, scenarios, initiative):
        """Generate a realistic bug description using GPT-4."""
        prompt = f"""Generate a detailed bug report for a software development project with the following context:

Initiative: {initiative['description'] if isinstance(initiative, dict) and 'description' in initiative else 'Not specified'}

Generate a comprehensive bug report that includes the issue description, impact, and any relevant technical details. Make it detailed, realistic, and specific to the initiative while keeping it generic enough to apply to any software project."""

        return self.llm.generate_ticket_description(
            title=f"Bug: {initiative.get('description', 'Initiative') if isinstance(initiative, dict) else initiative}",
            ticket_type="Bug",
            prompt=prompt
        )

    def _generate_task_description(self, scenarios, initiative):
        """Generate a detailed technical task description using GPT-4."""
        prompt = f"""Generate a detailed technical task description for a software development project with the following context:

Initiative: {initiative['description'] if isinstance(initiative, dict) and 'description' in initiative else 'Not specified'}

Generate a comprehensive technical task description that includes the implementation details, requirements, and any relevant technical considerations. Make it detailed, realistic, and specific to the initiative while keeping it generic enough to apply to any software project."""

        return self.llm.generate_ticket_description(
            title=f"Task: {initiative.get('description', 'Initiative') if isinstance(initiative, dict) else initiative}",
            ticket_type="Task",
            prompt=prompt
        )

    def _generate_subtask(self, task_id: str, task_description: str, sprint_id: Optional[str] = None) -> Subtask:
        """Generate a subtask for a task."""
        subtask_id = f"SUBTASK-{self.next_ticket_id()}"
        
        # Get the parent task information
        parent_task = self.tasks.get(task_id)
        if parent_task:
            parent_task_dict = parent_task.dict()
        else:
            parent_task_dict = None
        
        # Generate subtask content with parent task context
        subtask_description, story_points = self.llm.generate_subtask(
            task_description=task_description,
            task_id=task_id,
            parent_task=parent_task_dict
        )
        
        # Extract technical details from the subtask content
        technical_details = self._extract_technical_details(subtask_description)
        
        # Generate summary using LLM
        summary = self.llm.generate_summary(subtask_description, "Subtask", parent_task.components[0].value if parent_task else "Backend")
        
        subtask = Subtask(
            id=subtask_id,
            type="Sub-task",
            summary=summary,
            description=subtask_description,
            status="In Progress",
            priority="Medium",
            parent_ticket=task_id,
            sprint_id=sprint_id,
            reporter_id=self._get_random_team_member_id(),
            assignee_id=self._get_random_team_member_id(),
            components=parent_task.components if parent_task else ["Backend"],  # Use parent task's components
            fix_versions=[self._get_current_release()],
            created_at=self._generate_timestamp(),
            updated_at=self._generate_timestamp(),
            story_points=story_points,
            technical_details=technical_details
        )
        
        return subtask 