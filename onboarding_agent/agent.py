from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool

from .sub_agents.question_viewer.agent import question_viewer
from .sub_agents.query_builder_with_data.agent import query_builder_with_data

root_agent = Agent(
    name="onboarding_agent",
    model="gemini-2.0-flash",
    description="Onboarding agent who decide which agent to delegate to",
    instruction="""
    You are a manager agent that is responsible for overseeing the work of the other agents.

    Always delegate the task to the appropriate agent. Use your best judgement
    to determine which agent to delegate to.

    You are responsible for delegating tasks to the following agent:
    1: On first time or default call question_viewer agent to get the question with data preview and query suggestion.
    - question_viewer: get the question with data preview and query suggestion.
    2: On confirmation or sugggestion or update request , we need to call query builder to update the suggestion or build and get data from confirmation or suggestion all query related data.
    - query_builder_with_data: create query to perform crud operation and perform action.
    """,
    sub_agents=[question_viewer, query_builder_with_data],
    tools=[],
)