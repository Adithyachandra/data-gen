import random
import string
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import uuid

def generate_id(prefix: str = "") -> str:
    """Generate a unique identifier with an optional prefix."""
    return f"{prefix}{str(uuid.uuid4())[:8]}"

def generate_email(first_name: str, last_name: str, domain: str) -> str:
    """Generate an email address from name components."""
    return f"{first_name.lower()}.{last_name.lower()}@{domain}"

def random_date_between(start_date: datetime, end_date: datetime) -> datetime:
    """Generate a random datetime between start_date and end_date."""
    time_between = end_date - start_date
    days_between = time_between.days
    random_days = random.randrange(days_between)
    return start_date + timedelta(days=random_days)

def weighted_choice(options: Dict[Any, float]) -> Any:
    """Choose an option based on weights."""
    items = list(options.items())
    weights = [item[1] for item in items]
    choices = [item[0] for item in items]
    return random.choices(choices, weights=weights, k=1)[0]

def generate_ticket_id(project_prefix: str, number: int) -> str:
    """Generate a JIRA-style ticket ID."""
    return f"{project_prefix}-{number}"

def random_subset(items: List[Any], min_items: int = 1, max_items: Optional[int] = None) -> List[Any]:
    """Select a random subset of items."""
    if max_items is None:
        max_items = len(items)
    count = random.randint(min_items, min(max_items, len(items)))
    return random.sample(items, count)

def generate_paragraph(
    min_words: int = 10,
    max_words: int = 50,
    technical: bool = False,
    formal: bool = False
) -> str:
    """Generate a paragraph of text with configurable style."""
    # Sample word banks for different styles
    technical_words = [
        "implement", "integrate", "optimize", "refactor", "deploy",
        "architecture", "database", "API", "interface", "component",
        "service", "module", "function", "class", "method",
        "system", "process", "algorithm", "framework", "platform"
    ]
    
    formal_words = [
        "additionally", "consequently", "furthermore", "however", "moreover",
        "therefore", "accordingly", "subsequently", "nevertheless", "whereas",
        "propose", "suggest", "recommend", "indicate", "demonstrate"
    ]
    
    common_words = [
        "the", "be", "to", "of", "and", "a", "in", "that", "have", "I",
        "it", "for", "not", "on", "with", "he", "as", "you", "do", "at"
    ]
    
    # Choose word bank based on style
    word_bank = common_words
    if technical:
        word_bank.extend(technical_words)
    if formal:
        word_bank.extend(formal_words)
    
    # Generate sentence
    num_words = random.randint(min_words, max_words)
    words = [random.choice(word_bank) for _ in range(num_words)]
    words[0] = words[0].capitalize()
    
    return " ".join(words) + "."

def generate_name() -> tuple[str, str]:
    """Generate a random first and last name."""
    first_names = [
        "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael",
        "Linda", "William", "Elizabeth", "David", "Barbara", "Richard", "Susan",
        "Joseph", "Jessica", "Thomas", "Sarah", "Charles", "Karen", "Christopher",
        "Nancy", "Daniel", "Lisa", "Matthew", "Betty", "Anthony", "Margaret",
        "Mark", "Sandra", "Donald", "Ashley", "Steven", "Kimberly", "Paul",
        "Emily", "Andrew", "Donna", "Joshua", "Michelle", "Kenneth", "Carol"
    ]
    
    last_names = [
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
        "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
        "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
        "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark",
        "Ramirez", "Lewis", "Robinson", "Walker", "Young", "Allen", "King",
        "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores", "Green"
    ]
    
    return random.choice(first_names), random.choice(last_names) 