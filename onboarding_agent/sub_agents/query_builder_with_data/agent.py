from google.adk.agents import Agent
from google.adk.tools.tool_context import ToolContext


def update_field_or_attribute(topic: str, tool_context: ToolContext) -> dict:
    """Get a nerdy joke about a specific topic."""
    print(f"--- Tool: update_field_or_attribute called for topic: {topic} {tool_context}---")


    return {"status": "success", "query": 'select * from account where accountType = "customer"', "topic": topic}


# Create the funny nerd agent
query_builder_with_data = Agent(
    name="query_builder_with_data",
    model="gemini-2.0-flash",
    description="An agent that tells nerdy jokes about various topics.",
    instruction="""
    You are a query builder  agent that helps user build a mysql query for different operation get, create, udpate attribute, udpate values like field or attribute.

    When asked to update a field or attribute:
    Use the update_field_or_attribute tool to update a field or attribute about the requested topic. Create sql query to update the field or attribute for specific entity.

    Available entities include:
    - account
    - contact
    - opportunity

    schema:
    account: this is schema for account entity
    {
    "id": { "type": "string", "description": "The id of the entity" },
    "name": { "type": "string", "description": "The name of the entity" },
    "type": { "type": "string", "description": "The type to find account type" },
    "type_c": { "type": "string", "description": "The type to find account type" },
    "ownerId": { "type": "string", "description": "The id of the owner" },
    "owner_c": { "type": "string", "description": "The name of the custom owner" }
    }
    use tool update_field_or_attribute.

    """,
    tools=[update_field_or_attribute],
)
