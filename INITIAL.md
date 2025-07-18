## FEATURE:

### Overview
The repo is initially empty and so this feature will define the initial functionality of the project.  This feature should consist of an agent architecture, designed in LangGraph.  The agent should take in a natural language prompt from the user, containing one or more pieces of health information.  The agent should write the health information to the corresponding database using its tools.

### Design
The objective of this agent is quite simple, so using the `create_react_agent` prebuilt from langgraph should provide enough functionality.  The agent should parse the prompt for any health data, format into the expected format as defined by its tools, and write the data to the corresponding database(s) by calling tools.  The agent should continue until it has written all relevant data.  It should then respond with a message summarizing all data that it successfully logged.  It would probably be simplest and most transparent to simply write one tool per database.  This would simplify schema definitions.  The tools should use the python airtable api to write to specified airtable tables.  

The instructions to the agent should include the current datetime, in American Central time.  The user may prompt with relative time phrases, like "yesterday at noon" and so the agent must be able to derive an exact datetime.

### LLM
The agent will initially be powered by an LLM running locally, using ollama.  I may want to later switch this to a cloud model.  Because of this, the following LLM options should be included in the codebase, and the selection should be defined in a config file:
- ollama local
- openai api
- claude api

### Databases
All databases are hosted on airtable and they are defined below with table names followed by the data that can be provided to each.  All values are required, except for datetime.  If the agent does not provide a datetime, airtable will simply insert the current datetime, so if the user states that the health data is current, e.g. "I just took the following heart measurement...", the agent does not need to provide it to the logging tool.  

**heart_log**
- datetime (timestamp): the datetime of the measurement
- systolic_mmhg (int): systolic pressure measurement
- diastolic_mmhg (int): diastolic pressure measurement
- rate_bpm (int): heart rate measurement

**body_log**
- datetime (timestamp): the datetime of the measurement
- weight_lb (float): body weight in lbs
- smm_lb (float): skeletal muscle mass in lbs
- pbf (float): percent body fat, in decimal form, e.g. 0.14
- ecw_tcw (float): extracellular water to total body water ratio in decimal format, e.g. 0.4

**nutrition_log**
- datetime (timestamp): the datetime of the food consumption
- short_description (str): A brief one-line description of the food item
- protein_g (float): Amount of protein in grams
- sodium_mg (float): Amount of sodium in milligrams
- potassium_mg (float): Amount of potassium in milligrams
- long_description (str): A detailed description of the food item with context

**caffeine_log**
- datetime (timestamp): the datetime of the measurement
- item_description (str): a short, couple word description of the item being logged, e.g. "green tea"
- caffeine_mg (float): the amount of caffeine in mg

**alcohol_log**
- datetime (timestamp): the datetime of the measurement
- item_description (str): a short, couple word description of the item being logged, e.g. "pint of beer"
- alcohol_oz (float): the amount of alcohol consumed, in ounces

**sauna_log**
- datetime (timestamp): the datetime of the measurement
- duration_min (int): the amount of time spent in the sauna in minutes

## EXAMPLES:

### Logging Tool
This is an example of a similar logging tool implementation.  It logs body data to an airtable data table.  This uses the `function_tool` decorator from openai's agent framework, so that will have to be modified.  Also, it doesn't log datetime, so that will have to be included.

```
import os
from agents import Agent, function_tool
from pyairtable import Api

# setup body data log tool
@function_tool
def write_body_log(
    weight_lb: float,
    smm_lb: float,
    pbf: float,
    ecw_tbw: float
) -> str:
    """
    Write body composition information to the user's external log.
    
    This tool allows recording of body composition metrics for the user into a persistent
    storage system. It captures 4 metrics - weight, skeletal muscle mass, body fat percentage, and ECW/TBW ratio.
    
    Args:
        weight_lb (float): Body weight in lbs
        smm_lb (float): Skeletal muscle mass in lbs
        pbf (float): Body fat percentage in decimal format, e.g. 0.25 for 25%
        ecw_tbw (float): Extracellular water to total body water ratio in decimal format, e.g. 0.4 for 40%
    
    Returns:
        str: The record ID of the created entry if successful
    
    Example:
        record_id = write_body_log(169.7, 82.5, 0.150, 0.365)
    """
    api = Api(os.getenv("AIRTABLE_PAT"))
    table = api.table(os.getenv("AIRTABLE_BASE_ID"), "body_log")
    
    record = table.create({
        "weight_lb": weight_lb,
        "smm_lb": smm_lb,
        "pbf": pbf,
        "ecw_tbw": ecw_tbw
    })
    
    return record["id"]
```

## DOCUMENTATION:

### LangGraph
for ANY question about LangGraph, use the langgraph-docs-mcp server to help answer -- 
+ call list_doc_sources tool to get the available llms.txt file
+ call fetch_docs tool to read it
+ reflect on the urls in llms.txt 
+ reflect on the input question 
+ call fetch_docs on any urls relevant to the question

### Airtable 
`pyairtable` is the python library for working with the airtable api.  This library should be used to connect the agent's tools to the health data tables.  The documentation can be found at: https://pyairtable.readthedocs.io/en/stable/getting-started.html

## OTHER CONSIDERATIONS:

- Include a .env.example, which should include examples of all environment variables which the developer needs to provide in their `.env` file
- Include the project structure in the README.
- Use python_dotenv and load_env() for environment variables.
- A virtual environment has not yet been setup.  Please use `uv` to do so and install all required dependencies into the virtual environment.
