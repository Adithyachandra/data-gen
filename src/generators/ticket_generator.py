from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import random

from src.models.ticket import (
    Ticket, Epic, Story, Task, Subtask, Bug,
    TicketType, TicketStatus, TicketPriority, Component,
    Comment, FixVersion, Sprint, SprintStatus, TicketRelationType
)
from src.models.team import TeamMember, Team
from src.generators.utils import (
    generate_id, generate_ticket_id, random_date_between,
    weighted_choice, generate_paragraph, random_subset
)
from src.config.sample_company import INNOVATECH_CONFIG, PRODUCT_INITIATIVES, PRODUCT_SCENARIOS, STORY_TEMPLATES
from src.generators.llm_generator import LLMGenerator

class TicketGenerator:
    def __init__(self, team_members: Dict[str, TeamMember], teams: Dict[str, Team], config: dict):
        self.config = config
        self.team_members = team_members
        self.teams = teams
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

    def generate_epic(self, component: Component) -> Epic:
        """Generate an epic with related stories."""
        epic_id = generate_ticket_id("EPIC", self.ticket_counter)
        self.ticket_counter += 1
        
        # Select epic owner from team members
        epic_owner = random.choice(list(self.team_members.values()))
        
        # Find the product and initiative in the config
        product = None
        initiative = None
        if self.current_initiative:
            for p in self.config['products']:
                for i in p['initiatives']:
                    if i['name'] == self.current_initiative:
                        product = p
                        initiative = i
                        break
                if product:
                    break
        
        # Generate description using GPT-4 with context
        prompt = f"""Generate a detailed epic description for a software development project with the following context:
        Company: {self.config['company']['name']}
        Industry: {self.config['company']['industry']}
        Product: {product['name'] if product else 'Not specified'}
        Initiative: {initiative['name'] if initiative else 'Not specified'}
        Component: {component.value}
        
        The epic should:
        1. Align with the company's business goals
        2. Support the product initiative
        3. Focus on the specified component
        4. Include clear success criteria
        5. Consider technical and business impact
        
        Format the response in markdown."""
        
        description = self.llm.generate_ticket_description(
            title=f"Epic: {component.value} Enhancement Initiative",
            ticket_type="Epic",
            component=component.value,
            prompt=prompt
        )
        
        # Generate summary from description
        summary = self.llm.generate_summary(description, "Epic", component.value)
        
        epic = Epic(
            id=epic_id,
            summary=summary,
            description=description,
            status=TicketStatus.IN_PROGRESS,
            priority=TicketPriority.HIGH,
            reporter_id=epic_owner.id,
            assignee_id=epic_owner.id,
            components=[component],
            created_at=datetime.now() - timedelta(days=random.randint(30, 90)),
            updated_at=datetime.now() - timedelta(days=random.randint(1, 30)),
            story_points=13,
            target_start=datetime.now() - timedelta(days=30),
            target_end=datetime.now() + timedelta(days=60)
        )
        
        self.epics[epic_id] = epic
        return epic

    def generate_story(self, epic: Epic, component: Component) -> Story:
        """Generate a story within an epic."""
        story_id = generate_ticket_id("STORY", self.ticket_counter)
        self.ticket_counter += 1
        
        # Select story owner
        story_owner = random.choice(list(self.team_members.values()))
        
        # Generate story content using the simpler format
        story_content = self.llm.generate_story(component.value, epic.summary)
        
        # Parse the content to extract acceptance criteria
        lines = story_content.strip().split('\n')
        acceptance_criteria = []
        user_persona = ""
        story_points = 5
        
        for i, line in enumerate(lines):
            if line.startswith('As a '):
                user_persona = line[5:].strip()
            elif line.startswith('1.') or line.startswith('2.') or line.startswith('3.'):
                acceptance_criteria.append(line[2:].strip())
            elif line.startswith('Story Points:'):
                try:
                    story_points = int(line.split(':')[1].strip())
                except (ValueError, IndexError):
                    story_points = 5
        
        # Generate summary from the first line (As a...)
        summary = lines[0] + ' ' + lines[1] + ' ' + lines[2]
        
        story = Story(
            id=story_id,
            summary=summary,
            description=story_content,
            status=TicketStatus.IN_PROGRESS,
            priority=TicketPriority.MEDIUM,
            epic_link=epic.id,
            reporter_id=story_owner.id,
            assignee_id=story_owner.id,
            components=[component],
            created_at=datetime.now() - timedelta(days=random.randint(15, 45)),
            updated_at=datetime.now() - timedelta(days=random.randint(1, 15)),
            story_points=story_points,
            acceptance_criteria=acceptance_criteria,
            user_persona=user_persona
        )
        
        self.stories[story_id] = story
        return story

    def generate_task(self, story: Story, component: Component) -> Task:
        """Generate a task within a story."""
        task_id = generate_ticket_id("TASK", self.ticket_counter)
        self.ticket_counter += 1
        
        # Select task owner
        task_owner = random.choice(list(self.team_members.values()))
        
        # Find the product and initiative in the config
        product = None
        initiative = None
        if self.current_initiative:
            for p in self.config['products']:
                for i in p['initiatives']:
                    if i['name'] == self.current_initiative:
                        product = p
                        initiative = i
                        break
                if product:
                    break
        
        # Generate task content using GPT-4 with context
        prompt = f"""Generate a detailed task description for a software development project with the following context:
        Company: {self.config['company']['name']}
        Industry: {self.config['company']['industry']}
        Product: {product['name'] if product else 'Not specified'}
        Initiative: {initiative['name'] if initiative else 'Not specified'}
        Component: {component.value}
        Story: {story.summary}
        
        The task should:
        1. Provide technical implementation details
        2. Include performance requirements
        3. Specify testing requirements
        4. Define documentation needs
        5. List dependencies
        6. Include estimated hours
        7. Consider security implications
        8. Define review requirements
        
        Format the response in markdown."""
        
        task_content = self.llm.generate_ticket_description(
            title=f"Task: Implement {component.value} Component",
            ticket_type="Task",
            component=component.value,
            prompt=prompt
        )
        
        # Generate summary from description
        summary = self.llm.generate_summary(task_content, "Task", component.value)
        
        # Parse the generated content to extract estimated hours and technical details
        estimated_hours = self.llm.extract_estimated_hours(task_content)
        technical_details = self.llm.extract_technical_details(task_content)
        
        task = Task(
            id=task_id,
            summary=summary,
            description=task_content,
            status=TicketStatus.IN_PROGRESS,
            priority=TicketPriority.MEDIUM,
            epic_link=story.epic_link,
            parent_ticket=story.id,
            reporter_id=task_owner.id,
            assignee_id=task_owner.id,
            components=[component],
            created_at=datetime.now() - timedelta(days=random.randint(5, 15)),
            updated_at=datetime.now() - timedelta(days=random.randint(1, 5)),
            estimated_hours=estimated_hours,
            technical_details=technical_details
        )
        
        self.tasks[task_id] = task
        return task

    def generate_subtask(self, task: Task, component: Component) -> Subtask:
        """Generate a subtask within a task."""
        subtask_id = generate_ticket_id("SUBTASK", self.ticket_counter)
        self.ticket_counter += 1
        
        # Select subtask owner
        subtask_owner = random.choice(list(self.team_members.values()))
        
        # Find the product and initiative in the config
        product = None
        initiative = None
        if self.current_initiative:
            for p in self.config['products']:
                for i in p['initiatives']:
                    if i['name'] == self.current_initiative:
                        product = p
                        initiative = i
                        break
                if product:
                    break
        
        # Generate subtask content using GPT-4 with context
        prompt = f"""Generate a detailed subtask description for a software development project with the following context:
        Company: {self.config['company']['name']}
        Industry: {self.config['company']['industry']}
        Product: {product['name'] if product else 'Not specified'}
        Initiative: {initiative['name'] if initiative else 'Not specified'}
        Component: {component.value}
        Task: {task.summary}
        
        The subtask should:
        1. Focus on a specific implementation detail
        2. Include technical specifications
        3. Define testing requirements
        4. Specify documentation needs
        5. List dependencies
        6. Include estimated hours
        7. Consider security implications
        8. Define review requirements
        
        Format the response in markdown."""
        
        subtask_content = self.llm.generate_ticket_description(
            title=f"Subtask: Implement {component.value} Subcomponent",
            ticket_type="Subtask",
            component=component.value,
            prompt=prompt
        )
        
        # Generate summary from description
        summary = self.llm.generate_summary(subtask_content, "Subtask", component.value)
        
        # Parse the generated content to extract estimated hours and technical details
        estimated_hours = self.llm.extract_estimated_hours(subtask_content)
        technical_details = self.llm.extract_technical_details(subtask_content)
        
        subtask = Subtask(
            id=subtask_id,
            summary=summary,
            description=subtask_content,
            status=TicketStatus.IN_PROGRESS,
            priority=TicketPriority.MEDIUM,
            epic_link=task.epic_link,
            parent_ticket=task.id,
            reporter_id=subtask_owner.id,
            assignee_id=subtask_owner.id,
            components=[component],
            created_at=datetime.now() - timedelta(days=random.randint(1, 5)),
            updated_at=datetime.now() - timedelta(days=random.randint(1, 2)),
            estimated_hours=estimated_hours,
            technical_details=technical_details
        )
        
        self.subtasks[subtask_id] = subtask
        return subtask

    def generate_bug(self, component: Component, related_tickets: List[str] = None) -> Bug:
        """Generate a bug ticket."""
        bug_id = generate_ticket_id("BUG", self.ticket_counter)
        self.ticket_counter += 1
        
        # Select bug reporter and assignee
        reporter = random.choice(list(self.team_members.values()))
        assignee = random.choice(list(self.team_members.values()))
        
        bug = Bug(
            id=bug_id,
            summary=f"Bug: {component.value} Issue",
            description=self.llm.generate_ticket_description(
                title=f"Bug: {component.value} Issue",
                ticket_type="Bug",
                component=component.value
            ),
            status=TicketStatus.IN_PROGRESS,
            priority=TicketPriority.HIGH,
            severity=TicketPriority.HIGH,
            reporter_id=reporter.id,
            assignee_id=assignee.id,
            components=[component],
            created_at=datetime.now() - timedelta(days=random.randint(1, 10)),
            updated_at=datetime.now() - timedelta(hours=random.randint(1, 24)),
            related_tickets=related_tickets or [],
            steps_to_reproduce=[
                "Navigate to the affected page",
                "Enter test data",
                "Click submit button"
            ],
            actual_behavior="System shows error message",
            expected_behavior="System should process the request successfully"
        )
        
        self.bugs[bug_id] = bug
        return bug

    def generate_comment(self, ticket: Ticket, author: TeamMember) -> Comment:
        """Generate a comment for a ticket."""
        return Comment(
            id=generate_id("COM"),
            author_id=author.id,
            content=generate_paragraph(
                min_words=10,
                max_words=30,
                technical=random.random() > 0.5
            ),
            created_at=datetime.now() - timedelta(days=random.randint(1, 5)),
            reactions={"👍": [random.choice(list(self.team_members.keys()))]}
        )

    def generate_sprint(self, team_id: str, start_date: datetime = None) -> Sprint:
        """Generate a sprint for a team."""
        sprint_id = generate_id("SPR")
        if start_date is None:
            start_date = datetime.now()
        
        # Sprint duration from company config
        duration = timedelta(days=self.config.sprint_duration_days)
        end_date = start_date + duration
        
        # Generate sprint goal based on team's focus
        team = self.teams[team_id]
        tech_focus = random.choice(team.tech_stack).value if team.tech_stack else "general"
        
        sprint = Sprint(
            id=sprint_id,
            name=f"Sprint {self.sprint_counter}",
            goal=f"Improve {tech_focus} capabilities and deliver key features",
            start_date=start_date,
            end_date=end_date,
            status=SprintStatus.ACTIVE if start_date <= datetime.now() <= end_date else SprintStatus.PLANNED,
            team_id=team_id,
            demo_date=end_date - timedelta(days=1),
            planning_notes=generate_paragraph(min_words=20, max_words=50, formal=True)
        )
        
        self.sprints[sprint_id] = sprint
        self.sprint_counter += 1
        return sprint

    def generate_sprints_for_team(self, team_id: str, num_sprints: int = 3) -> List[Sprint]:
        """Generate a sequence of sprints for a team."""
        sprints = []
        current_date = datetime.now()
        
        # Generate past sprints
        for i in range(num_sprints - 1):
            start_date = current_date - timedelta(days=self.config.sprint_duration_days * (num_sprints - i))
            sprint = self.generate_sprint(team_id, start_date)
            if start_date + timedelta(days=self.config.sprint_duration_days) < current_date:
                sprint.status = SprintStatus.COMPLETED
                sprint.story_points_completed = int(sprint.story_points_committed * random.uniform(0.7, 1.0))
                sprint.velocity = sprint.story_points_completed / self.config.sprint_duration_days
                sprint.retrospective_notes = generate_paragraph(min_words=30, max_words=100, formal=True)
            sprints.append(sprint)
        
        # Generate current sprint
        current_sprint = self.generate_sprint(team_id, current_date)
        sprints.append(current_sprint)
        
        return sprints

    def assign_ticket_to_sprint(self, ticket: Ticket, sprint: Sprint):
        """Assign a ticket to a sprint and update relevant metrics."""
        ticket.sprint_id = sprint.id
        sprint.tickets.append(ticket.id)
        
        if hasattr(ticket, 'story_points') and ticket.story_points:
            sprint.story_points_committed += ticket.story_points
            if ticket.status == TicketStatus.DONE:
                sprint.story_points_completed += ticket.story_points

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

    def generate_sprint_tickets(self, sprint_id: str, team_id: str, num_tickets: int) -> List[Dict]:
        """Generate tickets for a sprint"""
        tickets = []
        epic = self.generate_epic(random.choice(list(self.teams.values())[0].components))
        tickets.append(epic)
        
        # Generate stories linked to epic
        for _ in range(num_tickets // 2):
            story = self.generate_story(epic, random.choice(epic.components))
            tickets.append(story)
            
            # Generate tasks linked to both story and epic
            for _ in range(2):
                task = self.generate_task(story, random.choice(story.components))
                tickets.append(task)
                
                # Generate subtasks linked to task, story, and epic
                for _ in range(2):
                    subtask = self.generate_subtask(task, random.choice(task.components))
                    tickets.append(subtask)
        
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
                sprints = self.generate_sprints_for_team(team.id)
                
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
        """Set the current product initiative to focus on."""
        if initiative_name not in PRODUCT_INITIATIVES:
            raise ValueError(f"Unknown product initiative: {initiative_name}")
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
            initiative_name = self.current_initiative or random.choice(list(PRODUCT_INITIATIVES.keys()))
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

Initiative: {initiative['description']}
Feature: {feature}
Team Focus Areas: {', '.join(team_focus)}
Objectives: {', '.join(initiative['objectives'])}
Success Metrics: {', '.join(initiative['success_metrics'])}

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
            prompt=prompt
        )

    def _generate_story_description(self, feature, scenarios, team_focus, tech_stack, initiative=None, specific_feature=None, persona=None):
        """Generate a detailed story description using GPT-4."""
        prompt = f"""Generate a detailed story description for a software development project with the following context:

Feature: {feature}
Specific Feature: {specific_feature}
Team Focus Areas: {', '.join(team_focus)}
Tech Stack: {', '.join(tech_stack)}
Persona: {persona['role']} - {', '.join(persona['needs'])}
Initiative: {initiative['description'] if initiative else 'None'}

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
            prompt=prompt
        )

    def _generate_bug_description(self, scenarios, team_focus, tech_stack, feature):
        """Generate a realistic bug description using GPT-4."""
        prompt = f"""Generate a detailed bug report for a software development project with the following context:

Feature: {feature}
Team Focus Areas: {', '.join(team_focus)}
Tech Stack: {', '.join(tech_stack)}

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
            prompt=prompt
        )

    def _generate_task_description(self, improvement, scenarios, team_focus, tech_stack, feature):
        """Generate a detailed technical task description using GPT-4."""
        prompt = f"""Generate a detailed technical task description for a software development project with the following context:

Improvement: {improvement}
Feature: {feature}
Team Focus Areas: {', '.join(team_focus)}
Tech Stack: {', '.join(tech_stack)}

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
            prompt=prompt
        ) 