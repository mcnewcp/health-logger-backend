# Health Logger Backend

A LangGraph-based health data logging system that processes natural language inputs containing health information and writes structured data to Airtable databases.

## Overview

This system uses a LangGraph agent to parse natural language descriptions of health activities and measurements, then automatically logs them to appropriate Airtable databases. It supports multiple LLM providers (Ollama, OpenAI, Claude) and handles six different types of health data.

## Features

### 🤖 Agent Architecture
- **LangGraph-based Agent**: Uses `create_react_agent` prebuilt functionality
- **Natural Language Processing**: Parses user prompts for health data
- **Multi-database Support**: Writes to 6 different health logging tables
- **Datetime Intelligence**: Handles relative time phrases with Central Time context

### 🔧 LLM Provider Flexibility
- **Multiple LLM Options**: Supports Ollama (local), OpenAI API, and Claude API
- **Config-driven Selection**: LLM provider chosen via configuration file
- **Future-proof Design**: Easy switching between local and cloud models

### 🗄️ Database Integration
Six specialized Airtable tables for different health metrics:
- **heart_log**: Blood pressure and heart rate measurements
- **body_log**: Body composition metrics (weight, muscle mass, body fat, water ratio)
- **nutrition_log**: Food intake with macro and micronutrient data
- **caffeine_log**: Caffeine consumption tracking
- **alcohol_log**: Alcohol consumption monitoring
- **sauna_log**: Sauna session duration logging

## Quick Start

### Prerequisites
- Python 3.10+
- UV (for dependency management)
- Airtable account with configured base and tables
- LLM provider (Ollama, OpenAI, or Claude API key)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/health-logger-backend.git
   cd health-logger-backend
   ```

2. **Install dependencies with UV**
   ```bash
   uv sync
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your actual configuration
   ```

### Environment Configuration

Edit your `.env` file with the following settings:

```env
# Airtable Configuration
AIRTABLE_PAT=your_personal_access_token_here
AIRTABLE_BASE_ID=your_base_id_here

# LLM Configuration
LLM_PROVIDER=ollama  # options: ollama, openai, claude
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here

# Application Configuration
TIMEZONE=America/Chicago
```

### Airtable Setup

Create an Airtable base with the following tables and fields:

#### heart_log
- Timestamp (DateTime)
- Blood Pressure (Text)
- Systolic BP (Number)
- Diastolic BP (Number) 
- Heart Rate (Number)
- Notes (Text)

#### body_log
- Timestamp (DateTime)
- Weight (lbs) (Number)
- Muscle Mass (lbs) (Number)
- Body Fat % (Number)
- Water % (Number)
- Notes (Text)

#### nutrition_log
- Timestamp (DateTime)
- Food Item (Text)
- Calories (Number)
- Protein (g) (Number)
- Carbs (g) (Number)
- Fat (g) (Number)
- Sodium (mg) (Number)
- Fiber (g) (Number)
- Notes (Text)

#### caffeine_log
- Timestamp (DateTime)
- Source (Text)
- Caffeine (mg) (Number)
- Notes (Text)

#### alcohol_log
- Timestamp (DateTime)
- Drink Type (Text)
- Volume (oz) (Number)
- Alcohol % (Number)
- Standard Units (Number)
- Notes (Text)

#### sauna_log
- Timestamp (DateTime)
- Duration (min) (Number)
- Temperature (°F) (Number)
- Notes (Text)

## Usage Examples

### Basic Usage

```python
from src.agent.agent import HealthLoggerAgent

agent = HealthLoggerAgent()

# Natural language input
response = agent.process("I just measured my blood pressure: 120/80 with heart rate 72")
print(response)
# Output: "Successfully logged heart data: 120/80 mmHg, 72 bpm at 2024-01-15 14:30:00 CST (Record ID: recXXXXXXXXXXXXXX)"

# Multiple data types
response = agent.process("Yesterday at noon I had a protein shake with 25g protein and 150mg sodium. This morning I weighed 170 lbs.")
print(response)
# Output: Multiple successful logs for nutrition and body data
```

### Convenience Functions

```python
from src.agent.agent import log_health_data

# Quick logging without managing agent instance
response = log_health_data("I had coffee this morning - about 95mg caffeine")
print(response)
```

### Async Usage

```python
import asyncio
from src.agent.agent import log_health_data_async

async def log_health():
    response = await log_health_data_async("20 minute sauna session at 180°F")
    print(response)

