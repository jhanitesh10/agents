from typing import List, Dict, Any, Optional
from langchain_core.tools import tool
from pydantic import BaseModel, Field
import logging
from datetime import datetime
from copilotkit.langchain import copilotkit_emit_state
from langchain_core.runnables import RunnableConfig

steps = [
    {
        "id": "step_1",
        "name": "Account Identification",
        "description": "Identify and verify the target account for onboarding",
        "is_completed": False,
        "order": 1
    },
    {
        "id": "step_2",
        "name": "Buying Roles",
        "description": "Identify key decision makers and their roles in the buying process",
        "is_completed": False,
        "order": 2
    },
    {
        "id": "step_3",
        "name": "Role Mapping",
        "description": "Map identified roles to their responsibilities and influence",
        "is_completed": False,
        "order": 3
    },
    {
        "id": "step_4",
        "name": "Value Messaging",
        "description": "Develop and align value propositions for different stakeholders",
        "is_completed": False,
        "order": 4
    },
    {
        "id": "step_5",
        "name": "Summary",
        "description": "Review and summarize the onboarding process and next steps",
        "is_completed": False,
        "order": 5
    }
]

class GetStepsInput(BaseModel):
    count: Optional[int] = Field(default=None, description="Number of steps to return")
    state: Optional[Dict] = Field(description="State of the steps")

@tool(
    "getSteps",
    args_schema=GetStepsInput,
    return_direct=True,
    description="Return a list of onboarding steps. Can optionally limit by count. If no count is provided, all steps will be returned."
)
async def getSteps(count: Optional[int] = None, state: Optional[Dict] = None) -> List[Dict[str, Any]]:
    """
    Returns a list of all steps with their details.

    Returns:
        List[Dict[str, Any]]: List of step details including id, name, description,
                             is_completed, and order
    """
    try:
        if state is None:
            state = {}

        logging.info(f"Getting steps with count: {count}")

        config = RunnableConfig()
        await copilotkit_emit_state(config, state)

        if count is not None:
            if count < 0:
                raise ValueError("Count cannot be negative")
            result = steps[:count]
        else:
            result = steps

        state["steps"] = result
        state["timestamp"] = datetime.now().isoformat()

        await copilotkit_emit_state(config, state)

        return state, result
    except Exception as e:
        logging.error(f"Error in getSteps: {str(e)}")
        raise

class GetStepByIdInput(BaseModel):
    stepId: str = Field(description="The ID of the step to retrieve")
    state: Optional[Dict] = Field(description="State of the steps")

@tool(
    "getStepById",
    args_schema=GetStepByIdInput,
    return_direct=True,
    description="Return a specific step by its ID."
)
async def getStepById(stepId: str, state: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Returns a specific step by its ID.

    Args:
        stepId (str): The ID of the step to retrieve

    Returns:
        Dict[str, Any]: Step details if found, empty dict if not found
    """
    try:
        if state is None:
            state = {}

        logging.info(f"Getting step with ID: {stepId}")

        config = RunnableConfig()
        await copilotkit_emit_state(config, state)

        if not stepId:
            raise ValueError("Step ID cannot be empty")

        result = next((step for step in steps if step["id"] == stepId), {})
        if not result:
            logging.warning(f"No step found with ID: {stepId}")

        state["step"] = result
        state["timestamp"] = datetime.now().isoformat()

        await copilotkit_emit_state(config, state)

        return state, result
    except Exception as e:
        logging.error(f"Error in getStepById: {str(e)}")
        raise
