import json
from datetime import datetime
from typing import Literal, cast
from dotenv import load_dotenv

from langchain_core.messages import AIMessage, SystemMessage, HumanMessage, ToolMessage
from langgraph.graph import StateGraph
from langgraph.types import Command
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool

from state import ResearchState
from config import Config

from tools.questions import getQuestions, getQuestionsByStep, getQuestionById
from query_builder import buildQuery, executeQuery

load_dotenv('.env')

cfg = Config()

class OnboardingAgent:
    def __init__(self):
        """
        Initialize the OnboardingAgent.
        """
        self._initialize_tools()
        self._build_workflow()

    def _initialize_tools(self):
        """
        Initialize the available tools and create a name-to-tool mapping.
        """
        self.tools = [getQuestions, getQuestionsByStep, getQuestionById]
        self.tools_by_name = {tool.name: tool for tool in self.tools}

    def _build_workflow(self):
        """
        Build the workflow graph with nodes and edges.
        """
        workflow = StateGraph(ResearchState)

        # Add nodes
        workflow.add_node("call_model_node", self.call_model_node)
        workflow.add_node("tool_node", self.tool_node)
        workflow.add_node("query_builder_node", self.query_builder_node)

        # Define graph structure
        workflow.set_entry_point("call_model_node")
        workflow.set_finish_point("call_model_node")
        workflow.add_edge("tool_node", "call_model_node")
        workflow.add_edge("query_builder_node", "call_model_node")

        self.graph = workflow.compile()

    def _build_system_prompt(self, state: ResearchState) -> str:
        """
        Build the system prompt based on current state.
        """
        prompt_parts = [
            "You are an expert onboarding assistant. Your goal is to help users answer questions and build queries.\n\n"
            "Follow these steps:\n"
            "1. Use getSteps tool to get the list of steps\n"
            "2. Use getQuestions tool to get the list of questions\n"
            "3. After getting questions, use the query builder agent to convert natural language descriptions into SOQL queries\n\n"
            "For SOQL queries:\n"
            "- Use buildQuery agent to convert natural language to SOQL\n"
            "- Use executeQuery agent to run the generated SOQL\n"
            "- Always verify the query results before proceeding\n\n"
        ]
        return "\n".join(prompt_parts)

    async def call_model_node(self, state: ResearchState, config: RunnableConfig) -> Command[Literal["tool_node", "query_builder_node", "__end__"]]:
        """
        Node for calling the model and handling the system prompt, messages, state, and tool bindings.
        """
        # Ensure last message is of correct type
        if not state.messages:
            state.messages.append(HumanMessage(content="Let's start by getting the steps."))

        last_message = state.messages[-1]
        if not isinstance(last_message, (AIMessage, SystemMessage, HumanMessage, ToolMessage)):
            last_message = HumanMessage(content=last_message.content)
            state.messages[-1] = last_message

        # Call LLM
        model = cfg.FACTUAL_LLM.bind_tools(self.tools, parallel_tool_calls=False)
        response = await model.ainvoke([
            SystemMessage(content=self._build_system_prompt(state)),
            *state.messages,
        ], config)

        # Add response to messages
        state.messages.append(response)

        response = cast(AIMessage, response)

        # If the LLM decided to use a tool, we go to the tool node. Otherwise, we end the graph.
        if response.tool_calls:
            # Check if we should route to query builder node
            if any(tool_call["name"] in ["buildQuery", "executeQuery"] for tool_call in response.tool_calls):
                return Command(goto="query_builder_node", update={"messages": response})
            return Command(goto="tool_node", update={"messages": response})
        return Command(goto="__end__", update={"messages": response})

    async def tool_node(self, state: ResearchState, config: RunnableConfig) -> Command[Literal["call_model_node"]]:
        """
        Process tool calls from the last message
        """
        if not state.messages or not state.messages[-1].tool_calls:
            return "call_model_node"

        msgs = []
        tool_state = {}
        for tool_call in state.messages[-1].tool_calls:
            # Add a state key to the tool call so the tool can access state
            tool_call["args"]["state"] = state
            # Call the tool
            result = await self.tools[tool_call["name"]].ainvoke(tool_call["args"], config)
            # Add result to messages
            msgs.append(ToolMessage(content=str(result), tool_call_id=tool_call["id"]))
            # Add result to tool state
            tool_state[tool_call["name"]] = result

        # Add tool messages to state
        state.messages.extend(msgs)
        return "call_model_node"

    async def query_builder_node(self, state: ResearchState, config: RunnableConfig) -> Command[Literal["call_model_node"]]:
        """
        Process query builder calls from the last message
        """
        if not state.messages or not state.messages[-1].tool_calls:
            return "call_model_node"

        msgs = []
        for tool_call in state.messages[-1].tool_calls:
            if tool_call["name"] == "buildQuery":
                query = await buildQuery(tool_call["args"])
                msgs.append(ToolMessage(content=str(query), tool_call_id=tool_call["id"]))

        # Add tool messages to state
        state.messages.extend(msgs)
        return "call_model_node"

graph = OnboardingAgent().graph