asyncio.run(log_health())
```

### Multi-step Logging

```python
response = agent.process("""
This morning I:
- Weighed 169.5 lbs with 15% body fat
- Had coffee (95mg caffeine) 
- Spent 20 minutes in the sauna at 180°F
""")
# Agent will parse and log to body_log, caffeine_log, and sauna_log
```

### Batch Processing

```python
inputs = [
    "Blood pressure 118/75, heart rate 68",
    "Greek yogurt with berries - 180 calories, 20g protein",
    "Glass of red wine (5oz, 13% alcohol)"
]

responses = agent.process_batch(inputs)
for response in responses:
    print(response)
```

## Supported Input Formats

### Blood Pressure & Heart Rate
- "My blood pressure is 125/82 with heart rate 68"
- "BP: 118/75, HR: 72 bpm this morning"
- "Just measured: 120/80 mmHg"

### Body Measurements
- "I weighed 175.2 lbs today"
- "Weight: 170 lbs, body fat: 15.2%, muscle mass: 145 lbs"
- "Morning weigh-in: 168 lbs, water 65%"

### Nutrition
- "I had a protein shake with 25g protein and 150 calories"
- "Lunch: grilled chicken, 400 cal, 35g protein, 5g carbs"
- "Greek yogurt with berries - 180 calories, 20g protein"

### Caffeine
- "I had a cup of coffee (95mg caffeine) this morning"
- "Green tea - about 40mg caffeine"
- "Energy drink with 160mg caffeine at 2pm"

### Alcohol
- "Glass of red wine (5oz, 13% alcohol)"
- "Two beers yesterday evening"
- "Cocktail with 1.5oz vodka (40% ABV)"

### Sauna
- "20 minute sauna session"
- "Spent 25 minutes in the sauna at 180°F"
- "Sauna: 15 minutes this morning"

## Time Parsing

The system intelligently parses time references:

- **Current time**: Used when no time specified
- **Relative times**: "yesterday", "this morning", "tonight"
- **Specific times**: "yesterday at 3pm", "this morning at 8am"
- **Relative offsets**: "2 hours ago", "yesterday evening"

All times are handled in the configured timezone (default: America/Chicago).

## Development

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=html

# Run specific test file
uv run pytest tests/test_agent.py -v

# Install dev dependencies if needed
uv sync --group dev
```

### Code Quality

```bash
# Format code
uv run black src tests

# Lint code
uv run ruff check src tests

# Type checking (if using mypy)
uv run mypy src
```

### Project Structure

```
health-logger-backend/
├── src/
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── agent.py          # Main agent definition
│   │   ├── tools.py          # Database writing tools
│   │   └── prompts.py        # System prompts
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py       # Application configuration
│   │   └── llm_config.py     # LLM provider configuration
│   └── utils/
│       ├── __init__.py
│       ├── datetime_utils.py # Time parsing utilities
│       └── airtable_client.py # Airtable API wrapper
├── tests/
│   ├── __init__.py
│   ├── test_agent.py
│   ├── test_tools.py
│   ├── test_utils.py
│   └── test_config.py
├── .env.example
├── pyproject.toml
├── uv.lock
└── README.md
```

## Configuration

### LLM Provider Selection

The system supports three LLM providers:

1. **Ollama** (Local)
   ```env
   LLM_PROVIDER=ollama
   OLLAMA_BASE_URL=http://localhost:11434
   OLLAMA_MODEL=llama3.1
   ```

2. **OpenAI**
   ```env
   LLM_PROVIDER=openai
   OPENAI_API_KEY=your_api_key_here
   ```

3. **Claude**
   ```env
   LLM_PROVIDER=claude
   ANTHROPIC_API_KEY=your_api_key_here
   ```

### Agent Information

```python
# Get agent configuration info
info = agent.get_agent_info()
print(info)

# Validate configuration
validation = agent.validate_configuration()
if not validation["valid"]:
    print("Configuration errors:", validation["errors"])
```

## Error Handling

The system provides comprehensive error handling:

- **Configuration errors**: Missing API keys, invalid settings
- **Parsing errors**: Invalid datetime strings, malformed data
- **Database errors**: Airtable API failures, connection issues
- **LLM errors**: Provider unavailability, rate limits

All errors are returned as descriptive messages to help with debugging.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Ensure code quality (black, ruff, pytest)
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions:
- Create an issue on GitHub
- Check the test files for usage examples
- Review the configuration documentation above
