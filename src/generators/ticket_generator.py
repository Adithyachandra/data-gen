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
                        department=Department.ENGINEERING.value,
                        role=Role.SOFTWARE_ENGINEER.value,
                        seniority=Seniority.MID,
                        skills=[Skill.PYTHON.value, Skill.JAVA.value],
                        join_date=datetime.now() - timedelta(days=random.randint(30, 730))
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
                            member.team_id = team_data['id']
                            team_members_list.append(member)
                    
                    # Select a manager from the team members or create one
                    manager = None
                    if team_members_list:
                        manager = random.choice(team_members_list)
                    else:
                        manager_id = generate_id()
                        manager = TeamMember(
                            id=manager_id,
                            name=f"Manager of {team_data['name']}",
                            email=f"manager.{team_data['name'].lower().replace(' ', '.')}@company.com",
                            department=Department.ENGINEERING.value,
                            role=Role.ENGINEERING_MANAGER.value,
                            seniority=Seniority.SENIOR,
                            skills=[Skill.TEAM_LEADERSHIP.value, Skill.PROJECT_MANAGEMENT.value],
                            join_date=datetime.now() - timedelta(days=random.randint(365, 1095)),
                            team_id=team_data['id']
                        )
                        self.team_members[manager.id] = manager
                        team_members_list.append(manager)
                    
                    team = Team(
                        id=team_data['id'],
                        name=team_data['name'],
                        department=Department.ENGINEERING.value,
                        description=team_data.get('description', f"Team responsible for {team_data['name']}"),
                        manager_id=manager.id,
                        members=team_members_list,
                        created_date=datetime.now() - timedelta(days=random.randint(30, 365))
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

    def generate_epic(self, component: Component) -> Epic:
        """Generate an epic ticket."""
        epic_id = f"EPIC-{self.ticket_counter}"
        self.ticket_counter += 1
        reporter_id, assignee_id = self._assign_team_member()
        
        # Get team_id from the assignee
        team_id = self.team_members[assignee_id].team_id if assignee_id in self.team_members else None
        
        # Generate epic description using LLM
        epic_description = self._generate_epic_description(
            self.current_initiative,
            PRODUCT_SCENARIOS,
            self.config.get('team_focus', 'backend'),
            self.config.get('feature', 'feature')
        )
        
        # Generate a concise summary using LLM
        summary = self.llm.generate_summary(epic_description, "Epic", component.value)
        
        epic = Epic(
            id=epic_id,
            summary=summary,
            description=epic_description,
            status=TicketStatus.IN_PROGRESS,
            priority=TicketPriority.HIGH,
            reporter_id=reporter_id,
            assignee_id=assignee_id,
            team_id=team_id,
            components=[component],
            story_points=random.randint(8, 13),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.epics[epic_id] = epic
        return epic

    def generate_story(self, epic: Epic, component: Component) -> Story:
        """Generate a story ticket."""
        story_id = f"STORY-{self.ticket_counter}"
        self.ticket_counter += 1
        reporter_id, assignee_id = self._assign_team_member()
        
        # Get team_id from the assignee
        team_id = self.team_members[assignee_id].team_id if assignee_id in self.team_members else None
        
        # Generate story description using LLM
        story_description = self._generate_story_description(
            self.config.get('feature', 'feature'),
            PRODUCT_SCENARIOS,
            self.config.get('team_focus', 'backend'),
            self.config.get('tech_stack', 'Python'),
            self.current_initiative
        )
        
        # Generate a concise summary using LLM
        summary = self.llm.generate_summary(story_description, "Story", component.value)
        
        story = Story(
            id=story_id,
            summary=summary,
            description=story_description,
            status=TicketStatus.IN_PROGRESS,
            priority=TicketPriority.MEDIUM,
            reporter_id=reporter_id,
            assignee_id=assignee_id,
            team_id=team_id,
            epic_link=epic.id,
            components=[component],
            story_points=random.randint(3, 8),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.stories[story_id] = story
        return story

    def generate_task(self, component: Component) -> Task:
        """Generate a task ticket."""
        task_id = f"TASK-{self.ticket_counter}"
        self.ticket_counter += 1
        reporter_id, assignee_id = self._assign_team_member()
        
        # Get team_id from the assignee
        team_id = self.team_members[assignee_id].team_id if assignee_id in self.team_members else None
        
        # Generate task description using LLM
        task_description = self._generate_task_description(
            self.config.get('improvement', 'improvement'),
            PRODUCT_SCENARIOS,
            self.config.get('team_focus', 'backend'),
            self.config.get('tech_stack', 'Python'),
            self.config.get('feature', 'feature')
        )
        
        # Generate a concise summary using LLM
        summary = self.llm.generate_summary(task_description, "Task", component.value)
        
        task = Task(
            id=task_id,
            summary=summary,
            description=task_description,
            status=TicketStatus.IN_PROGRESS,
            priority=TicketPriority.MEDIUM,
            reporter_id=reporter_id,
            assignee_id=assignee_id,
            team_id=team_id,
            components=[component],
            story_points=random.randint(2, 5),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.tasks[task_id] = task
        return task

    def generate_subtask(self, task: Task, component: Component) -> Subtask:
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
        summary = self.llm.generate_summary(subtask_description, "Subtask", component.value)
        
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
            components=[component],
            created_at=datetime.now() - timedelta(days=random.randint(1, 5)),
            updated_at=datetime.now() - timedelta(days=random.randint(1, 3)),
            story_points=story_points,
            technical_details=None
        )
        
        self.subtasks[subtask_id] = subtask
        return subtask

    def generate_bug(self, component: Component, related_tickets: List[str] = None) -> Bug:
        """Generate a bug ticket."""
        bug_id = f"BUG-{self.ticket_counter}"
        self.ticket_counter += 1
        reporter_id, assignee_id = self._assign_team_member()
        
        # Get team_id from the assignee
        team_id = self.team_members[assignee_id].team_id if assignee_id in self.team_members else None
        
        # Generate bug description using LLM
        bug_description = self._generate_bug_description(
            PRODUCT_SCENARIOS,
            self.config.get('team_focus', 'backend'),
            self.config.get('tech_stack', 'Python'),
            self.config.get('feature', 'feature')
        )
        
        # Generate a concise summary using LLM
        summary = self.llm.generate_summary(bug_description, "Bug", component.value)
        
        # Parse the bug description to extract steps, behaviors, etc.
        # This assumes the LLM generates a structured response with these sections
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
            components=[component],
            story_points=random.randint(1, 3),
            created_at=datetime.now(),
            updated_at=datetime.now(),
            # Required Bug-specific fields
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
            id=generate_id("COM"),
            author_id=author.id,
            content=self.llm.generate_ticket_comment(
                ticket_description=ticket.description,
                ticket_type=ticket.type.value,
                author_role=author.role
            ),
            created_at=datetime.now() - timedelta(days=random.randint(1, 5)),
            reactions={"👍": [random.choice(list(self.team_members.keys()))]}
        )

    def generate_sprints_for_team(self, team_id: str, num_sprints: int) -> List[Sprint]:
        """Generate sprints for a team."""
        if team_id not in self.teams:
            raise ValueError(f"Team {team_id} not found")
            
        team = self.teams[team_id]
        sprints = []
        current_date = datetime.now()
        
        # Generate past sprints
        for i in range(num_sprints):
            sprint_id = generate_id("SPRINT")
            start_date = current_date - timedelta(days=self.sprint_duration_days * (num_sprints - i))
            end_date = start_date + timedelta(days=self.sprint_duration_days)
            
            # Generate a goal for the sprint
            if self.current_initiative:
                goal = f"Deliver key features for {self.current_initiative} initiative"
            else:
                goals = [
                    "Improve system performance and reliability",
                    "Enhance user experience and interface",
                    "Implement new features and capabilities",
                    "Fix critical bugs and technical debt",
                    "Optimize system architecture",
                    "Strengthen security measures",
                    "Improve code quality and test coverage"
                ]
                goal = random.choice(goals)
            
            sprint = Sprint(
                id=sprint_id,
                name=f"{team.name} Sprint {self.sprint_counter}",
                description=f"Sprint {self.sprint_counter} for {team.name}",
                goal=goal,
                start_date=start_date,
                end_date=end_date,
                status=SprintStatus.COMPLETED if i < num_sprints - 1 else SprintStatus.ACTIVE,
                team_id=team_id,
                tickets=[]
            )
            
            self.sprints[sprint_id] = sprint
            sprints.append(sprint)
            self.sprint_counter += 1
        
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
            epic = self.generate_epic(Component.BACKEND)  # Default to backend for now
            self.assign_ticket_to_sprint(epic, sprint)
            tickets.append(epic)
        
        # Generate stories
        for _ in range(num_stories):
            if self.epics:
                epic = random.choice(list(self.epics.values()))
                story = self.generate_story(epic, Component.BACKEND)  # Default to backend for now
            else:
                story = self.generate_story(None, Component.BACKEND)  # Default to backend for now
            self.assign_ticket_to_sprint(story, sprint)
            tickets.append(story)
        
        # Generate tasks
        for _ in range(num_tasks):
            task = self.generate_task(Component.BACKEND)  # Default to backend for now
            self.assign_ticket_to_sprint(task, sprint)
            tickets.append(task)
        
        # Generate subtasks
        for _ in range(num_subtasks):
            if self.tasks:
                parent_task = random.choice(list(self.tasks.values()))
                subtask = self.generate_subtask(parent_task, Component.BACKEND)  # Default to backend for now
                self.assign_ticket_to_sprint(subtask, sprint)
                tickets.append(subtask)
        
        # Generate bugs
        for _ in range(num_bugs):
            bug = self.generate_bug(Component.BACKEND)  # Default to backend for now
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
            epic = self.generate_epic(component)
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

    def generate_ticket(self, team, ticket_type=None, parent_epic=None):
        """Generate a single ticket with realistic content based on team context."""
        ticket_id = generate_id()
        
        # Get team's focus areas and tech stack
        team_focus = next((t["focus_areas"] for t in self.config.DEPARTMENT_STRUCTURE["Engineering"]["teams"] 
                          if t["name"] == team.name), [])
        tech_stack = next((t["tech_stack"] for t in self.config.DEPARTMENT_STRUCTURE["Engineering"]["teams"] 
                          if t["name"] == team.name), [])
        
        # Determine ticket type if not provided
        if not ticket_type:
            ticket_type = random.choice([TicketType.STORY, TicketType.BUG, TicketType.TASK])
            if random.random() < 0.1:  # 10% chance for epic
                ticket_type = TicketType.EPIC
        
        # Get relevant templates and scenarios
        component = random.choice(team.components)
        templates = STORY_TEMPLATES.get(component.value, {})
        scenarios = PRODUCT_SCENARIOS["Enterprise Workflow Automation"]
        
        # Generate content based on ticket type
        if ticket_type == TicketType.EPIC:
            # Use current initiative if set, otherwise random
            initiative_name = self.current_initiative if self.current_initiative else random.choice(list(PRODUCT_INITIATIVES.keys()))
            initiative = PRODUCT_INITIATIVES[initiative_name]
            # Select a specific feature from the product scenarios
            feature = random.choice(scenarios['key_features'])
            title = f"[{component.value}] {initiative['description']} - {feature}"
            description = self._generate_epic_description(
                initiative,
                scenarios,
                team_focus,
                feature
            )
        
        elif ticket_type == TicketType.STORY:
            # Use current initiative's objectives for stories
            if self.current_initiative:
                initiative = PRODUCT_INITIATIVES[self.current_initiative]
                objective = random.choice(initiative['objectives'])
                # Select a specific feature and persona
                feature = random.choice(scenarios['key_features'])
                persona = random.choice(scenarios['user_personas'])
                title = f"[{component.value}] {objective} for {feature}"
                description = self._generate_story_description(
                    objective,
                    scenarios,
                    team_focus,
                    tech_stack,
                    initiative,
                    feature,
                    persona
                )
            else:
                # Fall back to templates if no initiative specified
                if templates:
                    feature = random.choice(templates["features"])
                    persona = random.choice(scenarios['user_personas'])
                    title = f"[{component.value}] {feature}"
                    description = self._generate_story_description(
                        feature,
                        scenarios,
                        team_focus,
                        tech_stack,
                        None,
                        feature,
                        persona
                    )
                else:
                    title = f"[{component.value}] Generic story"
                    description = "Default story description"
        
        elif ticket_type == TicketType.BUG:
            feature = random.choice(scenarios['key_features'])
            title = f"[{component.value}] Fix issue with {feature} in {random.choice(team_focus)}"
            description = self._generate_bug_description(
                scenarios,
                team_focus,
                tech_stack,
                feature
            )
        
        else:  # TASK
            if templates:
                improvement = random.choice(templates["improvements"])
                feature = random.choice(scenarios['key_features'])
                title = f"[{component.value}] {improvement} for {feature}"
                description = self._generate_task_description(
                    improvement,
                    scenarios,
                    team_focus,
                    tech_stack,
                    feature
                )
            else:
                title = f"[{component.value}] Generic task"
                description = "Default task description"
        
        # Generate story points based on complexity
        story_points = random.choice(self.config.default_story_points)
        
        # Create and return the ticket
        return Ticket(
            id=ticket_id,
            title=title,
            description=description,
            ticket_type=ticket_type,
            status=TicketStatus.TODO,
            priority=random.choice(list(TicketPriority)),
            story_points=story_points,
            components=[component],
            epic_id=parent_epic.id if parent_epic else None
        )

    def _generate_epic_description(self, initiative, scenarios, team_focus, feature):
        """Generate a detailed epic description using GPT-4."""
        prompt = f"""Generate a detailed epic description for a software development project with the following context:

Initiative: {initiative if isinstance(initiative, str) else initiative.get('description', 'Not specified')}
Feature: {feature}
Team Focus Areas: {team_focus}
Objectives: {', '.join(initiative['objectives']) if isinstance(initiative, dict) and 'objectives' in initiative else 'Not specified'}
Success Metrics: {', '.join(initiative['success_metrics']) if isinstance(initiative, dict) and 'success_metrics' in initiative else 'Not specified'}

Please include:
1. Background and context
2. Feature focus and current pain points
3. Objectives and success metrics
4. Current challenges
5. Target users and their needs
6. Implementation areas
7. Technical considerations

Make the description detailed, realistic, and specific to the feature while keeping it generic enough to apply to any software project."""

        return self.llm.generate_ticket_description(
            title=f"Epic: {feature}",
            ticket_type="Epic",
            component="Backend",  # Default to Backend for now
            prompt=prompt
        )

    def _generate_story_description(self, feature, scenarios, team_focus, tech_stack, initiative=None, specific_feature=None, persona=None):
        """Generate a detailed story description using GPT-4."""
        prompt = f"""Generate a detailed story description for a software development project with the following context:

Feature: {feature}
Specific Feature: {specific_feature if specific_feature else feature}
Team Focus Areas: {team_focus}
Tech Stack: {tech_stack}
Persona: {persona['role'] + ' - ' + ', '.join(persona['needs']) if isinstance(persona, dict) else 'Not specified'}
Initiative: {initiative['description'] if isinstance(initiative, dict) and 'description' in initiative else 'Not specified'}

Please include:
1. User story format (As a... I want... So that...)
2. Feature context
3. Technical context
4. Detailed acceptance criteria
5. Technical requirements
6. Performance requirements
7. Security requirements
8. Testing requirements

Make the description detailed, realistic, and specific to the feature while keeping it generic enough to apply to any software project."""

        return self.llm.generate_ticket_description(
            title=f"Story: {feature}",
            ticket_type="Story",
            component="Backend",  # Default to Backend for now
            prompt=prompt
        )

    def _generate_bug_description(self, scenarios, team_focus, tech_stack, feature):
        """Generate a realistic bug description using GPT-4."""
        prompt = f"""Generate a detailed bug report for a software development project with the following context:

Feature: {feature}
Team Focus Areas: {team_focus}
Tech Stack: {tech_stack}

Please include:
1. Issue summary and impact
2. Detailed steps to reproduce
3. Expected behavior
4. Current behavior
5. Technical context
6. Proposed solution
7. Additional notes

Make the bug report detailed, realistic, and specific to the feature while keeping it generic enough to apply to any software project."""

        return self.llm.generate_ticket_description(
            title=f"Bug: {feature}",
            ticket_type="Bug",
            component="Backend",  # Default to Backend for now
            prompt=prompt
        )

    def _generate_task_description(self, improvement, scenarios, team_focus, tech_stack, feature):
        """Generate a detailed technical task description using GPT-4."""
        prompt = f"""Generate a detailed technical task description for a software development project with the following context:

Improvement: {improvement}
Feature: {feature}
Team Focus Areas: {team_focus}
Tech Stack: {tech_stack}

Please include:
1. Technical task summary
2. Context and background
3. Technical requirements
4. Performance requirements
5. Implementation notes
6. Dependencies
7. Testing requirements
8. Documentation requirements
9. Review requirements

Make the task description detailed, realistic, and specific to the feature while keeping it generic enough to apply to any software project."""

        return self.llm.generate_ticket_description(
            title=f"Task: {improvement}",
            ticket_type="Task",
            component="Backend",  # Default to Backend for now
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