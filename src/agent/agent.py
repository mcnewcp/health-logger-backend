"""Main health logging agent implementation using LangGraph."""

from typing import Any, Dict, List, Optional

from langgraph.prebuilt import create_react_agent
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage

from ..config.llm_config import create_llm, get_model_info
from ..config.settings import Settings, settings
from .prompts import get_system_prompt
from .tools import get_all_tools


class HealthLoggerAgent:
    """
    LangGraph-based agent for parsing natural language health data and logging to Airtable.
    
    This agent uses the create_react_agent prebuilt functionality to process user inputs
    containing health information and automatically calls the appropriate logging tools.
    """
    
    def __init__(self, config: Settings = settings):
        """
        Initialize the health logging agent.

        Args:
            config (Settings): Application configuration settings.

        Raises:
            Exception: If agent initialization fails.
        """
        self.config = config
        
        try:
            # Initialize LLM
            self.llm = create_llm(config)
            
            # Get all tools
            self.tools = get_all_tools()
            
            # Create the agent using LangGraph's create_react_agent
            self.agent = create_react_agent(
                model=self.llm,
                tools=self.tools,
                prompt=get_system_prompt(),
            )
            
        except Exception as e:
            raise Exception(f"Failed to initialize HealthLoggerAgent: {e}") from e
    
    def process(self, user_input: str) -> str:
        """
        Process a natural language health data input and log to appropriate databases.

        Args:
            user_input (str): Natural language description of health data.

        Returns:
            str: Response message indicating what was logged or any errors.
        """
        try:
            # Create messages for the agent
            messages = [HumanMessage(content=user_input)]
            
            # Run the agent
            response = self.agent.invoke({"messages": messages})
            
            # Extract the final message from the response
            if response and "messages" in response:
                final_message = response["messages"][-1]
                return final_message.content if hasattr(final_message, 'content') else str(final_message)
            else:
                return "Agent completed processing but returned no response."
                
        except Exception as e:
            return f"Error processing health data: {str(e)}"
    
    async def process_async(self, user_input: str) -> str:
        """
        Asynchronously process a natural language health data input.

        Args:
            user_input (str): Natural language description of health data.

        Returns:
            str: Response message indicating what was logged or any errors.
        """
        try:
            # Create messages for the agent
            messages = [HumanMessage(content=user_input)]
            
            # Run the agent asynchronously
            response = await self.agent.ainvoke({"messages": messages})
            
            # Extract the final message from the response
            if response and "messages" in response:
                final_message = response["messages"][-1]
                return final_message.content if hasattr(final_message, 'content') else str(final_message)
            else:
                return "Agent completed processing but returned no response."
                
        except Exception as e:
            return f"Error processing health data: {str(e)}"
    
    def process_batch(self, user_inputs: List[str]) -> List[str]:
        """
        Process multiple health data inputs in batch.

        Args:
            user_inputs (List[str]): List of natural language health data descriptions.

        Returns:
            List[str]: List of response messages for each input.
        """
        responses = []
        for user_input in user_inputs:
            response = self.process(user_input)
            responses.append(response)
        return responses
    
    def get_available_tools(self) -> List[str]:
        """
        Get a list of available logging tools.

        Returns:
            List[str]: List of tool names available to the agent.
        """
        return [tool.name for tool in self.tools]
    
    def get_tool_descriptions(self) -> Dict[str, str]:
        """
        Get descriptions of all available tools.

        Returns:
            Dict[str, str]: Tool names mapped to their descriptions.
        """
        return {tool.name: tool.description for tool in self.tools}
    
    def get_agent_info(self) -> Dict[str, Any]:
        """
        Get information about the agent configuration.

        Returns:
            Dict[str, Any]: Agent configuration information.
        """
        return {
            "llm_info": get_model_info(self.config),
            "available_tools": self.get_available_tools(),
            "tool_descriptions": self.get_tool_descriptions(),
            "timezone": self.config.app.timezone,
            "airtable_configured": bool(
                self.config.airtable.personal_access_token and
                self.config.airtable.base_id
            ),
        }
    
    def validate_configuration(self) -> Dict[str, Any]:
        """
        Validate the current configuration and return status information.

        Returns:
            Dict[str, Any]: Configuration validation results.
        """
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": [],
        }
        
        # Check LLM configuration
        try:
            self.config.validate_required_keys()
        except ValueError as e:
            validation_results["valid"] = False
            validation_results["errors"].append(f"LLM configuration error: {e}")
        
        # Check Airtable configuration
        if not self.config.airtable.personal_access_token:
            validation_results["valid"] = False
            validation_results["errors"].append("Airtable Personal Access Token is not configured")
        
        if not self.config.airtable.base_id:
            validation_results["valid"] = False
            validation_results["errors"].append("Airtable Base ID is not configured")
        
        # Test Airtable connection if configured
        if (self.config.airtable.personal_access_token and 
            self.config.airtable.base_id):
            try:
                from ..utils.airtable_client import AirtableClient
                client = AirtableClient(self.config)
                client.test_connection()
                validation_results["airtable_connection"] = "success"
            except Exception as e:
                validation_results["warnings"].append(f"Airtable connection test failed: {e}")
                validation_results["airtable_connection"] = "failed"
        
        return validation_results


def create_health_logger_agent(config: Settings = settings) -> HealthLoggerAgent:
    """
    Factory function to create a health logger agent.

    Args:
        config (Settings): Application configuration settings.

    Returns:
        HealthLoggerAgent: Configured health logging agent.
    """
    return HealthLoggerAgent(config)


# Convenience functions for direct usage
def log_health_data(user_input: str, config: Settings = settings) -> str:
    """
    Convenience function to quickly log health data without managing an agent instance.

    Args:
        user_input (str): Natural language description of health data.
        config (Settings): Application configuration settings.

    Returns:
        str: Response message indicating what was logged or any errors.
    """
    agent = create_health_logger_agent(config)
    return agent.process(user_input)


async def log_health_data_async(user_input: str, config: Settings = settings) -> str:
    """
    Convenience function to asynchronously log health data.

    Args:
        user_input (str): Natural language description of health data.
        config (Settings): Application configuration settings.

    Returns:
        str: Response message indicating what was logged or any errors.
    """
    agent = create_health_logger_agent(config)
    return await agent.process_async(user_input)


# Default agent instance for module-level usage
_default_agent: Optional[HealthLoggerAgent] = None


def get_default_agent() -> HealthLoggerAgent:
    """
    Get the default agent instance (singleton pattern).

    Returns:
        HealthLoggerAgent: Default agent instance.
    """
    global _default_agent
    if _default_agent is None:
        _default_agent = create_health_logger_agent()
    return _default_agent