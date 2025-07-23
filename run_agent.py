#!/usr/bin/env python3
"""
CLI script for running the Health Logger Agent.

This script provides a simple command-line interface to process health data
using natural language inputs and log them to Airtable.

Usage:
    python run_agent.py "I just measured my blood pressure: 120/80"
    python run_agent.py --help
"""

import argparse
import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.agent.agent import HealthLoggerAgent, log_health_data


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="Health Logger Agent - Process natural language health data and log to Airtable",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_agent.py "I just measured my blood pressure: 120/80 with heart rate 72"
  python run_agent.py "I weighed 175.2 lbs this morning"
  python run_agent.py "Had coffee with 95mg caffeine at 8am"
  python run_agent.py "Greek yogurt with berries - 180 calories, 20g protein"
  python run_agent.py "20 minute sauna session at 180°F"
  python run_agent.py "Glass of red wine (5oz, 13% alcohol) yesterday evening"

Supported Health Data Types:
  • Blood pressure & heart rate (heart_log)
  • Body measurements (body_log) 
  • Nutrition data (nutrition_log)
  • Caffeine intake (caffeine_log)
  • Alcohol consumption (alcohol_log)
  • Sauna sessions (sauna_log)

Configuration:
  Make sure your .env file is configured with:
  - AIRTABLE_PAT (Personal Access Token)
  - AIRTABLE_BASE_ID 
  - LLM_PROVIDER (ollama, openai, or claude)
  - Corresponding API keys for your chosen LLM provider
        """
    )
    
    parser.add_argument(
        "prompt",
        nargs="?",
        help="Natural language description of health data to log"
    )
    
    parser.add_argument(
        "--info",
        action="store_true",
        help="Show agent configuration information"
    )
    
    parser.add_argument(
        "--validate",
        action="store_true", 
        help="Validate configuration without processing data"
    )
    
    parser.add_argument(
        "--tools",
        action="store_true",
        help="List available logging tools"
    )
    
    args = parser.parse_args()
    
    # Handle info flag
    if args.info:
        try:
            agent = HealthLoggerAgent()
            info = agent.get_agent_info()
            print("🤖 Health Logger Agent Configuration:")
            print(f"LLM Provider: {info['llm_info']['provider']}")
            print(f"Model: {info['llm_info']['model']}")
            print(f"Timezone: {info['timezone']}")
            print(f"Airtable Configured: {'✅' if info['airtable_configured'] else '❌'}")
            print(f"Available Tools: {len(info['available_tools'])}")
            return
        except Exception as e:
            print(f"❌ Error getting agent info: {e}")
            sys.exit(1)
    
    # Handle validate flag
    if args.validate:
        try:
            agent = HealthLoggerAgent()
            validation = agent.validate_configuration()
            if validation["valid"]:
                print("✅ Configuration is valid!")
                if validation.get("airtable_connection") == "success":
                    print("✅ Airtable connection test passed")
                elif validation.get("airtable_connection") == "failed":
                    print("⚠️  Airtable connection test failed")
            else:
                print("❌ Configuration has errors:")
                for error in validation["errors"]:
                    print(f"  • {error}")
            
            if validation["warnings"]:
                print("⚠️  Warnings:")
                for warning in validation["warnings"]:
                    print(f"  • {warning}")
            return
        except Exception as e:
            print(f"❌ Error validating configuration: {e}")
            sys.exit(1)
    
    # Handle tools flag
    if args.tools:
        try:
            agent = HealthLoggerAgent()
            tools = agent.get_tool_descriptions()
            print("🛠️  Available Logging Tools:")
            for tool_name, description in tools.items():
                print(f"  • {tool_name}: {description}")
            return
        except Exception as e:
            print(f"❌ Error getting tools: {e}")
            sys.exit(1)
    
    # Handle main prompt processing
    if not args.prompt:
        parser.print_help()
        print("\n❌ Error: Please provide a health data prompt to process.")
        sys.exit(1)
    
    print(f"🔄 Processing: {args.prompt}")
    
    try:
        response = log_health_data(args.prompt)
        print(f"✅ Response: {response}")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()