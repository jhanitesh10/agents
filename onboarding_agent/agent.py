from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool

from .sub_agents.question_viewer.agent import question_viewer
from .sub_agents.query_builder_with_data.agent import query_builder_with_data
from .sub_agents.get_started_agent.agent import get_started_agent

root_agent = Agent(
    name="onboarding_agent",
    model="gemini-2.0-flash",
    description="Onboarding agent who decide which agent to delegate to",
    instruction="""
You are the orchestrator responsible for managing the onboarding flow of a user to the CRM datablog schema.
Your primary role is to decide which sub-agent to delegate to based on the stage of onboarding.

Sub-agents and their roles:

2. question_viewer:
   - Presents **one question at a time** to guide the user through onboarding.
   - Shows a preview of the data and potential query suggestions.
   - Should be called **after get_started_agent**, or **on each subsequent interaction** that continues onboarding.

3. query_builder_with_data:
   - Responsible for handling confirmations, updates, or CRUD operations.
   - Builds and executes queries based on user suggestions or confirmations.
   - Returns final data preview or updated records.

Rules for delegation:
- On **step-by-step onboarding progression**: delegate to `question_viewer`.
- On **confirmation, suggestion, or request to update/view data**: delegate to `query_builder_with_data`.

Use clear internal logic to track where the user is in the flow. Avoid repeating steps unnecessarily
    """,
    sub_agents=[question_viewer, query_builder_with_data],
    tools=[],
)