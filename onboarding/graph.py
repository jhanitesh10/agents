import json
from datetime import datetime
from typing import Literal, cast, Dict, Any
from dotenv import load_dotenv
import logging
import uuid

from langchain_core.messages import AIMessage, SystemMessage, HumanMessage, ToolMessage
from langgraph.graph import StateGraph
from langgraph.types import Command
from langchain_core.runnables import RunnableConfig
from copilotkit.langchain import copilotkit_emit_state
from langchain_openai import ChatOpenAI

from state import OnboardingState
from config import Config

from tools.steps import getSteps, getStepById
from tools.questions import getQuestions, getQuestionsByStep, getQuestionById
from query_builder import QueryBuilderAgent

load_dotenv('.env')

cfg = Config()

class OnboardingAgent:
    def __init__(self):
        self.query_builder = QueryBuilderAgent()  # Initialize query_builder first
        self._initialize_tools()
        self._build_workflow()

    def _initialize_tools(self):
        # Initialize all available tools
        self.tools = [
            getSteps,
            getStepById,
            getQuestions,
            getQuestionsByStep,
            getQuestionById,
            self.query_builder.tools[0],  # buildQuery tool
            self.query_builder.tools[1],  # getQueryData tool
        ]
        # Create name mapping using the tool's name from the decorator
        self.tools_by_name = {
            "getSteps": getSteps,
            "getStepById": getStepById,
            "getQuestions": getQuestions,
            "getQuestionsByStep": getQuestionsByStep,
            "getQuestionById": getQuestionById,
            "buildQuery": self.query_builder.tools[0],
            "getQueryData": self.query_builder.tools[1],
        }

    def _build_workflow(self):
        # Create the graph
        workflow = StateGraph(OnboardingState)

        # Add nodes
        workflow.add_node("orchestrator", self.orchestrator_node)
        workflow.add_node("steps_node", self.steps_node)
        workflow.add_node("questions_node", self.questions_node)
        workflow.add_node("query_node", self.query_node)

        # Define the graph structure
        workflow.set_entry_point("orchestrator")

        # Add edges
        workflow.add_edge("orchestrator", "steps_node")
        workflow.add_edge("steps_node", "questions_node")
        workflow.add_edge("questions_node", "query_node")
        workflow.add_edge("query_node", "orchestrator")

        # Set finish point
        workflow.set_finish_point("orchestrator")

        # Initialize with default state
        initial_state = OnboardingState(
            messages=[HumanMessage(content="Let's start the onboarding process.")],
            steps=[],
            current_step=None,
            questions=[],
            query_results=None
        )

        # Compile the graph with the initial state
        self.graph = workflow.compile(initial_state)

    def _build_system_prompt(self, state: OnboardingState) -> str:
        return """You are an expert onboarding assistant. Follow these steps:
1. First, get the list of steps using getSteps
2. Then, get questions for the current step using getQuestions
3. Finally, use the query builder to generate and execute SOQL queries

Current State:
- Steps: {steps_count}
- Current Step: {current_step}
- Questions: {questions_count}
- Query Results: {has_results}
""".format(
            steps_count=len(state.steps) if state.steps else 0,
            current_step=state.current_step or "None",
            questions_count=len(state.questions) if state.questions else 0,
            has_results="Available" if state.query_results else "None"
        )

    async def orchestrator_node(self, state: OnboardingState, config: RunnableConfig) -> Command[Literal["steps_node", "questions_node", "query_node", "__end__"]]:
        """Main orchestrator node that decides the flow"""
        try:
            if not state.messages:
                state.messages = [HumanMessage(content="Let's start by getting the steps.")]
                return Command(goto="steps_node")

            # Call LLM to decide next step
            model = cfg.FACTUAL_LLM.bind_tools(self.tools, parallel_tool_calls=False)
            response = await model.ainvoke([
                SystemMessage(content=self._build_system_prompt(state)),
                *state.messages
            ], config)

            # Add response to messages
            state.messages.append(response)
            response = cast(AIMessage, response)

            # Check for tool calls in the response
            if hasattr(response, 'tool_calls') and response.tool_calls:
                tool_call = response.tool_calls[0]  # Get the first tool call
                tool_name = tool_call.get('name')

                # Route based on tool name
                if tool_name in ["buildQuery", "getQueryData"]:
                    return Command(goto="query_node")
                elif tool_name in ["getQuestions", "getQuestionsByStep", "getQuestionById"]:
                    return Command(goto="questions_node")
                elif tool_name in ["getSteps", "getStepById"]:
                    return Command(goto="steps_node")

            # Default routing based on state
            if not state.steps:
                return Command(goto="steps_node")
            elif not state.questions:
                return Command(goto="questions_node")
            elif not state.query_results:
                return Command(goto="query_node")

            return Command(goto="__end__")
        except Exception as e:
            logging.error(f"Error in orchestrator node: {str(e)}")
            # Add error message to state
            state.messages.append(SystemMessage(
                content=f"An error occurred: {str(e)}"
            ))
            return Command(goto="__end__")

    async def steps_node(self, state: OnboardingState, config: RunnableConfig) -> Command[Literal["orchestrator"]]:
        """Node for handling steps"""
        try:
            # Get steps
            result = await getSteps(state=state)
            if isinstance(result, dict) and "result" in result:
                state.steps = result["result"]
            else:
                state.steps = result

            # Set current step if not set
            if not state.current_step and state.steps:
                state.current_step = state.steps[0]["id"]

            return Command(goto="orchestrator")
        except Exception as e:
            logging.error(f"Error in steps node: {str(e)}")
            return Command(goto="orchestrator")

    async def questions_node(self, state: OnboardingState, config: RunnableConfig) -> Command[Literal["orchestrator"]]:
        """Node for handling questions"""
        try:
            if not state.current_step:
                return Command(goto="orchestrator")

            # Get questions for current step
            result = await getQuestionsByStep(stepId=state.current_step, state=state)
            if isinstance(result, dict) and "result" in result:
                state.questions = result["result"]
            else:
                state.questions = result

            return Command(goto="orchestrator")
        except Exception as e:
            logging.error(f"Error in questions node: {str(e)}")
            return Command(goto="orchestrator")

    async def query_node(self, state: OnboardingState, config: RunnableConfig) -> Command[Literal["orchestrator"]]:
        """Node for handling queries"""
        try:
            if not state.questions:
                return Command(goto="orchestrator")

            # Build and execute query for the first question
            question = state.questions[0]
            state, query_result = await self.query_builder.execute(
                query_description=question["description"],
                state=state
            )
            state.query_results = query_result

            return Command(goto="orchestrator")
        except Exception as e:
            logging.error(f"Error in query node: {str(e)}")
            return Command(goto="orchestrator")

# Create the graph instance
graph = OnboardingAgent().graph
