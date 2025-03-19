# Software Company Data Generator

A powerful tool for generating synthetic data that simulates a software company's operations, including team structures, JIRA tickets, email discussions, and meeting transcripts.

## Features

1. **Team Structure Generation**
   - Auto-generate realistic team hierarchies
   - Customizable team roles and relationships
   - Modifiable team compositions

2. **JIRA-Style Ticket Generation**
   - Generate EPICs, Stories, Tasks, and Subtasks
   - Include FixVersions and Bugs
   - Realistic ticket assignments and relationships

3. **Email Discussion Generation**
   - Create realistic email threads related to tickets
   - Configurable scenarios and conversation flows
   - Natural language interactions between team members

4. **Meeting Transcript Generation**
   - Generate realistic meeting transcripts
   - Configurable meeting lengths and scenarios
   - Support for different meeting types (standup, planning, retrospective)

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and add your OpenAI API key

## Usage

[Documentation to be added as features are implemented]

## Configuration

The system can be configured through:
1. Environment variables
2. Configuration files in the `config` directory
3. Command-line arguments

## Contributing

[To be added]

## License

MIT License 