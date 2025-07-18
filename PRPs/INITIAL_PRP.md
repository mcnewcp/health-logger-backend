# Pull Request Preview: Health Logger Backend - Initial Setup

## Overview
This PR establishes the foundational architecture for a health data logging system using a LangGraph agent. The agent processes natural language inputs containing health information and writes structured data to Airtable databases.

## Key Features

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

## Technical Implementation

### 📁 Project Structure
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
│   └── test_utils.py
├── .env.example
├── requirements.txt
├── pyproject.toml
└── README.md
```

### 🛠️ Key Components

#### Agent Tools (6 tools, one per database)
- `write_heart_log()`: Logs blood pressure and heart rate
- `write_body_log()`: Records body composition metrics
- `write_nutrition_log()`: Tracks food intake and nutrients
- `write_caffeine_log()`: Monitors caffeine consumption
- `write_alcohol_log()`: Records alcohol intake
- `write_sauna_log()`: Logs sauna session duration

#### Configuration System
- Environment-based configuration using `python-dotenv`
- LLM provider selection (Ollama/OpenAI/Claude)
- Airtable API credentials and base IDs

#### Datetime Processing
- Central Time zone support
- Relative time phrase parsing ("yesterday at noon", "this morning")
- Optional datetime handling (defaults to current time if not specified)

## Dependencies

### Core Dependencies
- `langgraph`: Agent framework
- `pyairtable`: Airtable API client
- `python-dotenv`: Environment variable management
- `pydantic`: Data validation
- `python-dateutil`: Advanced datetime parsing

### LLM Providers
- `ollama`: Local LLM support
- `openai`: OpenAI API integration
- `anthropic`: Claude API integration

### Development Dependencies
- `pytest`: Unit testing framework
- `black`: Code formatting
- `ruff`: Linting and code quality

## Environment Configuration

The `.env.example` file will include:
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

## Testing Strategy

### Unit Tests Coverage
- **Agent functionality**: Prompt parsing and tool orchestration
- **Database tools**: Each logging tool with success/failure scenarios
- **Datetime utilities**: Time parsing and timezone handling
- **Configuration**: LLM provider switching and environment loading

### Test Categories
- **Expected use cases**: Standard health data logging scenarios
- **Edge cases**: Unusual input formats, missing data
- **Failure cases**: Invalid data, API errors, configuration issues

## Usage Examples

### Basic Usage
```python
from src.agent.agent import HealthLoggerAgent

agent = HealthLoggerAgent()

# Natural language input
response = agent.process("I just measured my blood pressure: 120/80 with heart rate 72")
# Output: "Successfully logged heart rate data: 120/80 mmHg, 72 bpm at 2024-01-15 14:30:00"

# Multiple data types
response = agent.process("Yesterday at noon I had a protein shake with 25g protein and 150mg sodium. This morning I weighed 170 lbs.")
# Output: "Successfully logged: 1) Nutrition data for protein shake, 2) Body weight measurement"
```

### Multi-step Logging
```python
response = agent.process("""
This morning I:
- Weighed 169.5 lbs with 15% body fat
- Had coffee (95mg caffeine) 
- Spent 20 minutes in the sauna
""")
# Agent will parse and log to body_log, caffeine_log, and sauna_log
```

## Development Environment Setup

1. **Virtual Environment**: Uses `uv` for dependency management
2. **Code Quality**: Black formatting + Ruff linting
3. **Testing**: Pytest with comprehensive coverage
4. **Documentation**: Google-style docstrings throughout

## Future Considerations

- **API Endpoint**: FastAPI wrapper for web interface
- **Data Validation**: Enhanced Pydantic models for input validation
- **Logging**: Structured logging for debugging and monitoring
- **Error Handling**: Robust error recovery and user feedback
- **Batch Processing**: Support for bulk data entry

## Files Created/Modified

### New Files
- `src/agent/agent.py` - Main agent implementation
- `src/agent/tools.py` - Database writing tools  
- `src/agent/prompts.py` - System prompts
- `src/config/settings.py` - Application configuration
- `src/config/llm_config.py` - LLM provider setup
- `src/utils/datetime_utils.py` - Time parsing utilities
- `src/utils/airtable_client.py` - Airtable API wrapper
- `tests/test_*.py` - Comprehensive test suite
- `.env.example` - Environment configuration template
- `requirements.txt` - Project dependencies
- `pyproject.toml` - UV/build configuration

### Modified Files
- `README.md` - Updated with setup instructions and usage examples

## Impact Assessment

### Benefits
- **Flexible Architecture**: Easy to extend with new health metrics
- **Multiple LLM Support**: Can switch between local and cloud models
- **Comprehensive Logging**: Covers major health tracking categories
- **User-friendly**: Natural language interface for data entry

### Risks
- **API Dependencies**: Relies on Airtable and LLM provider availability
- **Data Quality**: Natural language parsing may introduce errors
- **Configuration Complexity**: Multiple provider options require careful setup

## Next Steps

1. **Implementation**: Build core agent and tools
2. **Testing**: Comprehensive unit test coverage
3. **Documentation**: Complete README with setup instructions
4. **Validation**: Test with real health data scenarios
5. **Deployment**: Package for production use

---

This PRP outlines a robust, extensible health logging system that leverages modern AI agent architecture to provide an intuitive interface for health data management.