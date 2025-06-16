from typing import List, Dict, Any, Optional
from langchain_core.tools import tool
from pydantic import BaseModel, Field
import logging
from datetime import datetime
from copilotkit.langchain import copilotkit_emit_state
from langchain_core.runnables import RunnableConfig


questions = [
    # Account Identification Questions
    {
        "id": "question_1",
        "name": "How do you identify your customer accounts?",
        "description": "This helps Boomerang understand how to determine which accounts in your CRM represent actual customers versus prospects, partners, or other entities.",
        "is_answered": False,
        "step": {"id": "step_1"},
        "preview": {
            "enabled": True,
            "data_type": "text",
            "placeholder": "Enter company name"
        }
    },
    {
        "id": "question_2",
        "name": "Where do you capture the buying roles of the contacts (Decision Maker, Influencer, etc.)",
        "description": "This helps Boomerang understand the roles and responsibilities of the contacts in the buying process.",
        "is_answered": False,
        "step": {"id": "step_2"},
        "preview": {
            "enabled": True,
            "data_type": "select",
            "options": ["Technology", "Healthcare", "Finance", "Manufacturing", "Retail", "Other"]
        }
    },
]

class GetQuestionsInput(BaseModel):
    count: Optional[int] = Field(default=None, description="Number of questions to return")
    state: Optional[Dict] = Field(description="State of the questions")

@tool(
    "getQuestions",
    args_schema=GetQuestionsInput,
    return_direct=True,
    description="Return a list of onboarding questions. Can optionally limit by count. If no count is provided, all questions will be returned."
)
async def getQuestions(count: Optional[int] = None, state: Optional[Dict] = None) -> List[Dict[str, Any]]:
    """
    Returns a list of all questions with their details.

    Returns:
        List[Dict[str, Any]]: List of question details including id, name, description,
                                is_answered, step_id, and preview configuration
    """
    try:
        if state is None:
            state = {}

        logging.info(f"Getting questions with count: {count}")

        config = RunnableConfig()
        await copilotkit_emit_state(config, state)

        if count is not None:
            if count < 0:
                raise ValueError("Count cannot be negative")
            result = questions[:count]
        else:
            result = questions

        state.questions = result
        state.timestamp = datetime.now().isoformat()

        await copilotkit_emit_state(config, state)

        return state, result
    except Exception as e:
        logging.error(f"Error in getQuestions: {str(e)}")
        raise

class GetQuestionsByStepInput(BaseModel):
    stepId: str = Field(description="The ID of the step to get questions for")
    state: Optional[Dict] = Field(description="State of the questions")

@tool(
    "getQuestionsByStep",
    args_schema=GetQuestionsByStepInput,
    return_direct=True,
    description="Return a list of questions for a specific step ID."
)
async def getQuestionsByStep(stepId: str, state: Optional[Dict] = None) -> List[Dict[str, Any]]:
    """
    Returns questions for a specific step.

    Args:
        stepId (str): The ID of the step to get questions for

    Returns:
        List[Dict[str, Any]]: List of questions for the specified step
    """
    try:
        if state is None:
            state = {}

        logging.info(f"Getting questions for step: {stepId}")

        config = RunnableConfig()
        await copilotkit_emit_state(config, state)

        if not stepId:
            raise ValueError("Step ID cannot be empty")

        result = [q for q in questions if q["step"]["id"] == stepId]
        if not result:
            logging.warning(f"No questions found for step: {stepId}")

        state.questions = result
        state.timestamp = datetime.now().isoformat()

        await copilotkit_emit_state(config, state)

        return state, result
    except Exception as e:
        logging.error(f"Error in getQuestionsByStep: {str(e)}")
        raise

class GetQuestionByIdInput(BaseModel):
    questionId: str = Field(description="The ID of the question to retrieve")
    state: Optional[Dict] = Field(description="State of the questions")

@tool(
    "getQuestionById",
    args_schema=GetQuestionByIdInput,
    return_direct=True,
    description="Return a specific question by its ID."
)
async def getQuestionById(questionId: str, state: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Returns a specific question by its ID.

    Args:
        questionId (str): The ID of the question to retrieve

    Returns:
        Dict[str, Any]: Question details if found, empty dict if not found
    """
    try:
        if state is None:
            state = {}

        logging.info(f"Getting question with ID: {questionId}")

        config = RunnableConfig()
        await copilotkit_emit_state(config, state)

        if not questionId:
            raise ValueError("Question ID cannot be empty")

        result = next((q for q in questions if q["id"] == questionId), {})
        if not result:
            logging.warning(f"No question found with ID: {questionId}")

        state.question = result
        state.timestamp = datetime.now().isoformat()

        await copilotkit_emit_state(config, state)

        return state, result
    except Exception as e:
        logging.error(f"Error in getQuestionById: {str(e)}")
        raise
