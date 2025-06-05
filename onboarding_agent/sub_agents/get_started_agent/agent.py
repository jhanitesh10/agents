from google.adk.agents import Agent
from pydantic import BaseModel, Field
from typing import Optional, List, Literal, Dict, Union

class Suggestion(BaseModel):
    text: str = Field(..., description="Display text on the suggestion chip")
    prompt: str = Field(..., description="Instruction or prompt triggered when selected")
    metadata: Dict[str, str] = Field(
        ...,
        description="Structured data for action tracking"
    )

class TextComponent(BaseModel):
    type: Literal["text"]
    data: str = Field(..., description="Text content to display")

class SuggestionComponent(BaseModel):
    type: Literal["suggestion"]
    suggestions: List[Suggestion] = Field(..., description="List of suggestion chips")

Component = Union[TextComponent, SuggestionComponent]

class GetStartedOutputSchema(BaseModel):
    status: Literal["success", "error"]
    components: Optional[List[Component]] = None
    error_message: Optional[str] = None

def get_started_agent_tool() -> dict:
    """Returns onboarding start options as confirmation chips."""
    print(f"--- Tool: get_started_agent_tool called ---")

    try:
        return {
            "status": "success",
            "components": [
                {
                    "type": "text",
                    "data": "Welcome to your onboarding assistant."
                },
                {
                    "type": "suggestion",
                    "suggestions": [
                        {
                            "text": "Start Onboarding",
                            "prompt": "Start onboarding flow",
                            "metadata": {
                                "action": "start_onboarding",
                                "source": "get_started"
                            }
                        }
                    ]
                }
            ]
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Error generating onboarding components: {str(e)}"
        }

get_started_agent = Agent(
    name="get_started_agent",
    model="gemini-2.0-flash",
    description="An assistant that helps users start CRM workspace onboarding.",
    instruction="""
    You are a welcoming assistant that triggers when a user starts interacting with the CRM for the first time.

    IMPORTANT: You MUST follow these rules:
    1. ALWAYS use the get_started_agent_tool() to generate the response
    2. Return the tool's response exactly as received without modification
    3. Do not add any additional text or explanations
    4. Do not create custom responses - only use the tool's output

    The response structure will be validated against this schema:
    {
        "status": "success",
        "components": [
            {
                "type": "text",
                "data": "Welcome message"
            },
            {
                "type": "suggestion",
                "suggestions": [
                    {
                        "text": "Button text",
                        "prompt": "Action prompt",
                        "metadata": {
                            "action": "action_type",
                            "source": "get_started"
                        }
                    }
                ]
            }
        ]
    }

    Remember:
    - Only use get_started_agent_tool()
    - Return its response exactly
    - No additional content
    """,
    tools=[get_started_agent_tool],
    # output_schema=GetStartedOutputSchema,
    output_key="get_started_agent",
)